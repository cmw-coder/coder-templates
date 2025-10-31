#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 10/9/2025 13:48
# @Author  : H3C Comware AI group
# @function: 配置常量和路径设置
import os
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).parent

# Excel配置
EXCEL_FILE_PATH = os.path.join(BASE_DIR, 'input', '确定性测试点.xlsx')
DEFAULT_SHEET = '测试点'

# 路径配置
BACKGROUND_DOCS_DIR = os.path.join(BASE_DIR, 'input')  # , '1000测试点的conftest和拓扑'
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 执行配置
CLAUDE_CODE_SCRIPT = 'path/to/claude_script'  # 需要替换为实际路径
NETWORK_API_ENDPOINT = 'http://api.example.com/execute'  # 需要替换为实际API

# 其他常量
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
MANUAL_BACKGROUND_INFO = os.path.join(BASE_DIR, "background_info")

# 历史确定性脚本信息
HISTORY_DETERMINISTIC_SCRIPT_B75_SVN = "http://10.153.3.214/comware-test-script/04.TestbladeV3.0/确定性设计/B75"
HISTORY_DETERMINISTIC_SCRIPT_B75 = r"D:\Downloads\B75"
HISTORY_DETERMINISTIC_SCRIPT_V9_SVN = "http://10.153.3.214/comware-test-script/04.TestbladeV3.0/确定性设计/V9"
HISTORY_DETERMINISTIC_SCRIPT_V9 = r"D:\Downloads\V9"
