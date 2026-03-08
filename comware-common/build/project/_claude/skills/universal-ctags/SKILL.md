---
name: universal-ctags
description: 当前skill，通过ctags软件，负责c、cpp、h、hpp文件相关的各种操作，例如获取c文件内所有函数声明，获取h文件内所有结构体&联合体&枚举。
---

# Universal Ctags指导手册

## 概述
当前skill，通过ctags软件，负责c\cpp\h\hpp文件相关的各种操作，比如获取c文件大纲视图（即所有函数声明的列表），获取h文件内所有结构体&联合体&枚举。

## 背景知识
1. ctags对c语言支持的元素类型
```
输入：
ctags --list-kinds=c
输出：
d  macro definitions
e  enumerators (values inside an enumeration)
f  function definitions
g  enumeration names
h  included header files
l  local variables [off]
m  struct, and union members
p  function prototypes [off]
s  structure names
t  typedefs
u  union names
v  variable definitions
x  external and forward variable declarations [off]
z  function parameters inside function or prototype definitions [off]
L  goto labels [off]
D  parameters inside macro definitions [off]
```
2. ctags软件help信息节选
```
输入：
ctags --help
输出：
Usage: ctags [options] [file(s)]

Input/Output Options
  --exclude=<pattern>
       Exclude files and directories matching <pattern>.
       See also --exclude-exception option.
  --exclude-exception=<pattern>
      Don't exclude files and directories matching <pattern> even if
      they match the pattern specified with --exclude option.
  省略...
Output Format Options
  --format=(1|2)
       Force output of specified tag file format [2].
  --output-format=(u-ctags|e-ctags|etags|xref|json)
      Specify the output format. [u-ctags]
  省略...
Language Selection and Mapping Options
  省略...
Tags File Contents Options
  省略...
Option File Options
  省略...
optlib Options
  省略...
Language Specific Options
  省略...
Listing Options
  省略...
Miscellaneous Options
  省略...
```

## CLI Libraries
### Basic Operations
#### 在C工程中搜索信息
```
# ubuntu的命令行界面/windows的cmd窗口
1. 建立C工程的索引，生成tags文件
ctags --language-force-c -R /path/to/your/c-project
2. 使用字符搜索命令，在tags文件中搜索信息
# ubuntu的命令行界面
grep "dns_domain_AddList" tags
# windows的cmd窗口
findstr "dns_domain_AddList" tags
```
```示例输出结果
dns_domain_AddList      dns/app/dns_domain.c    /^STATIC VOID dns_domain_AddList (IN DNS_DOMAIN_INFO_S * pstDomainInfo,$/;"     f       typeref:typename:STATIC VOID
dns_domain_AddListForXml        dns/app/dns_domain.c    /^STATIC VOID dns_domain_AddListForXml (IN DNS_DOMAIN_INFO_S * pstDomainInfo,$/;"       f       typeref:typename:STATIC VOID
```
### c - Basic Operations
#### 获取结构视图/大纲视图(即c文件内所有函数声明的列表)
```
# ubuntu的命令行界面/windows的cmd窗口
ctags -x --kinds-c=f /path/to/your/file.c
```
```示例输出结果
DNS_Ambiguous_FillSingleSrvGrp function   5283 dns/app/dns_ambiguous.c ULONG DNS_Ambiguous_FillSingleSrvGrp(IN USHORT usServerGroupId,
DNS_Ambiguous_Init function   5378 dns/app/dns_ambiguous.c ULONG DNS_Ambiguous_Init(VOID)
dns_Ambiguous_SrvGrpVpnEvent function    681 dns/app/dns_ambiguous.c VOID dns_Ambiguous_SrvGrpVpnEvent(IN UINT uiEvent, IN VRF_INDEX vrfIndex, IN CHAR *pcVpnName)
```
### h - Basic Operations
#### 获取结构体&联合体&枚举的列表(即h文件内所有数据结构)
```
# ubuntu的命令行界面/windows的cmd窗口
ctags -x --kinds-c=gsu /path/to/your/file.h
```
```示例输出结果
tagDNSDomainRuleShow struct       43 dns/app/dns_domain.h typedef struct tagDNSDomainRuleShow
tagDNS_DOMAIN    union       33 dns/app/dns_domain.h typedef struct tagDNS_DOMAIN
tagDNS_DOMAINMsg struct       54 dns/app/dns_domain.h ISSU typedef struct tagDNS_DOMAINMsg
```