#!/usr/bin/env python3
"""
NETCONF文档处理工具
将Word文档转换为Markdown并分析NETCONF相关章节信息

作者: Claude Code
版本: 2.0 - 合并版本
"""
import sys
import io

# 设置标准输出编码为UTF-8，解决Windows控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import re
import markdown
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import argparse
import json
import os
import logging
import traceback
import pypandoc
from pathlib import Path

# 导入word_revision_extractor模块
try:
    from word_revision_extractor import WordNetconfRevisionExtractor
except ImportError:
    print("警告: 无法导入word_revision_extractor模块，将只进行文档转换")
    WordNetconfRevisionExtractor = None

# --- 配置日志记录器 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- 输出文件夹配置 ---
DEFAULT_OUTPUT_DIR = "converted_docs"  # 默认输出文件夹名称


def save_with_encoding_fallback(content: str, file_path: str) -> bool:
    """
    使用多种编码方式尝试保存文件内容，处理编码兼容性问题

    参数:
        content (str): 要保存的文本内容
        file_path (str): 目标文件路径

    返回:
        bool: 保存成功返回True，所有编码方式都失败返回False
    """
    # 定义编码尝试顺序：从最通用的到更兼容的
    encoding_attempts = [
        ('utf-8', 'UTF-8'),
        ('utf-8-sig', 'UTF-8 with BOM'),  # 带BOM的UTF-8，某些软件识别更好
        ('utf-16', 'UTF-16'),             # 双字节编码，支持更多字符
        ('gb18030', 'GB18030'),           # 中文最全面的编码
        ('gbk', 'GBK'),                   # 简体中文
        ('big5', 'Big5'),                 # 繁体中文
        ('shift_jis', 'Shift_JIS'),       # 日文
        ('euc-jp', 'EUC-JP'),             # 日文另一种编码
        ('euc-kr', 'EUC-KR'),             # 韩文
        ('latin-1', 'Latin-1'),           # 西欧编码，能处理任意字节但不保证正确显示
    ]

    last_error = None

    for encoding, encoding_name in encoding_attempts:
        try:
            with open(file_path, 'w', encoding=encoding, newline='') as f:
                f.write(content)
            print(f"✓ 使用 {encoding_name} 编码成功保存")
            return True

        except UnicodeEncodeError as e:
            print(f"× {encoding_name} 编码失败: {str(e)}")
            last_error = e
            continue

        except Exception as e:
            print(f"× {encoding_name} 编码出现其他错误: {str(e)}")
            last_error = e
            continue

    # 如果所有编码都失败，尝试使用错误替换模式
    print("所有标准编码方式均失败，尝试使用UTF-8错误替换模式...")
    try:
        # 使用errors参数处理无法编码的字符
        with open(file_path, 'w', encoding='utf-8', errors='replace', newline='') as f:
            f.write(content)
        print("✓ 使用UTF-8错误替换模式保存成功（部分字符可能被替换）")
        return True

    except Exception as e:
        print(f"× UTF-8错误替换模式也失败: {str(e)}")
        last_error = e

    # 最后尝试：使用ignore模式
    print("尝试使用UTF-8忽略模式...")
    try:
        with open(file_path, 'w', encoding='utf-8', errors='ignore', newline='') as f:
            f.write(content)
        print("✓ 使用UTF-8忽略模式保存成功（部分字符可能被忽略）")
        return True

    except Exception as e:
        print(f"× UTF-8忽略模式也失败: {str(e)}")
        print(f"最终错误: {str(last_error)}")
        return False


def convert_docx_to_markdown(docx_path: str, output_dir: str = DEFAULT_OUTPUT_DIR) -> str:
    """
    将 DOCX 文件转换为 Markdown

    参数:
        docx_path (str): 输入的 DOCX 文件的路径
        output_dir (str): 输出文件夹名称，默认为 DEFAULT_OUTPUT_DIR

    返回:
        str: 转换后的 Markdown 文件路径，如果失败则返回 None
    """
    # 检查 pandoc 是否已安装
    try:
        pypandoc.get_pandoc_version()
    except OSError:
        print("错误：未找到 pandoc。请确保已经安装 pandoc 并且在系统的 PATH 中。")
        return None

    # 检查文件是否存在
    if not os.path.exists(docx_path):
        print(f"错误：指定的文件不存在: {docx_path}")
        return None

    if not docx_path.endswith('.docx'):
        print(f"错误：指定的文件不是 .docx 格式: {docx_path}")
        return None

    try:
        # 获取DOCX文件所在目录
        docx_dir = os.path.dirname(os.path.abspath(docx_path))

        # 创建输出文件夹路径（与DOCX文件同目录）
        full_output_dir = os.path.join(docx_dir, output_dir)
        os.makedirs(full_output_dir, exist_ok=True)

        # 生成markdown文件路径
        original_filename = os.path.basename(docx_path)
        base_filename = os.path.splitext(original_filename)[0]
        md_path = os.path.join(full_output_dir, f"{base_filename}.md")

        print(f"正在转换: {docx_path} -> {md_path}")

        # 使用pypandoc转换内容到内存，然后以多种编码方式尝试保存
        try:
            markdown_content = pypandoc.convert_file(docx_path, 'md')
    
            # 尝试多种编码方式保存Markdown文件
            save_success = save_with_encoding_fallback(markdown_content, md_path)

            if not save_success:
                print(f"所有编码方式均失败，尝试使用pypandoc直接保存")
                # 回退到原始方法
                pypandoc.convert_file(docx_path, 'md', outputfile=md_path)

        except Exception as pandoc_error:
            print(f"pypandoc转换失败: {str(pandoc_error)}")
            # 回退到原始方法
            pypandoc.convert_file(docx_path, 'md', outputfile=md_path)

        if os.path.exists(md_path):
            print(f"✓ 转换成功: {md_path}")
            return md_path
        else:
            print(f"转换失败: 未找到生成的文件 {md_path}")
            return None

    except Exception as e:
        print(f"转换文件 {docx_path} 时出错: {str(e)}")
        print(traceback.format_exc())
        return None


def get_content_until_next_heading(start_node, stop_tags: List[str]) -> str:
    """
    从一个起始的BeautifulSoup节点开始，收集其后所有同级节点的内容，
    直到遇到任何一个在stop_tags列表中的标签为止。

    参数:
        start_node: BeautifulSoup的标签节点，作为开始点。
        stop_tags: 一个包含标签名称的列表，如 ['h2', 'h3']，遇到这些标签时停止收集。

    返回:
        一个包含所有收集到的节点内容的HTML字符串。
    """
    content_html = []
    for sibling in start_node.find_next_siblings():
        if sibling.name in stop_tags:
            break
        content_html.append(str(sibling))
    return "".join(content_html).strip()


def html_to_text(html_string: Optional[str]) -> Optional[str]:
    """
    将包含HTML标签的字符串转换为纯文本。

    参数:
        html_string: 一个包含HTML的字符串。

    返回:
        一个只包含文本内容的字符串，或在输入为None时返回None。
    """
    if not html_string:
        return None
    soup = BeautifulSoup(html_string, 'html.parser')
    return soup.get_text(separator='\n', strip=True)


def clean_markdown_to_text(markdown_string: str) -> str:
    """
    一个关键的辅助函数，用于将一小段Markdown（如标题行）
    转换为纯文本，以便进行比较和映射。
    """
    html = markdown.markdown(markdown_string)
    return BeautifulSoup(html, 'html.parser').get_text(strip=True)


def parse_markdown_with_bs4(file_path: str) -> List[Dict]:
    """
    使用 markdown 和 BeautifulSoup 解析文件，提取二级章节及其下的特定内容。

    参数:
        file_path (str): Markdown文件的路径。

    返回:
        一个字典列表，每个字典包含：
        - 'h2_title_name': str
        - 'h2_content': str
        - 'XPATH': str or None
        - 'Supported_operations': str or None
    """
    # 跳过包含'nqa_md'的文件
    if 'nqa_md' in file_path:
        return []

    # 尝试多种编码方式读取文件
    markdown_text = None
    encoding_errors = []

    # 首先尝试 UTF-8
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在。")
        return []
    except UnicodeDecodeError as e:
        encoding_errors.append(f"UTF-8: {str(e)}")
    except Exception as e:
        encoding_errors.append(f"UTF-8: {str(e)}")

    # 如果 UTF-8 失败，尝试 GBK
    if markdown_text is None:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                markdown_text = f.read()
        except UnicodeDecodeError as e:
            encoding_errors.append(f"GBK: {str(e)}")
        except Exception as e:
            encoding_errors.append(f"GBK: {str(e)}")

    # 如果 GBK 也失败，尝试忽略编码错误
    if markdown_text is None:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                markdown_text = f.read()
                print(f"警告: 文件 '{file_path}' 使用忽略编码错误的方式读取")
        except Exception as e:
            encoding_errors.append(f"UTF-8(ignore): {str(e)}")

        # 如果忽略错误也失败，尝试 GBK 忽略错误
        if markdown_text is None:
            try:
                with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
                    markdown_text = f.read()
                    print(f"警告: 文件 '{file_path}' 使用 GBK 忽略编码错误的方式读取")
            except Exception as e:
                encoding_errors.append(f"GBK(ignore): {str(e)}")

    # 如果所有尝试都失败
    if markdown_text is None:
        print(f"错误: 无法读取文件 '{file_path}'，尝试的编码方式均失败:")
        for error in encoding_errors:
            print(f"  - {error}")
        return []

    html_content = markdown.markdown(markdown_text)
    soup = BeautifulSoup(html_content, 'html.parser')

    # 获取包含'/'的H2标题
    clean_titles_from_bs4 = [
        h2.get_text(strip=True) for h2 in soup.find_all('h2')
        if '/' in h2.get_text(strip=True)
    ]

    all_raw_h2_lines = re.findall(r'^##\s+\S.*$', markdown_text, re.MULTILINE)
    raw_h2_lines = [line for line in all_raw_h2_lines if '/' in line]

    if not clean_titles_from_bs4:
        print(f"{file_path}未找到任何标题中包含'/'的二级章节。")
        return []

    if len(clean_titles_from_bs4) != len(raw_h2_lines):
        print("警告: BeautifulSoup 解析出的H2标题数量与正则表达式找到的不匹配。")
        return []

    # 创建从干净标题到原始标题行的映射
    title_map = {}
    for raw_line in raw_h2_lines:
        title_content_only = raw_line.lstrip('#').strip()
        cleaned_version = clean_markdown_to_text(title_content_only)
        title_map[cleaned_version] = raw_line

    results = []

    for current_clean_title in clean_titles_from_bs4:
        current_raw_line = title_map.get(current_clean_title)
        if not current_raw_line:
            print(f"警告: 无法在映射中找到标题 '{current_clean_title}' 的原始行。跳过此章节。")
            continue

        try:
            current_index_in_all = all_raw_h2_lines.index(current_raw_line)
        except ValueError:
            continue

        next_raw_line = None
        if current_index_in_all + 1 < len(all_raw_h2_lines):
            next_raw_line = all_raw_h2_lines[current_index_in_all + 1]

        regex_start = rf'^{re.escape(current_raw_line)}\s*\n'

        if next_raw_line:
            regex_end = rf'(?=\n^{re.escape(next_raw_line)})'
            pattern = re.compile(regex_start + '(.*?)' + regex_end, re.DOTALL | re.MULTILINE)
        else:
            pattern = re.compile(regex_start + '(.*)', re.DOTALL | re.MULTILINE)

        match = pattern.search(markdown_text)
        h2_markdown_content = match.group(1).strip() if match else ""

        # 提取XPath和Supported operations
        xpath_text, operations_text = None, None
        if h2_markdown_content:
            section_html = markdown.markdown(h2_markdown_content)
            section_soup = BeautifulSoup(section_html, 'html.parser')
            netconf_h3 = section_soup.find('h3', string=lambda t: t and "NETCONF XPATH and supported operations" in t)

            if netconf_h3:
                xpath_h4, operations_h4 = None, None
                for sibling in netconf_h3.find_next_siblings():
                    if sibling.name in ['h3', 'h2']: break
                    if sibling.name == 'h4':
                        text = sibling.get_text(strip=True)
                        if not xpath_h4 and "XPATH" in text:
                            xpath_h4 = sibling
                        elif not operations_h4 and "Supported operations" in text:
                            operations_h4 = sibling

                stop_tags = ['h2', 'h3', 'h4']
                if xpath_h4:
                    xpath_text = html_to_text(get_content_until_next_heading(xpath_h4, stop_tags))
                if operations_h4:
                    operations_text = html_to_text(get_content_until_next_heading(operations_h4, stop_tags))

        results.append({
            'h2_title_name': current_clean_title,
            'h2_content': h2_markdown_content,
            'XPATH': xpath_text,
            'Supported_operations': operations_text
        })

    return results


def analyze_markdown_file(md_file_path: str, output_dir: str = DEFAULT_OUTPUT_DIR):
    """
    分析单个Markdown文件，提取NETCONF相关章节信息并生成JSON文件

    参数:
        md_file_path (str): Markdown文件的路径
        output_dir (str): 输出文件夹名称，默认为 DEFAULT_OUTPUT_DIR

    返回:
        dict: 分析结果统计信息
    """
    # 判断output_dir是否为绝对路径
    if os.path.isabs(output_dir):
        full_output_dir = output_dir
    else:
        # 获取Markdown文件所在目录
        md_dir = os.path.dirname(os.path.abspath(md_file_path))
        # 如果MD文件已经在输出文件夹中，则直接使用该文件夹
        if os.path.basename(md_dir) == output_dir:
            full_output_dir = md_dir
        else:
            # 否则在MD文件所在目录创建输出文件夹
            full_output_dir = os.path.join(md_dir, output_dir)

    os.makedirs(full_output_dir, exist_ok=True)
    print(f"\n--- 开始分析文件: {md_file_path} ---")

    parsed_data = parse_markdown_with_bs4(md_file_path)

    if not parsed_data:
        print(f"未能从文件中解析出任何符合条件的二级章节: {md_file_path}")
        return {
            'chapters_found': 0,
            'chapters_with_xpath': 0,
            'chapters_with_support': 0,
            'chapters_with_both': 0,
            'chapters_with_edit': 0
        }

    # 统计信息
    total_chapters = 0
    chapters_with_xpath = 0
    chapters_with_support = 0
    chapters_with_both = 0
    chapters_with_edit = 0

    # 处理章节信息
    itre_heading_dict = {}
    for chapter in parsed_data:
        total_chapters += 1

        support_ops = chapter.get('Supported_operations')
        has_xpath = chapter.get('XPATH') is not None
        has_support = support_ops is not None
        has_edit = has_support and "edit" in support_ops

        if has_xpath: chapters_with_xpath += 1
        if has_support: chapters_with_support += 1
        if has_xpath and has_support: chapters_with_both += 1
        if has_edit: chapters_with_edit += 1

        heading = chapter['h2_title_name']
        itre_heading_dict[heading] = {
            'chapter_name': heading,
            'markdown_content': chapter['h2_content'],
            'xpath': chapter['XPATH'],
            'support_xml_operations': support_ops
        }

    # 保存结果到JSON文件
    if itre_heading_dict:
        # 生成JSON文件名：使用原始文件的base名称
        original_filename = os.path.basename(md_file_path)
        base_filename = os.path.splitext(original_filename)[0]
        json_file_path = os.path.join(full_output_dir, f"{base_filename}.new.json")

        try:
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(itre_heading_dict, json_file, ensure_ascii=False, indent=4)
            print(f"✓ 分析结果已保存到: {json_file_path}")
        except Exception as e:
            print(f"保存JSON文件失败: {json_file_path}, 错误: {e}")

    # 打印分析结果
    print(f"分析完成 - 总章节数: {total_chapters}, 有XPath: {chapters_with_xpath}, 有操作: {chapters_with_support}")

    return {
        'chapters_found': total_chapters,
        'chapters_with_xpath': chapters_with_xpath,
        'chapters_with_support': chapters_with_support,
        'chapters_with_both': chapters_with_both,
        'chapters_with_edit': chapters_with_edit
    }


def process_docx_file(docx_path: str, output_dir: str = DEFAULT_OUTPUT_DIR, extract_revisions: bool = True):
    """
    处理单个DOCX文件：转换为Markdown并分析，同时提取修订内容

    参数:
        docx_path (str): DOCX文件的路径
        output_dir (str): 输出文件夹名称，默认为 DEFAULT_OUTPUT_DIR
        extract_revisions (bool): 是否提取修订内容，默认为 True
    """
    print(f"\n{'='*60}")
    print(f"开始处理DOCX文件: {docx_path}")
    print(f"{'='*60}")

    # 第一步：转换DOCX为Markdown
    md_file_path = convert_docx_to_markdown(docx_path, output_dir)

    if not md_file_path:
        print("转换失败，终止处理")
        return

    # 第二步：分析Markdown文件
    analysis_stats = analyze_markdown_file(md_file_path, output_dir)

    # 第三步：提取修订内容（根据参数决定是否执行）
    revision_stats = {}
    if extract_revisions and WordNetconfRevisionExtractor:
        print(f"\n--- 开始提取修订内容 ---")
        try:
            revision_extractor = WordNetconfRevisionExtractor(docx_path)
            revision_data = revision_extractor.extract()

            if revision_data:
                # 使用与netconf_doc_processor相同的输出目录
                docx_dir = os.path.dirname(os.path.abspath(docx_path))
                full_output_dir = os.path.join(docx_dir, output_dir) if not os.path.isabs(output_dir) else output_dir

                # 保存修订结果到相同目录
                name = os.path.splitext(os.path.basename(docx_path))[0]
                revision_path = os.path.join(full_output_dir, f"{name}.revisions.json")
                revision_extractor.save_json(revision_path)

                # 统计修订信息
                total_revisions = sum(len(revs) for revs in revision_data.values())
                revision_stats = {
                    'total_revisions': total_revisions,
                    'sections_with_revisions': len(revision_data),
                    'revisions_data': revision_data
                }

                print(f"提取完成 - 总修订数: {total_revisions}, 涉及章节: {len(revision_data)}")

                # 打印修订摘要
                revision_extractor.print_summary()
            else:
                print("未检测到修订内容")
                revision_stats = {'total_revisions': 0, 'sections_with_revisions': 0}
        except Exception as e:
            print(f"修订提取失败: {str(e)}")
            revision_stats = {'total_revisions': 0, 'sections_with_revisions': 0}
    else:
        if not extract_revisions:
            print("跳过修订提取（根据参数设置）")
        else:
            print("跳过修订提取（模块未加载）")
        revision_stats = {'total_revisions': 0, 'sections_with_revisions': 0}

    # 打印最终统计
    print(f"\n--- 处理完成 ---")
    print(f"原始文件: {docx_path}")
    print(f"输出文件夹: {output_dir}")
    print(f"Markdown文件: {md_file_path}")
    print(f"找到章节: {analysis_stats['chapters_found']}")
    print(f"包含XPath: {analysis_stats['chapters_with_xpath']}")
    print(f"包含操作: {analysis_stats['chapters_with_support']}")
    print(f"支持编辑: {analysis_stats['chapters_with_edit']}")
    print(f"修订记录: {revision_stats.get('total_revisions', 0)}")

    return analysis_stats, revision_stats


if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="将Word文档转换为Markdown并分析NETCONF相关章节信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 处理单个DOCX文件（使用默认输出文件夹 output，会提取修订内容）
  python netconf_doc_processor.py document.docx

  # 指定输出文件夹
  python netconf_doc_processor.py -o my_output document.docx

  # 处理多个DOCX文件
  python netconf_doc_processor.py file1.docx file2.docx file3.docx

  # 使用通配符处理多个文件（在支持的shell中）
  python netconf_doc_processor.py *.docx

  # 指定输出文件夹并处理多个文件
  python netconf_doc_processor.py -o results *.docx

  # 处理文件但不提取修订内容
  python netconf_doc_processor.py --no-revisions document.docx
        """
    )

    # 添加可选参数：输出文件夹
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"输出文件夹名称（默认: {DEFAULT_OUTPUT_DIR}）"
    )

    # 添加可选参数：是否提取修订内容
    parser.add_argument(
        "--no-revisions",
        action="store_true",
        default=False,
        help="不提取修订内容（默认会提取修订内容）"
    )

    # 添加位置参数：DOCX文件路径（支持多个）
    parser.add_argument(
        "docx_files",
        nargs='+',  # 表示接受1个或多个参数
        type=str,
        help="要处理的DOCX文件路径（支持多个文件）"
    )

    # 解析命令行参数
    args = parser.parse_args()

    # 验证输出文件夹名称
    output_dir = args.output_dir.strip()
    if not output_dir:
        print("警告: 输出文件夹名称为空，使用默认值")
        output_dir = DEFAULT_OUTPUT_DIR

    # 根据命令行参数决定是否提取修订内容
    extract_revisions = not args.no_revisions

    # 验证所有文件是否存在且为DOCX格式
    valid_files = []
    for docx_file in args.docx_files:
        if not os.path.exists(docx_file):
            print(f"错误: 文件不存在: {docx_file}")
            continue

        if not docx_file.endswith('.docx'):
            print(f"错误: 文件不是DOCX格式: {docx_file}")
            continue

        valid_files.append(docx_file)

    if not valid_files:
        print("没有有效的文件需要处理。")
        exit(1)

    print(f"准备处理 {len(valid_files)} 个DOCX文件...")
    print(f"输出文件夹: {output_dir}")
    print(f"提取修订内容: {'是' if extract_revisions else '否'}")

    # 处理每个有效的DOCX文件
    total_stats = {
        'total_files': len(valid_files),
        'total_chapters': 0,
        'total_chapters_with_xpath': 0,
        'total_chapters_with_support': 0,
        'total_chapters_with_edit': 0,
        'total_revisions': 0,
        'sections_with_revisions': 0
    }

    for docx_file in valid_files:
        try:
            # 调用更新后的process_docx_file函数，传递extract_revisions参数
            analysis_stats, revision_stats = process_docx_file(docx_file, output_dir, extract_revisions)

            # 收集分析统计信息
            total_stats['total_chapters'] += analysis_stats['chapters_found']
            total_stats['total_chapters_with_xpath'] += analysis_stats['chapters_with_xpath']
            total_stats['total_chapters_with_support'] += analysis_stats['chapters_with_support']
            total_stats['total_chapters_with_edit'] += analysis_stats['chapters_with_edit']

            # 收集修订统计信息
            total_stats['total_revisions'] += revision_stats.get('total_revisions', 0)
            total_stats['sections_with_revisions'] += revision_stats.get('sections_with_revisions', 0)

        except Exception as e:
            print(f"处理文件时发生错误: {docx_file}, 错误: {e}")
            continue

    # 打印总体统计报告
    print(f"\n{'='*60}")
    print("总体处理统计报告")
    print(f"{'='*60}")
    print(f"处理文件总数: {total_stats['total_files']}")
    print(f"提取章节总数: {total_stats['total_chapters']}")
    print(f"包含XPath的章节: {total_stats['total_chapters_with_xpath']}")
    print(f"包含操作的章节: {total_stats['total_chapters_with_support']}")
    print(f"支持编辑操作的章节: {total_stats['total_chapters_with_edit']}")
    print(f"修订记录总数: {total_stats['total_revisions']}")
    print(f"涉及修订的章节: {total_stats['sections_with_revisions']}")

    if total_stats['total_chapters'] > 0:
        print(f"\n文档分析百分比统计:")
        print(f"XPath覆盖率: {(total_stats['total_chapters_with_xpath']/total_stats['total_chapters']*100):.1f}%")
        print(f"操作覆盖率: {(total_stats['total_chapters_with_support']/total_stats['total_chapters']*100):.1f}%")
        print(f"编辑操作覆盖率: {(total_stats['total_chapters_with_edit']/total_stats['total_chapters']*100):.1f}%")

    if total_stats['total_files'] > 0:
        print(f"\n修订统计:")
        avg_revisions_per_file = total_stats['total_revisions'] / total_stats['total_files']
        print(f"平均每文件修订数: {avg_revisions_per_file:.1f}")

    print(f"\n{'='*60}")
    print("所有处理完成！")
    print(f"所有结果已保存至: {output_dir} 文件夹")
    print(f"{'='*60}")