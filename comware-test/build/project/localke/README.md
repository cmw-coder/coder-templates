# 本地KE库使用说明

## 目录结构

```
localke/
├── cmd/              # 命令参考库
│   └── cmd.txt       # 命令文件（格式: 命令 | 说明）
├── background/       # 测试背景库
│   └── conftest.py   # 测试背景配置文件
├── example/          # 测试示例库
│   └── *.py, *.md    # 测试示例脚本和文档
├── design/           # 设计参考库
│   └── *.md, *.txt   # 设计文档和规格说明
├── users/            # 用户级私有库
├── logs/             # 日志文件
└── README.md         # 本说明文件
```

## 添加自定义命令

1. 编辑 `cmd/cmd.txt` 文件
2. 按照格式添加命令：`命令 | 说明`
3. 保存文件
4. 系统会自动检索新添加的命令

### 示例

```bash
# 编辑命令库
vim ~/project/localke/cmd/cmd.txt

# 添加命令（格式: 命令 | 说明）
display ospf peer | 显示OSPF邻居信息
display bgp routing-table | 显示BGP路由表

# 保存后即可使用
```

## 添加测试背景

1. 将 `conftest.py` 文件放到 `background/` 目录
2. 系统会自动检索测试背景配置

## 添加测试示例

1. 将测试脚本（`.py`）或文档（`.md`）放到 `example/` 目录
2. 系统会自动检索测试示例

## 注意事项

- ✅ 文件编码必须为 UTF-8
- ✅ 命令格式必须正确（使用 `|` 分隔）
- ✅ 不要删除目录结构
- ✅ 可以创建子目录组织文件

## 检索顺序

1. **本地KE库**（优先）
   - 检索本地命令库、背景库、示例库
   - 快速、个性化

2. **后台KE库**（Fallback）
   - 如果本地KE库为空或检索失败
   - 自动使用后台KE库
   - 确保功能正常运行

## 用户隔离

- ✅ 每个用户的本地KE库完全独立
- ✅ 互不影响，互不干扰
- ✅ 支持个性化配置

### 示例

```
h16540用户: /home/h16540/project/localke/
s07262用户: /home/s07262/project/localke/
x05999用户: /home/x05999/project/localke/
```

## 当前用户信息

- **用户名**: h16540
- **本地KE库路径**: `/home/h16540/project/localke/`
- **创建时间**: 2026-04-01

## 故障排查

### 问题1: 检索不到本地命令

**解决方案**:
1. 检查命令格式是否正确（`命令 | 说明`）
2. 检查文件编码是否为UTF-8
3. 查看日志：`~/project/localke/logs/ke_manager.log`

### 问题2: 权限不足

**解决方案**:
```bash
# 检查目录权限
ls -la ~/project/localke/

# 修改权限（如果需要）
chmod -R 755 ~/project/localke/
```

## 更多信息

详细使用指南请参考：`MULTI_USER_GUIDE.md`
