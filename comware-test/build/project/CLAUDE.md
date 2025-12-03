
## 核心思想：规划驱动开发
**原则**：在写测试代码前，先优先查阅相关conftest.py和*.topx完成"宪法-规范-计划-任务"的思考流程，然后严格按照思考流程和执行流程完成用户的任务。

---

## 一、四阶段思考流程（内化）

### 1. Constitution（宪法思考）
**思考点**：
- **砍功能**：这个测试点是否在核心范围？砍掉衍生/边缘测试
- **定边界**：明确"不做"什么（不测试无关模块、不验证非press定义逻辑）
- **设原则**：单一职责、最小依赖、完整清理

### 2. Specification（规范思考）
**思考点**：
- **澄清需求**：将模糊需求转为明确场景
  - ❌ "测试端口状态" → ✅ "测试端口从admin down到up的协议状态同步"
- **定义场景**：用Given-When-Then快速描述
- **数据明确**：输入/输出来自哪个press/KE章节

### 3. Plan（计划思考）
**思考点**：
- **结构设计**：套用标准模板，明确setup/teardown逻辑
- **代码复用**：哪些操作可参考test_example/类似例子
- **设备引用**：确保与.topox定义的设备名一致

### 4. Tasks（任务拆解）
**思考点**：
- **任务列表**：拆解为3-5个可执行小任务
- **验收标准**：每个任务完成后如何验证

---

## 二、执行流程

### 2.1 需求分析阶段（融合Constitution+Specification）
- [ ] **优先查阅**：相关conftest.py和*.topox文件是否存在？存在需要优先阅读
- [ ] **宪法思考**：这个测试点真的必要吗？有没有过度设计？
- [ ] **边界明确**：列出"不做"的事项
- [ ] **需求澄清**：将用户需求转为明确的Given-When-Then
- [ ] **资料检查**：检查关联的conftest.py和.topox文件

### 2.2 私域资料调研（精简）
- [ ] **必须查阅**：press/对应模块.md（业务依据）
- [ ] **必须查阅**：KE/对应操作库.md （操作方法） KE/conftest.py(基础配置) KE/*.topox 组网信息
- [ ] **如有则查**：test_example/相似例子.py（最佳实践）
- [ ] **输出确认**：在代码头部明确引用来源

```python
__private_docs__ = {
    '业务规范': ('press/模块A.md', '4.2章节'),
    '操作指南': ('KE/基础操作库.md', '3.1章节'),
    '参考案例': ('test_example/test_xx.py', '')  # 如有
}
```

### 2.3 脚本生成（融合Plan思考）
将脚本生成并保存到test_scripts/三级目录/xxx(如果当前目录下已有类似目录优先放到已有的对应目录下面)
```python
# 1. 套用标准结构（禁止修改）
class TestClassName:
    @classmethod
    def setup_class(cls):
        """基于Plan思考：conftest.py是否满足需求？"""
        pass  # 如果conftest.py满足则留空,否则需要补充业务配置
                
    @classmethod 
    def teardown_class(cls):
        """基于宪法思考：必须完整清理"""
        # 清理逻辑
    
    def test_step_1(self):
        """基于Tasks拆解"""
        # 严格按照pypilot API
        # 设备名与.topox一致
        # 操作在press/KE中有依据
    def test_step_2(self):
        """基于Tasks拆解"""
        # 严格按照pypilot API
        # 设备名与.topox一致
        # 操作在press/KE中有依据
```

### 2.4 质量检查（严格执行）
**第一步：静态检查**
```bash
pylint script.py  # 修复所有E级别错误
```

**第二步：完成后自行再次Review**
- [ ] 设备命名一致性：`gl.DUTx` = `.topox`定义
- [ ] 操作可溯源：每个关键操作都可在press/KE中找到依据
- [ ] 清理完整：teardown_class能100%恢复环境
- [ ] 结构合规：没有多余的pytest方法

**第三步：使用aigc_tool工具运行脚本(预计等待3-5分钟左右，建议使用timeout等待)**
判断~/project/.aigc_tool/aigc.json文件存在字段内容"exec_ip": "10.141.xxx.xx"则表示物理环境已经配置就绪否则则表示没配置物理环境，需用户退出再次进入才能使用运行环境
```
最多10轮迭代：
1. 运行脚本
2. 分析结果
3. 修复问题
4. 回滚环境
```

**第四步：简要总结**

## 三、工具使用

### 3.1 Pylint检查命令
```bash
source .venv/bin/activate
pylint [生成的脚本].py
```

### 3.2 aigc_tool工具相关命令
#### 1. 脚本执行命令
**命令**: python ~/project/.aigc_tool/aigc_tool.py run --scriptspath "/home/$(whoami)/project/test_scripts/OSPFV3/xxx.py" 
**功能**: 在已部署环境中执行脚本  
**参数**:   
- `scriptspath`（必填）：脚本目录的路径  
**返回值**: 返回错误信息或者脚本运行信息
**注意**: 该接口不支持并行运行，必须串行启动并启动timeout进行等待

#### 2.回滚配置命令
**命令**: python ~/project/.aigc_tool/aigc_tool.py restore 
**功能**：在已部署环境中将之前执行错的环境恢复 
**注意**：重新调用 脚本执行命令 时，必须调用回滚配置命令
**返回值**: 返回执行结果信息
**注意**: 每个脚本运行后，必须执行回滚，避免互相影响

#### aigc_tool脚本运行示例
step 1: 执行python ~/project/.aigc_tool/aigc_tool.py run --scriptspath "/home/$(whoami)/project/test_scripts/OSPFV3/xxx.py"
step 2: 预计等待3-5分钟，会返回结果，如果等待5分钟后，结果仍然未返回，可以使用sleep等待，知道结果返回后分析错误并进行修复
step 3: 回滚脚本，重新执行 python ~/project/.aigc_tool/aigc_tool.py restore 
step 4: 又到step 1,直到运行成功
---


