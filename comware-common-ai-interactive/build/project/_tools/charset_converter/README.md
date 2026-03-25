# 文件编码转换脚本

## 概述

这两个Python脚本用于转换project目录下除了.svn目录的.c和.h文件的编码：

1. `convert_to_utf8.py` - 将GB编码文件转换为UTF-8编码，并记录转换清单
2. `convert_to_gb.py` - 使用转换清单将UTF-8编码的文件转换回GB编码，跳过原始UTF-8文件

## 特性

- **智能转换清单**：记录哪些文件被实际转换，避免修改原始UTF-8文件
- **自动排除.svn目录**
- **支持创建备份文件**
- **支持dry-run模式**（只显示要转换的文件，不实际转换）
- **自动检测文件编码**
- **递归处理所有子目录**
- **相对路径存储**：转换清单使用相对路径，便于项目迁移

## 使用方法

### 1. 转换为UTF-8编码

```bash
# 基本用法（会自动创建备份文件，并生成转换清单）
python3 convert_to_utf8.py /path/to/project

# 指定转换清单文件路径
python3 convert_to_utf8.py /path/to/project --log-file custom_log.txt

# 不创建备份文件
python3 convert_to_utf8.py /path/to/project --no-backup

# 只查看要处理的文件，不实际转换
python3 convert_to_utf8.py /path/to/project --dry-run
```

### 2. 转换为GB编码

```bash
# 基本用法（使用转换清单跳过原始UTF-8文件）
python3 convert_to_gb.py /path/to/project

# 指定转换清单文件路径
python3 convert_to_gb.py /path/to/project --conversion-log custom_log.txt

# 禁用跳过原始UTF-8文件功能（转换所有UTF-8文件）
python3 convert_to_gb.py /path/to/project --no-skip-original-utf8

# 强制转换所有文件（包括非UTF-8编码的文件）
python3 convert_to_gb.py /path/to/project --force

# 不创建备份文件
python3 convert_to_gb.py /path/to/project --no-backup

# 只查看要处理的文件，不实际转换
python3 convert_to_gb.py /path/to/project --dry-run
```

## 编码检测

脚本会尝试以下编码来检测文件：
- utf-8
- gb2312
- gbk
- gb18030
- mac_roman (Mac Roman编码)
- big5
- latin1
- iso-8859-1

## 转换清单工作原理

为了避免修改原始UTF-8文件，脚本实现了智能的转换清单功能：

### 1. 从GB到UTF-8转换时：
- **只转换GB编码文件**：跳过已经是UTF-8的文件
- **跳过Mac Roman文件**：Mac Roman编码的文件也像原始UTF-8文件一样被跳过
- **生成转换清单**：记录哪些文件被**实际转换**了（GB编码转UTF-8的文件）
- **相对路径存储**：清单使用相对于项目根目录的路径

### 2. 从UTF-8到GB转换时：
- **默认使用清单**：只转换在清单中记录的文件
- **跳过原始UTF-8**：如果文件是UTF-8编码但不在清单中，说明它本来就是UTF-8，跳过不转换
- **跳过Mac Roman文件**：Mac Roman编码的文件也会被跳过（不会被转换）
- **可禁用此功能**：使用`--no-skip-original-utf8`参数可以禁用此功能，转换所有UTF-8文件
- **注意**：即使使用`--force`参数，Mac Roman文件也不会被转换，因为它们不是UTF-8编码

## 注意事项

1. **备份文件**：默认情况下，脚本会创建备份文件（`.bak` 或 `.backup` 后缀）
2. **.svn目录**：脚本会自动排除所有.svn目录
3. **文件类型**：只处理.c和.h文件
4. **Mac Roman支持**：
   - 脚本会自动检测Mac Roman编码的文件
   - Mac Roman文件会像原始UTF-8文件一样被跳过，不会被转换
   - 这确保Mac Roman文件的内容不会被破坏
5. **转换顺序**：
   - **第一步**：先使用`convert_to_utf8.py`转换项目，生成转换清单
   - **第二步**：使用`convert_to_gb.py`转换回GB编码，自动跳过原始UTF-8文件和Mac Roman文件
   - 如果项目移动了位置，需要确保转换清单文件也在同一目录下
6. **字符丢失**：由于编码转换可能无法完全映射所有字符，部分字符可能会丢失（使用errors='ignore'参数）

## 脚本位置

- `~/project/.tools/charset_converter/convert_to_utf8.py`
- `~/project/.tools/charset_converter/convert_to_gb.py`

## 测试

可以使用测试目录验证脚本功能：
```bash
# 创建测试目录
mkdir -p ~/project/.tools/charset_converter/test_encoding_project

# 测试dry-run模式
python3 convert_to_utf8.py ~/project/.tools/charset_converter/test_encoding_project --dry-run
python3 convert_to_gb.py ~/project/.tools/charset_converter/test_encoding_project --dry-run

# 完整测试转换清单功能
python3 convert_to_utf8.py ~/project/.tools/charset_converter/test_encoding_project
python3 convert_to_gb.py ~/project/.tools/charset_converter/test_encoding_project --dry-run  # 查看哪些文件会被转换
```