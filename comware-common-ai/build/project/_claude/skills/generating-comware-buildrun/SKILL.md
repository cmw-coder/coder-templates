---
name: generating-comware-buildrun
description: 生成Comware网络操作系统的BuildRun代码，包括开发新的BuildRun插件、理解现有BuildRun代码、调试BuildRun相关问题、代码审查和优化的Comware规范化实现。
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
metadata:
   author: comware-dev-team
   version: "0.1"
compatibility: 适用于Comware网络操作系统开发环境
---

# generating-comware-BuildRun

为Comware开发人员提供全面的BuildRun代码生成的要点和参考模板。模板包含了从简单到复杂的各种情况，可以作为AI助手开发BuildRun代码的参考。

## Instruction
1. 阅读全文内容，理解BuildRun的概念和开发要点
2. 每一个要点先根据用户输入的信息，尝试从项目代码中找到相关内容
3. 根据代码中搜寻的结果，与用户通过交互式询问确认所有要点内容正确
4. 之后根据用户要求，生成代码或审查、优化代码等
5. 所有需澄清的内容，都需要与用户交互式确认。

## BuildRun 是什么？

- 根据当前配置DBM库生成命令字符串
- 是获取当前配置的一种手段：
  - `display this`：显示当前命令视图下的 BuildRun
  - `display current-configuration`：显示整机所有 BuildRun

###  BuildRun 从哪里来？

- BuildRun 是根据 **DBM 配置库** 生成的，通常是生效配置库
- 有些基于接口视图的BuildRun在接口是临时口状态时使用未生效配置库

生成过程（通过主控板 dbmd 进程）：

1. 收到“收集 BuildRun”的请求
2. 获取当前命令模板、命令模式
3. 模板分类处理（如 system 模板）
4. 调用某业务模板的 BuildRun 回调函数
5. 打开主控板业务 DBM 生效或未生效配置库
6. 根据当前模板、模式遍历 DBM 配置生效或未生效库
7. 输出配置 BuildRun 字符串

### 重要的参考文件

- comware/bdr.h, 描述了BuildRun的API接口函数
- comware/dbm.h, 描述了BuildRun使用的DB数据如何保存和读取

## BuildRun要点总结和开发模板

### 要点
1. 命令行形式与BuildRun一一对应

- BuildRun本质是将DBM中的二进制配置转换为命令行字符串
- 每个命令行视图对应一个或多个BuildRun回调函数
- 通过CLI_RegBuildRun或CLI_RegBatchBuildRun函数注册命令模板与回调函数的映射关系
- 使用CLI_AppendBuildRunInfo()或CLI_AppendBuildRunInfoEx()函数输出命令行

模板示例：
```C
STATIC ULONG example_BuildRun(IN const CHAR *pcCmdMode, OUT VOID *pBuildRunBuf)
{
    ULONG ulRet = ERROR_SUCCESS;

    /* 检查配置是否存在或是否为默认值 */
    if (是默认配置)
    {
        /* 输出默认配置（undo命令） */
        ulRet = CLI_AppendBuildRunInfoEx(CLI_BDR_DEF, pBuildRunBuf, " undo command-name\r\n");
    }
    else
    {
        /* 输出实际配置 */
        ulRet = CLI_AppendBuildRunInfo(pBuildRunBuf, " command-name parameter1 parameter2\r\n");
    }

    return ulRet;
}
```

2. DBM数据结构与命令行对应关系

- DBM支持多种数据结构类型：BSTRING、FIFO、ARRAY、SORTLIST、AVLLIST
- 每个配置项在DBM中有对应的数据结构定义
- 数据结构通常定义在模块的*_dbm.h文件中
- Key-Value结构：Key标识配置类型，Value存储配置数据

模板示例：
```C
/* 在dbm头文件中定义 */
#define MODULE_DBMKEY_EXAMPLE "example_key"
typedef struct tagMODULE_EXAMPLE_S
{
    UINT uiParam1;
    UINT uiParam2;
    CHAR szName[32];
} MODULE_EXAMPLE_S;

/* 在BuildRun函数中使用 */
STATIC ULONG example_BuildRun(IN const CHAR *pcCmdMode, OUT VOID *pBuildRunBuf)
{
    MODULE_EXAMPLE_S stExample;
    ULONG ulRet = ERROR_SUCCESS;

    memset(&stExample, 0, sizeof(stExample));

    /* 从DBM获取配置 */
    ulRet = MODULE_DBM_GetCfgBinary(MODULE_DBMKEY_EXAMPLE,
                                    sizeof(MODULE_EXAMPLE_S),
                                    &stExample);

    if (ERROR_SUCCESS == ulRet)
    {
        /* 转换为命令行 */
        ulRet = CLI_AppendBuildRunInfo(pBuildRunBuf,
                                       " example %u %u name %s\r\n",
                                       stExample.uiParam1,
                                       stExample.uiParam2,
                                       stExample.szName);
    }

    return ulRet;
}
```

3. DBM Handle选择：生效库 vs 未生效库

- 可使用DBM_OpenCfgDB同时打开生效库和未生效库
- 生效库（Used Configuration DB）：当前生效的配置
- 未生效库（Unused Configuration DB）：用户配置但未生效的配置
- BuildRun通常读取生效库（DBM_MODE_READ模式），但根据上下文可能访问未生效库，比如接口视图下的命令，接口是临时口的时候需要从未生效库获取

模板示例：
```C
STATIC HDBINSTANCE open_used_db(VOID)
{
    ULONG ulRet;
    DBM_DB_ATTRIBUTE_S stDbmAttr;
    HDBINSTANCE hHandle;

    memset(&stDbmAttr, 0, sizeof(DBM_DB_ATTRIBUTE_S));
    stDbmAttr.uiPersistFlag = DBM_PERSIST_FLAG_CFG;
    stDbmAttr.enBackupFlag = DBM_NEED_BACKUP;
    stDbmAttr.uiHashSize = MODULE_DBM_HASHSIZE;

    /* 打开生效配置数据库 */
    ulRet = DBM_Open((UCHAR *)MODULE_USEDCONFIG_DBNAME,
                     (UCHAR *)MODULE_FEATURE_NAME,
                     DBM_MODE_READ,  /* 只读模式 */
                     &stDbmAttr,
                     &hHandle);

    if (ERROR_SUCCESS != ulRet)
    {
        hHandle = DBM_INVALID_HDBINSTANCE;
    }

    return hHandle;
}
```

4. 从DBM库中获取数据结构

- 使用DBM_GetBinary()获取简单配置
- 使用DBM_GetArray()或DBM_GetArrayRange()获取数组配置
- 使用DBM_GetSortList()或DBM_GetNextSortList()获取排序列表

模板示例：
```C
STATIC ULONG get_config_from_dbm(IN HDBINSTANCE hHandle)
{
    INT32 iDataLen;
    MODULE_CONFIG_S stConfig;
    ULONG ulIterator = 0;
    DBM_KEY_S stKey;

    /* 方法1: 获取单个二进制配置 */
    iDataLen = DBM_GetBinary(hHandle,
                            (UCHAR *)MODULE_DBMKEY_CONFIG,
                            strlen(MODULE_DBMKEY_CONFIG),
                            0UL,
                            sizeof(MODULE_CONFIG_S),
                            &stConfig);

    /* 方法2: 遍历所有Key */
    while (DBM_GetKeys(hHandle, 1, &ulIterator, &stKey) == ERROR_SUCCESS)
    {
        /* 处理每个Key */
        // ...
    }
    DBM_FreeIterator(ulIterator);

    /* 方法3: 获取排序列表 */
    while (DBM_GetNextSortList(hHandle,
                              (UCHAR *)MODULE_DBMKEY_LIST,
                              strlen(MODULE_DBMKEY_LIST),
                              &ulIterator,
                              NULL,
                              NULL,
                              sizeof(MODULE_ITEM_S),
                              &stItem) > 0)
    {
        /* 处理每个列表项 */
        // ...
    }
    DBM_FreeIterator(ulIterator);

    return ERROR_SUCCESS;
}
```

5. DBM数据结构的字节序处理

- DBM中数据以网络字节序（大端）存储
- 读取后需要转换为主机字节序
- 使用ntohs(), ntohl(), htons(), htonl()函数

模板示例：
```C
STATIC VOID convert_dbm_data(INOUT MODULE_CONFIG_S *pstConfig)
{
    /* 网络序转主机序 */
    pstConfig->uiParam1 = ntohl(pstConfig->uiParam1);
    pstConfig->uiParam2 = ntohs(pstConfig->uiParam2);

    /* 字符串不需要转换 */
    // pstConfig->szName 保持不变
}

STATIC VOID prepare_dbm_data(INOUT MODULE_CONFIG_S *pstConfig)
{
    /* 主机序转网络序 */
    pstConfig->uiParam1 = htonl(pstConfig->uiParam1);
    pstConfig->uiParam2 = htons(pstConfig->uiParam2);
}
```

6. 默认值处理

- 如果配置不存在或为默认值，输出undo命令或指定的默认值
- 使用CLI_AppendBuildRunInfoEx(CLI_BDR_DEF, ...)输出默认配置
- 等价于CLI_AppendBuildRunInfoEx, 通过检查BDR_IsShowDefaultCfg()函数返回值，判断是否需要输出默认值
- 需要知道每个参数的默认值
- 默认值一般通过宏定义或初始定制文件读取

模板示例：
```C
STATIC ULONG handle_default_values(IN const CHAR *pcCmdMode, OUT VOID *pBuildRunBuf)
{
    MODULE_CONFIG_S stConfig;
    ULONG ulRet = ERROR_SUCCESS;

    memset(&stConfig, 0, sizeof(stConfig));

    ulRet = MODULE_DBM_GetCfgBinary(MODULE_DBMKEY_CONFIG,
                                    sizeof(MODULE_CONFIG_S),
                                    &stConfig);

    if ((ERROR_SUCCESS != ulRet) ||
        (stConfig.uiParam1 == MODULE_DEFAULT_PARAM1) ||
        (stConfig.uiParam2 == MODULE_DEFAULT_PARAM2))
    {
        /* 输出默认配置（undo命令） */
        ulRet = CLI_AppendBuildRunInfoEx(CLI_BDR_DEF, pBuildRunBuf,
                                         "undo module-config\r\n");
    }
    else
    {
        /* 输出实际配置 */
        ulRet = CLI_AppendBuildRunInfo(pBuildRunBuf,
                                       "module-config param1 %u param2 %u\r\n",
                                       stConfig.uiParam1, stConfig.uiParam2);
    }

    return ulRet;
}

STATIC ULONG handle_default_values2(IN const CHAR *pcCmdMode, OUT VOID *pBuildRunBuf)
{
    MODULE_CONFIG_S stConfig;
    ULONG ulRet = ERROR_SUCCESS;

    memset(&stConfig, 0, sizeof(stConfig));

    ulRet = MODULE_DBM_GetCfgBinary(MODULE_DBMKEY_CONFIG,
                                    sizeof(MODULE_CONFIG_S),
                                    &stConfig);
    if ((ERROR_SUCCESS != ulRet) ||
        (stConfig.uiParam1 == MODULE_DEFAULT_PARAM1) ||
        (stConfig.uiParam2 == MODULE_DEFAULT_PARAM2))
    {
        if (BOOL_TRUE == BDR_IsShowDefaultCfg())
        {
          (VOID)CLI_AppendBuildRunInfo(pBuildRunBuf, "undo module-config\r\n");
        }
    }
}

```

7. 完整的BuildRun模块模板
```C
/*****************************************************************************
Copyright (c) 2010, Hangzhou H3C Technologies Co., Ltd. All rights reserved.
-------------------------------------------------------------------------------
                            module_bdr.c
Project Code: Comware V7
 Module Name: MODULE
Date Created: 2010-6-16
      Author: author
 Description: BuildRun processing for module

-------------------------------------------------------------------------------
Modification History
DATE        NAME             DESCRIPTION
--------------------------------------------------------------------------
*****************************************************************************/
#ifdef __cplusplus
  extern "C"{
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#include <sys/basetype.h>
#include <sys/error.h>
#include <sys/assert.h>
#include <arpa/inet.h>
#include <vector.h>
#include <list.h>
#include <lipc.h>
#include <cliapi.h>
#include <bdr.h>
#include <dbm.h>
#include <tlv.h>

#include "../include/module.h"
#include "../include/module_dbm.h"

/* 全局选项配置 */
STATIC OPT_OPTION_S g_astModuleBdrOptions[] =
{
    {"Option1", OPTION_BOOL, &g_bOption1, sizeof(BOOL_T)},
    {0,0,0,0}
};

/*****************************************************************************
  Func Name: module_BuildRun_example
Date Created: YYYY/MM/DD
     Author: author
Description: Example BuildRun function
      Input: pcCmdMode  命令模式
     Output: pBuildRunBuf  BuildRun缓冲区
     Return: ERROR_SUCCESS 成功
             ERROR_FAILED  失败
    Caution:
-------------------------------------------------------------------------------
Modification History
DATE        NAME             DESCRIPTION
--------------------------------------------------------------------------
*****************************************************************************/
STATIC ULONG module_BuildRun_example(IN const CHAR *pcCmdMode, OUT VOID *pBuildRunBuf)
{
    MODULE_CONFIG_S stConfig;
    ULONG ulRet = ERROR_SUCCESS;

    IGNORE_PARAM(pcCmdMode);
    DBGASSERT(NULL != pBuildRunBuf);

    memset(&stConfig, 0, sizeof(stConfig));

    /* 从DBM获取配置 */
    ulRet = MODULE_DBM_GetCfgBinary(MODULE_DBMKEY_CONFIG,
                                    sizeof(MODULE_CONFIG_S),
                                    &stConfig);

    /* 字节序转换（如果需要） */
    MODULE_DbmConvertN2H(&stConfig);

    /* 检查是否为默认配置 */
    if ((ERROR_SUCCESS != ulRet) ||
        (MODULE_DEFAULT_VALUE == stConfig.uiParam))
    {
        /* 默认配置：输出undo命令 */
        ulRet = CLI_AppendBuildRunInfoEx(CLI_BDR_DEF, pBuildRunBuf,
                                         " undo module command\r\n");
    }
    else
    {
        /* 实际配置：输出配置命令 */
        CHAR szCmdName[CLI_LINE_LENGTH + 1];
        szCmdName[0] = '\0';

        /* 转换字符串格式（如果需要） */
        ulRet = CLI_ConvertToCmdStrEx(stConfig.szName,
                                      sizeof(szCmdName),
                                      szCmdName);
        if (ERROR_SUCCESS == ulRet)
        {
            ulRet = CLI_AppendBuildRunInfo(pBuildRunBuf,
                                           " module command %s value %u\r\n",
                                           szCmdName, stConfig.uiParam);
        }
    }

    return ulRet;
}

/*****************************************************************************
  Func Name: module_BuildRun_complex
Date Created: YYYY/MM/DD
     Author: author
Description: Complex BuildRun with DBM iteration
      Input: pcCmdMode  命令模式
     Output: pBuildRunBuf  BuildRun缓冲区
     Return: ERROR_SUCCESS 成功
             ERROR_FAILED  失败
    Caution:
-------------------------------------------------------------------------------
Modification History
DATE        NAME             DESCRIPTION
--------------------------------------------------------------------------
*****************************************************************************/
STATIC ULONG module_BuildRun_complex(IN const CHAR *pcCmdMode, OUT VOID *pBuildRunBuf)
{
    HDBINSTANCE hHandle;
    MODULE_ITEM_S stItem;
    ULONG ulIterator = 0;
    ULONG ulRet = ERROR_SUCCESS;
    CHAR szBdrStr[CLI_LINE_LENGTH + 1];

    IGNORE_PARAM(pcCmdMode);

    /* 打开DBM数据库 */
    hHandle = MODULE_OpenUsedDB(DBM_MODE_READ);
    if (DBM_INVALID_HDBINSTANCE == hHandle)
    {
        return ERROR_SUCCESS;
    }

    /* 遍历排序列表 */
    while (DBM_GetNextSortList(hHandle,
                              (UCHAR *)MODULE_DBMKEY_ITEM_LIST,
                              strlen(MODULE_DBMKEY_ITEM_LIST),
                              &ulIterator,
                              NULL,
                              NULL,
                              sizeof(MODULE_ITEM_S),
                              &stItem) > 0)
    {
        /* 字节序转换 */
        MODULE_DbmConvertN2H(&stItem);

        /* 构建命令行字符串 */
        szBdrStr[0] = '\0';
        snprintf(szBdrStr, sizeof(szBdrStr),
                 " module item %s id %u\r\n",
                 stItem.szItemName, stItem.uiItemId);

        /* 添加到BuildRun缓冲区 */
        ulRet |= CLI_AppendBuildRunInfo(pBuildRunBuf, "%s", szBdrStr);
    }

    DBM_FreeIterator(ulIterator);
    MODULE_CloseDB(hHandle);

    return ulRet;
}

/*****************************************************************************
  Func Name: module_main_BuildRun
Date Created: YYYY/MM/DD
     Author: author
Description: Main BuildRun function that calls other BuildRun functions
      Input: pcCmdMode  命令模式
     Output: pBuildRunBuf  BuildRun缓冲区
     Return: ERROR_SUCCESS 成功
             ERROR_FAILED  失败
    Caution:
-------------------------------------------------------------------------------
Modification History
DATE        NAME             DESCRIPTION
--------------------------------------------------------------------------
*****************************************************************************/
STATIC ULONG module_main_BuildRun(IN const CHAR *pcCmdMode, OUT VOID *pBuildRunBuf)
{
    ULONG ulErrCode = ERROR_SUCCESS;

    /* 调用各个BuildRun函数 */
    ulErrCode |= module_BuildRun_example(pcCmdMode, pBuildRunBuf);
    ulErrCode |= module_BuildRun_complex(pcCmdMode, pBuildRunBuf);

    /* 根据选项决定是否调用其他BuildRun */
    if (BOOL_TRUE == g_bOption1)
    {
        ulErrCode |= module_BuildRun_option1(pcCmdMode, pBuildRunBuf);
    }

    if (ERROR_SUCCESS != ulErrCode)
    {
        ulErrCode = ERROR_FAILED;
    }

    return ulErrCode;
}

/*****************************************************************************
  Func Name: MODULE_ParseOptAgrc
Date Created: YYYY-MM-DD
    Author : author
Description: 解析定制参数
      Input: 无
     Output: 无
     Return: None
    Caution:
-------------------------------------------------------------------------------
Modification History
DATE        NAME             DESCRIPTION
-------------------------------------------------------------------------------
******************************************************************************/
VOID MODULE_ParseOptAgrc(VOID)
{
    INT iAgrc = 0;
    CHAR **ppcArgv = NULL;

    /* 获取定制参数 */
    ppcArgv = BDR_GetOpt(&iAgrc);
    if (NULL != ppcArgv)
    {
        (VOID)OPT_ParseEx(iAgrc, ppcArgv,
                         g_astModuleBdrOptions,
                         sizeof(g_astModuleBdrOptions)/sizeof(OPT_OPTION_S));
    }

    return;
}

/*****************************************************************************
  Func Name: module_reg_BuildRun
Date Created: YYYY-MM-DD
     Author: author
Description: BuildRun注册函数
      Input: 无
     Output: 无
     Return: 无
    Caution:
-------------------------------------------------------------------------------
Modification History
DATE        NAME             DESCRIPTION
-------------------------------------------------------------------------------
******************************************************************************/
STATIC ULONG module_reg_BuildRun(VOID)
{
    ULONG ulRet = ERROR_SUCCESS;

    /* 初始化定制参数 */
    MODULE_ParseOptAgrc();

    /* 注册BuildRun回调函数 */
    ulRet |= CLI_RegBuildRun(CLI_TEMPLET_SYSTEM,        /* 系统模板 */
                            CLI_BuildRunTYPE_CALLBACK, /* 回调类型 */
                            module_main_BuildRun,      /* 回调函数 */
                            NULL,                      /* 回调数据 */
                            MODULE_BuildRun_LEVEL);    /* 优先级 */

    /* 注册子模板（如果需要） */
    ulRet |= CLI_RegBuildRun(CLI_TEMPLET_SYSTEM,
                            CLI_BuildRunTYPE_SUBTEMPLET,
                            NULL,
                            CLI_TEMPLET_MODULE_SUB,
                            MODULE_BuildRun_SUB_LEVEL);

    return ulRet;
}

/*****************************************************************************
  Func Name: MODULE_InitBdrInfo
Date Created: YYYY-MM-DD
     Author: author
Description: BuildRun插件初始化入口
      Input: 无
     Output: 无
     Return: none
    Caution:
-------------------------------------------------------------------------------
Modification History
DATE        NAME             DESCRIPTION
-------------------------------------------------------------------------------
******************************************************************************/
STATIC VOID MODULE_CONSTRUCT MODULE_InitBdrInfo(VOID)
{
    BDR_OPSET_S stModuleBdrIntf;

    memset(&stModuleBdrIntf, 0, sizeof(BDR_OPSET_S));

    /* 设置插件名称 */
    strlcpy(stModuleBdrIntf.szPlugName,
            (CHAR *)MODULE_FEATURE_NAME,
            sizeof(stModuleBdrIntf.szPlugName));

    /* 注册BuildRun信息收集函数 */
    stModuleBdrIntf.pfRegBuildRun = module_reg_BuildRun;

    /* 注册命令模板函数（如果需要） */
    stModuleBdrIntf.pfRegTemplet = NULL; /* 或注册模板函数 */

    /* 注册到BuildRun系统 */
    (VOID)BDR_RegOpSet(&stModuleBdrIntf);

    return;
}

#ifdef __cplusplus
}
#endif /* end of __cplusplus */
```

8. 关键注意事项

  1. 错误处理：所有DBM操作都需要检查返回值
  2. 内存管理：使用DBM_FreeIterator()释放迭代器
  3. 资源清理：使用DBM_Close()关闭数据库句柄
  4. 线程安全：BuildRun可能在多线程环境下执行
  5. 性能考虑：避免在BuildRun中进行复杂的计算或阻塞操作
  6. 字符串处理：使用CLI_ConvertToCmdStrEx()处理命令行字符串转义

9. BuildRun执行流程总结

  1. CLI收集BuildRun请求
  2. 调用DBM_PrepareBuildRun()准备
  3. 各模块的BuildRun回调函数被调用
  4. 回调函数从DBM读取配置并生成命令行字符串
  5. 使用CLI_AppendBuildRunInfo()或CLI_AppendBuildRunInfoEx()输出
  6. 调用DBM_ExecuteBuildRun()执行
  7. 配置持久化到文件

### **总结**

通过分析dbm.h和多个BuildRun代码文件，总结了以下关键要点和模板：

**核心要点**

1. BuildRun本质：将DBM中的二进制配置转换为命令行字符串
2. DBM结构：Key-Value存储，支持多种数据类型（BSTRING、ARRAY、SORTLIST等）
3. 数据库选择：使用生效配置库（Used Configuration DB）
4. 字节序处理：DBM使用网络字节序，需要转换
5. 默认值处理：配置不存在或为默认值时输出undo命令

**开发模板要点**

1. 基本结构：每个BuildRun函数遵循(IN const CHAR *pcCmdMode, OUT VOID *pBuildRunBuf)格式
2. DBM操作：打开→读取→转换→关闭的标准流程
3. 命令行输出：使用CLI_AppendBuildRunInfo()或CLI_AppendBuildRunInfoEx()系列函数
4. 错误处理：检查所有DBM操作的返回值
5. 资源管理：及时释放迭代器和关闭数据库句柄
