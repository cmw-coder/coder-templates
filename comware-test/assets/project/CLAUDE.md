# SDD规范驱动测试脚本生成宪法

**核心定位**：本宪法定义所有测试脚本生成任务的**强制三阶段框架**，确保渐进式交付与规范驱动。全流程严格遵循"先规划后编码"原则，所有核心任务建议为**最高优先级独立任务**。交付的脚本需要通过python -u ~/project/.aigc_tool/aigc_tool.py run 运行验证通过。
用户@的文件一定要优先查看，这些文件是用户希望你优先参考的，你要仔细分析这些文件内容，从中提取可用的内容。
查找本地文件时.aigc_tool文件夹，.venv文件夹下的内容不需要读取

---

## 1. 三阶段工作流框架（强制顺序）

**Phase 1: Specification** → 查阅参考用户@的文件(如有), 产出或修改已有的 `test_scripts/*/topoConfig.md`（拓扑配置说明）+  `test_scripts/*/spec.md`（测试规范）

**Phase 2: Tasks** → 基于Phase 1的交付物，继续查阅相关内容(如有需要)，产出 `test_scripts/*/tasks.md`（任务清单）

**Phase 3: Implementation** → 根据前两个阶段交付物，并按照任务清单完成脚本交付

**强制交付顺序**：必须完成并交付 `spec.md` 和 `tasks.md` 后，才能开始编码。编码完成后必须通过 `aigc_tool` 运行验证。

---

## 2. 工具使用与可追溯性要求

### 2.1 环境准备工具
- **云端数据库搜索相似conftest业务背景**：
  ```bash
  python3 ~/project/.aigc_tool/data_search_h3c_example.py \
    --description "业务描述（如：ISIS SR）" \
    --indexname "background_ke"
  ```
-**调用时机**: 如果当前工程没有合适的业务背景conftest*.py, 则可以调用该接口获取云端数据库的数据
  
### 2.2 搜索官方文档工具
- **搜索配置示例**：
  ```bash
  python3 ~/project/.aigc_tool/data_search_h3c_example.py \
    --description "关键业务描述" \
    --indexname "v9_press_example"
  ```

### 2.3 代码实现工具
- **搜索测试用例参考**：
  ```bash
  python3 ~/project/.aigc_tool/data_search_h3c_example.py \
    --description "关键业务描述" \
    --indexname "example_ke"
  ```
---

## 3. 通用约束与原则

### 3.1 代码生成原则
- **单需求/测试点单脚本**：每个测试需求/测试点仅生成一个测试脚本文件，所有测试场景封装为同一测试类下的不同test_step_x方法
- **不生成空文件**：禁止生成无用的 `__init__.py` 等空文件
- **头文件明确模块引入**：必须显式导入所需模块，例如：
  ```python
  import pytest
  from pytest_atf.atf_globalvar import globalVar as gl
  from pytest_atf import run_multithread, atf_assert, atf_check, atf_skip, atf_logs
  ```
### 3.2 测试范围控制
- **核心测试点**：仅实现用户明确指定的测试点
- **衍生测试点**：仅在KE有相关案例时可适当扩展
- **测试边界**：严禁扩散到无关功能模块

### 3.3 私域资料引用规范（必须遵循）
所有测试设计必须有据可查，必须引用私有文档，永远不要忘记优先查看本地目录的相关内容，这是用户最希望你参考的，搜索工具只是用来补充你缺失的信息：
- **业务规范**：`press/对应模块.md`，优先参考press目录下的文件内容，分析可用片段，如果需要额外的配置示例信息，可以调用工具进行搜索，详见2.1章节
- **操作方法**：`KE/*/对应操作库.md`、`KE/*/conftest*.py`、`KE/*/*.topox` ，优先参考KE目录下的文件内容，没有找到conftest*.py时可以调用工具进行搜索选择相似业务的conftest进行参考，详见2.2章节
- **最佳实践**：`test_example/相似例子.py`，优先查看test_exampl目录下的文件内容，如果需要补充配置示例脚本可以调用工具进行搜索，详见2.3章节

### 3.4 设备与配置一致性
- **命名一致**：脚本中的设备名（`gl.DUTx`）必须与 `.topox` 拓扑文件严格对应
- **配置优先**：**优先复用 `test_scripts` 目录下现有配置**，否则优先从本地工程其他位置拷贝可用配置，其次考虑调用工具进行搜索
- **清理强制**：所有 `teardown_class` 必须实现完整配置清除逻辑

### 3.5 **核心原则**：Flat is better than nested. 禁止任何形式的过度封装。

#### 3.5.1. **禁止二次封装 (No Over-Abstraction)**:
   - **严禁**在脚本内定义非必要的 Helper Function 或 Wrapper Class（例如：不要自己写一个 `config_isis_interface()` 函数，而是直接在 test step 里调用 `gl.DUT1.configure()`）。
   - **严禁**对基础 API（如 `pypilot`, `gl.DUTx`）进行包装。测试步骤应"直白"地写在 `test_` 方法中。
   - 除非某段逻辑极其复杂且被 **3个以上** 测试用例复用，否则不允许提取独立函数。

#### 3.5.2. **风格一致性 (Consistency)**:
   - 代码结构必须严格对齐 `test_example` 中的官方范例。
   - 引用变量时，严格使用全局对象（如 `gl.DUT1`, `gl.DUT2`），不要自己创建局部别名。
   - 校验逻辑直接使用 `atf_assert` 或 `atf_check`，不要自己写 `if result != expect: raise Error`。

---

## 4. 拓扑与基础配置准备流程

### 4.1 查找与评估阶段
**交付物**: `test_scripts/xxx/topoConfig.md`

**执行流程**:
1. **优先查找**: 在 `test_scripts` 目录下搜索是否存在匹配的 `*.topox` 和 `conftest*.py`，如果该目录下存在，一般不建议修改
2. **次级查找**: 若test_scripts下无匹配，搜索项目其他位置（如 `KE/` 目录）查找可用配置
3. **工具搜索**：使用工具搜索相似配置
   ```bash
   python3 ~/project/.aigc_tool/data_search_h3c_example.py \
     --description "[拓扑需求]" \
     --indexname "background_ke"
   ```
4. **评估匹配度**: 评估找到的topox/conftest是否满足当前测试需求，如果找到的话则拷贝到`test_scripts`对应目录下

### 4.2 生成topoConfig.md
**规则**:
- **若找到匹配配置**: 在 `topoConfig.md` 中**引用**现有文件路径，并说明为何适用
- **若未找到匹配配置**: 基于 `press/` 业务规范和 `KE/` 操作库以及搜索内容，**设计**新的拓扑和配置需求
- **必须标注**: 明确标注"**无需额外补充**"或"**需补充以下内容**"
- **必须记录**: 记录搜索过程中的关键词和有用结果

**文档模板**:
```markdown
# 拓扑与基础配置说明

## 1. 工具搜索记录
- 搜索时间: [时间]
- 搜索关键词: [关键词]
- 有用结果: [简要说明]

## 2. 现有资源评估
- topox文件: [路径或"需新建"]
- conftest.py: [路径或"需新建"]
- 适用性分析: [基于搜索结果的分析]

## 3. 需求对齐
- 拓扑要求: [设备数量/类型/连接关系]
- 基础配置要求: [预置配置项]

## 4. 额外补充内容（如无则填"无"）
- 状态: "无需额外补充" 或 "需补充以下内容"
- 需修改topox: [具体修改点]
- 需修改conftest: [具体补充项]
```
---

## 5. Phase 1: Specification（测试规范）

### 5.1 拓扑与基础配置准备（⚠️ 必须独立task任务完成）

**独立任务性质**：此部分**必须作为Phase 1中的最高优先级独立子任务**完成，交付物为 `test_scripts/xxx/topoConfig.md`

```markdown
#### 执行流程（严格遵循）：
1. **步骤1**: 优先读取用户本地工程文件内容，其次按需使用工具搜索相似拓扑和配置
2. **步骤2**: 按第4章流程查找topox和conftest.py（`test_scripts`目录优先）
3. **步骤3**: 生成 `test_scripts/xxx/topoConfig.md`，明确标注"需补充内容"或"无需补充"
```
### 5.2 测试范围原则
- 核心测试点: [用户指定的测试点]
- 衍生测试点: 仅在KE有相关案例时适当扩展
- 测试边界: 不扩散到无关功能
- 不生成空文件（详见3.1节）
- 头文件明确模块引入（详见3.1节）
- **工具使用记录**：在调研阶段必须记录使用的搜索关键词

### 5.3 测试点分析
**原始需求**: [用户输入的测试点]

通过私域资料调研后完成需求澄清（必须遵循3.3节并记录工具使用）

**澄清后需求**:
1. 功能点: [精确描述1]
2. 功能点: [精确描述2]
3. 边界条件: [明确边界]

### 5.4 测试场景设计
**场景1**: [Given-When-Then格式]
- Given: 拓扑环境已部署（基于.topox）
- When: 执行[具体操作]
- Then: 验证[预期结果]

### 5.5 数据需求
- 输入数据: [来源于press文档x.x章节]
- 预期输出: [符合KE文件要求]
- 验证点: [可验证的具体指标]

**核心价值**: 在编码前就明确"只测试什么"，避免范围蔓延，强迫在编写前澄清模糊需求（如"验证端口状态" → "验证端口admin状态为up，protocol状态为up"）。

---

## 6. Phase 2: Tasks（任务清单）

### 6.1 设计模板（只是伪代码，禁止直接拷贝）
```python
class Test[模块名][功能名]:
    
    @classmethod
    def setup_class(cls):
        """基于topoConfig.md指定的conftest.py配置"""
        if topoConfig.md指示"无需额外补充":
            # 仅需验证基础环境
            gl.DUT1.checkcommand("...")
            pass
        else:
            # 按topoConfig.md补充配置
            gl.DUT1.configure("...")  # 示例伪代码，禁止直接使用
            
    @classmethod
    def teardown_class(cls):
        """清理逻辑 - 必须实现（详见3.4节）"""
        
    def test_step_1_验证xxx功能(self):
        """基于搜索到的示例实现"""
        # 步骤1: [引用press文档]
        # 步骤2: [引用test_example]
        # 验证: [明确check内容]
        
    def test_step_2_验证xxx功能件(self):
        """基于搜索到的示例实现"""
        # 步骤1: [引用press文档]
        # 步骤2: [引用test_example]
        # 验证: [明确check内容]
```

### 6.2 任务拆解清单

#### Task 0: 拓扑与基础配置准备【独立任务】
**交付物**: `test_scripts/xxx/topoConfig.md`（已在Phase 1生成）和conftest.py(根据topoConfig.md复用已有的或新生成)

**执行动作**:
- [ ] 若topoConfig.md标注"需新建"：启动**独立子任务**生成新的topox和conftest.py到test_scripts对应目录下
- [ ] 若topoConfig.md标注"需修改"：启动**独立子任务**拷贝已有的到test_scripts对应目录下并进行修改
- [ ] 若topoConfig.md标注"无需补充"：拷贝现有文件到test_scripts对应目录
- [ ] 验证topox与conftest.py可用性

**强制阻断条件**: **本任务未完成，禁止启动Task 1-3**

#### Task 1: 调研私域资料
- [ ] 优先读取本地文件，需要额外信息使用工具搜索 `press/[模块].md`（业务规范）
- [ ] 优先读取本地文件，需要额外使用工具搜索 `KE/[基础操作].md`（操作方法）
- [ ] 优先读取本地文件，需要额外使用工具搜索，分析 `test_example/相似案例.py`
- 产出: `__private_docs__` 引用定义 + 搜索记录文件

#### Task 2: 编写setup/teardown
- [ ] 基于Task 0的结果，判断conftest*.py是否存在且基础配置满足需求，满足则为空即可
- [ ] 优先使用`test_scripts`目录下的conftest*.py和.topox，没有则优先从本地工程查找，其次调用搜索工具
- [ ] 检查conftest*.py是否满足spec.md中的环境需求
- [ ] 编写`teardown_class`清理逻辑（必须符合3.4节标准）

#### Task 3: 实现test_step_1
- **文件**: `test_scripts/[三级目录]/test_[模块]_[功能].py`
- **实现要求**：
  1. 优先参考本地目录文件，结合测试点获取可用的片段
  2. 分析测试点，如果需要额外的参考信息搜索参考片段：
     ```bash
     python3 ~/project/.aigc_tool/data_search_h3c_example.py \
       --description "缺失的参考信息片段秒速" \
       --indexname "example_ke"
     ```
  2. 直接复用现有写法，禁止自定义封装函数
- **约束**: 严格遵循pypilot API，代码风格参照KE或example，禁止二次封装

**核心价值**: 明确可追踪的进度，每个任务都可验证、可闭环，所有工具使用可追溯。

---

## 7. Phase 3: Implementation & Quality

### 7.1 脚本实现模板参照6.1章节设计模板

### 7.2 按照如上章节 4. 拓扑与基础配置准备流程 5. Phase 1: Specification（测试规范） 6. Phase 2: Tasks（任务清单）严格执行完成产出交付物。

### 7.3 质量检查标准

#### 7.3.1 Pylint静态检查
```bash
source .venv/bin/activate
pylint "/home/$(whoami)/project/test_scripts/XXX/xxx.py"  # 修复所有E级别致命错误，请在~/project/目录下执行
```

#### 7.3.2 运行验证（强制）
**环境检查**：若 `~/project/.aigc_tool/aigc.json` 中存在 `"exec_ip": "10.141.xxx.xx"` 字段，则表示物理环境已配置就绪。

**验证循环**（最多10轮迭代）：
```python
for attempt in range(10):
    # 1. 运行测试
    result = python -u ~/project/.aigc_tool/aigc_tool.py run --scriptspath "/home/$(whoami)/project/test_scripts/XXX/xxx.py"
    # must wait timeout 5m 
    
    # 2. 分析结果并修复
    if success:
        break
    else:
        fix_based_on_result(result) #修复时注意参考调研资料，如果非脚本问题不修复
    
    # 3. 回滚配置
    python -u ~/project/.aigc_tool/aigc_tool.py restore
```

**交付要求**：完成Phase 3后，必须确保脚本通过 `aigc_tool` 运行验证，方可视为任务完成。

---

## 8. 工作流程约束总结

### 执行顺序（强制）：
1. **Phase 1**: 
   - 产出 `topoConfig.md` + `spec.md`

2. **Phase 2**:
   - 拆解具体任务，特别关注Task 0（拓扑准备）
   - 产出`tasks.md`

3. **Phase 3**:
   - 基于前两阶段交付物编码
   - 使用工具搜索代码参考 → 记录
   - 运行验证通过`aigc_tool`

### 关键检查点：
- ✅ 是否优先复用了`test_scripts`目录下的现有配置？
- ✅ 是否避免了二次封装，直接使用基础API？
- ✅ 是否通过了pylint静态检查？
- ✅ 是否通过了aigc_tool运行验证？
- ✅ 所有私域资料引用是否都有据可查？
