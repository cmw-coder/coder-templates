#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 11/9/2025 15:45
# @Author  : H3C Comware AI group
# @function: 通用工具函数


import os
import json

from unrar import rarfile
from datetime import datetime

rarfile.UNRAR_TOOL = r"C:\Program Files\WinRAR\UnRAR.exe"


def unrar_files_in_directory(directory_path, password=None):
    """
    Recursively finds and extracts all .rar files in a given directory.

    Args:
        directory_path (str): The path to the directory to search in.
        password (str, optional): The password for encrypted RAR files.
                                  Defaults to None.
    """
    if not os.path.isdir(directory_path):
        print(f"错误: 路径 '{directory_path}' 不是一个有效的文件夹。")
        return

    print(f"开始在文件夹 '{directory_path}' 中搜索并解压 RAR 文件...")

    # 使用 os.walk 遍历目录树
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith(".rar"):
                rar_path = os.path.join(root, filename)

                try:
                    # 创建 rarfile 对象
                    rf = rarfile.RarFile(rar_path, 'r')

                    # 检查是否需要密码
                    if rf.needs_password() and password:
                        rf.setpassword(password)
                    elif rf.needs_password() and not password:
                        print(f"警告: 文件 '{filename}' 需要密码，但未提供。跳过解压。")
                        continue

                    # 设置解压目标路径为 RAR 文件所在的目录
                    extract_to = os.path.splitext(rar_path)[0]
                    if not os.path.exists(extract_to):
                        os.makedirs(extract_to)

                    print(f"正在解压文件: {filename} -> 到文件夹: {extract_to}")
                    rf.extractall(path=extract_to)
                    print(f"解压完成: {filename}\n")

                except rarfile.RarCannotExec as e:
                    print(f"错误: 未找到 WinRAR 或 UnRAR.exe。请确保它已安装并添加到系统 PATH 中。")
                    print(e)
                    return
                except rarfile.BadRarFile:
                    print(f"错误: 文件 '{filename}' 可能已损坏，无法解压。")
                except Exception as e:
                    print(f"解压 '{filename}' 时发生未知错误: {e}")


def ensure_directory_exists(dir_path):
    """确保目录存在，不存在则创建"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def format_timestamp(timestamp=None, format_str='%Y-%m-%d %H:%M:%S'):
    """格式化时间戳"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(format_str)


def save_json(data, filepath):
    """保存数据为JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    folder_to_process = r"D:\Documents\确定性脚本CC生成\1000测试点的conftest和拓扑"
    unrar_files_in_directory(folder_to_process, password=None)
    pass
