#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将project目录下除了.svn目录外的.c和.h文件从UTF-8转换为GB2312编码
"""

import os
import sys
import argparse
import concurrent.futures
from pathlib import Path
from threading import Lock


def detect_encoding(file_path):
    """简化编码检测"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        # 首先尝试UTF-8（严格模式）
        try:
            raw_data.decode('utf-8')
            return 'utf-8', 0.95
        except UnicodeDecodeError:
            pass

        # 然后尝试GB编码
        gb_encodings = ['gb18030', 'gb2312', 'gbk']
        for enc in gb_encodings:
            try:
                raw_data.decode(enc, errors='strict')
                return enc, 0.8
            except UnicodeDecodeError:
                try:
                    raw_data.decode(enc, errors='ignore')
                    return enc, 0.6
                except UnicodeDecodeError:
                    continue

        # 最后尝试Mac Roman编码
        try:
            raw_data.decode('mac_roman', errors='strict')
            return 'mac_roman', 0.7
        except UnicodeDecodeError:
            try:
                raw_data.decode('mac_roman', errors='ignore')
                return 'mac_roman', 0.5
            except UnicodeDecodeError:
                pass

        return None, 0.0
    except Exception as e:
        print(f"检测文件 {file_path} 编码时出错: {e}")
        return None, 0.0


def is_utf8_file(file_path, min_confidence=0.8, verbose=False):
    """检查文件是否是UTF-8编码（严格模式）"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        # 尝试用UTF-8严格解码
        try:
            raw_data.decode('utf-8')
            return True  # 严格模式成功，肯定是UTF-8
        except UnicodeDecodeError:
            # 严格模式失败，不是UTF-8
            return False
    except Exception as e:
        if verbose:
            print(f"检查UTF-8文件 {file_path} 时出错: {e}")
        return False


def convert_to_gb2312(file_path, backup=False, encoding_mode='gb18030', verbose=False):
    """将UTF-8文件转换为gb18030编码

    Args:
        file_path: 文件路径
        backup: 是否创建备份
        encoding_mode: 目标编码模式（我们只使用gb18030）
        verbose: 是否显示详细输出
    """
    try:
        # 检查是否是UTF-8文件
        if not is_utf8_file(file_path, verbose=verbose):
            if verbose:
                print(f"文件 {file_path} 不是UTF-8编码，跳过")
            return False

        current_encoding, confidence = detect_encoding(file_path)
        if verbose:
            print(f"文件: {file_path}")
            print(f"  当前编码: {current_encoding} (置信度: {confidence:.2%})")

        # 读取文件内容
        with open(file_path, 'rb') as f:
            content = f.read()

        # 解码为UTF-8
        try:
            decoded_content = content.decode('utf-8')
        except UnicodeDecodeError as e:
            if verbose:
                print(f"  无法用UTF-8解码: {e}")
            return False

        # 备份原始文件
        if backup:
            backup_path = str(file_path) + '.backup'
            with open(backup_path, 'wb') as f:
                f.write(content)
            if verbose:
                print(f"  已创建备份: {backup_path}")

        # 统计可能丢失的字符（gb18030应该支持所有字符，但检查一下）
        lost_chars = []
        for char in decoded_content:
            try:
                char.encode('gb18030')
            except UnicodeEncodeError:
                if char not in lost_chars:
                    lost_chars.append(char)

        if lost_chars and verbose:
            print(f"  警告: {len(lost_chars)}个字符可能无法编码到gb18030:")
            for i, char in enumerate(lost_chars[:5]):  # 只显示前5个
                print(f"    '{char}' (Unicode: U+{ord(char):04X})")
            if len(lost_chars) > 5:
                print(f"    ... 还有{len(lost_chars)-5}个字符")

        # 转换编码 - 总是使用gb18030
        try:
            encoded_content = decoded_content.encode('gb18030', errors='ignore')
            target_encoding = 'gb18030'
        except UnicodeEncodeError as e:
            if verbose:
                print(f"  转换为gb18030失败: {e}")
            return False

        # 写入编码后的文件
        with open(file_path, 'wb') as f:
            f.write(encoded_content)

        if verbose:
            print(f"  已转换为gb18030编码")
            if lost_chars:
                print(f"  注意: 有字符丢失，建议检查文件内容")
        return True

    except Exception as e:
        if verbose:
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


def load_conversion_log(log_file_path, root_dir):
    """加载UTF-8转换清单
    返回一个包含所有在清单中的文件路径的集合
    注意: 清单中的路径是相对于根目录的，需要转换为绝对路径
    """
    converted_files = set()

    if not os.path.exists(log_file_path):
        print(f"警告: 转换日志文件 {log_file_path} 不存在")
        return converted_files

    try:
        root_path = Path(root_dir).resolve()
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                # 将相对路径转换为绝对路径（使用 Path.resolve() 确保路径格式统一）
                abs_path = str((root_path / line).resolve())
                converted_files.add(abs_path)
        print(f"已加载转换清单: {log_file_path} (包含 {len(converted_files)} 个文件)")
    except Exception as e:
        print(f"错误: 无法读取转换清单 {log_file_path}: {e}")

    return converted_files


def main():
    parser = argparse.ArgumentParser(description='将UTF-8编码的.c和.h文件转换为中文编码')
    parser.add_argument('root_dir', help='要处理的根目录')
    parser.add_argument('--backup', action='store_true',
                       help='创建备份文件（默认不创建备份）')
    parser.add_argument('--dry-run', action='store_true',
                       help='只显示要转换的文件，不实际转换')
    parser.add_argument('--force', action='store_true',
                       help='强制转换非UTF-8编码的文件')
    parser.add_argument('--min-confidence', type=float, default=0.8,
                       help='UTF-8检测的最小置信度 (默认: 0.8)')
    parser.add_argument('--encoding', choices=['gb2312', 'gbk', 'gb18030'],
                       default='gb18030',
                       help='目标编码 (默认: gb18030，最兼容)')
    parser.add_argument('--conversion-log', default='utf8_conversion.log',
                       help='从UTF-8转换时生成的日志文件路径 (默认: utf8_conversion.log)')
    parser.add_argument('--no-skip-original-utf8', action='store_true',
                       help='禁用跳过原始UTF-8文件功能 (默认: 开启跳过)')
    parser.add_argument('--workers', type=int, default=64,
                       help='并发工作线程数 (默认: 64)')
    parser.add_argument('--verbose', action='store_true',
                       help='显示详细输出 (默认: 静默模式)')

    args = parser.parse_args()

    root_dir = args.root_dir
    if not os.path.isdir(root_dir):
        print(f"错误: 目录 {root_dir} 不存在")
        sys.exit(1)

    print(f"开始处理目录: {root_dir}")
    print(f"排除.svn目录")
    print(f"UTF-8检测最小置信度: {args.min_confidence}")
    print(f"目标编码: {args.encoding}")

    # 加载转换清单（如果需要跳过原始UTF-8文件）
    converted_files = set()
    if not args.no_skip_original_utf8:
        converted_files = load_conversion_log(args.conversion_log, root_dir)

    # 查找文件
    files = find_files_to_convert(root_dir)
    print(f"找到 {len(files)} 个.c/.h文件")

    if args.dry_run:
        print("\n要处理的文件列表:")

        files_by_category = {
            'to_convert': [],      # 应该转换的文件（在清单中）
            'skip_original': [],   # 原始UTF-8文件（不在清单中，跳过）
            'non_utf8': [],        # 非UTF-8文件（需要--force）
        }

        for file_path in files:
            # 使用 resolve() 确保路径格式与 converted_files 中的一致
            file_path_str = str(Path(file_path).resolve())
            is_utf8 = is_utf8_file(file_path, args.min_confidence, verbose=args.verbose)

            if not is_utf8 and not args.force:
                encoding, confidence = detect_encoding(file_path)
                files_by_category['non_utf8'].append((file_path, encoding or '未知', confidence))
            elif not args.no_skip_original_utf8 and converted_files and file_path_str not in converted_files:
                # 原始UTF-8文件，跳过
                files_by_category['skip_original'].append((file_path, 'UTF-8', 1.0))
            else:
                # 应该转换的文件
                encoding, confidence = detect_encoding(file_path)
                files_by_category['to_convert'].append((file_path, encoding or 'UTF-8', confidence))

        print(f"\n应该转换的文件 ({len(files_by_category['to_convert'])}个):")
        for file_path, encoding, confidence in files_by_category['to_convert'][:20]:
            print(f"  {file_path} ({encoding}, 置信度: {confidence:.2%})")
        if len(files_by_category['to_convert']) > 20:
            print(f"  ... 还有 {len(files_by_category['to_convert']) - 20} 个文件")

        if files_by_category['skip_original']:
            print(f"\n跳过原始UTF-8文件 ({len(files_by_category['skip_original'])}个):")
            for file_path, encoding, confidence in files_by_category['skip_original'][:20]:
                print(f"  {file_path} ({encoding}, 置信度: {confidence:.2%})")
            if len(files_by_category['skip_original']) > 20:
                print(f"  ... 还有 {len(files_by_category['skip_original']) - 20} 个文件")
            print(f"  这些文件本来就是UTF-8编码，不会转换为GB")

        print(f"\n非UTF-8编码的文件 ({len(files_by_category['non_utf8'])}个):")
        for file_path, encoding, confidence in files_by_category['non_utf8'][:20]:
            print(f"  {file_path} ({encoding}, 置信度: {confidence:.2%})")
        if len(files_by_category['non_utf8']) > 20:
            print(f"  ... 还有 {len(files_by_category['non_utf8']) - 20} 个文件")

        if args.force:
            print(f"\n注意: 使用 --force 参数将强制转换所有文件")
        if args.no_skip_original_utf8:
            print(f"\n注意: 已禁用跳过原始UTF-8文件功能")
        return

    # 转换文件 - 使用线程池并发处理
    # 线程安全的统计变量
    success_count = 0
    fail_count = 0
    skip_count = 0
    skip_original_count = 0  # 跳过的原始UTF-8文件计数
    failed_files = []

    # 线程锁
    success_lock = Lock()
    fail_lock = Lock()
    skip_lock = Lock()
    skip_original_lock = Lock()
    failed_lock = Lock()

    def process_file_gb(file_path):
        nonlocal success_count, fail_count, skip_count, skip_original_count, failed_files

        # 使用 resolve() 确保路径格式与 converted_files 中的一致
        file_path_str = str(Path(file_path).resolve())

        try:
            # 检查是否是UTF-8文件
            is_utf8 = is_utf8_file(file_path, args.min_confidence, verbose=args.verbose)

            if not is_utf8 and not args.force:
                encoding, confidence = detect_encoding(file_path)
                with skip_lock:
                    skip_count += 1
                return

            # 检查是否是原始UTF-8文件（应该跳过）
            if not args.no_skip_original_utf8 and converted_files and file_path_str not in converted_files:
                with skip_original_lock:
                    skip_original_count += 1
                return

            # 转换文件
            if convert_to_gb2312(file_path, backup=args.backup, encoding_mode=args.encoding, verbose=args.verbose):
                with success_lock:
                    success_count += 1
            else:
                with fail_lock:
                    fail_count += 1
                with failed_lock:
                    failed_files.append((file_path, "转换失败"))

        except Exception as e:
            with fail_lock:
                fail_count += 1
            with failed_lock:
                failed_files.append((file_path, f"处理异常: {e}"))

    # 并发处理
    print(f"开始并发处理 {len(files)} 个文件...")
    max_workers = min(args.workers, len(files))  # 使用用户指定的线程数

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = [executor.submit(process_file_gb, file_path) for file_path in files]

        # 等待完成并显示进度
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            try:
                future.result()  # 等待任务完成，捕获可能的异常
                if completed % 20 == 0 or completed == len(files):
                    print(f"进度: {completed}/{len(files)} ({completed/len(files)*100:.1f}%)")
            except Exception as e:
                with fail_lock:
                    fail_count += 1
                with failed_lock:
                    failed_files.append(("未知文件", f"任务异常: {e}"))

    print(f"\n{'='*50}")
    print(f"处理完成:")
    print(f"  成功转换: {success_count} 个文件")
    print(f"  跳过(非UTF-8): {skip_count} 个文件")
    if not args.no_skip_original_utf8:
        print(f"  跳过(原始UTF-8): {skip_original_count} 个文件")
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
        fail_log = '/tmp/convert_to_gb2312_failed.log'
        with open(fail_log, 'w', encoding='utf-8') as f:
            f.write("转换到GB18030失败文件列表:\n")
            f.write("=" * 60 + "\n")
            for file_path, reason in failed_files:
                f.write(f"{file_path} - {reason}\n")
        print(f"失败文件列表已保存到: {fail_log}")


if __name__ == '__main__':
    main()
