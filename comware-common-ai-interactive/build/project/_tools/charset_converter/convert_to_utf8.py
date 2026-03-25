#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将project目录下除了.svn目录外的.c和.h文件转换为UTF-8编码
"""

import os
import sys
import argparse
import datetime
from pathlib import Path


def detect_encoding(file_path):
    """检测文件编码 - 主要检测GB编码、UTF-8和Mac Roman
    策略：优先确保GB文件的正确检测，避免误判为Mac Roman
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        # 1. 首先检查是否是UTF-8（严格模式）
        try:
            raw_data.decode('utf-8')
            return 'utf-8', 0.95
        except UnicodeDecodeError:
            pass

        # 2. 检查GB编码 - 使用启发式方法避免误判
        gb_encodings = ['gb18030', 'gb2312', 'gbk']

        best_gb_encoding = None
        best_gb_confidence = 0.0

        for enc in gb_encodings:
            try:
                # 尝试严格解码
                decoded = raw_data.decode(enc, errors='strict')

                # 分析解码后的内容
                chinese_chars = 0
                total_chars = 0
                suspicious_chars = 0  # 可疑字符（可能是Mac Roman特殊字符误判）

                for char in decoded:
                    total_chars += 1

                    # 检查中文字符
                    if ('\u4e00' <= char <= '\u9fff' or  # 基本汉字
                        '\u3400' <= char <= '\u4dbf' or  # 扩展A
                        '\u3000' <= char <= '\u303f'):   # 中文标点
                        chinese_chars += 1
                    # 检查可疑的Mac Roman特殊字符（当中文字符出现时）
                    elif char in {'©', '®', '™', '•', '§', '¶'}:
                        suspicious_chars += 1

                if total_chars > 0:
                    chinese_ratio = chinese_chars / total_chars
                    suspicious_ratio = suspicious_chars / total_chars

                    # 计算置信度
                    confidence = 0.0

                    if chinese_ratio > 0.2:  # 20%以上中文字符，很可能是GB
                        confidence = 0.9 + min(chinese_ratio * 0.1, 0.05)
                    elif chinese_ratio > 0.05:  # 5%-20%中文字符
                        confidence = 0.7 + (chinese_ratio - 0.05) * 1.33
                    elif chinese_ratio > 0:  # 有中文字符但很少
                        confidence = 0.6
                    else:  # 没有中文字符
                        confidence = 0.5

                    # 如果有可疑字符，降低置信度
                    if suspicious_ratio > 0:
                        confidence = max(confidence - suspicious_ratio * 0.5, 0.3)

                    if confidence > best_gb_confidence:
                        best_gb_encoding = enc
                        best_gb_confidence = confidence

            except UnicodeDecodeError:
                # 严格解码失败，尝试ignore模式
                try:
                    raw_data.decode(enc, errors='ignore')
                    # ignore模式成功，但置信度较低
                    if 0.4 > best_gb_confidence:
                        best_gb_encoding = enc
                        best_gb_confidence = 0.4
                except UnicodeDecodeError:
                    continue

        # 如果有较高的GB置信度，返回GB编码
        if best_gb_encoding and best_gb_confidence >= 0.6:
            return best_gb_encoding, best_gb_confidence

        # 3. 检查Mac Roman编码（只有当GB置信度不高时）
        if not best_gb_encoding or best_gb_confidence < 0.6:
            try:
                # 尝试Mac Roman严格解码
                decoded = raw_data.decode('mac_roman', errors='strict')

                # 检查是否包含典型的Mac Roman内容
                mac_special_chars = 0
                total_chars = 0
                mac_special_set = {'©', '®', '™', '•', '§', '¶', '†', '‡', '‰', '€'}

                for char in decoded:
                    total_chars += 1
                    if char in mac_special_set:
                        mac_special_chars += 1
                    elif '\x80' <= char <= '\xff':  # 其他非ASCII Mac Roman字符
                        mac_special_chars += 0.5

                if total_chars > 0:
                    special_ratio = mac_special_chars / total_chars

                    # 计算Mac Roman置信度
                    if special_ratio > 0.1:  # 10%以上特殊字符
                        mac_confidence = 0.8 + min(special_ratio * 0.2, 0.15)
                    elif special_ratio > 0.01:  # 1%-10%
                        mac_confidence = 0.6 + (special_ratio - 0.01) * 2.22
                    else:  # 很少或没有特殊字符
                        mac_confidence = 0.5

                    # 如果Mac Roman置信度高于GB，返回Mac Roman
                    if mac_confidence > best_gb_confidence:
                        return 'mac_roman', mac_confidence

            except UnicodeDecodeError:
                # Mac Roman严格解码失败
                pass

        # 4. 返回最好的编码（可能是GB或None）
        if best_gb_encoding:
            return best_gb_encoding, best_gb_confidence

        # 5. 如果都不行，返回未知
        return None, 0.0

    except Exception as e:
        print(f"检测文件 {file_path} 编码时出错: {e}")
        return None, 0.0


def convert_to_utf8(file_path, backup=False):
    """将文件转换为UTF-8编码"""
    try:
        # 检测当前编码
        encoding, confidence = detect_encoding(file_path)

        if encoding is None:
            print(f"无法检测 {file_path} 的编码，跳过")
            return False

        print(f"文件: {file_path}")
        print(f"  当前编码: {encoding} (置信度: {confidence:.2%})")

        # 如果已经是UTF-8，跳过
        if encoding.lower() in ['utf-8', 'utf-8-sig']:
            print(f"  已经是UTF-8编码，跳过")
            return True

        # 只处理GB编码文件，Mac Roman文件也跳过（同原始UTF-8一样处理）
        if encoding.lower() not in ['gb18030', 'gb2312', 'gbk']:
            print(f"  不是GB编码文件，跳过 (包括Mac Roman文件)")
            return False

        # 读取文件内容
        with open(file_path, 'rb') as f:
            content = f.read()

        # 解码并重新编码为UTF-8
        # 统一使用gb18030解码（因为它兼容gb2312和gbk）
        try:
            decoded_content = content.decode('gb18030', errors='ignore')
        except UnicodeDecodeError as e:
            print(f"  使用gb18030解码失败: {e}")
            return False

        # 备份原始文件
        if backup:
            backup_path = str(file_path) + '.bak'
            with open(backup_path, 'wb') as f:
                f.write(content)
            print(f"  已创建备份: {backup_path}")

        # 写入UTF-8编码的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(decoded_content)

        print(f"  已转换为UTF-8编码")
        return True

    except Exception as e:
        print(f"转换文件 {file_path} 时出错: {e}")
        return False


def find_files_to_convert(root_dir):
    """查找需要转换的文件"""
    files_to_convert = []
    root_path = Path(root_dir)

    for file_path in root_path.rglob('*.[ch]'):
        # 排除.svn目录
        if '.svn' in str(file_path).split(os.sep):
            continue

        # 只处理.c和.h文件
        if file_path.suffix.lower() in ['.c', '.h']:
            files_to_convert.append(file_path)

    return files_to_convert


def main():
    parser = argparse.ArgumentParser(description='将.c和.h文件转换为UTF-8编码')
    parser.add_argument('root_dir', help='要处理的根目录')
    parser.add_argument('--backup', action='store_true',
                       help='创建备份文件（默认不创建备份）')
    parser.add_argument('--dry-run', action='store_true',
                       help='只显示要转换的文件，不实际转换')
    parser.add_argument('--log-file', default='utf8_conversion.log',
                       help='记录转换文件的日志文件路径 (默认: utf8_conversion.log)')

    args = parser.parse_args()

    root_dir = args.root_dir
    if not os.path.isdir(root_dir):
        print(f"错误: 目录 {root_dir} 不存在")
        sys.exit(1)

    print(f"开始处理目录: {root_dir}")
    print(f"排除.svn目录")

    # 创建根目录的Path对象
    root_path = Path(root_dir).resolve()

    # 查找文件
    files = find_files_to_convert(root_dir)

    # 确保所有文件路径都是绝对路径
    files = [Path(f).resolve() if isinstance(f, str) else f.resolve() for f in files]
    print(f"找到 {len(files)} 个.c/.h文件")

    if args.dry_run:
        print("\n要处理的文件列表:")
        for file_path in files[:50]:  # 只显示前50个
            print(f"  {file_path}")
        if len(files) > 50:
            print(f"  ... 还有 {len(files) - 50} 个文件")
        return

    # 转换文件
    success_count = 0
    fail_count = 0
    skip_count = 0
    failed_files = []
    converted_files = []  # 记录实际被转换的文件

    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] ", end='')

        # 检测编码
        encoding, confidence = detect_encoding(file_path)
        if encoding is None:
            fail_count += 1
            failed_files.append((file_path, "无法检测编码"))
            continue

        # 如果已经是UTF-8，跳过
        if encoding.lower() in ['utf-8', 'utf-8-sig']:
            skip_count += 1
            continue

        # 转换文件
        if convert_to_utf8(file_path, backup=args.backup):
            success_count += 1
            # 记录相对路径（相对于根目录）
            rel_path = file_path.relative_to(root_path)
            converted_files.append(str(rel_path))  # 记录转换成功的文件
        else:
            fail_count += 1
            failed_files.append((file_path, "转换失败"))

    # 保存转换清单
    if converted_files:
        try:
            log_path = args.log_file
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("# UTF-8转换文件清单\n")
                f.write("# 这些文件是从非UTF-8编码转换为UTF-8的\n")
                f.write("# 可以使用此清单在转回GB编码时跳过原始UTF-8文件\n")
                f.write("# 生成时间: " + datetime.datetime.now().isoformat() + "\n")
                f.write("=" * 60 + "\n")
                for file_path in converted_files:
                    f.write(file_path + "\n")
            print(f"\n转换清单已保存到: {log_path}")
            print(f"  包含 {len(converted_files)} 个文件")
        except Exception as e:
            print(f"\n警告: 无法保存转换清单到 {args.log_file}: {e}")

    print(f"\n{'='*50}")
    print(f"处理完成:")
    print(f"  成功转换: {success_count} 个文件")
    print(f"  跳过(已UTF-8): {skip_count} 个文件")
    print(f"  失败: {fail_count} 个文件")
    print(f"  总计: {len(files)} 个文件")

    # 显示失败文件
    if failed_files:
        print(f"\n失败文件列表 ({len(failed_files)} 个):")
        for i, (file_path, reason) in enumerate(failed_files[:20], 1):
            print(f"  {i}. {file_path} ({reason})")
        if len(failed_files) > 20:
            print(f"  ... 还有 {len(failed_files) - 20} 个失败文件")

        # 保存失败文件列表到文件
        fail_log = '/tmp/convert_to_utf8_failed.log'
        with open(fail_log, 'w', encoding='utf-8') as f:
            f.write("转换到UTF-8失败文件列表:\n")
            f.write("=" * 60 + "\n")
            for file_path, reason in failed_files:
                f.write(f"{file_path} - {reason}\n")
        print(f"失败文件列表已保存到: {fail_log}")


if __name__ == '__main__':
    main()