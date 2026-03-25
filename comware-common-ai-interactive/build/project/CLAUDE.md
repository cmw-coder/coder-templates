# SVN Project Checkout
- 首次使用工作区时，MUST使用 `Skill(svn-checkout)` 完成SVN项目配置和代码检出
- 该skill会通过对话方式收集SVN凭证、分支路径、检出目录等参数
- 配置信息持久化到 `~/.svn_project_env`，后续所有脚本（checkout-list、abuild、build-job、svn-utils）自动加载
- 再次调用时，如果代码已检出，skill会进入维护模式（查看状态、更新、提交等）

# abuild
- abuild命令，直接在 /home/xx/project 目录下，bash窗口键入‘abuild -e 64sim9cen -uko’命令即可
- 详细请查阅，skill=abuild
- MUST,每次插入代码后，询问用户是否执行abuild编译，查看是否有语法错误，用户确认后MUST执行abuild
- 建议执行Abuild之前，再转换为gbk格式

# Comware AI代码生成总则
**需要开发人员澄清的内容，必须澄清**
**在用户要求范围内做最小化生成，不要做额外的工作**
**每一次代码生成都有反思**
