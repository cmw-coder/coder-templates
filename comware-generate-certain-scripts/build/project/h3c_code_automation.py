#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 23/9/2025 14:41
# @Author  : H3C Comware AI group
# @function:
# ============================================
# H3C Code CLI 自动化工具 v3.6 (Python版本)
# ============================================

import os
import sys
import time
import shutil
import hashlib
import subprocess
import signal
import threading
import tempfile
import json

from datetime import datetime
from pathlib import Path


class H3CCodeAutomation:
    def __init__(self):
        self.H3CCODERVERSION = "V3.6"
        self.TIME_STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.USERNAME_LINUX = os.getenv('USER') or os.getenv('USERNAME')
        self.SESSION_FILE = ".h3c_session"
        self.PROJECT_ID = None
        self.SESSION_ID = None
        self.PROJECT_PATH = None
        self.monitor_thread = None
        self.monitor_running = False

        # 初始化环境变量
        self.setup_environment()

    def setup_environment(self):
        """设置环境变量"""
        os.environ['ANTHROPIC_BASE_URL'] = "https://api.deepseek.com/anthropic"
        os.environ['ANTHROPIC_AUTH_TOKEN'] = "sk-45bdb25aa4934166862a359a4df4443a"
        os.environ['ANTHROPIC_MODEL'] = "deepseek-chat"
        os.environ['ANTHROPIC_SMALL_FAST_MODEL'] = "deepseek-chat"
        os.environ['DISABLE_AUTOUPDATER'] = "1"
        os.environ['CLAUDE_CODE_MAX_OUTPUT_TOKENS'] = "50000"
        os.environ['CLAUDE_CODE_ENABLE_TELEMETRY'] = "1"
        os.environ['OTEL_METRICS_EXPORTER'] = "otlp,prometheus"
        os.environ['OTEL_LOGS_EXPORTER'] = "otlp"
        os.environ['OTEL_EXPORTER_OTLP_PROTOCOL'] = "grpc"
        os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = "http://10.112.112.154:4317"
        os.environ['OTEL_METRIC_EXPORT_INTERVAL'] = "100000"
        os.environ['OTEL_LOGS_EXPORT_INTERVAL'] = "50000"

    def print_header(self):
        """打印头部信息"""
        print("")
        print("[系统] 初始化环境信息...")

        current_datetime = datetime.now()
        YYYY = current_datetime.strftime("%Y")
        MM = current_datetime.strftime("%m")
        DD = current_datetime.strftime("%d")
        hh = current_datetime.strftime("%H")
        nn = current_datetime.strftime("%M")
        ss = current_datetime.strftime("%S")

        print(f"[用户] 当前用户: {self.USERNAME_LINUX}")
        print(f"[时间] 执行时间: {YYYY}-{MM}-{DD} {hh}:{nn}:{ss}")
        print(f"[标识] 时间戳: {self.TIME_STAMP}")

    def load_session_info(self):
        """从会话文件加载信息"""
        if os.path.exists(self.SESSION_FILE):
            session_vars = {}
            try:
                with open(self.SESSION_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            # 移除引号
                            value = value.strip("'").strip('"')
                            session_vars[key] = value

                self.PROJECT_ID = session_vars.get('PROJECT_ID')
                self.SESSION_ID = session_vars.get('SESSION_ID')

                if self.PROJECT_ID and self.SESSION_ID:
                    print("[系统] 检测到本地保存的会话信息...")
                    print(f"[项目] 项目标识: {self.PROJECT_ID}")
                    print(f"[会话] SessionID: {self.SESSION_ID}")
                    return True
            except Exception as e:
                print(f"[错误] 读取会话文件失败: {e}")

        return False

    def save_session_info(self):
        """保存会话信息到文件"""
        try:
            with open(self.SESSION_FILE, 'w', encoding='utf-8') as f:
                f.write(f"PROJECT_ID='{self.PROJECT_ID}'\n")
                f.write(f"SESSION_ID='{self.SESSION_ID}'\n")
            print(f"[系统] 已保存会话信息到 {self.SESSION_FILE}")
        except Exception as e:
            print(f"[错误] 保存会话信息失败: {e}")
            sys.exit(1)

    def get_project_id_input(self):
        """获取项目ID输入"""
        print("")
        print("[项目ID] 请输入项目标识符...")
        print("[提示] 项目类型请输入格式: NV202509090001 (NV+年月日+4位序号)")
        print("[提示] 临时项目请输入格式: V9 (B75 B64 B70)")
        print("[提示] 按回车键可取消输入")
        print("")

        try:
            project_id = input("请输入项目ID: ").strip()

            if not project_id:
                print("[系统] 用户取消输入，程序退出")
                input("按回车键继续...")
                sys.exit(0)

            # 验证项目ID格式
            id_valid = False
            id_type = "unknown"

            # 检查是否为项目格式 (NV+12位数字)
            if project_id.startswith("NV"):
                if len(project_id) == 14 and project_id[2:].isdigit():
                    id_valid = True
                    id_type = "project"
                    print(f"[验证] 项目ID格式正确: {project_id}")
            # 检查是否为临时项目
            elif project_id in ["V9", "B75", "B70", "B64"]:
                id_valid = True
                id_type = "temporary"
                print(f"[验证] 临时项目ID格式正确: {project_id}")
            else:
                print(f"[系统] 输入NV='{project_id}'不符合预期")

            # 生成SESSION_ID
            username_num = ''.join(filter(str.isdigit, self.USERNAME_LINUX))
            self.SESSION_ID = f"AI{username_num}{datetime.now().strftime('%Y%m%d%H%M%S')}"
            project_id = f"{project_id}_{self.SESSION_ID}"

            self.PROJECT_ID = project_id
            print(f"[项目] 项目类型: {id_type}")
            print(f"[项目] 项目标识: {self.PROJECT_ID}")
            print("")
            print(f"本次任务的 SessionID 为：")
            print(f"    {self.SESSION_ID}")
            print("")
            print("目录下已经创建的 SessionID 标识文件，后续commit时请使用此标识")
            print("")
            print("请确认 SessionID 是否正确，然后按下 [回车] 继续...")

            input()

            # 保存会话信息
            self.save_session_info()

            # 创建SessionID标识文件
            session_file_path = f"{self.SESSION_ID}.txt"
            if not os.path.exists(session_file_path):
                with open(session_file_path, 'w') as f:
                    pass
                print(f"已在当前目录创建标识文件: \"{session_file_path}\"")
            else:
                print(f"[系统] 标识文件 \"{session_file_path}\" 已存在")

            return True

        except KeyboardInterrupt:
            print("\n[系统] 用户取消输入，程序退出")
            sys.exit(0)

    def setup_backup_paths(self):
        """设置备份路径"""
        print("")
        print("[网络] 配置备份路径...")

        # 基础备份路径
        self.DEST_BASE = "/opt/coder/statistics/build"
        self.DEST_BEFORE = f"{self.DEST_BASE}/{self.USERNAME_LINUX}/{self.PROJECT_ID}/{self.TIME_STAMP}/before"
        self.DEST_AFTER = f"{self.DEST_BASE}/{self.USERNAME_LINUX}/{self.PROJECT_ID}/{self.TIME_STAMP}/after"
        self.DEST_PROJECTS_BEFORE = f"{self.DEST_BASE}/{self.USERNAME_LINUX}/{self.PROJECT_ID}/{self.TIME_STAMP}/projects_before"
        self.DEST_PROJECTS_AFTER = f"{self.DEST_BASE}/{self.USERNAME_LINUX}/{self.PROJECT_ID}/{self.TIME_STAMP}/projects"

        # 创建备份目录
        try:
            os.makedirs(self.DEST_BEFORE, exist_ok=True)
            os.makedirs(self.DEST_AFTER, exist_ok=True)
            os.makedirs(self.DEST_PROJECTS_BEFORE, exist_ok=True)
            os.makedirs(self.DEST_PROJECTS_AFTER, exist_ok=True)
            print(f"[路径] 备份根目录: {self.DEST_BASE}/{self.USERNAME_LINUX}/{self.PROJECT_ID}")
            print(f"[路径] 执行前备份: {self.DEST_BEFORE}")
            print(f"[路径] 执行后备份: {self.DEST_AFTER}")
        except Exception as e:
            print(f"[错误] 无法创建备份目录: {e}")
            input("按回车键继续...")
            sys.exit(1)

    def setup_project_path(self, args):
        """设置项目路径"""
        print("")
        print("[项目] 配置项目路径...")

        if len(args) > 1:
            self.PROJECT_PATH = args[1]
            print("[项目] 使用指定路径作为项目路径")
        else:
            self.PROJECT_PATH = os.getcwd()
            print("[项目] 使用当前目录作为项目路径")

        print(f"[项目] 项目路径: {self.PROJECT_PATH}")

        # 切换到项目目录
        try:
            os.chdir(self.PROJECT_PATH)
            print("[项目] 成功切换到项目目录")
        except Exception as e:
            print(f"[错误] 无法访问项目路径: {self.PROJECT_PATH}")
            print(f"[错误] 错误信息: {e}")
            input("按回车键继续...")
            sys.exit(1)

    def setup_claude_backup(self):
        """设置Claude备份"""
        print("")
        print("[Claude] 配置Claude项目备份...")

        self.CLAUDE_PROJECTS_BASE = os.path.expanduser("~/.claude/projects")
        print(f"[Claude] Claude项目目录: {self.CLAUDE_PROJECTS_BASE}")

        # 标准化项目路径
        self.PROJECT_PATH_NORMALIZED = self.PROJECT_PATH.replace(':', '_').replace('/', '_').replace(' ', '_')
        print(f"[Claude] 标准化路径: {self.PROJECT_PATH_NORMALIZED}")

        # 查找匹配的项目目录
        self.MATCHED_PROJECT_DIR = ""
        self.CLAUDE_BACKUP_ENABLED = 0

        if os.path.exists(self.CLAUDE_PROJECTS_BASE):
            print("[Claude] 扫描现有Claude项目目录...")

            for item in os.listdir(self.CLAUDE_PROJECTS_BASE):
                dir_path = os.path.join(self.CLAUDE_PROJECTS_BASE, item)
                if os.path.isdir(dir_path):
                    dir_name = item
                    normalized_dir = dir_name.replace('--', '').replace('-', '')

                    normalized_path_check = self.PROJECT_PATH_NORMALIZED.replace('--', '').replace('-', '').replace('_',
                                                                                                                    '')
                    if normalized_dir.lower() == normalized_path_check.lower():
                        self.MATCHED_PROJECT_DIR = dir_path
                        self.CLAUDE_BACKUP_ENABLED = 1
                        print(f"[Claude] 精确匹配: {dir_path}")
                        break

            if not self.CLAUDE_BACKUP_ENABLED:
                print("[Claude] 暂未找到精确匹配的项目目录")
        else:
            print("[Claude] Claude项目目录不存在")

        # 设置Claude备份目录
        self.CLAUDE_BACKUP_DIR = f"{self.DEST_BASE}/{self.USERNAME_LINUX}/{self.PROJECT_ID}/{self.TIME_STAMP}/projects"
        print(f"[Claude] Claude备份目录: {self.CLAUDE_BACKUP_DIR}")

        if self.CLAUDE_BACKUP_ENABLED:
            print(f"[Claude] 模式：精确匹配监控 - {self.MATCHED_PROJECT_DIR}")
        else:
            print("[Claude] 模式：未找到匹配项目，将启动监控等待创建")
            self.CLAUDE_BACKUP_ENABLED = 1

    def record_snapshot(self):
        """记录快照"""
        self.SNAPSHOT_FILE = os.path.join(os.path.expanduser("~"), ".project_snapshot.json")

        snapshot_dict = {}
        if os.path.exists(self.SNAPSHOT_FILE):
            with open(self.SNAPSHOT_FILE, 'r', encoding='utf-8', errors="replace") as rp:
                snapshot_dict = json.load(rp)

        temp_folder = os.path.join(self.PROJECT_PATH, "output")
        for root, dirs, files in os.walk(temp_folder):
            for file in files:
                if file.endswith('.py') and file not in ['conftest.py', '__init__.py']:
                    file_path = os.path.join(root, file)
                    file_md5 = self.calculate_file_md5(file_path)
                    if file_path in snapshot_dict:
                        if file_md5 not in snapshot_dict[file_path]:
                            snapshot_dict[file_path] = file_md5
                    else:
                        snapshot_dict[file_path] = file_md5
        temp_folder = os.path.join(os.path.expanduser("~"), ".claude/projects")
        for root, dirs, files in os.walk(temp_folder):
            for file in files:
                if file.endswith(".jsonl"):
                    file_path = os.path.join(root, file)
                    file_md5 = self.calculate_file_md5(file_path)
                    if file_path in snapshot_dict:
                        if file_md5 not in snapshot_dict[file_path]:
                            snapshot_dict[file_path] = file_md5
                    else:
                        snapshot_dict[file_path] = file_md5
        with open(self.SNAPSHOT_FILE, 'w', encoding='utf-8', errors="replace") as wp:
            json.dump(snapshot_dict, wp, ensure_ascii=False, indent=4)
        pass

    def backup_python_files_revise(self):
        snapshot_dict = {}
        if os.path.exists(self.SNAPSHOT_FILE):
            with open(self.SNAPSHOT_FILE, 'r', encoding='utf-8', errors="replace") as rp:
                snapshot_dict = json.load(rp)

        temp_folder = os.path.join(self.PROJECT_PATH, "output")
        for root, dirs, files in os.walk(temp_folder):
            for file in files:
                if file.endswith('.py') and file not in ['conftest.py', '__init__.py']:
                    file_path = os.path.join(root, file)
                    file_md5 = self.calculate_file_md5(file_path)
                    if file_path in snapshot_dict:
                        if file_md5 not in snapshot_dict[file_path]:
                            snapshot_dict[file_path] = file_md5
                    else:
                        snapshot_dict[file_path] = file_md5
                        shutil.copy2(file_path, self.DEST_AFTER)

        temp_folder = os.path.join(os.path.expanduser("~"), ".claude/projects")
        for root, dirs, files in os.walk(temp_folder):
            for file in files:
                if file.endswith(".jsonl"):
                    file_path = os.path.join(root, file)
                    file_md5 = self.calculate_file_md5(file_path)
                    if file_path in snapshot_dict:
                        if file_md5 not in snapshot_dict[file_path]:
                            snapshot_dict[file_path] = file_md5
                    else:
                        snapshot_dict[file_path] = file_md5
                        shutil.copy2(file_path, self.DEST_PROJECTS_AFTER)
        with open(self.SNAPSHOT_FILE, 'w', encoding='utf-8', errors="replace") as wp:
            json.dump(snapshot_dict, wp, ensure_ascii=False, indent=4)
        pass

    def backup_python_files(self, backup_dir, phase="before"):
        """备份Python文件"""
        print("")
        print(f"[备份] 开始备份执行{phase}的Python代码...")
        print(f"[备份] 目标目录: {backup_dir}")

        # 确保备份目录存在
        try:
            os.makedirs(backup_dir, exist_ok=True)
            print("[备份] 备份目录创建成功")
        except Exception as e:
            print(f"[错误] 无法创建备份目录: {e}")
            input("按回车键继续...")
            sys.exit(1)

        py_count = 0

        temp_folder = os.path.join(self.PROJECT_PATH, "output")
        for root, dirs, files in os.walk(temp_folder):
            # # 跳过特定目录
            # if '.venv' in dirs:
            #     dirs.remove('.venv')
            # if 'test_example' in dirs:
            #     dirs.remove('test_example')

            for file in files:
                if file.endswith('.py') and file not in ['conftest.py', '__init__.py']:
                    file_path = os.path.join(root, file)
                    try:
                        shutil.copy2(file_path, backup_dir)
                        py_count += 1
                        if py_count < 10:
                            print(f"[Python] 实时备份: {file_path}")
                        elif py_count == 10:
                            print("...（更多文件备份中，确认工程路径是否正确）")
                    except Exception as e:
                        print(f"[错误] 备份文件失败 {file_path}: {e}")

        print(f"[备份] 总共备份了 {py_count} 个Python文件")

    def calculate_file_md5(self, file_path):
        """计算文件的MD5值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None

    def claude_monitor(self):
        """Claude项目监控线程"""
        print("[Claude] 监控器启动")

        monitor_dir = self.MATCHED_PROJECT_DIR
        if not monitor_dir:
            print("[Claude] 等待模式：监控整个Claude目录等待项目创建")
        else:
            print(f"[Claude] 精确模式：监控目录 {monitor_dir}")

        while self.monitor_running:
            # 检查Claude项目目录中的jsonl文件
            if not monitor_dir:
                # 等待模式：扫描整个Claude目录寻找匹配项目
                if os.path.exists(self.CLAUDE_PROJECTS_BASE):
                    for item in os.listdir(self.CLAUDE_PROJECTS_BASE):
                        dir_path = os.path.join(self.CLAUDE_PROJECTS_BASE, item)
                        if os.path.isdir(dir_path):
                            dir_name = item
                            normalized_dir = dir_name.replace('--', '').replace('-', '')

                            normalized_path_check = self.PROJECT_PATH_NORMALIZED.replace('--', '').replace('-',
                                                                                                           '').replace(
                                '_', '')

                            if normalized_dir.lower() == normalized_path_check.lower():
                                print(f"[Claude] 发现新创建的匹配项目: {dir_path}")
                                monitor_dir = dir_path
                                break

            # 备份jsonl文件
            if monitor_dir and os.path.exists(monitor_dir):
                for file in os.listdir(monitor_dir):
                    if file.endswith('.jsonl'):
                        file_path = os.path.join(monitor_dir, file)
                        if os.path.isfile(file_path):
                            # 检查文件修改时间
                            file_time = os.path.getmtime(file_path)
                            current_time = time.time()
                            sec_diff = abs(current_time - file_time)

                            if sec_diff <= 300:  # 5分钟内修改的文件
                                try:
                                    shutil.copy2(file_path, self.CLAUDE_BACKUP_DIR)
                                    print(f"[Claude] 备份成功: {file}")
                                except Exception as e:
                                    print(f"[Claude] 备份失败: {file}: {e}")

            # 备份Python文件到after目录
            if os.path.exists(self.PROJECT_PATH):
                try:
                    os.makedirs(self.DEST_AFTER, exist_ok=True)

                    for root, dirs, files in os.walk(self.PROJECT_PATH):
                        if '.venv' in dirs:
                            dirs.remove('.venv')
                        if 'test_example' in dirs:
                            dirs.remove('test_example')

                        for file in files:
                            if file.endswith('.py') and file not in ['conftest.py', '__init__.py']:
                                file_path = os.path.join(root, file)
                                filename = os.path.basename(file_path)

                                before_file = os.path.join(self.DEST_BEFORE, filename)
                                after_file = os.path.join(self.DEST_AFTER, filename)

                                # 检查文件是否发生变化
                                should_backup = True

                                if os.path.exists(before_file):
                                    md5_before = self.calculate_file_md5(before_file)
                                    md5_current = self.calculate_file_md5(file_path)

                                    if md5_before and md5_current and md5_before == md5_current:
                                        should_backup = False

                                if should_backup and os.path.exists(after_file):
                                    md5_after_back = self.calculate_file_md5(after_file)
                                    md5_current = self.calculate_file_md5(file_path)

                                    if md5_after_back and md5_current and md5_after_back == md5_current:
                                        should_backup = False

                                if should_backup:
                                    try:
                                        shutil.copy2(file_path, self.DEST_AFTER)
                                        print(f"[Python] 实时备份: {file_path}")
                                    except Exception as e:
                                        print(f"[错误] 备份失败 {file_path}: {e}")

                except Exception as e:
                    print(f"[错误] 备份Python文件失败: {e}")

            # 等待5秒
            time.sleep(5)

    def start_claude_monitor(self):
        """启动Claude监控"""
        if not self.CLAUDE_BACKUP_ENABLED:
            print("[Claude] 跳过Claude项目监控（初始化失败）")
            return

        print("[Claude] 启动Claude项目实时备份...")

        # 创建Claude备份目录
        try:
            os.makedirs(self.CLAUDE_BACKUP_DIR, exist_ok=True)
            print(f"[Claude] Claude备份目录创建成功: {self.CLAUDE_BACKUP_DIR}")
        except Exception as e:
            print(f"[警告] 无法创建Claude备份目录: {e}")
            self.CLAUDE_BACKUP_ENABLED = 0
            return

        # 启动监控线程
        self.monitor_running = True
        self.monitor_thread = threading.Thread(target=self.claude_monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("[Claude] 增强型后台监控任务已启动")

        if not self.MATCHED_PROJECT_DIR:
            print("[Claude] 监控模式：等待模式 - 动态检测项目创建")
        else:
            print(f"[Claude] 监控模式：精确匹配 - {self.MATCHED_PROJECT_DIR}")

    def stop_claude_monitor(self):
        """停止Claude监控"""
        if self.monitor_running:
            print("[Claude] 停止Claude监控任务...")
            self.monitor_running = False

            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)

            # 最后一次备份检查
            self.final_claude_backup()

    def final_claude_backup(self):
        """最终Claude备份检查"""
        print("[Claude] 执行最后一次备份检查...")

        # 如果最初没有匹配项目，尝试重新查找
        if not self.MATCHED_PROJECT_DIR:
            print("[Claude] 重新扫描Claude项目目录寻找新创建的项目...")

            if os.path.exists(self.CLAUDE_PROJECTS_BASE):
                for item in os.listdir(self.CLAUDE_PROJECTS_BASE):
                    dir_path = os.path.join(self.CLAUDE_PROJECTS_BASE, item)
                    if os.path.isdir(dir_path):
                        dir_name = item
                        normalized_dir = dir_name.replace('--', '').replace('-', '')
                        normalized_path_check = self.PROJECT_PATH_NORMALIZED.replace('--', '').replace('-', '')

                        if normalized_dir.lower() == normalized_path_check.lower():
                            print(f"[Claude] 发现新创建的匹配项目: {dir_path}")
                            self.MATCHED_PROJECT_DIR = dir_path
                            break

        if self.MATCHED_PROJECT_DIR and os.path.exists(self.MATCHED_PROJECT_DIR):
            print(f"[Claude] 检查项目目录: {self.MATCHED_PROJECT_DIR}")
            print("[Claude] 检查备份目录中的jsonl文件...")

            # 备份所有jsonl文件
            for file in os.listdir(self.MATCHED_PROJECT_DIR):
                if file.endswith('.jsonl'):
                    file_path = os.path.join(self.MATCHED_PROJECT_DIR, file)
                    if os.path.isfile(file_path):
                        try:
                            shutil.copy2(file_path, self.CLAUDE_BACKUP_DIR)
                            print(f"[Claude] 最终备份: {file}")
                        except Exception as e:
                            print(f"[Claude] 最终备份失败: {file}: {e}")
        else:
            print("[Claude] 未发现匹配的Claude项目目录")

        print("[Claude] 当前项目Claude备份完成")

    def run_claude_cli(self):
        """运行Claude CLI"""
        print("")
        print("===========================================")
        print(f"[启动] 正在启动H3C CODE CLI工具 版本: {self.H3CCODERVERSION}")
        print("[提示] 请在CLI中输入您的需求")
        print("===========================================")
        print("")

        try:
            # 这里需要确认：原脚本是运行 `python3 main.py` 还是 `claude` 命令？
            # 根据您的文件结构，应该是运行 main.py
            subprocess.run([sys.executable, "main.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[错误] Claude CLI执行失败: {e}")
        except KeyboardInterrupt:
            print("\n[系统] 用户中断Claude CLI执行")
        except Exception as e:
            print(f"[错误] 执行Claude CLI时发生错误: {e}")

    def cleanup(self):
        """清理资源"""
        print("")
        print("[清理] 正在清理资源...")

        # 停止监控
        self.stop_claude_monitor()

        print("[清理] 恢复原始工作目录")
        # 这里可以根据需要恢复到原始目录

    def run(self, args):
        """主运行方法"""
        try:
            # 初始化
            self.print_header()

            # 加载或获取会话信息
            if not self.load_session_info():
                self.get_project_id_input()

            # 设置备份路径
            self.setup_backup_paths()

            # 设置项目路径
            self.setup_project_path(args)

            # # 设置Claude备份
            # self.setup_claude_backup()

            # 备份执行前的文件
            self.record_snapshot()
            # self.backup_python_files(self.DEST_BEFORE, "前")

            # # 启动Claude监控
            # self.start_claude_monitor()

            # 运行Claude CLI
            self.run_claude_cli()
            # time.sleep(120)

            # 备份执行后的文件
            # self.backup_python_files(self.DEST_AFTER, "后")
            self.backup_python_files_revise()

            # # 清理
            # self.cleanup()

            # 完成信息
            print("")
            print("===========================================")
            print(f"[完成] H3C Code CLI {self.H3CCODERVERSION} 执行完毕")
            print(f"[时间] 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("===========================================")
            print("")

        except KeyboardInterrupt:
            print("\n[系统] 用户中断程序执行")
            self.cleanup()
        except Exception as e:
            print(f"[错误] 程序执行失败: {e}")
            self.cleanup()
            sys.exit(1)


def main():
    """
    主函数
    :return:
    """
    automation = H3CCodeAutomation()
    automation.run(sys.argv)


if __name__ == "__main__":
    main()
