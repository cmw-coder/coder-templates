---
name: abuild
description: 当前skill，通过调用现有的bash命令和py脚本，提交C语言工程的abuild任务，获取abuild编译结果(编译成功返回版本地址，编译失败返回编译错误(如语法错误等))，辅助代码调试与修复。
---

# abuild指导手册

## 概述
在大型C语言工程项目中，abuild系统用于将多个模块代码统一编译，生成可部署或测试的产品版本。编译成功时会返回版本路径，便于后续部署到物理设备或Simware虚拟设备进行功能测试；若编译失败，则提供详细的错误日志（如语法错误、字段不存在等），辅助代码调试与修复。

## 快速开始
### 如何通过abuild编译结果，修改错误代码
1. 在Linux的bash终端键入abuild命令，例如‘abuild -e 64sim7cen -uko’,一般而言编译sim版本很快
    - abuild命令会在Jenkins中创建编译任务
2. 编译完成返回类似以下的url，
    - http://10.153.3.174:8080/job/V9CodeXV2/17825/console
    - 如果该步，返回内容包含‘Job completed: SUCCESS’，可以提前停止
3. 将上面返回url，进行格式转换，并调用jenkins_text_fetcher.py获取编译结果，如下所示
    - python3 jenkins_text_fetcher.py job/V9CodeXV2/17825/consoleText
4. 根据编译结果字符串，对工程代码进行修改。 

## 注意
1. 确保当前工作区或OS为Linux系统，以下功能只支持Linux；
2. 确保系统可执行命令中有‘abuild’，可通过‘which abuild’来判断；

## Linux命令库
### 提交abuild编译任务
```bash
# 基本用法（必须指定 IPE 包名）
abuild -e <ipe_package_name>
# 示例：编译多个包，使用 release 模式
abuild -e 64sim9cen,64sim9dis -r
# 示例：覆盖自动检测的模块列表
abuild -e 64sim9cen --modules L2VPN,LSM
# 查看帮助
abuild --help
```
> **注意：** abuild命令会在 Jenkins 中创建编译任务。
> 编译完成后返回类似以下的URL:
> http://10.153.3.174:8080/job/V9CodeXV2/17825/console

## Python脚本库
### 基本操作
```bash
# 获取指定任务的控制台输出
python3 jenkins_text_fetcher.py job/<job-name>/lastBuild/consoleText

# 获取输出并保存到文件
python3 jenkins_text_fetcher.py job/<job-name>/lastBuild/consoleText output.txt

# 测试Jenkins连接
python3 jenkins_text_fetcher.py test_connection
```
> **注意：** jenkins_text_fetcher.py的输入参数，需要转换格式，从‘http://10.153.3.174:8080/job/V9CodeXV2/17825/console’
> 转换为‘job/V9CodeXV2/17825/consoleText’
>
> **注意：** jenkins_text_fetcher.py的输入http链接，是从abuild命令返回值中获取的，所以要先执行abuild命令，再执行jenkins_text_fetcher.py，
> 获取编译日志。


## 参考信息
### abuild参数手册
在文件 references/abuild_guide.txt 中详细阐述了 abuild命令的参数，如果有需要请参阅。



