#!/usr/bin/env python3
"""
YANG文件转换器 - 支持转换为YIN和DSDL格式

作者: Claude Code
版本: 2.1 - YIN+DSDL版本
"""

import os
import subprocess
import xml.etree.ElementTree as ET
import json
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from lxml import etree as lxml_etree


def find_yang_files(directory):
    """
    递归搜索一个目录，查找所有的YANG文件。

    Args:
        directory (str): 要搜索的目录。

    Returns:
        list: 一个包含找到的YANG文件路径的列表。
    """
    yang_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".yang"):
                yang_files.append(os.path.join(root, file))
    return yang_files


def get_pyang_path():
    """
    获取pyang可执行文件的路径（跨平台）

    Returns:
        str: pyang文件的路径，如果找不到则返回 None
    """
    # 优先使用系统 PATH 中的 pyang（Linux/macOS 通过 pip install pyang 安装）
    try:
        import shutil
        system_pyang = shutil.which('pyang')
        if system_pyang:
            print(f"使用系统 pyang: {system_pyang}")
            return system_pyang
    except Exception:
        pass

    # 如果系统 PATH 中找不到，则在脚本所在目录查找
    # Windows 上是 pyang.exe，Linux/macOS 上是 pyang
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pyang_filename = "pyang.exe" if os.name == "nt" else "pyang"
    pyang_path = os.path.join(script_dir, pyang_filename)

    if os.path.exists(pyang_path):
        print(f"使用本地 pyang: {pyang_path}")
        return pyang_path
    else:
        print(f"错误: 找不到 pyang")
        print(f"  - 请安装: pip install pyang")
        print(f"  - 或将 pyang 放在脚本目录: {script_dir}")
        return None


def convert_yang_to_yin(yang_file, output_dir):
    """
    使用 pyang 将 YANG 文件转换为 YIN 文件。

    Args:
        yang_file (str): YANG 文件的路径。
        output_dir (str): YIN 文件的保存目录。

    Returns:
        str: 生成的 YIN 文件的路径，如果出错则返回 None。
    """
    pyang_path = get_pyang_path()
    if not pyang_path:
        return None

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    yin_file = os.path.join(output_dir, os.path.basename(yang_file).replace(".yang", ".yin"))
    yang_file_directory = os.path.dirname(yang_file)

    command = [
        pyang_path,
        "-p", yang_file_directory,  # 导入模块的搜索路径
        "-f", "yin",  # 将输出格式设置为 YIN
        "-o", yin_file,
        yang_file
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        return yin_file
    except subprocess.CalledProcessError as e:
        print(f"转换 {yang_file} 为YIN时出错: {e.stderr}")
        return None
    except Exception as e:
        print(f"转换 {yang_file} 为YIN时出现未知错误: {str(e)}")
        return None




def convert_yang_to_dsdl(yang_file, output_dir, dependency_dir=None):
    """
    使用 pyang 将 YANG 文件转换为 DSDL XML 格式。

    Args:
        yang_file (str): YANG 文件的路径。
        output_dir (str): DSDL XML 文件的保存目录。
        dependency_dir (str): YANG 依赖文件目录（可选）。

    Returns:
        str: 生成的 DSDL XML 文件的路径，如果出错则返回 None。
    """
    pyang_path = get_pyang_path()
    if not pyang_path:
        return None

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dsdl_file = os.path.join(output_dir, os.path.basename(yang_file).replace(".yang", "_dsdl.xml"))
    yang_file_directory = os.path.dirname(yang_file)

    # 构建pyang命令，参考提供的代码示例
    cmd = [pyang_path, "-f", "dsdl"]

    # 添加依赖文件路径
    if dependency_dir:
        cmd.extend(["-p", dependency_dir])
    # else:
    #     cmd.extend(["-p", yang_file_directory])

    cmd.append(yang_file)

    try:
        print(f"正在转换 {yang_file} 为DSDL XML...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
        dsdl_content = result.stdout

        # 使用lxml进行美化输出，参考提供的代码示例
        root = lxml_etree.fromstring(dsdl_content.encode('utf-8'))
        pretty_xml = lxml_etree.tostring(
            root,
            pretty_print=True,
            encoding='utf-8',
            xml_declaration=True
        ).decode('utf-8')

        # 写入美化后的XML文件
        with open(dsdl_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)

        print(f"✓ DSDL转换成功: {dsdl_file}")
        return dsdl_file

    except subprocess.CalledProcessError as e:
        print(f"转换 {yang_file} 为DSDL时出错:")
        print(f"pyang错误信息: {e.stderr}")
        return None
    except lxml_etree.XMLSyntaxError as e:
        print(f"解析DSDL输出时出错: {e}")
        return None
    except Exception as e:
        print(f"转换 {yang_file} 为DSDL时出现未知错误: {str(e)}")
        return None


def parse_yin_for_yang_structure(yin_file):
    """
    解析一个YIN文件，以识别模块、表 (lists) 和子表。

    Args:
        yin_file (str): YIN文件的路径。

    Returns:
        dict: 一个包含模块名、表和子表的字典。
    """
    try:
        tree = ET.parse(yin_file)
        root = tree.getroot()
        namespace = {'yin': 'urn:ietf:params:xml:ns:yang:yin:1'}

        module_name = root.get('name')

        def find_lists(element, is_sub_table=False):
            tables = []
            sub_tables = []

            # 寻找对应于YANG中表的 'list' 元素
            for child in element.findall('yin:list', namespace):
                table_name = child.get('name')
                if is_sub_table:
                    sub_tables.append(table_name)
                else:
                    tables.append(table_name)

                # 递归搜索嵌套的列表 (子表)
                nested_tables, nested_sub_tables = find_lists(child, is_sub_table=True)
                tables.extend(nested_tables)
                sub_tables.extend(nested_sub_tables)

            # container 中也可能包含列表
            for container in element.findall('yin:container', namespace):
                nested_tables, nested_sub_tables = find_lists(container, is_sub_table)
                tables.extend(nested_tables)
                sub_tables.extend(nested_sub_tables)

            return tables, sub_tables

        tables, sub_tables = find_lists(root)

        return {
            "module": module_name,
            "tables": list(set(tables)),
            "sub_tables": list(set(sub_tables))
        }

    except ET.ParseError as e:
        print(f"解析YIN文件 {yin_file} 时出错: {e}")
        return None
    except FileNotFoundError:
        print(f"文件未找到: {yin_file}")
        return None




def process_yang_files(yang_dir, output_formats, output_dir=None, dependency_dir=None):
    """
    处理指定yang文件夹中的所有YANG文件，将其转换为指定格式并提取其结构。

    Args:
        yang_dir (str): yang文件夹的路径
        output_formats (list): 输出格式列表 ['yin', 'dsdl'] 或其中之一
        output_dir (str): 输出文件夹的路径（可选）
        dependency_dir (str): YANG依赖文件目录（可选，用于DSDL转换）

    Returns:
        dict: 处理结果字典
    """
    # 检查源目录是否存在
    if not os.path.isdir(yang_dir):
        print(f"错误: 目录 '{yang_dir}' 不存在。")
        return None

    # 查找要处理的YANG文件
    yang_files_to_process = find_yang_files(yang_dir)

    if not yang_files_to_process:
        print(f"在 {yang_dir} 中没有找到YANG文件。")
        return None

    print(f"在 '{yang_dir}' 中找到待处理的YANG文件: {len(yang_files_to_process)}")

    # 设置输出目录
    if not output_dir:
        yang_parent = os.path.dirname(yang_dir)
        yang_name = os.path.basename(yang_dir)

        if set(output_formats) == {'yin', 'dsdl'}:
            output_dir = os.path.join(yang_parent, f"{yang_name}_converted")
        elif 'yin' in output_formats:
            output_dir = os.path.join(yang_parent, f"{yang_name}_to_yin")
        elif 'dsdl' in output_formats:
            output_dir = os.path.join(yang_parent, f"{yang_name}_to_dsdl")
        else:
            output_dir = os.path.join(yang_parent, f"{yang_name}_output")

    results = {
        'yin_files': [],
        'dsdl_files': [],
        'yin_structures': []
    }

    # 处理每个YANG文件
    for yang_file in yang_files_to_process:
        print(f"\n正在处理: {yang_file}")

        # 转换为YIN格式
        if 'yin' in output_formats:
            yin_file = convert_yang_to_yin(yang_file, output_dir)
            if yin_file:
                results['yin_files'].append(yin_file)
                print(f"  ✓ YIN转换成功: {yin_file}")

                # 解析YIN结构
                yin_structure = parse_yin_for_yang_structure(yin_file)
                if yin_structure:
                    results['yin_structures'].append({
                        "file_path": yin_file,
                        "module": yin_structure["module"],
                        "tables": yin_structure["tables"],
                        "sub_tables": yin_structure["sub_tables"]
                    })

        # 转换为DSDL格式
        if 'dsdl' in output_formats:
            dsdl_file = convert_yang_to_dsdl(yang_file, output_dir, dependency_dir)
            if dsdl_file:
                results['dsdl_files'].append(dsdl_file)

    # 保存结构分析结果
    if results['yin_structures']:
        json_path = os.path.join(os.path.dirname(output_dir), os.path.basename(yang_dir) + "_yin.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results['yin_structures'], f, indent=4, ensure_ascii=False)
        print(f"\nYIN结构分析结果已保存至: {json_path}")

    return results


def main():
    """
    主函数，用于处理命令行参数并启动YANG文件转换过程。
    """
    parser = argparse.ArgumentParser(
        description='将YANG文件转换为YIN和/或DSDL格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 只转换为YIN格式
  python yang_converter.py --yin /path/to/yang/files

  # 只转换为DSDL格式
  python yang_converter.py --dsdl /path/to/yang/files

  # 同时转换为YIN和DSDL格式（默认）
  python yang_converter.py --yin --dsdl /path/to/yang/files
  python yang_converter.py /path/to/yang/files

  # 转换为所有格式
  python yang_converter.py --all /path/to/yang/files

  # 指定输出目录和依赖目录（用于DSDL）
  python yang_converter.py --dsdl /path/to/yang/files -o /path/to/output -p /path/to/dependencies

  # 简写形式
  python yang_converter.py -yd /path/to/yang/files
        """
    )

    parser.add_argument(
        'yang_dir',
        help='YANG文件夹路径'
    )

    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        help='输出文件夹路径（可选，默认在yang文件夹同级目录创建转换文件夹）'
    )

    parser.add_argument(
        '-p', '--path',
        dest='dependency_dir',
        help='YANG依赖文件目录（可选，用于DSDL转换）'
    )

    # 格式选择参数
    format_group = parser.add_mutually_exclusive_group(required=False)
    format_group.add_argument(
        '--yin',
        action='store_true',
        help='转换为YIN格式'
    )
    format_group.add_argument(
        '--dsdl',
        action='store_true',
        help='转换为DSDL格式'
    )
    format_group.add_argument(
        '-yd', '--yin-dsdl',
        action='store_true',
        help='同时转换为YIN和DSDL格式（默认行为）'
    )
    format_group.add_argument(
        '--all',
        action='store_true',
        help='转换为所有格式（YIN和DSDL）'
    )

    args = parser.parse_args()

    # 确定输出格式
    if args.all:
        output_formats = ['yin', 'dsdl']
    elif args.dsdl:
        output_formats = ['dsdl']
    elif args.yin_dsdl or (not args.yin and not args.dsdl):
        output_formats = ['yin', 'dsdl']
    elif args.yin:
        output_formats = ['yin']
    else:
        output_formats = ['yin', 'dsdl']  # 默认

    print(f"输出格式: {', '.join(output_formats).upper()}")
    if args.dependency_dir and 'dsdl' in output_formats:
        print(f"依赖目录: {args.dependency_dir}")

    # 处理YANG文件
    result = process_yang_files(args.yang_dir, output_formats, args.output_dir, args.dependency_dir)

    if result:
        print(f"\n{'='*60}")
        print("转换完成！")
        print(f"{'='*60}")

        if result['yin_files']:
            print(f"YIN文件: {len(result['yin_files'])} 个")
        if result['dsdl_files']:
            print(f"DSDL文件: {len(result['dsdl_files'])} 个")
        if result['yin_structures']:
            print(f"YIN结构: {len(result['yin_structures'])} 个已分析")

    else:
        print("处理失败。")
        sys.exit(1)


if __name__ == "__main__":
    main()