#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 10/9/2025 13:45
# @Author  : H3C Comware AI group
# @function: 主程序入口 - 协调各个模块执行完整流程

import logging
import asyncio

from src.data_loader import ExcelDataLoader
from src.environment_setup import EnvironmentBuilder
from src.claudecode_executor import ClaudeCodeExecutor

# from src.file_finder import BackgroundFinder
# from src.executor import NetworkExecutor
from config import EXCEL_FILE_PATH, DEFAULT_SHEET


def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/execution.log', encoding="utf-8"),
            logging.StreamHandler()
        ]
    )


def main():
    """
    主函数
    :return:
    """
    # 初始化日志
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # 1. 从Excel读取数据
        logger.info("开始从Excel读取数据...")
        data_loader = ExcelDataLoader(EXCEL_FILE_PATH)
        data_loader.load_data(sheet_name=DEFAULT_SHEET)  # 可根据需要指定sheet
        data_loader.data_grouped()
        # print(data_loader.data_list)
        # print(data_loader.group_data_dict)

        # 2. 创建工作目录
        logger.info("开始创建工作目录...")
        env_builder = EnvironmentBuilder(data_loader.headers, data_loader.group_data_dict)
        env_builder.prepare_environment()
        # print(env_builder.effective_output_dir)

        # 3. 调用CC生成,确定性py脚本
        logger.info("开始调用CC生成脚本...")
        cc_executor = ClaudeCodeExecutor(env_builder.effective_output_dir)
        asyncio.run(cc_executor.execute())
        logger.info("所有CC执行完毕,请校验...")

        # 4. 调用执行接口,在simware中运行,并保存运行日志
        logger.info("开始执行数通接口,在simware中运行...")
        # executor = ClaudeCodeExecutor(env_builder.effective_output_dir)
        # asyncio.run(executor.execute())
        # logger.info("所有任务执行完成")
        logger.info("数通接口打桩中...")
    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        raise


if __name__ == "__main__":
    main()
