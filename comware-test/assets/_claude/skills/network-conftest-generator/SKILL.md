---
name: network-conftest-generator
description: 生成并配置用于新华三技术有限公司H3C网络设备自动化的 pytest conftest.py。负责测试背景搭建和测试背景清理。
---

# 网络测试环境生成器

## 目标
制定todo list, 按照任务列表, 生成 `conftest.py` 文件，该文件是网络设备测试背景的代码文件。它负责测试背景搭建和测试背景清理，确保所有网络测试用例在统一的组网环境中执行并提供设备资源、拓扑配置和测试数据的共享机制。

## 工作流程

### 步骤 1：初始化检查
目标：确保工作区内存在一个可用的 conftest.py 基准文件。

1. **检查文件**：使用 `Ls` 检查当前工作区是否存在 `conftest.py`。
2. **执行拷贝 (如果缺失)**：
   - **若文件不存在**：
     - 读取模版文件：`{当前skill路径}/templates/conftest.py`。
     - 使用cp命令将该文件拷贝到当前工作区中。
     - *（此时工作区内已确保存在 `conftest.py`，继续执行步骤 2）*
   - **若文件已存在**：
     - 直接跳到步骤 2。

### 步骤 2：深度校验与知识检索
目标：**这是最关键的一步。**对比“当前conftest.py文件能力”与“用户实际需求”，并利用查询命令填补知识空白。
1. **读取现状**
   - 读取当前 conftest.py 的完整内容。
   - 读取拓扑文件（通常是 .topox），获取物理设备列表（如 DUT1, DUT2）。
2. **解析用户输入**：
   - **分析需求**：提取测试用例中的配置需求。
   - **查阅标准**：读取`{当前skill路径}/templates/H3C_数据库检索指南.md`，了解每一个数据库对于conftest.py的作用。 每个数据库都需要多次的检索，执行以下参考命令搜索数据库进行参考。

      **background_ke库检索，该库有历史背景背景代码conftest.py**: 搭建DPI功能，必须检索
         ```bash
         python {当前skill路径}/script/data_search_h3c_example.py --description "DPI安全测试" --indexname "background_ke"
         ```
      
      **v9_press_example库检索，该库有常见的组网配置**: 配置交换机实现多网段互通
         ```bash
         python {当前skill路径}/script/data_search_h3c_example.py --description "交换机多网段配置" --indexname "v9_press_example"
         ```

      **example_ke库检索，该库有测试用例的实现代码，包含部分背景配置代码**: DHCP中继测试用例，必须检索
         ```bash
         python {当前skill路径}/script/data_search_h3c_example.py --description "DHCP中继" --indexname "example_ke"
         ```

      **cmd_ke库检索，用于存储网络设备命令行**: 配置接口IP地址
         ```bash
         python {当前skill路径}/script/data_search_h3c_example.py --description "ip address " --indexname "cmd_ke"

         python {当前skill路径}/script/data_search_h3c_example.py --description "配置接口IP地址" --indexname "cmd_ke"
         ```

      **press_config_des库检索，存储标准化的配置步骤说明，提供详细的配置流程和参数说明。**: 需要配置时间段策略
         ```bash
         python {当前skill路径}/script/data_search_h3c_example.py --description "时间段配置" --indexname "press_config_des"
         ```
3. **需求对比**：
   - 分析用户的具体测试需求。
   - 检查读取到的代码内容是否已包含这些逻辑。
   - *注意：如果是刚拷贝的默认模版，通常因缺乏特定配置（如只有单设备）而被判定为“不符合”。*

### 步骤 3：决策与执行
根据步骤 2 的对比结果执行：

#### 情况 A：内容不符合 (Mismatch)
1.  **制定计划 (Todo List)**：
   -    向用户简述修改计划（例如：“1. 配置端口地址；2. 创建静态路由”）。
2.  **重构代码**：
    *   基于当前文件内容，修改或添加代码。
    *   **关键**：再次调用步骤2中的python命令，了解计划所需的背景知识。
3.  **覆盖写入**：使用 `Write` 将更新后的代码写入 `conftest.py`。
4.  **反馈**：回复“已参考 H3C 知识库，更新 conftest.py 以支持您的测试需求。”

#### 情况 B：内容符合 (Match)
1.  **动作**：不做任何修改。
2.  **反馈**：回复“现有 conftest.py 已符合需求，无需修改。”并退出。



## 注意事项
1. 步骤2中，不要生成或者修改conftest
2. 必须查阅标准
3. 生成代码遇到业务盲区或需要参考标准配置时，**必须**使用 `Bash` 执行以下脚本获取标准参考。**查阅标准**不局限于步骤2，在步骤3中也可以使用。