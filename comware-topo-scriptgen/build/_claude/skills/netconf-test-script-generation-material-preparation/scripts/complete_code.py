# complete_code.py

import os
import re
import asyncio
import shutil
import threading
import time
import datetime
import pandas as pd
import subprocess
from typing import List, Dict, Any
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, ResultMessage

# --- 全局常量 ---
DEBUG_PROMPT_PATH = r"d:\文档\netconf\debug_prompt"
# 如果调试目录已存在且在此列表中，则会被删除重建
NEED_RE_DEBUG = ["ACL_Intervals_debug", "ACL_IPv4AdvanceRules_debug"]  # (此处省略了您的完整列表)


# --- 辅助类与函数 ---

class ThreadSafeLogger:
    # 线程安全的日志记录器
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        with self.lock:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_message)
        print(log_message.strip())

    def error(self, message: str):
        self.log(message, "ERROR")


def copy_specified_files(src_dir, dst_dir, file_names=None):
    """
    从源目录中拷贝指定文件名的文件到目标目录（递归查找）
    假如filename为空，则拷贝原文件夹下所有文件

    Args:
        src_dir (str): 源目录
        dst_dir (str): 目标目录
        file_names (list[str], optional): 需要拷贝的文件名列表（包含扩展名）
    """
    os.makedirs(dst_dir, exist_ok=True)
    copied = 0

    for root, _, files in os.walk(src_dir):
        for file in files:
            # 如果file_names为None或文件在指定列表中，则拷贝文件
            if file_names is None or file in file_names:
                src_path = os.path.join(root, file)
                dst_path = os.path.join(dst_dir, file)
                shutil.copy2(src_path, dst_path)
                copied += 1
                print(f"已拷贝: {src_path} -> {dst_path}")

    if copied == 0:
        print("未找到指定文件。")
    else:
        print(f"拷贝完成，共拷贝 {copied} 个文件。")


async def run_claude_step(client: ClaudeSDKClient, prompt: str, task_start_time: float, timeout_seconds: int,
                          logger: ThreadSafeLogger) -> Dict[str, Any]:
    # 执行单个Claude步骤，包含超时和429错误重试逻辑
    result_data = {'prompt': prompt, 'success': False, 'error': None, 'cost': 0, 'duration': 0}
    attempt = 0
    while True:
        attempt += 1
        step_start_time = time.time()

        if time.time() - task_start_time > timeout_seconds:
            result_data['error'] = "任务在API调用前已超时"
            logger.error("任务超时，放弃重试。")
            return result_data

        try:
            response_text_parts = []
            logger.log(f"开始Claude API调用 (第 {attempt} 次尝试)...")
            await client.query(prompt)

            async for message in client.receive_response():
                if time.time() - task_start_time > timeout_seconds:
                    await client.interrupt()
                    result_data.update({'error': "接收响应时超时", 'success': False})
                    return result_data

                if isinstance(message, AssistantMessage):
                    response_text_parts.extend(block.text for block in message.content if hasattr(block, 'text'))
                elif isinstance(message, ResultMessage):
                    result_data.update({
                        'cost': message.total_cost_usd,
                        'success': not message.is_error,
                        'error': message.result if message.is_error else None
                    })
                    break

            result_data['duration'] = time.time() - step_start_time
            result_data['analysis'] = ''.join(response_text_parts)

            if result_data['success']:
                logger.log(f"Claude API调用成功 (尝试次数: {attempt}).")
                return result_data
            else:
                logger.error(f"Claude API返回逻辑错误: {result_data.get('error')}")
                return result_data

        except Exception as e:
            error_str = str(e)
            logger.log(f"Claude API调用失败 (尝试次数: {attempt}): {error_str}", "WARNING")
            result_data['error'] = error_str
            if "API Error: 429" in error_str:
                wait_seconds = 60
                match = re.search(r'limit will reset at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', error_str)
                if match:
                    reset_time = datetime.datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                    wait_seconds = max(2, (reset_time - datetime.datetime.now()).total_seconds() + 2)

                if (time.time() + wait_seconds) > (task_start_time + timeout_seconds):
                    logger.error("等待时间将导致任务超时，放弃重试。")
                    return result_data

                logger.log(f"触发API速率限制。等待 {wait_seconds:.0f} 秒后重试...")
                await asyncio.sleep(wait_seconds)
                continue
            else:
                logger.error("发生不可恢复的错误，不再重试。")
                return result_data


async def append_result_to_excel(result: Dict[str, Any], filename: str, lock: asyncio.Lock):
    # 安全地将结果追加到Excel文件
    if not isinstance(result, dict) or 'folder' not in result:
        return
    records = []
    folder_name = result['folder']
    if not result.get('step_results'):
        records.append({'Folder': folder_name, 'Step Name': 'Initialization', 'Success': result.get('success', False),
                        'Error': result.get('error', 'No steps executed')})
    else:
        for step_res in result['step_results']:
            records.append(
                {'Folder': folder_name, 'Step Name': step_res.get('step_name'), 'Success': step_res.get('success'),
                 'Cost ($)': step_res.get('cost'), 'Duration (s)': step_res.get('duration'),
                 'Error': step_res.get('error'), 'Prompt': step_res.get('prompt'),
                 'Claude Analysis': step_res.get('analysis')})
    new_df = pd.DataFrame(records).reindex(
        columns=['Folder', 'Step Name', 'Success', 'Cost ($)', 'Duration (s)', 'Error', 'Prompt', 'Claude Analysis'])
    async with lock:
        try:
            existing_df = pd.read_excel(filename) if os.path.exists(filename) else pd.DataFrame()
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_excel(filename, index=False, engine='openpyxl')
            print(f"💾 已将 '{folder_name}' 的报告保存到Excel。")
        except Exception as e:
            print(f"❌ 保存 '{folder_name}' 的报告到Excel失败: {e}")


def generate_summary_report(results: List[Dict[str, Any]], total_time: float, report_title: str):
    # 生成最终的控制台汇总报告
    successful = [r for r in results if isinstance(r, dict) and r.get('success')]
    total_cost = sum(r.get('total_cost', 0) for r in successful)
    print("\n" + "=" * 60 + f"\n📊 {report_title} 汇总报告\n" + "=" * 60)
    print(f"📁 总任务数: {len(results)}")
    print(f"✅ 成功: {len(successful)}")
    print(f"❌ 失败: {len(results) - len(successful)}")
    print(f"💰 总成本 (仅统计成功任务): ${total_cost:.4f}")
    print(f"⏱️  总耗时: {total_time:.2f} 秒 ({total_time / 60:.2f} 分钟)")
    print("=" * 60)


# --- 核心处理逻辑 ---

async def process_completion_folder(folder_path: str, logger: ThreadSafeLogger, timeout_minutes: int) -> Dict[str, Any]:
    # 处理单个文件夹的代码补全和备份任务
    task_start_time = time.time()
    folder_name = os.path.basename(folder_path)
    result = {'folder': folder_name, 'success': False, 'step_results': [], 'total_cost': 0, 'total_duration': 0}

    try:
        # 步骤 1: 代码补全
        logger.log(f"--- 开始为 {folder_name} 补全代码 ---")
        script_path = os.path.join(folder_path, "test_netconf.py")
        if os.path.exists(script_path) and "test_step_2" in open(script_path, "r", errors="ignore").read():
            logger.log("代码已补全，跳过此步骤。")
            completion_res = {'step_name': 'CodeCompletion', 'success': True, 'duration': 0, 'cost': 0}
        else:
            options = ClaudeAgentOptions(system_prompt={"type": "preset", "preset": "claude_code"},
                                         allowed_tools=["Bash", "Edit", "Glob", "Grep", "Read", "Write"],
                                         permission_mode="bypassPermissions", cwd=folder_path)
            async with ClaudeSDKClient(options=options) as client:
                prompt = "读claude.md补全test_netconf.py文件代码,中途不要询问我。"
                completion_res = await run_claude_step(client, prompt, task_start_time, timeout_minutes * 60, logger)
            completion_res['step_name'] = 'CodeCompletion'

        result['step_results'].append(completion_res)
        if not completion_res.get('success'):
            raise Exception(f"代码补全失败: {completion_res.get('error', '未知错误')}")
        logger.log("✅ 代码补全成功。")

        # 步骤 2: 创建或更新调试目录
        
        logger.log(f"--- 为 {folder_name} 准备调试环境 ---")
        debug_folder_path = f"{folder_path}_debug"

        if os.path.exists(debug_folder_path):
            logger.log(f"发现旧的调试文件夹且需要重新调试，正在删除: {debug_folder_path}", "WARNING")
            shutil.rmtree(debug_folder_path)


        shutil.copytree(folder_path, debug_folder_path)
        logger.log(f"已创建调试备份文件夹: {debug_folder_path}")
        copy_specified_files(DEBUG_PROMPT_PATH, debug_folder_path)


        result['success'] = True





    except Exception as e:
        result['error'] = str(e)
        logger.error(f"处理 {folder_name} 时发生错误: {e}")

    result['total_duration'] = time.time() - task_start_time
    result['total_cost'] = sum(r.get('cost', 0) for r in result['step_results'])
    return result


async def main():
    # 主函数
    destination_folder = r"D:\\yang\\B75_yin\\generated_modules"
    folders_to_process = [f.path for f in os.scandir(destination_folder) if
                          f.is_dir() and not f.name.endswith('_debug')]

    if not folders_to_process:
        print("未找到需要处理的文件夹。")
        return

    max_concurrent = 1
    timeout_minutes = 30
    excel_filename = os.path.join(destination_folder, "1_completion_report.xlsx")
    excel_lock = asyncio.Lock()

    if os.path.exists(excel_filename):
        os.remove(excel_filename)
        print(f"已删除旧报告: {excel_filename}")

    print(f"开始为 {len(folders_to_process)} 个文件夹进行代码补全...")
    start_time = time.time()

    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = []

    async def run_with_semaphore(folder_path):
        async with semaphore:
            logger = ThreadSafeLogger(os.path.join(folder_path, "completion_log.txt"))
            result = await process_completion_folder(folder_path, logger, timeout_minutes)
            await append_result_to_excel(result, excel_filename, excel_lock)
            return result

    for folder in folders_to_process:
        tasks.append(run_with_semaphore(folder))

    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time

    generate_summary_report(results, total_time, "代码补全")
    print(f"🎉 补全流程结束！报告已保存至 {excel_filename}")


if __name__ == "__main__":
    os.environ['ANTHROPIC_BASE_URL'] = 'https://open.bigmodel.cn/api/anthropic'
    os.environ['ANTHROPIC_AUTH_TOKEN'] = 'eb8424b62e54473491ec97f32bbccee6.Oz7nZBCmYoqsu1o2'
    os.environ["API_TIMEOUT_MS"] = "3000000"
    os.environ["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

    asyncio.run(main())