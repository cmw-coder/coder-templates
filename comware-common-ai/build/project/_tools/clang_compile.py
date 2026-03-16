import os
import json
from pathlib import Path

def generate_compile_commands():
    # 1. 自动获取 /home/{用户} 并拼接 project，作为绝对根目录
    # 这样写的好处是：不管你在哪个目录下执行脚本，都不会找错地方！
    project_root = Path.home() / "project"
    
    # 2. 精准定位 platform 和 public 目录
    platform_root = project_root / "platform"
    public_root = project_root / "public" / "PUBLIC" / "include"
    
    # 增加健壮性检查
    if not project_root.exists():
        print(f"❌ 错误: 找不到项目根目录 '{project_root}'")
        return
    if not platform_root.exists() or not platform_root.is_dir():
        print(f"❌ 错误: 找不到目标代码目录 '{platform_root}'")
        return

    # 定义需要被 clangd 识别的源文件
    source_exts = {'.c', '.cpp', '.cc', '.cxx'}
    source_files =[]

    print(f"🚀 开始执行: 目标项目 -> {project_root}")
    print(f"🔍 正在定向扫描目录: {platform_root} ...")
    
    # 3. 只对 platform_root 进行递归扫描，完美避开其他无关目录
    for filepath in platform_root.rglob('*'):
        if filepath.is_file() and filepath.suffix.lower() in source_exts:
            source_files.append(filepath)

    # 4. 基础编译参数设置
    base_flags =[
        "-std=gnu11",  # Comware 通常用 C 语言，可能有 gnu 扩展
        "-Wall",
        "-D__linux__", 
    ]

    # 5. 指定头文件包含目录
    include_flags =[]
    
    # 挂载 PUBLIC 外部公共库
    if public_root.exists():
        include_flags.append(f"-isystem{public_root}")
        comware_dir = public_root / "comware"
        if comware_dir.exists():
            include_flags.append(f"-isystem{comware_dir}")
        print(f"✅ 成功关联外部 PUBLIC 库: {public_root}")
    else:
        print(f"⚠️ 警告: 找不到 PUBLIC 目录，期望路径为 {public_root}")

    # 自动提取 platform 下所有的内部头文件目录
    internal_include_dirs = set()
    for filepath in platform_root.rglob('*.h'):
        internal_include_dirs.add(filepath.parent)
    
    for inc in internal_include_dirs:
         include_flags.append(f"-I{inc}")

    # 6. 生成 JSON 结构
    compile_commands =[]
    
    for src in source_files:
        compiler = "clang++" if src.suffix.lower() in {".cpp", ".cc", ".cxx"} else "clang"
        
        # 组装完整的编译参数
        arguments =[compiler] + base_flags + include_flags + ["-c", str(src)]
        
        entry = {
            "directory": str(project_root),  # 编译器的工作目录设为绝对路径的 project 根目录
            "arguments": arguments,
            "file": str(src)                 # 源文件的绝对路径
        }
        compile_commands.append(entry)

    # 7. 强制将 json 文件写入到 /home/{用户}/project/ 目录下
    output_file = project_root / "compile_commands.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(compile_commands, f, indent=4, ensure_ascii=False)
        
    print("-" * 50)
    print(f"🎉 成功生成编译数据库: {output_file}")
    print(f"📄 共处理 {len(source_files)} 个源文件")
    print("💡 提示: 用 VSCode/IDE 打开 project 文件夹，并重启 Clangd 服务即可生效。")

if __name__ == "__main__":
    generate_compile_commands()