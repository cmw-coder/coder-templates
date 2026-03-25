---
name: tree-sitter-c
description: 当前skill，通过python的tree-sitter-c包，负责c、cpp、h、hpp文件相关的各种操作，例如获取c文件内所有函数声明，获取h文件内所有结构体&联合体&枚举。
---

# tree-sitter-c指导手册

## 概述
当前skill，通过tree-sitter-c包，负责c\cpp\h\hpp文件相关的各种操作，比如获取c文件大纲视图（即所有函数声明的列表），获取h文件内所有结构体&联合体&枚举。

## Quick Start

## Python Libraries
### c - Basic Operations
#### 获取结构视图/大纲视图(即c文件内所有函数声明的列表)
```
python get_c_outline.py /path/to/your/file.c
```
> [!NOTE]
> 注意，get_c_outline.py 位于当前文件的同级目录scripts中，即‘./scripts/get_c_outline.py’.
```示例输出结果：
# 文件路径: D:/Downloads/test/example.c
# 文件大小: 95709 字节
# 结构视图/大纲视图:
# 格式: 开始行号:结束行号 函数定义
   140:   167 STATIC UINT32 iecmrp_kdata_CalcCrc32(IN const UCHAR *pucBuffer, IN UINT uiByteNum)
   185:   194 BOOL_T IECMRP_kdata_IsValidDomainId(IN USHORT usDomainId, IN USHORT usDomainNum)
...
  2649:  2662 ULONG IECMRP_RegMdc(VOID)
  2674:  2684 VOID IECMRP_DeregMdc(VOID)
```
### h - Basic Operations
#### 获取结构体|联合体|枚举列表
```
python get_h_data_struct.py /path/to/your/file.h
```
> [!NOTE]
> 注意，get_h_data_struct.py 位于当前文件的同级目录scripts中，即‘./scripts/get_h_data_struct.py’.
```示例输出结果：
# 文件路径: D:/Downloads/test/example.h
# 文件大小: 7697 字节
# 结构体|联合体|枚举的列表如下:
# 格式: 开始行号:结束行号 结构体|联合体|枚举的定义
    27:    31 typedef enum tagIECMRPK_TimerType
    34:    42 typedef struct tagIECMRPK_PortCb
...
    66:    78 typedef struct tagIECMRPK_InterDomainCb
    81:    89 typedef struct tagIECMRP_MdcCb
```
