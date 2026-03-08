#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# 文件: my_pyproject/get_h_data_struct.py
# 创建时间: 2025-12-16
# 开发人员: zhong
# 功能描述:
import tree_sitter_c as tsc
from tree_sitter import Language, Parser, Query, QueryCursor
import sys
import os


def _get_hfile_structs(file_path):
    if not os.path.exists(file_path):
        return f"错误：文件不存在：{file_path}"

    if not file_path.endswith(".h"):
        print(f"警告: 文件 '{file_path}' 可能不是H源文件", file=sys.stderr)

    try:
        C_LANGUAGE = Language(tsc.language())
        parser = Parser(C_LANGUAGE)

        with open(file_path, "r", encoding="gbk", errors="replace") as rp:
            content = rp.read()

        tree = parser.parse(bytes(content, "gbk"))

        query = Query(C_LANGUAGE,
                      "(type_definition [(struct_specifier)(union_specifier)(enum_specifier)]) @struct")
        query_cursor = QueryCursor(query)
        captures = query_cursor.captures(tree.root_node)

        content_lines = content.split("\n")
        structure_result = (f"# 文件路径: {file_path}\n"
                            f"# 文件大小: {os.path.getsize(file_path)} 字节\n"
                            f"# 结构体|联合体|枚举的列表如下:\n"
                            f"# 格式: 开始行号:结束行号 结构体|联合体|枚举的定义\n")
        if "struct" in captures.keys():
            temp_list = [[one_capture.start_point[0], one_capture.end_point[0]] for one_capture in captures["struct"]]
            temp_list.sort(key=lambda x: x[0])
            for start_line in temp_list:
                struct_text = content_lines[start_line[0]].rstrip()
                structure_result += f"{start_line[0] + 1:6d}:{start_line[1] + 1:6d} {struct_text}\n"
        else:
            structure_result += "获取H文件的结构体列表失败，请尝试其他办法。\n"
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
        print("用法: python get_h_data_struct.py <H文件路径>")
        print("示例: python get_h_data_struct.py /path/to/file.h")
        print("示例: python get_h_data_struct.py \"D:\\Downloads\\test\\iecmrp_kdata.h\"")
        sys.exit(1)

    # 获取文件路径（支持带空格的路径）
    file_path = sys.argv[1]

    # 获取并输出结构视图
    result = _get_hfile_structs(file_path)
    print(result)


if __name__ == '__main__':
    main()
