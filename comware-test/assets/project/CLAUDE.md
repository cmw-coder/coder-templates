
## 任务完成规约

我们将测试脚本开发分为 2 个规划阶段 + 1 个执行阶段，请严格按照如下二阶段规划工作流和执行阶段进行完成用户的艰巨任务，
必须交付Specification（测试规范）/tasks.md（具体执行清单）后再开始编码，编码完成后必须保证使用aigc_tool运行通过。

---

## 一、二阶段规划工作流

### Phase 1: Specification（测试规范）
**产出物**: spec.md（详细测试需求）
**目标**: 澄清测试需求，定义完整的测试场景，定义测试边界，砍掉过度测试设计

### 1.1 测试范围原则
- 核心测试点: [用户指定的测试点]
- 衍生测试点: 仅在KE有相关案例时适当扩展
- 测试边界: 不扩散到无关功能
- 不生成空文件（如无用的__init__.py）
- 头文件明确模块引入:例如:
 import pytest,from pytest_atf.atf_globalvar 
 import globalVar as gl,from pytest_atf 
 import run_multithread,atf_assert,atf_check,atf_skip,atf_logs

### 1.2 测试点分析
**原始需求**: [用户输入的测试点]
通过私域资料调研后完成需求澄清：
- [ ] **必须查阅**：KE/对应操作库.md （操作方法） KE/conftest.py(基础配置) KE/*.topx 组网信息
- [ ] **建议查阅**：press/对应模块.md（业务依据）
- [ ] **如有则查**：test_example/相似例子.py（最佳实践）
**澄清后需求**:
1. 功能点: [精确描述1]
2. 功能点: [精确描述2]
3. 边界条件: [明确边界]

### 1.3 测试场景设计
**场景1**: [Given-When-Then格式]
- Given: 拓扑环境已部署（基于.topox）
- When: 执行[具体操作]
- Then: 验证[预期结果]

### 1.4 数据需求
- 输入数据: [来源于press文档x.x章节]
- 预期输出: [符合KE文件要求]
- 验证点: [可验证的具体指标]


**价值**: 在这个阶段就明确"只测试什么"，避免测试范围蔓延，强迫在编写前澄清模糊需求，如"验证端口状态" → "验证端口admin状态为up，protocol状态为up"。

---

### Phase 2: Tasks（任务清单）
**产出物**: tasks.md（可执行的测试设计，具体执行清单）
**目标**: 拆解为可执行的多个任务
**设计模板**:
```python
# 这不是最终代码，而是设计模板，伪代码禁止
class Test[模块名][功能名]:
    
    @classmethod
    def setup_class(cls):
        """基于conftest.py的配置"""
        if conftest_exists and meets_requirements:
            # 无需额外配置
            gl.DUT1.checkcommand("...") # 对conftest.py中基础环境验证
            pass
        else:
            # 需要补充的配置代码
            gl.DUT1.configure("...")  # 示例伪代码，禁止使用
            
    @classmethod
    def teardown_class(cls):
        """清理逻辑 - 必须实现"""
        
    def test_step_1_验证基础功能(self):
        """基于KE/基础操作库/端口操作.md的步骤"""
        # 步骤1: [引用press文档]
        # 步骤2: [引用test_example]
        # 验证: [明确验收标准]
        
    def test_step_2_验证边界条件(self):
        """边界条件测试"""
        # ...
```
**任务拆解**:
```
### Task 1: 调研私域资料
- [ ] 查阅 press/[模块].md（业务规范）
- [ ] 必须查阅 KE/[基础操作].md（操作方法，尽可能查阅）
- [ ] 分析 test_example/相似案例.py
- 产出: __private_docs__ 引用定义

### Task 2: 编写setup/teardown
- [ ] 优先使用test_scripts目录下的，没有则判断是否存在其它可用的conftest.py和xxx.topox，存在则拷贝到/home/g23702/project/test_scripts目录下
- [ ] 检查conftest.py是否满足需求
- [ ] 编写teardown_class清理逻辑

### Task 3: 实现test_step_1
- 文件: test_scripts/[三级目录]/test_[模块]_[功能].py
- 要求: 严格遵循pypilot API

...
```

**价值**: 明确进度，每个任务都可验证、可追踪。。

---

## 二、执行阶段：脚本生成与质量检查

### Phase 3: Implementation & Quality（实现与质量）
基于前2阶段的产出物，执行具体实现：

#### 3.1 脚本生成（基于Tasks（任务清单））
```python
__private_docs__ = {
    '业务规范': ('press/模块A.md', '4.2章节'),
    '测试基准': ('test_example/test_xx.py', 'Case03')
}

class TestClass:
    @classmethod
    def setup_class(cls):
        """如果conftest.py存在且基础配置满足需求，则为空即可"""
        pass
                
    @classmethod 
    def teardown_class(cls):
        """必须在此处编写配置清除代码"""
        # 清理逻辑
    
    def test_step_1(self):
        """基于Task 3的实现"""
        # 使用gl.DUTx.PORTx（来自.topox）
        # 严格遵循pypilot方法
```

#### 3.2 质量检查流程
**步骤1**: Pylint静态检查（必须通过）
```bash
source .venv/bin/activate
pylint [脚本].py  # 修复所有E级别错误
```

**步骤2**: 人工Review检查清单
- [ ] 设备命名一致性（gl.DUTx vs .topox）
- [ ] 所有操作在press/KE中有依据
- [ ] __private_docs__引用完整
- [ ] teardown_class清理逻辑完整

**步骤3**: 必须进行脚本运行验证，保证运行通过（如~/project/.aigc_tool/aigc.json文件存在字段内容"exec_ip": "10.141.xxx.xx"则表示物理环境已经配置就绪否则则表示没配置物理环境，需用户退出再次进入才能使用运行环境）
运行示例： 
```python
# 最多10轮迭代
for attempt in range(10):
    # 1. 运行测试
    result = python ~/project/.aigc_tool/aigc_tool.py run --scriptspath "/home/$(whoami)/project/test_scripts/XXX/xxx.py"
    #wait timeout 5m 
    # 2. 分析结果并修复
    if success:
        break
    else:
        fix_based_on_result(result)
     # 3. 回滚配置
    python ~/project/.aigc_tool/aigc_tool.py restore
```

**步骤4**: 完成交付进行总结

---
