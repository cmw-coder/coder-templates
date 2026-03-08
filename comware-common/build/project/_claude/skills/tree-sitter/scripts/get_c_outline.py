#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件: my_pyproject/get_c_outline.py
# 创建时间: 2025-12-15
# 开发人员: zhong
# 功能描述: 提取C文件结构视图/大纲视图

import tree_sitter_c as tsc
from tree_sitter import Language, Parser, Query, QueryCursor
import sys
import os


def _get_file_outline(file_path):
    """获取C文件的结构视图"""
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return f"错误: 文件不存在: {file_path}"

    # 检查文件是否是C文件（可选）
    if not file_path.lower().endswith('.c'):
        print(f"警告: 文件 '{file_path}' 可能不是C源文件", file=sys.stderr)

    try:
        # 初始化C语言解析器
        C_LANGUAGE = Language(tsc.language())
        parser = Parser(C_LANGUAGE)

        # 读取C文件
        with open(file_path, "r", encoding="gbk", errors='replace') as rp:
            content = rp.read()

        # 解析代码
        tree = parser.parse(bytes(content, "gbk"))

        # 通过查询语句，输出C文件缩略图
        query = Query(C_LANGUAGE,
                      """(function_definition (type_identifier)(function_declarator)) @function""")
        query_cursor = QueryCursor(query)
        captures = query_cursor.captures(tree.root_node)

        content_lines = content.split("\n")
        structure_result = (f"# 文件路径: {file_path}\n"
                            f"# 文件大小: {os.path.getsize(file_path)} 字节\n"
                            f"# 结构视图/大纲视图:\n"
                            f"# 格式: 开始行号:结束行号 函数定义\n")

        if "function" in captures.keys():
            # 提取函数定义
            temp_list = [[one_capture.start_point[0], one_capture.end_point[0]] for one_capture in captures["function"]]
            # 按行号排序
            temp_list.sort(key=lambda x: x[0])
            for start_line in temp_list:
                # 获取函数名（尝试获取更完整的函数信息）
                function_text = content_lines[start_line[0]].strip()
                # 如果函数定义跨行，尝试获取更多行
                # if not function_text.endswith('{') and not function_text.endswith(';'):
                #     end_line = min(start_line + 3, len(content_lines) - 1)
                #     for i in range(start_line + 1, end_line + 1):
                #         if content_lines[i].strip().endswith('{') or content_lines[i].strip().endswith(';'):
                #             function_text += " " + content_lines[i].strip()
                #             break
                structure_result += f"{start_line[0] + 1:6d}:{start_line[1] + 1:6d} {function_text}\n"
        else:
            structure_result += "获取文件的结构视图失败，请尝试其他办法。\n"
        return structure_result
    except UnicodeDecodeError:
        return f"错误: 无法以GBK编码读取文件 '{file_path}'，请检查文件编码"
    except PermissionError:
        return f"错误: 没有权限读取文件 '{file_path}'"
    except Exception as e:
        return f"错误: 处理文件时发生异常: {str(e)}"


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python get_c_outline.py <C文件路径>")
        print("示例: python get_c_outline.py /path/to/file.c")
        print("示例: python get_c_outline.py \"D:\\Downloads\\test\\iecmrp_kdata.c\"")
        sys.exit(1)

    # 获取文件路径（支持带空格的路径）
    file_path = sys.argv[1]

    # 获取并输出结构视图
    result = _get_file_outline(file_path)
    print(result)


if __name__ == '__main__':
    main()
