# NETCONF XML 工具集

这是一个完整的NETCONF XML处理和分析工具集，包含了从YANG文件转换到测试代码生成的全套工具。支持YIN、DSDL两种格式转换，专注于基于文档分析的XPath测试生成。

## 工具概览

### 1. YANG文件处理工具

#### 1.1 yang_converter.py - YANG文件转换器（YIN+DSDL版）
- **功能**: 将YANG文件转换为YIN和/或DSDL格式文件（支持同时转换两种格式）
- **数据来源**: 指定目录下的YANG文件
- **支持的版本**: 任意版本的YANG文件
- **主要特性**:
  - 递归搜索指定目录下的所有.yang文件
  - 支持转换为YIN、DSDL格式，可单独或组合转换
  - 使用pyang工具进行格式转换
  - 支持命令行参数，灵活指定输入和输出路径
  - 自动处理模块导入路径和依赖关系
  - 智能默认输出目录生成
  - 自动识别配置和数据类型，生成对应的YIN结构
  - 生成JSON格式的结构分析报告
  - 使用lxml进行DSDL XML的美化输出
  - 支持依赖目录指定（用于DSDL转换）

**使用方法**:
```bash
# 查看帮助信息
python yang_converter.py -h

# 只转换为YIN格式
python yang_converter.py --yin "D:\yang\V9"

# 只转换为DSDL格式
python yang_converter.py --dsdl "D:\yang\V9"

# 同时转换为YIN和DSDL格式（默认）
python yang_converter.py --yin --dsdl "D:\yang\V9"
python yang_converter.py -yd "D:\yang\V9"
python yang_converter.py "D:\yang\V9"

# 转换为所有格式（YIN、DSDL）
python yang_converter.py --all "D:\yang\V9"

# 指定输出目录和依赖目录（用于DSDL转换）
python yang_converter.py --dsdl "D:\yang\V9" -o "D:\output\custom_folder" -p "D:\yang\dependencies"
```

**参数说明**:
- `yang_dir`: YANG文件夹路径（必填）
- `-o, --output`: 输出文件夹路径（可选）
- `-p, --path`: YANG依赖文件目录（可选，用于DSDL转换）
- `--yin`: 仅转换为YIN格式
- `--dsdl`: 仅转换为DSDL格式
- `-yd, --yin-dsdl`: 同时转换为YIN和DSDL格式（默认行为）
- `--all`: 转换为所有格式（YIN、DSDL）

**默认输出规则**:
- 同时转换YIN+DSDL: `{目录名}_converted` 文件夹
- 仅转换YIN: `{目录名}_to_yin` 文件夹
- 仅转换DSDL: `{目录名}_to_dsdl` 文件夹
- 转换所有格式: `{目录名}_converted` 文件夹

**输出文件**:
- **YIN文件**: 对应每个YANG文件生成同名的.yin文件
- **DSDL XML文件**: 对应每个YANG文件生成同名的_dsdl.xml文件（美化输出）
- **结构分析报告**: `{目录名}_yin.json`，包含模块、表格和子表格信息

### 2. 文档处理工具

#### 2.1 netconf_doc_processor.py - NETCONF文档处理器
- **功能**: 将Word文档转换为Markdown并分析NETCONF相关章节信息（合并工具）
- **数据来源**: 指定的DOCX文件路径（支持单个或多个文件）
- **依赖工具**: pypandoc (需要安装pandoc), python-docx, beautifulsoup4, markdown, word_revision_extractor
- **主要特性**:
  - 批量处理多个DOCX文件
  - 自动转换Word文档为Markdown格式
  - 智能提取包含'/'的二级章节
  - 解析NETCONF XPATH和Supported operations信息
  - 生成详细的分析统计报告
  - 统一的输出文件夹管理，支持自定义输出路径
  - 输出文件自动保存在与DOCX文件同目录的指定文件夹中
  - 可选的Word修订内容提取功能（需要word_revision_extractor模块）

**使用方法**:
```bash
# 查看帮助信息
python netconf_doc_processor.py -h

# 处理单个DOCX文件（使用默认输出文件夹 converted_docs，会提取修订内容）
python netconf_doc_processor.py document.docx

# 指定输出文件夹
python netconf_doc_processor.py -o my_output document.docx

# 处理多个DOCX文件
python netconf_doc_processor.py file1.docx file2.docx file3.docx

# 使用通配符处理多个文件（在支持的shell中）
python netconf_doc_processor.py *.docx

# 指定输出文件夹并处理多个文件
python netconf_doc_processor.py -o results *.docx

# 处理文件但不提取修订内容（提高处理速度）
python netconf_doc_processor.py --no-revisions document.docx

# 批量处理多个文件但不提取修订内容
python netconf_doc_processor.py --no-revisions -o results *.docx
```

**参数说明**:
- `docx_files`: DOCX文件路径列表（必填，支持多个文件）
- `-o, --output-dir`: 输出文件夹名称（可选，默认为 converted_docs）
- `--no-revisions`: 不提取修订内容（默认会提取修订内容，需要word_revision_extractor模块）

**输出文件**:
- **Markdown文件**: `{原文件名}.md`，保存在与DOCX文件同目录的输出文件夹中
- **分析结果**: `{原文件名}.new.json`，包含章节分析和XPath信息，保存在相同输出文件夹中
- **修订记录**: `{原文件名}.revisions.json`，Word文档修订内容（仅当未使用--no-revisions参数且模块可用时）

**输出路径规则**:
- 默认输出文件夹: `converted_docs`
- 输出路径: 与DOCX文件相同的目录下创建输出文件夹
- 例如: DOCX文件 `D:\documents\sample.docx` → 输出到 `D:\documents\converted_docs\`

### 3. XML分析工具

#### 3.1 xml_parse.py - XML解析器
- **功能**: 把xpath按/分割，根据分割后的tag数组在xml字符串中匹配xpath内容
- **核心方法**: `extract_xml_by_tags(xml_string, tags)`
- **应用场景**: 为其他工具提供XML内容提取功能

#### 3.2 extract_rpc.py - RPC XML内容提取器
- **功能**: 从py或tcl脚本中提取出xml字符串
- **核心方法**: `extract_rpc_xml_content(content)`
- **支持的文件格式**: Python (.py), Tcl (.tcl)

### 4. 测试文件夹生成工具

#### 4.1 xpath_test_generator.py - NETCONF XPath测试生成器（重命名和参数化）
- **功能**: 根据文档分析结果(.new.json文件)中的XPath，生成对应的测试文件夹结构
- **主要特性**:
  - 从文档分析结果中提取真实的XPath路径
  - 为每个XPath生成独立的测试文件夹
  - 提取对应的YIN子模块定义
  - 自动匹配文档内容（精确匹配或最长前缀匹配）
  - 复制并配置测试模板文件
  - 完整的参数化命令行支持

**使用方法**:
```bash
# 查看帮助信息
python xpath_test_generator.py -h

# 基本用法（所有参数必需）
python xpath_test_generator.py -y "D:\yang\B75_yin" -d "D:\netconf_doc" -t "C:\templates" -o "D:\output"

# 简写形式
python xpath_test_generator.py --yin-dir "D:\yang\B75_yin" --docs-dir "D:\netconf_doc" --template-dir "C:\templates" --output "D:\output"

# 只指定必需参数，跳过模板复制
python xpath_test_generator.py -y "D:\yang\B75_yin" -d "D:\netconf_doc" -o "D:\output"
```

**参数说明**:
- `-y, --yin-dir`: YIN文件目录路径（必需）
- `-d, --docs-dir`: 文档分析结果(.new.json文件)目录路径（必需）
- `-o, --output`: 输出目录路径（必需）
- `-t, --template-dir`: 模板文件目录路径（可选）

**输出结构**:
```
输出目录/
├── XPath1/
│   ├── yin.txt              # 提取的YIN子模块
│   ├── netconf.txt          # 匹配的文档内容
│   └── test_netconf.py      # 配置后的测试模板
├── XPath2/
│   ├── yin.txt
│   ├── netconf.txt
│   └── test_netconf.py
└── ...
```

**处理逻辑**:
1. 从`.new.json`文件中提取文档中识别的XPath
2. 将每个XPath转换为独立的测试文件夹
3. 从YIN文件中提取对应的子模块定义
4. 查找并匹配相关的文档内容
5. 复制并配置测试模板文件

### 5. 代码生成工具

#### 5.1 complete_code.py - NETCONF代码补全工具
- **功能**: 访问不同文件，使用Claude Code生成NETCONF测试代码
- **主要流程**:
  - 读取claude.md中的配置
  - 自动补全test_netconf.py文件
  - 创建调试环境和备份
  - 支持并行处理多个文件夹

#### 5.2 debug_code_save_to_json.py - 代码调试修复工具
- **功能**: 访问不同的文件夹，使用Claude Code修复代码
- **工作流程**:
  1. 执行pytest测试检查代码状态
  2. 如果测试失败，调用Claude进行代码修复
  3. 循环修复直到所有测试通过
  4. 将调试结果保存到JSON文件

**核心特性**:
- 支持超时控制和错误重试
- 自动保存调试日志
- 生成详细的调试报告
- 支持JSON格式的结果存储

## 核心工作流程变更

### 🆕 新的简化的工作流程

工具集已重新设计，专注于从**文档分析结果中提取真实的XPath**，而不是基于YIN文件的理论分析：

```
1. yang_converter.py → 转换YANG文件为YIN/DSDL格式
   ↓
2. netconf_doc_processor.py → 转换Word文档并提取XPath
   ↓
3. xpath_test_generator.py → 基于文档XPath生成测试结构
   ↓
4. complete_code.py → 生成测试代码
   ↓
5. debug_code_save_to_json.py → 调试和修复代码
```

### 完整工作流程

1. **YANG文件转换阶段**
   ```bash
   # 转换YANG文件为所有格式
   python yang_converter.py --all "D:\yang\V9"

   # 或选择特定格式
   python yang_converter.py --yin "D:\yang\V9"        # 仅YIN
   python yang_converter.py --dsdl "D:\yang\V9"       # 仅DSDL

   # 同时转换为YIN和DSDL格式（默认）
   python yang_converter.py "D:\yang\V9"

   # 指定依赖目录（用于DSDL转换）
   python yang_converter.py --dsdl "D:\yang\V9" -p "D:\yang\dependencies"
   ```

2. **文档处理与分析阶段**
   ```bash
   # 转换Word文档并分析XPath信息（使用默认输出文件夹 converted_docs，包含修订提取）
   python netconf_doc_processor.py document.docx

   # 指定输出文件夹
   python netconf_doc_processor.py -o analysis_results document.docx

   # 批量处理多个文档
   python netconf_doc_processor.py file1.docx file2.docx file3.docx

   # 通配符处理
   python netconf_doc_processor.py *.docx

   # 不提取修订内容以提高处理速度
   python netconf_doc_processor.py --no-revisions document.docx
   ```

3. **基于文档的测试生成阶段**
   ```bash
   # 生成基于真实文档XPath的测试文件夹结构（使用默认 converted_docs 文件夹中的分析结果）
   python xpath_test_generator.py -y "D:\yang\B75_yin" -d "D:\documents\converted_docs" -o "D:\test_folders"

   # 指定文档分析结果文件夹
   python xpath_test_generator.py -y "D:\yang\B75_yin" -d "D:\documents\analysis_results" -o "D:\test_folders"

   # 包含模板文件
   python xpath_test_generator.py -y "D:\yang\B75_yin" -d "D:\documents\converted_docs" -t "C:\templates" -o "D:\test_folders"
   ```

4. **代码生成阶段**
   ```bash
   # 自动生成NETCONF测试代码
   python complete_code.py
   ```

5. **代码调试与修复阶段**
   ```bash
   # 循环调试直到测试通过
   python debug_code_save_to_json.py
   ```

### 🔧 关键改进点

1. **真实XPath提取**: 从Word文档中提取实际使用的XPath，而非理论分析
2. **DSDL格式支持**: 新增DSDL XML格式转换，支持lxml美化输出
3. **参数化工具**: 所有工具支持命令行参数，使用更灵活
4. **智能匹配**: 文档内容与XPath的精确匹配和最长前缀匹配
5. **统一接口**: 合并重复工具，简化操作流程
6. **统一输出管理**: 文档处理输出文件自动保存在与DOCX文件同目录的指定文件夹中，避免文件分散

## 配置要求

### 环境依赖
- Python 3.8+
- pyang (用于YANG文件转换)
- pypandoc (用于Word文档转换)
- lxml (用于XML处理)
- beautifulsoup4 (用于HTML解析)
- markdown (用于Markdown处理)
- claude-agent-sdk (用于Claude Code集成)

### 路径配置
各工具中的路径需要根据实际环境进行调整：
- YANG文件目录: `D:\yang\{version}`
- 输出目录: `D:\yang\{version}_yin`, `D:\yang\{version}xml`
- 文档目录: `D:\netconf_doc`
- 测试代码目录: `D:\netconf_test_point_code`

## 输出文件

### 主要输出
- `{目录名}_converted/` - 所有格式文件目录（YIN、DSDL）
- `{目录名}_to_yin/` - 仅YIN格式文件目录
- `{目录名}_to_dsdl/` - 仅DSDL格式文件目录
- `converted_docs/` - 默认文档处理输出文件夹（与DOCX文件同目录）
- `{文档名}.md` - 转换后的Markdown文件（保存在输出文件夹中）
- `{文档名}.new.json` - 文档分析结果文件（包含XPath信息，保存在输出文件夹中）
- `{项目名}_report.json` - 调试和修复报告

### 报告格式
- JSON格式：结构化数据，便于程序处理
- Excel格式：调试过程中生成的历史报告（已迁移到JSON）

## 注意事项

1. **路径配置**: 使用前请确保所有路径配置正确
2. **依赖安装**: 确保所有Python依赖包已正确安装
3. **权限设置**: 某些工具需要文件读写权限
4. **并发控制**: 代码生成和调试工具支持并发，但建议根据系统性能调整
5. **错误处理**: 各工具都包含完善的错误处理机制，异常情况会输出详细日志

