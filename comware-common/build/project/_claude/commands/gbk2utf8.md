---
description: 将指定目录下的.c/.h文件从GBK编码转换为UTF-8编码
argument-hint: [directory_path] [--options]
allowed-tools: Bash(abuild:*), Bash(python:*), Bash(python3:*), Read, Write, Edit, Glob, Grep
---

# GBK 转 UTF-8 编码转换命令

## 功能说明

此命令用于将指定目录下的.c和.h文件从GBK（或GB2312、GB18030）编码转换为UTF-8编码。基于.tools/charset_converter/convert_to_utf8.py脚本。

## 用法

```
/gbk2utf8 <目录路径> [选项]
```

## 参数

- `directory_path`：要处理的目录路径（必选）
- `--options`：可选参数，支持：
  - `--dry-run`：只显示要转换的文件，不实际转换
  - `--backup`：创建备份文件（默认不创建备份）
  - `--log-file <文件路径>`：指定转换日志文件路径

## 示例

1. 转换当前目录下的文件：
   ```
   /gbk2utf8 .
   ```

2. 转换指定目录下的文件：
   ```
   /gbk2utf8 src
   ```

3. 只显示要转换的文件（不实际转换）：
   ```
   /gbk2utf8 . --dry-run
   ```

4. 转换时创建备份文件：
   ```
   /gbk2utf8 src --backup
   ```

5. 转换根目录下的文件（整个项目）：
   ```
   /gbk2utf8 .
   ```

## 脚本引用

基于.tools/charset_converter/convert_to_utf8.py脚本。

## 执行前确认

在执行转换前，请确保：
1. 如需备份重要文件，请使用--backup选项
2. 检查转换日志文件的内容
3. 转换后可能需要进行abuild编译测试以确保代码正常工作

## 注意事项

1. 此命令只处理.c和.h文件
2. 排除.svn目录
3. 默认不创建备份文件（如需备份请使用--backup选项）
4. 转换UTF-8编码的文件会自动跳过
5. 转换后建议运行abuild编译测试

## 执行步骤

1. 检测当前工作目录或指定目录下的.c/.h文件
2. 检测每个文件的编码类型
3. 对于GBK/GB2312/GB18030编码的文件，转换为UTF-8
4. 记录转换日志
5. 提供转换结果统计

## 转换完成后的建议

转换完成后，建议：
1. 运行abuild编译测试检查是否有语法错误
2. 检查转换日志文件
3. 如需备份，请使用--backup选项创建备份文件