---
display_name: Comware Common AI Interactive
description: 通过 Claude Code skill 实现交互式 SVN 检出的 AI 增强 Comware 开发环境
icon: ../../../site/static/icon/docker.svg
maintainer_github: coder
verified: true
tags: []
---

# Comware Common AI Interactive

通过 Claude Code skill 实现交互式 SVN 项目检出的 AI 增强 Comware 开发环境。

## 概述

本模板基于 `comware-common-ai`，核心区别在于：SVN 项目配置（分支选择、目录列表、凭证）不再通过 Terraform UI 参数表单收集，而是由内置的 Claude Code skill（`svn-checkout`）通过自然语言对话引导用户完成配置。

### 为什么选择交互式？

| 对比维度 | comware-common-ai | comware-common-ai-interactive |
|---|---|---|
| SVN 配置方式 | Terraform UI 表单（6 个参数） | Claude Code 对话 |
| 分支浏览 | 用户必须知道确切的 SVN 路径 | 通过 `svn list` 逐级交互式浏览 |
| 目录验证 | 输入时无验证 | 实时对 SVN 仓库进行验证 |
| 修改配置 | 需要重建工作区 | 编辑配置文件或重新运行 skill |
| 凭证存储 | Terraform state（加密） | `~/.svn_project_env`（chmod 600，密码 base64 编码） |

## 快速开始

1. **创建工作区** — 使用本模板创建（无需填写 SVN 参数）
2. **打开终端** — 在 code-server 中打开终端或通过 SSH 连接
3. **启动 Claude Code** 并输入：

   ```
   帮我检出 SVN 代码
   ```

   Claude 将使用 `svn-checkout` skill 引导你完成：
   - SVN 凭证设置（用户名默认为工作区所有者）
   - 分支选择（直接输入路径、自然语言描述或逐级交互浏览）
   - 平台模块选择（稀疏检出，加速初始化）
   - 公共代码配置（`PUBLIC/include` 始终包含）

4. **开始开发** — 所有标准工具（`abuild`、`checkout-list`、`shadow-branch` 等）与之前用法一致

## SVN 检出 Skill 用法示例

### 首次配置

```
> 帮我检出 V9R1 主分支代码，我需要 ospf 和 nqa 模块
```

Claude 会依次执行：
1. 询问你的 SVN 密码
2. 验证分支路径（`V9R1/trunk`）
3. 确认 `ospf` 和 `nqa` 在仓库中存在
4. 配置公共代码（包含 `PUBLIC/include`）
5. 将配置写入 `~/.svn_project_env` 并执行检出

### 交互式浏览

```
> 我需要检出代码，但不确定用哪个分支
```

Claude 会列出可用的主版本分支（`V7R1_SPRINGB64`、`V7R1_SPRINGB75`、`V9R1` 等），并逐级引导你选择 `trunk`、`branches_bugfix`、`branches_project` 等。

### 后续使用

```
> 查看一下我的 SVN 状态
```

如果代码已经检出，skill 会进入维护模式：显示 `svn status`，建议执行 update/commit/diff 等操作。

### 修改配置

```
> 我需要把 acl 模块也加到检出目录里
```

Claude 会将新模块添加到现有的稀疏检出中，并更新配置文件。

## 内置 Claude Code Skills

| Skill | 用途 |
|---|---|
| `svn-checkout` | 交互式 SVN 项目配置与检出 |
| `svn` | SVN 版本控制操作（update、commit、diff、merge 等） |
| `abuild` | Comware 构建系统指南 |
| `generating-comware-buildrun` | 代码生成最佳实践 |
| `tree-sitter` | C 代码大纲分析 |
| `universal-Ctags` | 代码索引与导航 |

## 配置文件说明

skill 会将所有 SVN 参数持久化到 `~/.svn_project_env`：

```bash
export SVN_USERNAME="username"
export SVN_PASSWORD_B64="base64_encoded_password"
export PROJECT_PLATFORM_SVN="http://10.153.120.80/cmwcode-open/V9R1/trunk"
export PROJECT_PLATFORM_FOLDER_LIST='["ospf","nqa"]'
export PROJECT_PLATFORM_PATH="$HOME/project/platform"
export PROJECT_PUBLIC_SVN="http://10.153.120.104/cmwcode-public/V9R1/trunk"
export PROJECT_PUBLIC_FOLDER_LIST='["PUBLIC/include"]'
export PROJECT_PUBLIC_PATH="$HOME/project/public"
```

该文件由以下组件自动加载：
- `project-env`（被所有 bin 脚本 source：`svn-utils`、`checkout-list`、`abuild`、`build-job`）
- `.bashrc`（交互式终端会话）
