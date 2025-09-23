#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 11/9/2025 15:27
# @Author  : H3C Comware AI group
# @function: 环境搭建模块,准备文件夹(init,conftest,topox),
import json
import os.path
import shutil
import subprocess
import logging
import time
import datetime

from config import BACKGROUND_DOCS_DIR, OUTPUT_DIR, MANUAL_BACKGROUND_INFO
from config import HISTORY_DETERMINISTIC_SCRIPT_B75

logger = logging.getLogger(__name__)


class EnvironmentBuilder:
    def __init__(self, headers, group_data_dict):
        self.script_path = 1  # script_path
        self.headers = headers
        self.group_data_dict = group_data_dict

        self.background_dir = BACKGROUND_DOCS_DIR
        self.manual_background_info = MANUAL_BACKGROUND_INFO

        self.output_dir = OUTPUT_DIR
        self.effective_output_dir = [None] * len(group_data_dict)

    def setup_environment(self, record):
        """为单条记录搭建环境"""
        try:
            # 构建命令参数
            cmd = [
                'python',  # 或使用特定解释器
                self.script_path,
                f"--record_id={record['id']}",
                # 添加其他必要参数
            ]

            # 执行脚本
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            if result.returncode == 0:
                logger.info(f"成功为记录 {record['id']} 搭建环境")
                return True
            else:
                logger.error(f"为记录 {record['id']} 搭建环境失败: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"为记录 {record['id']} 搭建环境超时")
            return False
        except Exception as e:
            logger.error(f"为记录 {record['id']} 搭建环境异常: {str(e)}")
            return False

    def copy_reference_info(self, output_folderpath: str):
        # 拷贝历史参考py脚本
        # 1.打桩,AI进行搜索
        # 2.暴力,
        satisfy_file = None
        for root, dirs, files in os.walk(HISTORY_DETERMINISTIC_SCRIPT_B75):
            if satisfy_file:
                break
            for file in files:
                if file.endswith(".py") and "__init__" not in file and "conftest" not in file:
                    satisfy_file = os.path.join(root, file)
                    break
        if satisfy_file:
            output_filepath = os.path.join(output_folderpath, "历史参考测试文件.py")
            output_filepath_metadata = os.path.join(output_folderpath, "历史参考测试文件_元数据.json")
            shutil.copy(satisfy_file, output_filepath)
            with open(output_filepath_metadata, 'w', encoding='utf-8') as wp:
                temp_metadata_dict = {
                    "历史参考测试文件_来源": satisfy_file
                }
                json.dump(temp_metadata_dict, wp, ensure_ascii=False, indent=4)
        else:
            logger.warning("没有找到历史参考py脚本")

        # 从背景信息文件夹,复制到工作文件夹
        for onele in os.listdir(self.manual_background_info):
            temp_elemnt = os.path.join(self.manual_background_info, onele)
            if os.path.isfile(temp_elemnt):
                shutil.copy(temp_elemnt, output_folderpath)
            elif os.path.isdir(temp_elemnt):
                shutil.copytree(temp_elemnt, os.path.join(output_folderpath, onele))
        pass

    def prepare_environment(self):
        # 遍历每组数据(以topox分组),创建文件夹
        timestamp_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        for idx, (topoxname, onegroup) in enumerate(self.group_data_dict.items()):
            output_foldername = f"{os.path.basename(topoxname)}_{timestamp_str}"
            output_folderpath = os.path.join(self.output_dir, output_foldername)
            if os.path.exists(output_folderpath):
                logger.warning(f"{output_folderpath}已经存在,请校验")
                raise
            else:
                os.makedirs(output_folderpath)

            # 开始查找背景文件(init,conftest,topox)
            from_backfolder = None
            if not os.path.exists(self.background_dir):
                logger.error(f"{self.background_dir},背景文件夹无效,请校验")
                raise
            for root, dirs, files in os.walk(self.background_dir):
                if from_backfolder:
                    break
                if topoxname in files:
                    from_backfolder = root

            if from_backfolder is None:
                logger.error(f"{topoxname}没有找到背景文件夹,请校验")
                raise
            # 开始复制数据,从背景文件夹,到工作文件夹
            for onele in os.listdir(from_backfolder):
                temp_fromfile = os.path.join(from_backfolder, onele)
                if os.path.isfile(temp_fromfile):
                    shutil.copy(temp_fromfile, output_folderpath)

            # 将同事excel测试点,写入工作文件夹中
            # # debug
            # onegroup = onegroup[:3]
            temp_dict_list = [dict(zip(self.headers, item)) for item in onegroup]
            with open(os.path.join(output_folderpath, "testpoints.json"), 'w', encoding='utf-8') as wp:
                json.dump(temp_dict_list, wp, ensure_ascii=False, indent=4)

            # 将参考的历史py脚本,拷贝到工作目录中
            self.copy_reference_info(output_folderpath)
            self.effective_output_dir[idx] = output_folderpath
        pass
