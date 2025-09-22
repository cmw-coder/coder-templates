#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 10/9/2025 13:45
# @Author  : H3C Comware AI group
# @function: Excel数据读取和组装模块
import openpyxl
import logging

from config import EXCEL_FILE_PATH, DEFAULT_SHEET
from collections import defaultdict

logger = logging.getLogger(__name__)


class ExcelDataLoader:
    def __init__(self, file_path=EXCEL_FILE_PATH):
        self.file_path = file_path
        self.headers = None
        self.expect_column = None
        self.data_list = None
        self.group_column = None
        self.group_data_dict = None

    def load_data(self, sheet_name=DEFAULT_SHEET):
        """
        从Excel指定sheet中,加载输入并组装成,数据列表
        :param sheet_name:
        :return:
        """
        try:
            wb = openpyxl.load_workbook(self.file_path)
            sheet = wb[sheet_name]
        except Exception as e:
            logger.error(f"加载Excel数据失败: {str(e)}")
            raise

        # 获取标题行
        headers = [str(cell.value) if cell.value is not None else "" for cell in sheet[1]]
        cache_line = [None] * len(headers)
        expect_column = {"原子命令行": -1, "原子点标题": -1, "测试步骤": -1}
        for onekey in expect_column.keys():
            if onekey in headers:
                expect_column[onekey] = headers.index(onekey)
            else:
                logging.error(f"{onekey}在第一行标题未找到,请校验")
                raise
        # 设置,分组锚定的列
        if "Topox" in headers:
            self.group_column = headers.index("Topox")
        else:
            logging.error(f"在excel标题行未找到Topox列,请校验")
            raise

        # 从第二行开始遍历
        data_list = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            # 将每一行转换为字符串列表
            row_data = [str(value).strip() if value is not None else "" for value in row]
            # 刷新缓存行
            for idx in range(len(row_data)):
                # 当前单元格有值,或属于期待列,刷新缓存行
                if row_data[idx] or idx in expect_column.values():
                    cache_line[idx] = row_data[idx]
            # 判断是否有效行,即期待单元格不为空
            if any([row_data[onevalue] for onevalue in expect_column.values()]):
                data_list.append(cache_line.copy())
        self.headers = headers
        self.expect_column = expect_column
        self.data_list = data_list

    def data_grouped(self):
        if not (self.data_list and self.expect_column):
            logging.error("分组依赖的数据为空,请校验")
            raise

        grouped_data = defaultdict(list)
        for idx, onedata in enumerate(self.data_list):
            if not len(onedata) > self.group_column:
                logging.warning(f"第{idx}行,{onedata[self.expect_column['原子命令行']]},没有对应topox,请校验")
                continue
            key = onedata[self.group_column]
            grouped_data[key].append(onedata)
        self.group_data_dict = grouped_data
