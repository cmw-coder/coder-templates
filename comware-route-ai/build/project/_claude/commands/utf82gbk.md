---
description: 将指定目录下的.c/.h文件从UTF-8编码转换为GBK/GB18030编码
argument-hint: [directory_path] [--options]
allowed-tools: Bash(abuild:*), Bash(python:*), Bash(python3:*), Read, Write, Edit, Glob, Grep
---

# UTF-8 转 GBK/GB18030 编码转换命令

## 功能说明

此命令用于将指定目录下的.c和.h文件从UTF-8编码转换为GB18030编码（兼容GBK、GB2312）。基于.tools/charset_converter/convert_to_gb.py脚本。

## 用法

```
/utf82gbk <目录路径> [选项]
```

## 参数

- `directory_path`：要处理的目录路径（必选）
- `--options`：可选参数，支持：
  - `--dry-run`：只显示要转换的文件，不实际转换
  - `--backup`：创建备份文件（默认不创建备份）
  - `--force`：强制转换非UTF-8编码的文件
  - `--encoding <编码类型>`：目标编码（gb2312、gbk或gb18030，默认gb18030）
  - `--conversion-log <文件路径>`：UTF-8转换日志文件路径（用于跳过原始UTF-8文件）
  - `--workers <数量>`：并发工作线程数（默认64）
  - `--verbose`：显示详细输出（默认静默模式，仅显示进度和汇总）

## 示例

1. 转换当前目录下的文件：
   ```
   /utf82gbk .
   ```

2. 转换指定目录下的文件：
   ```
   /utf82gbk src
   ```

3. 只显示要转换的文件（不实际转换）：
   ```
   /utf82gbk . --dry-run
   ```

4. 强制转换所有文件（包括非UTF-8文件）：
   ```
   /utf82gbk src --force
   ```

5. 指定GBK编码（而不是默认的GB18030）：
   ```
   /utf82gbk src --encoding gbk
   ```

6. 转换时创建备份文件：
   ```
   /utf82gbk src --backup
   ```

7. 转换根目录下的文件（整个项目）：
   ```
   /utf82gbk .
   ```

8. 查看详细的转换日志：
   ```
   /utf82gbk src --verbose
   ```

9. 指定并发线程数：
   ```
   /utf82gbk src --workers 32
   ```

## 脚本引用

基于.tools/charset_converter/convert_to_gb.py脚本。

## 执行前确认

在执行转换前，请确保：
1. 如需备份重要文件，请使用--backup选项
2. 如果有之前的UTF-8转换日志文件，可以指定以跳过原始UTF-8文件
3. 转换后可能需要进行abuild编译测试以确保代码正常工作

## 注意事项

1. 此命令只处理.c和.h文件
2. 排除.svn目录
3. 默认会跳过原始就是UTF-8编码的文件（如果指定了转换日志）
4. 默认不创建备份文件（如需备份请使用--backup选项）
5. 转换后建议运行abuild编译测试
6. 使用多线程并发处理，默认64线程，可通过--workers调整
7. 默认静默模式，如需查看逐文件详情请使用--verbose
8. SVN checkout 时会自动执行 UTF-8 转换，日志文件保存在 `/tmp/charset_converter/` 目录下：
   - `platform_utf8_conversion.log`（platform 代码）
   - `public_utf8_conversion.log`（public 代码）

## 特殊功能

1. **跳过原始UTF-8文件**：默认情况下，如果提供了转换日志文件（utf8_conversion.log），会跳过原始就是UTF-8编码的文件，只转换从GBK转过来的UTF-8文件
2. **字符丢失检查**：转换时会检查是否有字符无法编码到GB18030，并给出警告
3. **多种编码支持**：支持gb2312、gbk、gb18030三种目标编码

## 与自动转换的配合

SVN checkout 完成后会自动将代码转换为 UTF-8，转换日志保存在 `/tmp/charset_converter/` 下。
在执行 abuild 前需要转回 GBK 时，请指定对应的转换日志：

```
/utf82gbk platform --conversion-log /tmp/charset_converter/platform_utf8_conversion.log
/utf82gbk public --conversion-log /tmp/charset_converter/public_utf8_conversion.log
```

## 执行步骤

1. 检测当前工作目录或指定目录下的.c/.h文件
2. 检测每个文件的编码类型
3. 对于UTF-8编码的文件，转换为GB18030（或其他指定编码）
4. 记录转换统计信息
5. 提供转换结果统计

## 转换完成后的建议

转换完成后，建议：
1. 运行abuild编译测试检查是否有语法错误
2. 检查转换结果，特别是字符丢失警告
3. 如需备份恢复，请使用--backup选项创建备份文件
4. 对于从UTF-8转换回GBK的文件，建议检查中文字符是否正确显示