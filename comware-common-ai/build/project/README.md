# Comware AI 云开发环境

欢迎使用 Comware AI 云开发环境。本页介绍 VS Code 终端的基本用法以及
`h3ccodecli` 工具的使用方法。

---

## VS Code 终端

### 打开终端

- **快捷键**：按 `` Ctrl+` ``（反引号）切换终端面板。
- **菜单**：点击顶部菜单栏的 **Terminal > New Terminal**。
- **命令面板**：按 `Ctrl+Shift+P`，然后输入 `Terminal: Create New Terminal`。

### 常用操作

| 操作           | 快捷键 / 操作方式                                   |
| -------------- | ---------------------------------------------------- |
| 新建终端       | 点击终端面板中的 **+** 图标                          |
| 拆分终端       | 点击拆分图标，或按 `Ctrl+Shift+5`                    |
| 切换终端       | 点击终端标签页，或按 `Ctrl+PageUp/PageDown`          |
| 关闭终端       | 输入 `exit`，或点击垃圾桶图标                        |
| 最大化终端     | 双击终端面板标题栏                                   |
| 清屏           | 输入 `clear`，或按 `Ctrl+Shift+P` > `Terminal: Clear` |

### 提示

- 默认 Shell 为 **Bash**。
- 终端启动时的工作目录为项目目录（`~/project`）。
- 在终端中使用 `Ctrl+Shift+C` / `Ctrl+Shift+V` 进行复制/粘贴（也可以右键打开
  上下文菜单）。
- 可以拖动终端面板边框调整大小，或将其拖到侧边停靠为面板。

---

## h3ccodecli

`h3ccodecli` 是一个 CLI 工具，用于在当前工作区中配置并启动 **Claude Code**（AI
编程助手）。

### 首次使用

打开终端并运行：

```bash
h3ccodecli
```

该工具将：

1. **自动检测域账号**（通过 `whoami`）。
2. **查询 API** 获取你的个人 API Key。
3. **提示选择部门**——如果你的账号关联了多个部门（输入数字选择，或输入新的部门
   名称）。
4. **保存配置** 到 `~/.bashrc`（API Key、部门、模型设置等）。
5. **启动 Claude Code**（IDE 模式，已预配置权限）。

### 后续使用

后续运行 `h3ccodecli` 时，工具将：

- 从 `~/.bashrc` 加载已保存的配置。
- 异步验证 API Key 是否仍然有效。
- 直接启动 Claude Code，无需重新配置。

直接运行即可：

```bash
h3ccodecli
```

### 重置配置

如需重新认证或切换部门：

```bash
h3ccodecli --reset
```

这会清除 `~/.bashrc` 中保存的配置。之后重新运行 `h3ccodecli` 即可重新配置。

### 环境变量

`h3ccodecli` 会配置以下环境变量（保存在 `~/.bashrc` 中）：

| 变量名                            | 说明               |
| --------------------------------- | ------------------ |
| `ANTHROPIC_AUTH_TOKEN`            | 你的个人 API Key   |
| `ANTHROPIC_BASE_URL`             | API 端点地址       |
| `ANTHROPIC_MODEL`                | 默认模型           |
| `ANTHROPIC_DEFAULT_OPUS_MODEL`   | Opus 模型别名      |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet 模型别名    |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL`  | Haiku 模型别名     |
| `H3C_DEPARTMENT`                 | 你的部门           |
| `H3C_USERNAME`                   | 你的域账号         |

### 日志

初始化日志写入以下路径：

```
~/project/log/init_h3ccodecli.log
```

如果在配置过程中遇到问题，请查看此文件。

---

## 快速上手

1. 按 `` Ctrl+` `` 打开终端。
2. 运行 `h3ccodecli` 配置并启动 Claude Code。
3. 开始 AI 辅助编程！

> **提示**：你可以随时关闭此页面，之后在文件资源管理器中重新打开（项目根目录下的
> `README.md`）。
