#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 11/9/2025 19:20
# @Author  : H3C Comware AI group
# @function:
import os
import asyncio
import anyio
import json
import time
import logging
import datetime
import threading

from typing import List, Dict, Any
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class ThreadSafeLogger:
    """线程安全的日志记录器"""

    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.lock = threading.Lock()
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    def log(self, message):
        """线程安全地记录日志"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        with self.lock:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(log_message)
        print(log_message.strip())  # 同时在控制台输出


class ClaudeCodeExecutor:
    def __init__(self, effective_output_dir):
        self.effective_output_dir = effective_output_dir

    async def process_folder(self, folder_path: str, logger: ThreadSafeLogger) -> Dict[str, Any]:
        review_results = []
        try:
            logger.log(f"开始处理文件夹: {folder_path}")
            async with ClaudeSDKClient(
                    options=ClaudeCodeOptions(
                        # Core configuration
                        system_prompt="你是一个数通领域的测试脚本编写工程师,你的任务是模仿历史脚本,编写待测功能CLI的测试py脚本",
                        append_system_prompt="Additional system instructions",
                        max_turns=None,
                        model="deepseek-chat",  # "claude-3-5-sonnet-20241022",

                        # Tool management
                        allowed_tools=["Bash", "Read", "Write", "mcp__postgres__query"],
                        disallowed_tools=["WebSearch"],

                        # Session management
                        continue_conversation=False,

                        # Environment
                        cwd=folder_path,

                        # Permissions
                        permission_mode="bypassPermissions",  # "default", "acceptEdits", "plan", "bypassPermissions"
                    )
            ) as client:
                # Multi-step review in same session
                steps = [
                    ("1. 请调用 write-testscript subagent读取&分析&操作,当前测试文件夹."
                     "期间不要询问我的意见,你具有最高权限,全权负责,最终目标是生成所有测试点的测试py文件.")
                    # "1. 请你阅读当前文件夹,了解当前文件夹结构",
                    # ("2. 请你阅读当前文件夹下的 task_description.md 文件,按照内容要求,完成'测试脚本生成'任务,"
                    #  "期间不要询问我的意见,你具有最高权限,全权负责")
                ]
                for step in steps:
                    logger.log(f"执行步骤: {step}")
                    await client.query(step)

                    step_result = []
                    async for message in client.receive_response():
                        if hasattr(message, 'content'):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    text = block.text
                                    logger.log(text)  # 记录到日志文件
                                    step_result.append(text)

                        if type(message).__name__ == "ResultMessage":
                            review_results.append({
                                'step': step,
                                'analysis': ''.join(step_result),
                                'cost': message.total_cost_usd
                            })
                total_cost = sum(r['cost'] for r in review_results)
                logger.log(f"✅ 处理完成。总成本: ${total_cost:.4f}")

                return {
                    'folder': folder_path,
                    'success': True,
                    'results': review_results,
                    'total_cost': total_cost
                }
        except Exception as e:
            logger.log(f"❌ 处理文件夹 {folder_path} 时出错: {str(e)}")
            return {
                'folder': folder_path,
                'success': False,
                'error': str(e),
                'results': []
            }
        pass

    async def process_folders_parallel(self, folder_paths: List[str]):
        """并行处理多个文件夹"""
        results = []

        # 使用 asyncio.gather 来并行运行协程
        tasks = []

        for folder_path in folder_paths:
            # 为每个文件夹创建单独的日志文件
            log_file = os.path.join(folder_path, "run_log.txt")
            logger = ThreadSafeLogger(log_file)

            # 直接创建协程任务
            task = self.process_folder(folder_path, logger)
            tasks.append(task)

        # 使用 asyncio.gather 并行运行所有任务
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)

        for task_result in completed_tasks:
            if isinstance(task_result, Exception):
                results.append({
                    'folder': 'unknown',
                    'success': False,
                    'error': str(task_result)
                })
            else:
                results.append(task_result)

        return results

    async def execute(self):
        # 设置环境变量
        os.environ['ANTHROPIC_BASE_URL'] = 'https://api.deepseek.com/anthropic'  # 绿区用
        os.environ['ANTHROPIC_AUTH_TOKEN'] = 'sk-73d7aa62e90247f0bd6b2fda1ed0aef9'
        os.environ['ANTHROPIC_MODEL'] = 'deepseek-chat'
        os.environ['ANTHROPIC_SMALL_FAST_MODEL'] = 'deepseek-chat'  # 'deepseek-chat'

        # 过滤掉异常文件夹
        valid_folders = [folder for folder in self.effective_output_dir if os.path.exists(folder)]
        if not valid_folders:
            logger.error(f"没有有效的文件夹,CC启动失败,请校验")
            raise

        # 并行处理所有文件夹
        print(f"📁 开始处理 {len(valid_folders)} 个文件夹...")
        print("=" * 50)

        start_time = time.time()
        results = await self.process_folders_parallel(valid_folders)
        end_time = time.time()
        total_time = end_time - start_time

        # 汇总结果
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        total_cost = sum(r.get('total_cost', 0) for r in results if r.get('success', False))

        print("=" * 50)
        print(f"🎉 处理完成!")
        print(f"📊 成功: {successful}, 失败: {failed}")
        print(f"💰 总成本: ${total_cost:.4f}")
        print(f"⏱️  总耗时: {total_time:.2f} 秒")

        # 输出详细结果
        for result in results:
            if result.get('success'):
                print(f"✅ {result['folder']} - 成功 (成本: ${result['total_cost']:.4f})")
            else:
                print(f"❌ {result['folder']} - 失败: {result.get('error', '未知错误')}")
        pass
