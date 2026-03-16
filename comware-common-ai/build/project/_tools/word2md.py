#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word转Markdown转换工具
功能：
1. 自动检测并安装缺失的依赖（pandoc）
2. 支持 .docx 和 .docm 文件
3. 在Linux上处理.docm文件（通过解压/重新打包）
4. 支持单个文件和批量转换
5. 自动清理临时文件
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
import zipfile
import tempfile
import shutil
import platform

VERSION = "1.0.0"

def print_header():
    """打印工具标题"""
    print("=" * 60)
    print(f"Word转Markdown转换工具 v{VERSION}")
    print("=" * 60)

def check_dependencies():
    """检查并安装依赖"""
    print("检查系统依赖...")

    # 检查pandoc
    pandoc_installed = check_pandoc_installed()

    if not pandoc_installed:
        print("pandoc 未安装，尝试安装...")
        if install_pandoc():
            print("✅ pandoc 安装成功")
        else:
            print("⚠️  pandoc 安装失败，请手动安装：")
            print("   Ubuntu/Debian: sudo apt-get install pandoc")
            print("   CentOS/RHEL: sudo yum install pandoc")
            print("   macOS: brew install pandoc")
            print("   或从 https://pandoc.org/installing.html 下载")
            return False

    # 检查Python标准库
    missing_libs = []
    for lib in ["zipfile", "tempfile", "shutil", "argparse", "subprocess"]:
        try:
            __import__(lib)
        except ImportError:
            missing_libs.append(lib)

    if missing_libs:
        print(f"❌ 缺少Python库：{missing_libs}")
        print("请安装完整Python环境")
        return False

    print("✅ 所有依赖检查通过")
    return True

def check_pandoc_installed():
    """检查pandoc是否已安装"""
    try:
        subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_pandoc():
    """安装pandoc"""
    system = platform.system().lower()

    try:
        if system == "linux":
            # 尝试不同的包管理器
            package_managers = [
                ("apt-get", ["sudo", "apt-get", "install", "-y", "pandoc"]),
                ("yum", ["sudo", "yum", "install", "-y", "pandoc"]),
                ("dnf", ["sudo", "dnf", "install", "-y", "pandoc"]),
                ("zypper", ["sudo", "zypper", "install", "-y", "pandoc"]),
                ("pacman", ["sudo", "pacman", "-Sy", "--noconfirm", "pandoc"]),
            ]

            for pm_name, cmd in package_managers:
                try:
                    # 检查包管理器是否存在
                    subprocess.run(["which", pm_name], capture_output=True, check=True)
                    print(f"使用 {pm_name} 安装 pandoc...")

                    # 如果是apt-get，先更新
                    if pm_name == "apt-get":
                        subprocess.run(["sudo", "apt-get", "update"], capture_output=True, check=False)

                    subprocess.run(cmd, check=True)
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

        elif system == "darwin":  # macOS
            try:
                subprocess.run(["brew", "--version"], capture_output=True, check=True)
                subprocess.run(["brew", "install", "pandoc"], check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        # 通用方法：使用pip安装pypandoc
        print("尝试使用pip安装pypandoc...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pypandoc"], check=True)
        return True

    except subprocess.CalledProcessError as e:
        print(f"安装失败：{e}")
        return False

def convert_docm_to_docx(docm_path: Path) -> Path:
    """
    将.docm转换为.docx
    注意：在Linux上会丢失宏功能
    """
    docm_path = docm_path.resolve()
    docx_path = docm_path.with_suffix(".docx")

    print(f"📄 转换 .docm -> .docx: {docm_path.name}")

    try:
        # 验证是否为有效的ZIP文件
        with zipfile.ZipFile(docm_path, 'r') as test_zip:
            # 检查是否包含Word文档的基本文件
            file_list = test_zip.namelist()
            if not any(f.endswith('.xml') or 'word/' in f.lower() for f in file_list):
                print("⚠️  警告：文件可能不是有效的Word文档")

        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix="word2md_")

        try:
            # 解压
            with zipfile.ZipFile(docm_path, 'r') as docm_zip:
                docm_zip.extractall(temp_dir)

            # 重新打包为.docx
            with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        docx_zip.write(file_path, arcname)

            print(f"✅ .docx 文件已创建: {docx_path.name}")
            return docx_path

        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)

    except zipfile.BadZipFile:
        print(f"❌ 错误：{docm_path.name} 不是有效的ZIP文件")
        raise ValueError(f"文件 {docm_path.name} 不是有效的.docm文件")
    except Exception as e:
        print(f"❌ 转换失败：{e}")
        raise

def run_pandoc_conversion(input_file: Path, output_file: Path, format_type: str = "gfm"):
    """运行pandoc进行转换"""
    print(f"🔄 使用pandoc转换: {input_file.name} -> {output_file.name}")

    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 构建命令
    cmd = [
        "pandoc",
        str(input_file),
        "-t", format_type,  # 输出格式
        "--wrap=none",      # 不自动换行
        "-o", str(output_file),
    ]

    print(f"   命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            # 验证输出文件
            if output_file.exists() and output_file.stat().st_size > 0:
                size = output_file.stat().st_size
                print(f"✅ 转换成功! 文件大小: {size:,} 字节 ({size/1024:.1f} KB)")
                return True
            else:
                print("❌ 转换失败: 输出文件为空或不存在")
                return False
        else:
            print(f"❌ pandoc 错误 (代码 {result.returncode}):")
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    print(f"   {line}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ 转换超时 (60秒)")
        return False
    except Exception as e:
        print(f"❌ 转换异常: {e}")
        return False

def convert_single_file(input_path: Path, output_path: Path | None, format_type: str = "markdown"):
    """转换单个文件"""
    input_path = input_path.resolve()

    if not input_path.is_file():
        raise FileNotFoundError(f"文件不存在: {input_path}")

    # 确定输出路径
    if output_path is None:
        output_path = input_path.with_suffix(".md")
    else:
        output_path = Path(output_path).resolve()

    print(f"\n开始转换: {input_path.name}")
    print(f"输入: {input_path}")
    print(f"输出: {output_path}")
    print(f"格式: {format_type}")

    ext = input_path.suffix.lower()
    temp_files = []

    try:
        # 处理.docm文件
        if ext == ".docm":
            temp_docx = convert_docm_to_docx(input_path)
            if temp_docx:
                temp_files.append(temp_docx)
                input_file = temp_docx
            else:
                raise ValueError("无法转换.docm文件")
        elif ext == ".docx":
            input_file = input_path
        else:
            raise ValueError(f"不支持的文件类型: {ext} (只支持 .docx 和 .docm)")

        # 运行pandoc转换
        success = run_pandoc_conversion(input_file, output_path, format_type)

        if success:
            # 显示文件预览
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    preview = f.read(300)
                print(f"\n📋 内容预览 (前300字符):")
                print("-" * 40)
                print(preview + ("..." if len(preview) >= 300 else ""))
                print("-" * 40)
            except Exception as e:
                print(f"⚠️  无法预览文件: {e}")

        return success

    finally:
        # 清理临时文件
        for temp_file in temp_files:
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                    print(f"🧹 已清理临时文件: {temp_file.name}")
                except Exception as e:
                    print(f"⚠️  清理临时文件失败 {temp_file.name}: {e}")

def convert_directory(input_dir: Path, output_dir: Path | None, format_type: str = "markdown", recursive: bool = False):
    """转换目录下的所有文件"""
    input_dir = input_dir.resolve()

    if not input_dir.is_dir():
        raise NotADirectoryError(f"目录不存在: {input_dir}")

    # 确定输出目录
    if output_dir is None:
        output_dir = input_dir / "markdown_output"
    else:
        output_dir = Path(output_dir).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 批量转换目录")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"递归搜索: {'是' if recursive else '否'}")

    # 收集文件
    patterns = ["*.docx", "*.docm"]
    files_to_convert = []

    for pattern in patterns:
        if recursive:
            files_to_convert.extend(input_dir.rglob(pattern))
        else:
            files_to_convert.extend(input_dir.glob(pattern))

    if not files_to_convert:
        print("⚠️  未找到 .docx 或 .docm 文件")
        return

    print(f"找到 {len(files_to_convert)} 个文件需要转换")

    success_count = 0
    fail_count = 0
    failed_files = []

    for i, input_file in enumerate(files_to_convert, 1):
        print(f"\n[{i}/{len(files_to_convert)}] 处理: {input_file.name}")

        try:
            # 计算输出路径
            if input_dir == input_file.parent:
                relative_path = input_file.name
            else:
                relative_path = input_file.relative_to(input_dir)

            output_file = output_dir / relative_path.with_suffix(".md")
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # 转换文件
            if convert_single_file(input_file, output_file, format_type):
                success_count += 1
            else:
                fail_count += 1
                failed_files.append(str(input_file))

        except Exception as e:
            print(f"❌ 处理失败: {e}")
            fail_count += 1
            failed_files.append(str(input_file))

    # 显示统计信息
    print(f"\n{'='*60}")
    print("转换完成!")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print(f"📁 输出目录: {output_dir}")

    if failed_files:
        print("\n失败的文件:")
        for f in failed_files:
            print(f"  - {f}")

def main():
    """主函数"""
    print_header()

    parser = argparse.ArgumentParser(
        description="将Word文档(.docx/.docm)转换为Markdown格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s document.docx                   # 转换单个文件
  %(prog)s document.docx -o output.md      # 指定输出文件
  %(prog)s ./docs -r                       # 递归转换目录
  %(prog)s ./docs -o ./markdown -F markdown     # 指定输出目录和格式
        """
    )

    parser.add_argument(
        "input",
        help="输入文件或目录路径"
    )

    parser.add_argument(
        "-o", "--output",
        help="输出文件或目录路径（默认：同目录同名.md 或 markdown_output 目录）",
        default=None
    )

    parser.add_argument(
        "-F", "--format",
        help="Markdown格式（默认：markdown，可选：gfm, commonmark, markdown_strict等）",
        default="markdown",
        choices=["gfm","markdown","markdown_github", "markdown_mmd", "markdown_phpextra", "markdown_strict"]       
    )

    parser.add_argument(
        "-r", "--recursive",
        help="递归处理目录下的所有文件",
        action="store_true"
    )

    parser.add_argument(
        "--no-deps-check",
        help="跳过依赖检查",
        action="store_true"
    )

    parser.add_argument(
        "-v", "--version",
        help="显示版本信息",
        action="version",
        version=f"word2md v{VERSION}"
    )

    args = parser.parse_args()

    # 检查依赖
    if not args.no_deps_check:
        if not check_dependencies():
            print("\n❌ 依赖检查失败，请先安装所需软件")
            sys.exit(1)

    input_path = Path(args.input)

    try:
        if input_path.is_dir():
            # 目录模式
            convert_directory(input_path, args.output, args.format, args.recursive)
        else:
            # 文件模式
            success = convert_single_file(input_path, args.output, args.format)
            if not success:
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)

    print("\n✨ 所有操作完成!")

if __name__ == "__main__":
    main()