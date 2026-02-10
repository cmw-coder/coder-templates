import os
import re
import json
import asyncio
import threading
import time
import datetime
import subprocess
import pandas as pd
from typing import List, Dict, Any
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, ResultMessage
import tkinter
from tkinter import messagebox

# 创建隐藏的主窗口
root = tkinter.Tk()
root.withdraw()

# --- 辅助类与函数 ---
# --- 辅助类与函数 ---
success_check_str = """
+-------+------+------+-------+------+---------+
|   1   |  1   |  0   |   0   |  0   | 100.00% |
+-------+------+------+-------+------+---------+
"""

error_check_str = """
+-------+------+------+-------+------+--------+
|   1   |  0   |  0   |   1   |  0   | 0.00%  |
+-------+------+------+-------+------+--------+
"""

workflow_prompt = r"""
请使用以下步骤修复test_netconf.py代码:
工作流程：
while True:
    测试执行"D:\\RDTestClientData\\Common\\tools\\Python38\\python.exe" -u -m pytest "当前文件夹下的test_netconf.py绝对路径" --custom-check="{'skip-steps':0}" --testbed="当前文件夹下的test_bed.tbdx绝对路径" --script-log-path="当前文件夹路径\log" -s -W ignore::UserWarning -p no:cacheprovider --tb short， 结合设备响应消息和实际返回报文分析控制台日志。命令执行的比较久，命令执行过程中不要做其他事情,等待命令执行完毕。
    for 循环三次
        识别第一个失败的 `test_step` 函数，注意每次只修复第一个失败的测试步骤，然后再次执行命令
        结合实际返回的报文分析和检查项分析失败原因，检查失败步骤中发送的 XML 配置
        与 yin.txt和netconf.txt中模型规范进行比较，两者参数信息冲突时以yin.txt为主
        修复 XML 配置以确保测试正确执行
        循环重新运行测试以验证成功
    
    执行命令，所有测试步骤pass，退出循环


**为什么要for循环内部只修复第一个错误的测试步骤下发的xml？**
**回答：因为每个测试步骤之间测试的参数是互相关联的，后面错误的测试结果可能是前面错误测试步骤导致的。所以要每修复第一个错误的测试步骤，都要重新执行命令。**
"""

class ThreadSafeLogger:
    # 线程安全的日志记录器
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        with self.lock:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_message)
        print(log_message.strip())

    def error(self, message: str):
        self.log(message, "ERROR")

def run_pytest_and_check(folder_path: str) -> str:
    # 执行pytest命令并返回其完整的输出
    python_path = r"D:\\RDTestClientData\\Common\\tools\\Python38\\python.exe"
    test_script = os.path.join(folder_path, "test_netconf.py")
    test_bed = os.path.join(folder_path, "test_bed.tbdx")
    log_path = os.path.join(folder_path, "log")
    cmd = [python_path, "-u", "-m", "pytest", test_script, '--custom-check={"skip-steps":0}', f"--testbed={test_bed}",
           f"--script-log-path={log_path}", "-s", "-W", "ignore::UserWarning", "-p", "no:cacheprovider", "--tb",
           "short"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        return result.stdout + result.stderr
    except Exception as e:
        error_message = f"执行pytest命令时出错: {e}"
        print(error_message)
        return error_message

async def run_claude_step(client: ClaudeSDKClient, prompt: str, task_start_time: float, timeout_seconds: int,
                          logger: ThreadSafeLogger) -> Dict[str, Any]:
    # 执行单个Claude步骤，包含超时和429错误重试逻辑
    result_data = {'prompt': prompt, 'success': False, 'error': None, 'cost': 0.0, 'duration': 0.0}
    attempt = 0
    while True:
        attempt += 1
        step_start_time = time.time()
        if time.time() - task_start_time > timeout_seconds:
            result_data['error'] = "任务在API调用前已超时"
            logger.error(f"任务超时 ({timeout_seconds}秒), 放弃重试。")
            return result_data
        try:
            response_text_parts = []
            logger.log(f"开始Claude API调用 (第 {attempt} 次尝试)...")
            await client.query(prompt)
            async for message in client.receive_response():
                if time.time() - task_start_time > timeout_seconds:
                    await client.interrupt()
                    result_data.update({'error': f"接收响应时超时 ({timeout_seconds}秒)", 'success': False})
                    return result_data
                if isinstance(message, AssistantMessage):
                    response_text_parts.extend(block.text for block in message.content if hasattr(block, 'text'))
                elif isinstance(message, ResultMessage):
                    result_data.update({'cost': message.total_cost_usd, 'success': not message.is_error,
                                        'error': message.result if message.is_error else None})
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

def excel_to_json(excel_filename: str, json_filename: str) -> bool:
    """将旧Excel报告转换为JSON格式，返回转换是否成功"""
    print(f"\n🔄 检测到旧Excel报告：{excel_filename}，开始转换为JSON...")
    try:
        # 读取Excel文件
        df = pd.read_excel(excel_filename, engine='openpyxl')
        
        # 验证必要列是否存在
        required_columns = ['Folder', 'Step Name', 'Success', 'Cost ($)', 'Duration (s)', 'Error', 'Prompt', 'Claude Analysis']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            print(f"❌ Excel文件缺少必要列：{missing_cols}，转换失败")
            return False
        
        # 填充缺失值，确保数据格式统一
        df = df.fillna({
            'Cost ($)': 0.0,
            'Duration (s)': 0.0,
            'Error': '',
            'Prompt': '',
            'Claude Analysis': ''
        })
        
        # 转换为JSON格式（添加Last Updated字段）
        json_data = []
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for _, row in df.iterrows():
            json_data.append({
                'Folder': str(row['Folder']),
                'Step Name': str(row['Step Name']),
                'Success': bool(row['Success']),
                'Cost ($)': round(float(row['Cost ($)']), 4),
                'Duration (s)': round(float(row['Duration (s)']), 2),
                'Error': str(row['Error']),
                'Prompt': str(row['Prompt']),
                'Claude Analysis': str(row['Claude Analysis']),
                'Last Updated': current_time  # 转换时统一设置为当前时间
            })
        
        # 保存为JSON文件
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Excel转JSON成功！生成文件：{json_filename}")
        return True
    except Exception as e:
        print(f"❌ Excel转JSON失败：{str(e)}")
        return False

def load_existing_json(json_filename: str) -> List[Dict[str, Any]]:
    """加载已存在的JSON报告，如果文件不存在则返回空列表"""
    if not os.path.exists(json_filename):
        return []
    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 验证数据格式是否为列表
            if isinstance(data, list):
                return data
            else:
                print(f"⚠️ JSON文件格式错误（应为列表），将创建新文件。")
                return []
    except json.JSONDecodeError as e:
        print(f"⚠️ 解析JSON文件失败：{e}，将创建新文件。")
        return []
    except Exception as e:
        print(f"⚠️ 读取JSON文件失败：{e}，将创建新文件。")
        return []

async def update_json(result: Dict[str, Any], json_filename: str, lock: asyncio.Lock):
    """安全地更新或追加结果到JSON文件（保留原有数据）"""
    if not isinstance(result, dict) or 'folder' not in result:
        return

    folder_name = result['folder']
    records = []

    # 构建新记录（保持与原Excel列对应的字段）
    if not result.get('step_results'):
        records.append({
            'Folder': folder_name,
            'Step Name': 'Initialization',
            'Success': result.get('success', False),
            'Cost ($)': 0.0,
            'Duration (s)': 0.0,
            'Error': result.get('error', 'No steps executed'),
            'Prompt': '',
            'Claude Analysis': '',
            'Last Updated': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    else:
        for step_res in result['step_results']:
            records.append({
                'Folder': folder_name,
                'Step Name': step_res.get('step_name', ''),
                'Success': step_res.get('success', False),
                'Cost ($)': round(step_res.get('cost', 0.0), 4),
                'Duration (s)': round(step_res.get('duration', 0.0), 2),
                'Error': step_res.get('error') or '',
                'Prompt': step_res.get('prompt') or '',
                'Claude Analysis': step_res.get('analysis') or '',
                'Last Updated': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    async with lock:
        try:
            # 加载现有数据
            existing_data = load_existing_json(json_filename)
            
            # 过滤掉当前文件夹的旧记录（保留其他文件夹数据）
            updated_data = [item for item in existing_data if item.get('Folder') != folder_name]
            
            # 追加新记录
            updated_data.extend(records)
            
            # 保存到JSON文件（格式化输出，便于阅读）
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 已将 '{folder_name}' 的记录 {'更新' if any(item.get('Folder') == folder_name for item in existing_data) else '追加'} 到JSON。")
        except Exception as e:
            print(f"❌ 保存 '{folder_name}' 的记录到JSON失败: {e}")

def generate_summary_report(results: List[Dict[str, Any]], total_time: float, report_title: str):
    # 生成最终的控制台汇总报告
    successful = [r for r in results if isinstance(r, dict) and r.get('success')]
    total_cost = sum(r.get('total_cost', 0.0) for r in results if isinstance(r, dict))
    print("\n" + "=" * 60 + f"\n📊 {report_title} 汇总报告\n" + "=" * 60)
    print(f"📁 总任务数: {len(results)}")
    print(f"✅ 成功: {len(successful)}")
    print(f"❌ 失败: {len(results) - len(successful)}")
    print(f"💰 总成本: ${total_cost:.4f}")
    print(f"⏱️  总耗时: {total_time:.2f} 秒 ({total_time / 60:.2f} 分钟)")
    print("=" * 60)

# --- 核心处理逻辑 ---
async def process_new_folder(folder_path: str, logger: ThreadSafeLogger, timeout_minutes: int) -> Dict[str, Any]:
    """处理新文件夹：完整流程（pytest检查 + 可能的Claude修复 + 最终验证）"""
    task_start_time = time.time()
    folder_name = os.path.basename(folder_path)
    result = {'folder': folder_name, 'success': False, 'step_results': [], 'total_cost': 0.0, 'total_duration': 0.0}

    try:
        logger.log(f"开始完整流程：pytest检查 + 可能的Claude修复（总超时：{timeout_minutes}分钟）")

        test_script = os.path.join(folder_path, "test_netconf.py")
        if not os.path.exists(test_script) or  "test_step_2" not in open(test_script, "r", errors="ignore").read():
            logger.log("代码未补全，跳过完整流程。")
            raise Exception("代码未补全，无法执行完整流程")

        # 步骤1：首次连通性检查
        logger.log("步骤1/3：首次连通性检查...")
        initial_log = run_pytest_and_check(folder_path)
        log_file_path = os.path.join(folder_path, "pytest_initial_log.txt")
        with open(log_file_path, "w", encoding='utf-8') as f:
            f.write(initial_log)
        

        if success_check_str in initial_log:
            logger.log("✅ 首次检查通过，无需修复")
            result['success'] = True
            step_result = {
                'step_name': 'Initial_Check',
                'success': True,
                'cost': 0.0,
                'duration': time.time() - task_start_time,
                'error': None,
                'prompt': '',
                'analysis': '首次检查通过，代码无需修复'
            }
            result['step_results'].append(step_result)
        elif error_check_str in initial_log:
            logger.log("⚠️  检测到DUT1连接错误，需手动干预")
            result['success'] = False
            result['error'] = "DUT1设备连接错误（需手动检查）"
            step_result = {
                'step_name': 'Initial_Check',
                'success': False,
                'cost': 0.0,
                'duration': time.time() - task_start_time,
                'error': result['error'],
                'prompt': '',
                'analysis': '首次检查发现DUT1连接错误'
            }
            result['step_results'].append(step_result)
        else:
            # 步骤2：调用Claude修复
            logger.log("步骤2/3：调用Claude修复代码...")
            options = ClaudeAgentOptions(
                system_prompt={"type": "preset", "preset": "claude_code"},
                allowed_tools=["Bash", "Edit", "Glob", "Grep", "Read", "Write"],
                permission_mode="bypassPermissions",
                cwd=folder_path
            )
            async with ClaudeSDKClient(options=options) as client:
                prompt = workflow_prompt
                debug_res = await run_claude_step(client, prompt, task_start_time, timeout_minutes * 60, logger)
            debug_res['step_name'] = 'CodeDebugging_Attempt'
            result['step_results'].append(debug_res)

            if not debug_res.get('success'):
                raise Exception(f"Claude修复失败：{debug_res.get('error', '未知错误')}")

            # 步骤3：最终验证
            logger.log("步骤3/3：最终验证检查...")
            final_log = run_pytest_and_check(folder_path)
            log_file_path_final = os.path.join(folder_path, "pytest_final_log.txt")
            with open(log_file_path_final, "w", encoding='utf-8') as f:
                f.write(final_log)

            if success_check_str in final_log:
                logger.log("✅ 最终验证通过，代码修复成功")
                result['success'] = True
                verify_result = {
                    'step_name': 'Final_Verification',
                    'success': True,
                    'cost': 0.0,
                    'duration': time.time() - task_start_time - sum(r.get('duration', 0.0) for r in result['step_results']),
                    'error': None,
                    'prompt': '',
                    'analysis': '最终验证通过，修复后的代码可正常运行'
                }
                result['step_results'].append(verify_result)
            else:
                result['error'] = "代码修复失败，最终验证未通过"
                logger.error(result['error'])
                verify_result = {
                    'step_name': 'Final_Verification',
                    'success': False,
                    'cost': 0.0,
                    'duration': time.time() - task_start_time - sum(r.get('duration', 0.0) for r in result['step_results']),
                    'error': result['error'],
                    'prompt': '',
                    'analysis': f'最终验证失败\npytest日志片段：{final_log[:500]}...'
                }
                result['step_results'].append(verify_result)

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"完整流程执行失败：{e}")

    result['total_duration'] = time.time() - task_start_time
    result['total_cost'] = sum(r.get('cost', 0.0) for r in result['step_results'])
    return result

async def main():
    # 主函数
    destination_folder = r"D:\yang\B75_yin\generated_modules"
    folders_to_process = [f.path for f in os.scandir(destination_folder) if f.is_dir() and f.name.endswith('_debug')]

    if not folders_to_process:
        print("❌ 未找到需要处理的 '_debug' 文件夹。")
        return

    # 配置参数
    max_concurrent = 1
    timeout_minutes = 120
    # excel_filename = os. path.join(destination_folder, "2_debugging_report.xlsx")  # 旧Excel报告路径
    json_filename = os.path.join(destination_folder, "2_debugging_report.json")  # 新JSON报告路径
    json_lock = asyncio.Lock()

    # # --- Excel转JSON逻辑 ---
    # if os.path.exists(excel_filename) and not os.path.exists(json_filename):
    #     # 存在旧Excel但无JSON，执行转换
    #     convert_success = excel_to_json(excel_filename, json_filename)
    #     if convert_success:
    #         # 询问是否删除旧Excel文件
    #         delete_excel = messagebox.askyesno("删除旧Excel", "Excel转JSON已完成，是否删除原Excel文件？\n（建议备份后删除，避免后续混淆）")
    #         if delete_excel:
    #             try:
    #                 os.remove(excel_filename)
    #                 print(f"🗑️  已删除旧Excel文件：{excel_filename}")
    #             except Exception as e:
    #                 print(f"❌ 删除旧Excel文件失败：{e}")
    #     else:
    #         print("⚠️ Excel转JSON失败，将创建新的JSON报告（旧Excel数据未迁移）")
    # elif os.path.exists(excel_filename) and os.path.exists(json_filename):
    #     # 同时存在Excel和JSON，提示用户选择
    #     choice = messagebox.askquestion("报告文件冲突", "已同时存在Excel和JSON报告文件！\n是否以JSON为准继续？（Excel文件将保留，不影响）")
    #     if choice != 'yes':
    #         print("❌ 用户选择不以JSON为准，程序退出。")
    #         return
    #     else:
    #         print("✅ 用户选择以JSON为准，继续执行任务。")

    # 加载现有JSON数据，判断哪些文件夹已存在
    existing_data = load_existing_json(json_filename)
    existing_folders = set(item.get('Folder') for item in existing_data if item.get('Folder'))
    
    # 筛选：仅保留JSON中不存在的文件夹（已存在的直接跳过，保留原有数据）
    new_folders = [f for f in folders_to_process if os.path.basename(f) not in existing_folders]
    skipped_folders = [os.path.basename(f) for f in folders_to_process if os.path.basename(f) in existing_folders]
    
    # 显示任务信息
    print(f"\n📋 任务概况：")
    print(f"   待处理文件夹总数：{len(folders_to_process)}")
    print(f"   已存在于JSON报告，跳过的文件夹数：{len(skipped_folders)}")
    if skipped_folders:
        print(f"   跳过的文件夹：{', '.join(skipped_folders)}")
    print(f"   新增待处理文件夹数：{len(new_folders)}")
    print(f"   单个任务超时：{timeout_minutes} 分钟")
    print(f"   并发数：{max_concurrent}")
    print(f"   报告文件：{json_filename}")
    
    if not new_folders:
        print("\n🎉 所有文件夹均已存在于JSON报告中，无需处理！")
        return
    
    start_time = time.time()
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = []

    # 定义带并发控制的任务执行函数
    async def run_task(folder_path):
        async with semaphore:
            folder_name = os.path.basename(folder_path)
            # 初始化日志器
            log_file = os.path.join(folder_path, "process_log.txt")
            if os.path.exists(log_file):
                os.remove(log_file)
            logger = ThreadSafeLogger(log_file)

            # 仅执行新文件夹的完整处理流程
            result = await process_new_folder(folder_path, logger, timeout_minutes)

            # 更新JSON（追加新记录，保留原有数据）
            await update_json(result, json_filename, json_lock)
            return result

    # 为新增文件夹创建任务
    for folder in new_folders:
        tasks.append(run_task(folder))

    # 执行所有任务
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 整理结果（过滤异常）
    final_results = []
    for res in results:
        if isinstance(res, Exception):
            error_msg = f"任务执行异常：{str(res)}"
            print(f"❌ {error_msg}")
            final_results.append({'success': False, 'error': error_msg, 'folder': '未知文件夹', 'total_cost': 0.0})
        else:
            final_results.append(res)

    # 生成汇总报告
    total_time = time.time() - start_time
    generate_summary_report(final_results, total_time, "代码调试（仅新增文件夹）")
    print(f"\n🎉 所有新增文件夹处理完成！最终报告：{json_filename}")
    print(f"📌 提示：已保留JSON中原有文件夹的历史数据，仅追加新增文件夹的处理记录")
    print(f"📌 JSON文件支持直接用文本编辑器打开，或导入其他工具进行分析")

if __name__ == "__main__":
    # 环境变量配置
    os.environ['ANTHROPIC_BASE_URL'] = 'https://open.bigmodel.cn/api/anthropic'
    os.environ['ANTHROPIC_AUTH_TOKEN'] = 'eb8424b62e54473491ec97f32bbccee6.Oz7nZBCmYoqsu1o2'
    os.environ["API_TIMEOUT_MS"] = "7200000"  # 与timeout_minutes保持一致（120分钟）
    os.environ["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"

    # 运行主程序
    asyncio.run(main())