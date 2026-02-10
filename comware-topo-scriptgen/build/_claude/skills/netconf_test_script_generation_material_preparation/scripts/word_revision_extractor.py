# -*- coding: utf-8 -*-
"""
Word文档修订内容提取工具
功能：提取文档（含表格）中的插入和删除记录，按二级章节归类，支持NETCONF相关需求
版本：v2.1 (集成netconf_doc_processor)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph


# Word XML 命名空间 (用于属性获取)
NS_W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

class WordNetconfRevisionExtractor:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.filename = os.path.basename(docx_path)
        
        # 结果字典 { "二级章节名": [ {修订详情}, ... ] }
        self.revisions_data = {}
        
        # 状态变量：记录当前所处的章节
        self.current_h1 = ""
        self.current_h2 = "未命名章节(文档开头)"

    def _get_xml_text(self, element):
        """
        从 XML 元素中递归提取文本
        """
        text_parts = []
        for node in element.iter():
            # 获取 w:t (常规文本)
            if node.tag.endswith('}t'): # 匹配命名空间结尾的 t
                if node.text:
                    text_parts.append(node.text)
            # 获取 w:delText (删除线文本)
            elif node.tag.endswith('}delText'):
                if node.text:
                    text_parts.append(node.text)
        return "".join(text_parts)

    def _process_paragraph(self, paragraph):
        """
        处理单个段落：
        1. 检查是否是标题，更新当前章节状态
        2. 扫描 XML 查找 ins 和 del 标签
        """
        # --- 1. 更新章节上下文 (状态保持) ---
        # 注意：这里只读取样式名称，不读取具体文本内容，以免被修订内容干扰
        try:
            style_name = paragraph.style.name
            # 根据实际情况调整标题样式名，兼容中英文
            if style_name.startswith('Heading 1') or style_name.startswith('标题 1'):
                self.current_h1 = paragraph.text.strip()
                # 遇到一级标题，重置二级标题状态（可选，视需求而定）
                self.current_h2 = f"{self.current_h1} (概述)" 
            
            elif style_name.startswith('Heading 2') or style_name.startswith('标题 2'):
                # 更新当前二级章节
                clean_text = "".join([r.text for r in paragraph.runs]) # 获取不含修订标记的纯文本
                self.current_h2 = clean_text.strip() or "无标题章节"
        except Exception:
            pass

        # --- 2. 深入 XML 查找修订 ---
        # 获取底层 XML 元素
        p_element = paragraph._element
        
        # 【关键修复】这里 xpath 不传 namespaces 参数，python-docx 会自动处理 'w:' 前缀
        
        # A. 查找所有插入节点 <w:ins>
        for ins in p_element.xpath('.//w:ins'):
            self._add_record(ins, "插入", paragraph)

        # B. 查找所有删除节点 <w:del>
        for delete in p_element.xpath('.//w:del'):
            self._add_record(delete, "删除", paragraph)

    def _add_record(self, element, rev_type, paragraph):
        """解析修订节点并存入结果"""
        # 提取修订的具体文本内容
        content = self._get_xml_text(element)
        if not content.strip():
            return

        # 提取属性 (需要用完整的命名空间 URL)
        author = element.get(f"{{{NS_W}}}author", "Unknown")
        date_str = element.get(f"{{{NS_W}}}date", "")
        
        # 简单的日期格式化
        display_date = date_str.replace("T", " ")[:19] if date_str else ""

        # 判断是否在表格中
        location = "Table" if self._is_inside_table(paragraph) else "Text"

        # 构造记录对象
        record = {
            "type": rev_type,          # 插入 或 删除
            "text": content,           # 修订内容
            "section_level2": self.current_h2, # 【核心需求】所属二级章节
            "author": author,
            "date": display_date,
            "location_type": location
        }

        # 存入字典，按章节归类
        if self.current_h2 not in self.revisions_data:
            self.revisions_data[self.current_h2] = []
        
        self.revisions_data[self.current_h2].append(record)

    def _is_inside_table(self, paragraph):
        """判断段落是否在表格内"""
        try:
            # 向上查找父节点，看是否有 tbl 标签
            parent = paragraph._element.getparent()
            while parent is not None:
                if parent.tag.endswith('tbl'):
                    return True
                parent = parent.getparent()
        except:
            pass
        return False

    def iter_block_items(self, parent):
        """
        生成器：按文档顺序遍历所有块级元素（段落 + 表格）
        这对于保持章节上下文至关重要
        """
        if isinstance(parent, _Document):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            return

        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    def extract(self):
        """执行提取的主入口"""
        try:
            document = Document(self.docx_path)
        except Exception as e:
            print(f"Error: 无法打开文件 {self.docx_path}")
            print(f"Reason: {str(e)}")
            return {}

        # 重置状态
        self.revisions_data = {}
        self.current_h1 = ""
        self.current_h2 = "文档前言/未归类"

        # 遍历文档体（包含正文和表格）
        for block in self.iter_block_items(document):
            if isinstance(block, Paragraph):
                self._process_paragraph(block)
            elif isinstance(block, Table):
                # 表格本身不作为章节标题，但包含的内容需要提取
                for row in block.rows:
                    for cell in row.cells:
                        # 递归处理单元格内的段落
                        for p in cell.paragraphs:
                            self._process_paragraph(p)
        
        return self.revisions_data

    def save_json(self, output_path=None):
        """保存结果到文件"""
        if not self.revisions_data:
            return

        if not output_path:
            # 参考 netconf_doc_processor.py 的路径保存方式
            # 获取DOCX文件所在目录
            docx_dir = os.path.dirname(os.path.abspath(self.docx_path))

            # 在DOCX文件所在目录创建输出文件夹
            output_dir = os.path.join(docx_dir, "output")
            os.makedirs(output_dir, exist_ok=True)

            # 生成文件路径
            name = os.path.splitext(self.filename)[0]
            output_path = os.path.join(output_dir, f"{name}.revisions.json")

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.revisions_data, f, ensure_ascii=False, indent=4)
            print(f"[成功] 结果已保存至: {output_path}")
        except Exception as e:
            print(f"[错误] 保存 JSON 失败: {e}")

    def print_summary(self):
        """在控制台打印简报"""
        if not self.revisions_data:
            print(f"[{self.filename}] 未检测到修订内容。")
            return

        total_count = sum(len(v) for v in self.revisions_data.values())
        print(f"\n{'='*20} 提取报告 {'='*20}")
        print(f"文件: {self.filename}")
        print(f"总修订数: {total_count}")
        print("-" * 50)
        
        for section, revs in self.revisions_data.items():
            print(f"章节: [{section}] - {len(revs)} 处修订")

# --- 主程序逻辑 ---

def process_single_file(docx_path):
    if not os.path.isfile(docx_path):
        print(f"错误: 文件不存在 -> {docx_path}")
        return

    print(f"正在处理: {docx_path} ...")
    extractor = WordNetconfRevisionExtractor(docx_path)
    data = extractor.extract()

    extractor.print_summary()
    if data:
        extractor.save_json()

def main():
    parser = argparse.ArgumentParser(description='Word文档修订提取与NETCONF工具 (含二级章节定位)')
    parser.add_argument('file', nargs='?', help='Word文档路径 (.docx)')
    args = parser.parse_args()

    # 这里为了调试方便，如果没有传参，可以硬编码一个测试路径
    # docx_file = args.file or r"D:\TEST\test.docx" 
    docx_file = args.file

    if not docx_file:
        print("用法: python docx_process.py <文件路径>")
        # 兼容用户在 IDE 中直接运行的情况
        # docx_file = input("请输入文件路径: ").strip().strip('"')
        return

    process_single_file(docx_file)

if __name__ == "__main__":
    main()