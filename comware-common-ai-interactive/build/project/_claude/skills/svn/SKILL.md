---
name: svn
description: Comware工作区中SVN版本控制的完整工作流指导，涵盖日常操作（update/diff/log/commit/revert/status/blame）、高级操作（merge/switch/cleanup/resolve）、以及工作区内置工具（checkout-list/shadow-branch/svn-utils）的使用方法。
---

# SVN 版本控制指导手册

## 概述

本skill为Comware开发工作区提供SVN（Subversion）版本控制的完整操作指南。工作区中已预装`subversion`客户端，并提供了一套封装脚本（`svn-utils`、`checkout-list`、`shadow-branch`）简化常用操作。

## 重要前置知识

### 认证机制

工作区的SVN认证信息存储在 `~/.svn_project_env` 配置文件中（由 `svn-checkout` skill 在首次使用时创建），格式如下：

- `SVN_USERNAME` — SVN用户名
- `SVN_PASSWORD_B64` — Base64编码的SVN密码（避免特殊字符被Shell误解析）

配置文件由 `project-env` 脚本自动加载，所有工作区脚本（`svn-utils`、`checkout-list`、`abuild`、`build-job`）在启动时均会自动读取该文件。交互式终端会话中，`.bashrc` 也会自动source此文件。

所有SVN操作**应通过`svn-utils`中封装的函数执行**，无需手动传递凭证。如需在bash中直接使用：

```bash
source svn-utils
svn_with_auth <svn子命令> [参数...]
```

> [!NOTE]
> 如果尚未执行初始配置（`~/.svn_project_env` 不存在），请先使用 `Skill(svn-checkout)` 完成项目检出设置。

### 编码约定

Comware代码仓库中的`.c`/`.h`文件使用**GBK编码**存储。工作区在checkout后会自动转换为UTF-8便于编辑，在提交前需转换回GBK。

- checkout后自动转UTF-8：由`checkout-list`中的`convert_checkout_to_utf8()`完成
- 提交前转回GBK：使用`/utf82gbk`命令
- 手动转UTF-8：使用`/gbk2utf8`命令
- 转换日志位于`/tmp/charset_converter/`目录

> [!NOTE]
> 操作SVN时应排除`.svn`目录，避免损坏工作副本的元数据。

### 工作区目录结构

| 环境变量 | 说明 |
|---|---|
| `PROJECT_PLATFORM_PATH` | 平台代码本地路径 |
| `PROJECT_PUBLIC_PATH` | 公共代码本地路径 |
| `PROJECT_PLATFORM_SVN` | 平台代码SVN远程URL |
| `PROJECT_PUBLIC_SVN` | 公共代码SVN远程URL |

## 快速开始

### 日常开发流程

1. **更新代码**：`svn update` 拉取最新修改
2. **查看状态**：`svn status` 检查本地变更
3. **查看差异**：`svn diff` 确认修改内容
4. **转换编码**：提交前执行 `/utf82gbk` 将UTF-8转回GBK
5. **提交代码**：`svn commit -m "提交说明"` 提交到仓库

### 使用内置工具提交编译

如果需要通过abuild编译验证（而非直接提交到主分支），使用shadow-branch流程：

1. 在本地修改代码
2. 执行 `shadow-branch <项目路径>` 自动创建影子分支并同步变更
3. 执行 `abuild` 触发Jenkins编译
4. 编译通过后，再直接提交到主分支

## Linux命令库

### 查看状态

```bash
# 查看工作副本状态（显示已修改、新增、删除的文件）
svn status
svn status "$PROJECT_PLATFORM_PATH"

# 状态符号说明：
#   M  - 已修改（Modified）
#   A  - 已添加（Added）
#   D  - 已删除（Deleted）
#   ?  - 未纳入版本控制（Unversioned）
#   !  - 文件丢失（Missing）
#   C  - 冲突（Conflicted）
#   X  - 外部引用（eXternal）

# 只查看特定目录
svn status path/to/dir
```

### 更新代码

```bash
# 更新工作副本到最新版本
svn update
svn update "$PROJECT_PLATFORM_PATH"

# 更新到指定版本
svn update -r 12345

# 更新单个文件
svn update path/to/file.c

# 使用svn-utils封装（自动带认证）
source svn-utils
svn_with_auth update "$PROJECT_PLATFORM_PATH"
```

### 查看差异

```bash
# 查看所有本地未提交的修改
svn diff

# 查看指定文件的修改
svn diff path/to/file.c

# 查看两个版本之间的差异
svn diff -r 12345:12346

# 查看工作副本与指定版本的差异
svn diff -r 12345 path/to/file.c

# 输出差异到文件（用于代码审查）
svn diff > changes.patch
```

### 查看提交历史

```bash
# 查看最近10条提交日志
svn log -l 10

# 查看指定文件的提交历史
svn log path/to/file.c

# 查看详细变更（含修改文件列表）
svn log -v -l 10

# 查看指定版本范围的日志
svn log -r 12340:12345

# 查看指定版本的详细信息
svn log -r 12345 -v
```

### 提交代码

```bash
# 提交所有变更
svn commit -m "修复XXX功能的YYY问题"

# 提交指定文件
svn commit -m "修改说明" path/to/file1.c path/to/file2.h

# 使用svn-utils封装
source svn-utils
svn_with_auth commit -m "修改说明" path/to/file.c
```

> [!NOTE]
> 提交前**必须**确保代码已转换回GBK编码（使用`/utf82gbk`命令），否则会导致编码混乱。

### 撤销修改

```bash
# 撤销指定文件的本地修改（恢复到仓库版本）
svn revert path/to/file.c

# 撤销目录下所有修改（递归）
svn revert -R path/to/dir

# 撤销所有本地修改
svn revert -R .
```

> [!NOTE]
> `svn revert`是**不可逆操作**，会丢弃所有未提交的本地修改。执行前务必确认。

### 文件管理

```bash
# 添加新文件到版本控制
svn add path/to/new_file.c

# 递归添加目录
svn add path/to/new_dir

# 强制添加（忽略已存在的条目）
svn add --force path/to/dir

# 删除文件（从版本控制和磁盘移除）
svn delete path/to/file.c

# 移动/重命名文件（保留版本历史）
svn move path/to/old_name.c path/to/new_name.c

# 复制文件（保留版本历史）
svn copy path/to/source.c path/to/dest.c
```

### 查看文件信息

```bash
# 查看工作副本信息（URL、版本号等）
svn info
svn info "$PROJECT_PLATFORM_PATH"

# 查看远程URL的信息
source svn-utils
svn_with_auth info "$PROJECT_PLATFORM_SVN"

# 查看文件的逐行作者信息（blame/annotate）
svn blame path/to/file.c

# 查看指定版本范围的blame
svn blame -r 12300:HEAD path/to/file.c

# 查看远程文件内容（无需checkout）
source svn-utils
svn_with_auth cat "$PROJECT_PLATFORM_SVN/path/to/file.c"

# 查看指定版本的文件内容
svn_with_auth cat -r 12345 "$PROJECT_PLATFORM_SVN/path/to/file.c"

# 列出远程目录内容
source svn-utils
svn_with_auth list "$PROJECT_PLATFORM_SVN/path/to/dir"
svn_with_auth list -R "$PROJECT_PLATFORM_SVN/path/to/dir"  # 递归列出
```

### 冲突解决

```bash
# 查看冲突文件（状态为C的文件）
svn status | grep "^C"

# 手动解决冲突后标记为已解决
svn resolve --accept working path/to/file.c

# 接受仓库版本（放弃本地修改）
svn resolve --accept theirs-full path/to/file.c

# 接受本地版本（覆盖仓库修改）
svn resolve --accept mine-full path/to/file.c

# 交互式解决冲突
svn resolve --accept postpone path/to/file.c
# 然后手动编辑文件，移除冲突标记（<<<<<<<, =======, >>>>>>>）
# 编辑完成后：
svn resolve --accept working path/to/file.c
```

### 分支操作

```bash
# 查看当前分支URL
svn info | grep "^URL:"

# 切换工作副本到其他分支
source svn-utils
svn_with_auth switch <目标分支URL> "$PROJECT_PLATFORM_PATH"

# 从其他分支合并修改到当前工作副本
source svn-utils
svn_with_auth merge <源分支URL> "$PROJECT_PLATFORM_PATH"

# 合并指定版本范围
svn_with_auth merge -r 12340:12345 <源分支URL> "$PROJECT_PLATFORM_PATH"

# 回滚某个版本的修改（反向合并）
svn_with_auth merge -r 12345:12344 <分支URL> "$PROJECT_PLATFORM_PATH"
```

### 工作副本维护

```bash
# 清理锁定的工作副本（修复"locked"错误）
svn cleanup

# 深度清理（包括处理中断的操作）
svn cleanup --remove-unversioned

# 查看属性
svn proplist path/to/file
svn propget svn:keywords path/to/file

# 设置属性
svn propset svn:keywords "Id Rev Date" path/to/file
```

## 内置工具使用指南

### svn-utils — 认证封装库

`svn-utils`是所有其他SVN脚本的基础，提供自动认证封装。

```bash
# 在脚本中引用
source svn-utils

# 执行任意SVN命令（自动附加认证参数）
svn_with_auth <svn子命令> [参数...]

# 智能静默模式（输出类命令保留输出，其他命令静默执行）
svn_s <svn子命令> [参数...]
# 保留输出的命令：cat, diff, info, update
# 静默执行的命令：add, delete, commit, copy 等

# 删除远程分支
svn_remove_branch <远程分支URL>
```

### checkout-list — 初始代码检出

`checkout-list`用于工作区首次启动时的代码检出，支持稀疏检出（仅检出指定文件夹）。

```bash
# 检出平台代码（通常由工作区启动脚本自动执行）
checkout-list platform

# 检出公共代码
checkout-list public

# 查看帮助
checkout-list --help
```

> [!NOTE]
> `checkout-list`在检出完成后会自动将`.c`/`.h`文件从GBK转换为UTF-8编码。
> 转换日志保存在`/tmp/charset_converter/`目录下。

### shadow-branch — 影子分支管理

`shadow-branch`用于在不直接提交到主分支的情况下，将本地修改同步到一个临时的"影子分支"。主要用于`abuild`编译流程。

```bash
# 同步本地修改到影子分支（有修改时自动创建）
shadow-branch "$PROJECT_PLATFORM_PATH"

# 强制创建影子分支（即使没有修改）
shadow-branch -f "$PROJECT_PLATFORM_PATH"

# 保留现有影子分支（不重新创建）
shadow-branch -k "$PROJECT_PLATFORM_PATH"

# 删除影子分支
shadow-branch -r "$PROJECT_PLATFORM_PATH"

# 查看帮助
shadow-branch --help
```

**影子分支的工作流程：**

1. 检测当前分支URL和本地修改
2. 根据分支类型计算影子分支URL
3. 删除旧的影子分支（如果存在）
4. 从当前分支`svn copy`创建新的影子分支
5. 将本地的新增/删除/修改文件应用到影子分支
6. 提交到影子分支

## 常见问题与解决方案

### 工作副本被锁定

```
svn: E155004: Working copy 'xxx' locked
```

**解决方法：**
```bash
svn cleanup
# 如果仍然失败
svn cleanup --remove-unversioned
```

### 更新时遇到冲突

```
C    path/to/file.c
```

**解决方法：**
1. 查看冲突内容：`svn diff path/to/file.c`
2. 手动编辑文件解决冲突
3. 标记已解决：`svn resolve --accept working path/to/file.c`
4. 继续工作或提交

### 误删文件恢复

```bash
# 如果文件已从版本控制删除但未提交
svn revert path/to/file.c

# 如果需要从历史版本恢复
svn copy -r <版本号> <仓库URL>/path/to/file.c path/to/file.c
```

### 查看某文件在特定版本的内容

```bash
svn cat -r <版本号> path/to/file.c
# 或从远程URL
source svn-utils
svn_with_auth cat -r <版本号> "$PROJECT_PLATFORM_SVN/path/to/file.c"
```

## 注意

1. 本工作区运行在Linux环境中，所有SVN命令均为Linux版本
2. 提交代码前**必须**确保编码已转换回GBK格式（使用`/utf82gbk`命令）
3. 执行`svn revert`前务必确认，该操作不可恢复
4. 不要手动修改或删除`.svn`目录，否则会破坏工作副本
5. 工作区的SVN认证信息存储在 `~/.svn_project_env` 配置文件中，由 `project-env` 脚本自动加载到各工作区脚本。如需修改认证信息，可直接编辑该文件或重新运行 `Skill(svn-checkout)`
6. 使用`shadow-branch`时，影子分支名称包含工作区服务名（`CODER_SERVICE_NAME`），每个工作区独立
7. 如需在脚本中使用SVN命令，务必通过`source svn-utils`引入认证封装
