---
name: netconf-test-script-generation-material-preparation
description: 全栈 NETCONF/YANG 处理工作流。负责将 YANG 文件转换为 YIN/DSDL，解析 Word 需求文档提取 XPath，并基于文档分析结果自动生成测试文件夹结构。适用于 NETCONF 协议开发和测试场景。
allowed-tools: Bash, Read, Glob, Write
---

# NETCONF测试脚本生成工具

此 Skill 封装了一套用于处理 NETCONF 协议、YANG 模型和测试生成的 Python 工具链，请你按照工作流程逐步执行以下工具。

## 路径说明

**重要提示**：请区分以下两个不同的路径概念：
- **当前工作目录**：用户执行命令时所在的目录，yang 文件和 docx 文件应位于此目录
- **当前 SKILL 路径**：本 SKILL 定义文件所在的目录，即 `c:\Users\m31660\.claude\skills\netconf-test-script-generation-material-preparation\`

### 脚本位置
所有 Python 脚本均位于：`{当前SKILL路径}/scripts/`

### 默认路径配置
- **输入文件**：yang 文件和 docx 文件位于：**当前工作目录**
- **模板文件**：位于 `{当前SKILL路径}/templates/generate_prompt/`
- **pyang 工具**：内置在 `{当前SKILL路径}/scripts/pyang.exe`



## 标准工作流程 (Workflow)
### 材料准备阶段

**准备阶段**
- **Step 0: 环境检查**
  - 运行 `ls -F` 或 `dir` 查看当前工作目录内容
  - 确认 yang 文件和 docx 文件在**当前工作目录**
  - 确认 `{当前SKILL路径}/scripts/` 目录中存在所需的 Python 脚本

**执行阶段**
- [ ] **Step 1: 转换 YANG 文件**
  - 移动所有yang在当前工作目录下的同一文件夹里面。
  - 进入脚本目录：`cd "{当前SKILL路径}/scripts"`
  - 命令: `python yang_converter.py --all "<YANG_DIR>"`
    - `<YANG_DIR>` 是 yang 文件所在目录的**绝对路径**
  - *目标*: 获取生成的 YIN 文件目录路径 (记为 `$YIN_DIR`)

- [ ] **Step 2: 处理需求文档**
  - 确保在脚本目录：`cd "{当前SKILL路径}/scripts"`
  - 命令: `python netconf_doc_processor.py "<DOCX_FILE>"`
    - `<DOCX_FILE>` 是 docx 文件的**绝对路径**
  - *目标*: 获取生成的文档分析目录路径 (通常是 `converted_docs`，记为 `$DOC_DIR`)

- [ ] **Step 3: 生成测试结构**
  - 确保在脚本目录：`cd "{当前SKILL路径}/scripts"`
  - 命令: `python xpath_test_generator.py -y "$YIN_DIR" -d "$DOC_DIR" -t "{当前SKILL路径}/templates/generate_prompt/" -o "<OUTPUT_DIR>"`
  - *注意*:
    - 这里的 `-y` 和 `-d` 必须使用前两步实际生成的目录路径
    - `-t` 是模板目录，指向 SKILL 内的 generate_prompt 目录
    - `-o` 是输出目录，可以在**当前工作目录**下指定
    - 如果不需要复制模板文件，可以省略 `-t` 参数






## 核心工具 (Tools)

### 1. YANG 转换器 (`yang_converter.py`)
用于格式转换。
*   **用途**: 将 `.yang` 文件转换为 `.yin` 和/或 DSDL 格式
*   **常用命令**:
    *   `python yang_converter.py --all <yang_dir>` (转换为所有格式)
    *   `python yang_converter.py --yin <yang_dir>` (仅 YIN)
    *   `python yang_converter.py --dsdl <yang_dir>` (仅 DSDL)
*   **输出目录规则**:
    *   `--all` 或 `--yin --dsdl`: `{目录名}_converted/`
    *   仅 `--yin`: `{目录名}_to_yin/`
    *   仅 `--dsdl`: `{目录名}_to_dsdl/`
*   **注意事项**：
    *   使用内置的 pyang.exe 转换 yang 文件
    *   假如用户不提供依赖文件，控制台可能会打印缺少依赖信息，假如生成文件夹中有 yin 文件，则无需理会


### 2. 文档处理器 (`netconf_doc_processor.py`)
用于文档分析。
*   **用途**: 将 Word (.docx) 转换为 Markdown 并提取 NETCONF XPath 和操作信息。
*   **常用命令**:
    *   `python netconf_doc_processor.py <file.docx>`
    *   `python netconf_doc_processor.py *.docx` (批量处理)
*   **输出**: 默认在文档同级目录下生成 `converted_docs` 文件夹，内含 `.new.json`和 `.revision.json`分析文件。

### 3. XPath 测试生成器 (`xpath_test_generator.py`)
用于生成测试框架。
*   **用途**: 结合 YIN 文件和文档分析结果 (.new.json)，生成对应的测试文件夹结构。
*   **必需参数**:
    *   `-y <dir>`: YIN 文件目录 (通常是 `yang_converter.py` 的输出)
*   **可选参数**:
    *   `-d <dir>`: 文档分析结果目录 (通常是 `converted_docs`)
    *   `-o <dir>`: 目标输出目录
    *   `-t <dir>`: 模板文件目录，使用 `{当前SKILL路径}/templates/generate_prompt/`



## 示例 (Examples)

**场景：全流程生成测试**

> User: "我有 `D:\work\yang\v1` 下的模型文件和 `D:\work\docs\Spec.docx` 文档，当前工作目录是 `D:\work`"
> SKILL 路径: `c:\Users\m31660\.claude\skills\netconf-test-script-generation-material-preparation\`

Claude 应执行：
1. 进入脚本目录并转换 YANG 文件：
   ```bash
   cd "c:\Users\m31660\.claude\skills\netconf-test-script-generation-material-preparation\scripts"
   python yang_converter.py --all "D:\work\yang\v1"
   ```
   - 输出目录: `D:\work\yang\v1_converted\` (包含 .yin 文件)
   - 记录: `$YIN_DIR` = `D:\work\yang\v1_converted\`

2. 处理 Word 文档：
   ```bash
   python netconf_doc_processor.py "D:\work\docs\Spec.docx"
   ```
   - 输出目录: `D:\work\docs\converted_docs\` (在 Spec.docx 同级目录)
   - 记录: `$DOC_DIR` = `D:\work\docs\converted_docs\`

3. 生成测试结构：
   ```bash
   python xpath_test_generator.py -y "D:\work\yang\v1_converted" -d "D:\work\docs\converted_docs" -t "c:\Users\m31660\.claude\skills\netconf-test-script-generation-material-preparation\templates\generate_prompt/" -o "D:\work\test_output"
   ```

**关键点**：
- 所有 Python 脚本都在 SKILL 的 scripts 目录中执行
- yang/docx 文件路径使用绝对路径（在用户工作目录中）
- 模板路径指向 SKILL 内部路径
- 输出路径可以在用户工作目录中指定

**错误处理**:
- 如果某步骤失败，检查错误信息并告知用户
- 如果缺少依赖，提示用户安装相应的 Python 包

## 环境依赖

### Python 包依赖
在使用本 Skill 之前，需要确保安装以下 Python 包：
- `pypandoc` - Word 文档转换
- `python-docx` - Word 文档处理
- `beautifulsoup4` - HTML/XML 解析
- `markdown` - Markdown 处理
- `lxml` - XML 处理和美化

安装命令：
```bash
pip install pypandoc python-docx beautifulsoup4 markdown lxml
```
## 注意事项

1. **路径区分**（重要）:
   - **当前工作目录**：用户的工作目录，存放 yang/docx 文件
   - **SKILL 路径**：SKILL 定义目录，存放 Python 脚本和模板
   - 执行脚本时需要先 `cd` 到 SKILL 的 scripts 目录
   - 输入/输出路径建议使用绝对路径

2. **路径处理**:
   - Windows 路径包含空格时需要用引号括起来
   - 建议使用绝对路径避免路径混乱
   - 反斜杠路径在命令行中需要转义或使用正斜杠

3. **输出目录管理**:
   - yang_converter.py 的输出目录会自动生成，根据转换类型命名
   - netconf_doc_processor.py 的输出默认在文档同级的 `converted_docs` 目录
   - 建议每步执行后检查输出目录是否正确生成

4. **模板文件**:
   - 模板文件位于 `{当前SKILL路径}/templates/generate_prompt/` 目录
   - 包含: `test_netconf.py`, `conftest.py`, `Checklist.json` 等
   - 如果不需要复制模板，可以省略 `-t` 参数

5. **错误排查**:
   - pyang 警告信息可以忽略（只要有 .yin 文件生成）
   - 如果 pypandoc 报错，检查 pandoc 是否正确安装
   - 文档处理失败时，检查 .docx 文件格式是否正确
   - 如果提示找不到脚本，确认是否 `cd` 到了正确的 scripts 目录
