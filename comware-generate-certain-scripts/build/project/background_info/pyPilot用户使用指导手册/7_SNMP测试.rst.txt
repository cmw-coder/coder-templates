.. _topics-SNMP测试:


SNMP测试
================
SNMP是Simple Network Management Protocol的简写，代表简单网络管理协议，用于网络设备的管理。SNMP系统由网络管理系统如下4部分组成：

- NMS（Network Management System）
- SNMP Agent
- 被管对象Management object
- 管理信息库MIB（Management Information Base）


框架提供了NMS的部分功能，包括 GET、GETNEXT、GETBULK、WALK、SET操作，以及接收trap、inform信息，并支持自动接收并回复v2c版本的inform信息，同步支持ipv6。

上述这些方法封装在 ``SnmpManager`` 类中，创建对象时提供如下参数：

- ``agent`` agent的ip地址, 必选参数
- ``local`` 本地地址, 必选参数
- ``version`` snmp版本，仅支持v1 v2c v3，默认v2c
- ``entity`` 团体名称（仅v1 v2c版本有效）
- ``user`` 用户名称（仅v3版本有效）
- ``auth`` 认证密钥，必须为8字节或8字节的倍数（仅v3版本有效）
- ``priv`` 加密密钥，必须为8字节或8字节的倍数（仅v3版本有效）
- ``authP`` 认证密钥算法，支持 md5 sha（仅v3版本有效）
- ``privP`` 加密密钥算法，支持 3des des56 aes（仅v3版本有效）
- ``timeout`` 每次请求的超时时间，默认1s。
- ``stop_max_attempt`` 重试次数，默认5次。
- ``snmpengineid`` 本地的engineid，接收和响应v3 inform报文必填
- ``securityengineid`` agent的engineid，接收v3 trap报文必填


用法如下（以下两个示例功能相同）

.. code-block:: python
    :linenos:
    :emphasize-lines: 2,5,11

    # 引入snmp库
    from AtfLibrary.product.snmp_agent import SnmpManager

    # 创建nms对象，其中agent地址为100.1.1.1，本地地址为100.1.1.2， snmp版本为v3，并添加授权
    nms = SnmpManager('100.1.1.1', '100.1.1.2', version='v3', user='usm_auth_des', auth='12345678', priv='12345678')

    # 获取agent的系统名称
    result = nms.Get(oid=('SNMPv2-MIB', 'sysName', 0))

    # 创建nms对象，其中agent地址为2003::100:1，本地地址为2003::100:2， snmp版本为v2c，团体名为public
    nms = SnmpManager('2003::100:1', '2003::100:2', version='v2c', entity='public')

    # 获取agent的系统名称
    result = nms.Get(oid=('SNMPv2-MIB', 'sysName', 0))


.. code-block:: python
    :linenos:
    :emphasize-lines: 2,5,8,11

    # 调用new_snmp方法实例化 SnmpManager 对象，使用设备属性 gl.DUT.nms 即可调用snmp方法。
    # 参数agent地址为100.1.1.1，本地地址为100.1.1.2， snmp版本为v3，并添加授权
    gl.DUT.new_snmp('100.1.1.1', '100.1.1.2', version='v3', user='usm_auth_des', auth='12345678', priv='12345678')

    # 获取agent的系统名称
    result = gl.DUT.nms.Get(oid=('SNMPv2-MIB', 'sysName', 0))

    # 创建nms对象，其中agent地址为2003::100:1，本地地址为2003::100:2， snmp版本为v2c，团体名为public
    gl.DUT.new_snmp('2003::100:1', '2003::100:2', version='v2c', entity='public')

    # 获取agent的系统名称
    result = gl.DUT.nms.Get(oid=('SNMPv2-MIB', 'sysName', 0))


框架提供的方法 ``Get`` ``Getnext`` ``Getbulk`` ``Walk`` ``Set``，分别对应GET、GETNEXT、GETBULK、WALK、SET操作，各方法的参数基本一致，含义如下：

- ``oid``: 节点值
       - 支持OID形式（'1.3.6.1.2.1.1.5.0'）和名称形式（('SNMPv2-MIB', 'sysName', 0)）。 **由于MIB库过于庞大，只有SNMPv2-MIB支持名称形式，其它库只支持OID形式**
       - 当操作为GET、GETNEXT、GETBULK、SET时，节点必须为叶子节点
       - 当操作为GET、SET时，支持一次传多个节点，此时需要传入列表数据类型，如 oid=['1.3.6.1.2.1.1.1.0', ('SNMPv2-MIB', 'sysName', 0)]，此时返回值也为列表，列表元素格式参见上面示例的result值
- ``newValue`` SET操作时，修改的值，支持整型、字符串、元组（值，类型），或包含这3种类型的列表，为列表时必须与传入的节点数量一致
- ``version`` snmp版本，仅支持v1 v2c v3
- ``entity`` 团体名称（仅v1 v2c版本有效）
- ``user`` 用户名称（仅v3版本有效）
- ``auth`` 认证密钥，必须为8字节或8字节的倍数（仅v3版本有效）
- ``priv`` 加密密钥，必须为8字节或8字节的倍数（仅v3版本有效）
- ``authP`` 认证密钥算法，支持 md5 sha（仅v3版本有效）
- ``privP`` 加密密钥算法，支持 3des des56 aes（仅v3版本有效）
- ``nonRepeaters`` 指定非重复的 OID 的个数。在 Bulk 操作中，一般先查询一次非重复 OID 列表， 然后再对剩余 OID 进行批量查询，nonRepeaters 参数指定第一次查询的 OID 数量，数量不宜过大。（仅getbulk操作有效）
- ``maxRepetitions`` 指定每个 OID 要获取的数据行数，默认值为 10。仅getbulk操作有效）
- ``maxCalls`` getbulk时最大回调数，默认为0。（仅getbulk操作有效）
- ``timeout`` 每次请求的超时时间，默认1s。
- ``stop_max_attempt`` 重试次数，默认5次。

.. note:: 各方法提供的部分参数与创建 ``SnmpManager`` 对象的参数名称相同，调用各方法时，对于同名参数，只有本次调用生效，不会改变 ``SnmpManager`` 对象的属性值


返回值说明：

- Get、Getnext、Getbulk、Walk、Set几个方法返回 ``SnmpResponse`` 的对象，属性如下：

  - ``errorIndication``  请求时的出错信息，如没有收到snmp response报文，一般情况为三层不通导致
  - ``errorStatus``  差错状态，如 noError, noSuchName, tooBig等
  - ``errorIndex``   差错索引，主要用于记录错误的位置
  - ``varBinds``  请求的返回值，类型为元组，包含(请求oid, 返回值, 返回值类型)，或者为以元组为子元素的列表。
  - ``oid value value_type`` 当返回值为元组时，依次赋值给这三个该属性


GET类使用场景

.. code-block:: python
    :linenos:


    # 创建nms对象，其中agent地址为100.1.1.1，本地地址为100.1.1.2， snmp版本为v2c
    gl.DUT.new_snmp('100.1.1.1', '100.1.1.2', version='v2c', entity='public')
    

    # 获取agent的系统名称，使用团体名称为public
    # 返回值 result 为 SnmpResponse 对象，其属性 varBinds 的值为元组 ('1.3.6.1.2.1.1.5.0', 'C-007073', 'OctetString')
    # 此时 oid value value_type 3个属性的值分别为'1.3.6.1.2.1.1.5.0'  'C-007073'  'OctetString'
    result = gl.DUT.nms.Get(oid=('SNMPv2-MIB', 'sysName', 0))
    print(f'varBinds:{result.varBinds}, oid:{result.oid}, value:{result.value}, value_type:{result.value_type}')

    # 获取系统描述和系统名称
    # 返回值 result 为 SnmpResponse 对象, 其属性 varBinds 的值为列表 [('1.3.6.1.2.1.1.1.0', 'H3C Comware 此处省略若干', 'OctetString'), 
    #                                                               ('1.3.6.1.2.1.1.5.0', 'C-007073', 'OctetString')]
    # 此时 oid value value_type 3个属性的值均为空字符串
    result = gl.DUT.nms.Get(oid=['1.3.6.1.2.1.1.1.0', ('SNMPv2-MIB', 'sysName', 0)], entity='public')
    print(f'varBinds:{result.varBinds}, oid:{result.oid}, value:{result.value}, value_type:{result.value_type}')


    # 获取端口的up/down状态，由于IF-MIB库不支持名称形式，只能写OID形式
    # 返回值 result 为 SnmpResponse 对象, 其属性 varBinds 的值为列表 ('1.3.6.1.2.1.2.2.1.7.2245', 2, 'Unsigned32')
    result = gl.DUT.nms.Get(oid='1.3.6.1.2.1.2.2.1.7.2245', entity='public')
    print(f'varBinds:{result.varBinds}, oid:{result.oid}, value:{result.value}, value_type:{result.value_type}')


    # 获取节点 1.3.6.1.2.1.1.4.0 下一个节点的信息，即get 1.3.6.1.2.1.1.5.0 节点
    # 返回值 result 为 SnmpResponse 对象, 其属性 varBinds 的值为元组 ('1.3.6.1.2.1.1.5.0', 'C-007073', 'OctetString')
    # 此时 oid value value_type 3个属性的值分别为'1.3.6.1.2.1.1.5.0'  'C-007073'  'OctetString'
    result = gl.DUT.nms.Getnext(oid='1.3.6.1.2.1.1.4.0')
    print(f'varBinds:{result.varBinds}, oid:{result.oid}, value:{result.value}, value_type:{result.value_type}')

    # 获取节点 1.3.6.1.2.1.1 下3个节点的信息
    # 返回值 result 为 SnmpResponse 对象, 其属性 varBinds 的值为列表 [('1.3.6.1.2.1.1.1.0', 'H3C Comware 'H3C Comware 此处省略若干', 'OctetString'), 
    #                                                               ('1.3.6.1.2.1.1.2.0', 'SNMPv2-SMI::enterprises.25506.1.766', 'ObjectIdentifier'), 
    #                                                               ('1.3.6.1.2.1.1.3.0', 762422231, 'Unsigned32')]
    # 此时 oid value value_type 3个属性的值均为空字符串
    result = gl.DUT.nms.Getbulk(oid=('SNMPv2-MIB', 'system'), maxRepetitions=3)
    print(f'varBinds:{result.varBinds}, oid:{result.oid}, value:{result.value}, value_type:{result.value_type}')

    # 获取节点时，会有多种差错信息，SnmpResponse 对象的 errorStatus 为差错信息，
    # 返回值 result 为 SnmpResponse 对象, 下面两次请求 errorStatus 的值为 noSuchName, tooBig
    # 此时 oid value value_type 3个属性的值均为空字符串, varBinds属性的值为 []
    result = gl.DUT.nms.Get(oid='1.3.6.1.2.1.1.1.0.2', entity='public')
    print(f'varBinds:{result.varBinds}, errorStatus:{result.errorStatus}')

    result = gl.DUT.nms.Get(oid=[('SNMPv2-MIB', 'system')]*70)
    print(f'varBinds:{result.varBinds}, errorStatus:{result.errorStatus}')


    # 遍历节点，如给定节点1.3.6.1.2.1.1，则会遍历1.3.6.1.2.1.1下面的所有子节点，而不会继续遍历节点1.3.6.1.2.1.2
    # 遍历时，也支持设置最大索引，如下两个示例，第一个共计遍历节点779个，第二个遍历节点111个
    # 遇到错误或差错时，会停止遍历操作，返回错误 errorIndication 或差错 errorStatus
    # 返回值 result 为 SnmpResponse 对象, 其属性 varBinds 的值为列表，包含遍历到的所有节点值，格式与上述相同
    result = gl.DUT.nms.Walk(oid='1.3.6.1.2.1.1')
    print(f'varBinds:{result.varBinds})

    result = gl.DUT.nms.Walk(oid='1.3.6.1.2.1.2', maxIndex=30)
    print(f'varBinds:{result.varBinds})


SET类使用场景

newValue参数数据类型说明：
    - 除如下4类，其它与MIB-Browser软件Set界面显示的 ``Syntax`` 相同：
        Octets: OctetString， OctetString_Hex: OctetString， IP address: IpAddress， OID: ObjectIdentifier， Bits: BitString
    - 整型，默认数据类型为 Integer32
    - 字符串，默认数据类型为 OctetString

.. code-block:: python
    :linenos:

    # 调用new_snmp方法实例化 SnmpManager 对象，使用设备属性 gl.DUT.nms 调用snmp方法。
    # 参数agent地址为100.1.1.1，本地地址为100.1.1.2， snmp版本为v2c
    gl.DUT.new_snmp('100.1.1.1', '100.1.1.2', version='v2c', entity='public')

    # 修改节点值时，需要增加 newValue参数
    # 返回值 result 为 SnmpResponse 对象, 其属性 varBinds 的值为修改后获取的该节点的值 ('1.3.6.1.2.1.1.5.0', 'H3C_A', 'OctetString')
    # 此时 oid value value_type 3个属性的值均为空字符串
    # 参数 newValue='H3C_A' 等同于 newValue=('H3C_A', 'OctetString')
    result = gl.DUT.nms.Set(oid=('SNMPv2-MIB', 'sysName', 0), newValue='H3C_A', entity='public')

    # 修改端口的up/down状态，由于IF-MIB库不支持名称形式，只能写OID形式
    # 返回值 result 为 SnmpResponse 对象, 其属性 varBinds 的值为列表 ('1.3.6.1.2.1.2.2.1.7.2245', 2, 'Unsigned32')
    # 参数 newValue=2 等同于 newValue=(2, 'Integer32')
    result = gl.DUT.nms.Set(oid='1.3.6.1.2.1.2.2.1.7.2245', newValue=(2, 'Integer32'), entity='public')
    print(f'varBinds:{result.varBinds}')

    # 支持同时修改多个节点，此时节点数与newValue的个数必须一致，否则不会修改任何节点
    # 返回值 result 为 SnmpResponse 对象, 其属性 varBinds 的值为修改后获取的该节点的值 [('1.3.6.1.2.1.2.2.1.7.2245', 1, 'Unsigned32'), 
    #                                                                               ('1.3.6.1.2.1.1.5.0', 'H3C_A', 'OctetString')]
    # 此时 oid value value_type 3个属性的值均为空字符串
    result = gl.DUT.nms.Set(oid=['1.3.6.1.2.1.2.2.1.7.2245', ('SNMPv2-MIB', 'sysName', 0)], newValue=[1, ('H3C_A', 'OctetString')])
    print(f'varBinds:{result.varBinds}')

    # 节点值需要为16进制的值时，在mib browser上为 # 0x78 0x01 0x01 0x02格式，需要指定值的类型为OctetString_Hex
    result = gl.DUT.nms.Set(oid='1.3.6.1.2.1.2.2.1.xx.xxx', newValue=('78010102', 'OctetString_Hex'))
    print(f'varBinds:{result.varBinds}')


框架提供了方法 ``StartCaptureTrap`` ``StopAndCheckCaptureTrap`` ``AnswerInform``, 用于捕获trap/inform、自动回复inform报文（只支持v1和v2c版本），其作用及参数介绍如下：

- StartCaptureTrap
    - ``version`` snmp版本，仅支持v1 v2c
    - ``entity`` 团体名称
    - ``trap`` trap类型，支持 coldStart warmStart linkDown linkUp authFailure egpNeighborLoss enterpriseSpecific七种
    - ``inform`` inform类型，支持 coldStart warmStart linkDown linkUp authFailure egpNeighborLoss enterpriseSpecific七种
    - ``timeout`` 超时时间，该时间需要大于用户操作的时间 **加上** trap报文发送的时间

- StopAndCheckCaptureTrap
    - 无参数
  
- AnswerInform
    - 无参数


接收trap/inform使用场景

.. code-block:: python
    :linenos:
    :emphasize-lines: 10,12

    # 引入snmp库
    from AtfLibrary.product.snmp_agent import SnmpManager

    # 创建nms对象，其中agent地址为100.1.1.1，本地地址为100.1.1.2， snmp版本为v2c
    nms = SnmpManager('100.1.1.1', '100.1.1.2', version='v2c', entity='public')

    # StartCaptureTrap 用于启动捕获v1 v2c版本的trap信息或inform信息
    # StopAndCheckCaptureTrap 两个等待捕获结束并检查是否捕获到预期的trap 或 inform信息
    # 返回值 result 为 True 或 False
    nms.StartCaptureTrap(trap='warmStart', version='v2c', timeout=50)
    print('do something...')
    result = nms.StopAndCheckCaptureTrap()
    print(result)



自动回复inform使用场景

.. code-block:: python
    :linenos:
    :emphasize-lines: 10,12

    # 引入snmp库
    from AtfLibrary.product.snmp_agent import SnmpManager

    # 创建nms对象，其中agent地址为100.1.1.1，本地地址为100.1.1.2， snmp版本为v2c
    nms = SnmpManager('100.1.1.1', '100.1.1.2', version='v2c', entity='public')

    # StartCaptureTrap 用于启动捕获v1 v2c版本的trap信息或inform信息
    # AnswerInform 自动回复接收到的inform信息
    # 返回值 result 为 True 或 False
    nms.StartCaptureTrap(inform='warmStart', timeout=50)
    print('do something...')
    result = nms.AnswerInform()
    print(result)



接收v3 trap使用场景

.. code-block:: python
    :linenos:
    :emphasize-lines: 5,7

    # 引入snmp库
    from AtfLibrary.product.snmp_agent import SnmpManager

    # 创建nms对象，其中agent地址为143.157.150.2，本地地址为143.157.150.1， snmp版本为v3
    nms = SnmpManager('143.157.150.2', '143.157.150.1', version='v3', user='RBACtest', auth='123456TESTauth&!', priv='123456TESTencr&!',authP="sha",privP="aes",securityengineid="800063a2800cda41c6923b00000001")

    result = nms.ReceiveV3Trap()
    print(result)



接收并响应v3 inform使用场景

.. code-block:: python
    :linenos:
    :emphasize-lines: 5,7

    # 引入snmp库
    from AtfLibrary.product.snmp_agent import SnmpManager

    # 创建nms对象，其中agent地址为143.157.150.2，本地地址为143.157.150.1， snmp版本为v3
    nms = SnmpManager('143.157.150.2', '143.157.150.1', version='v3', user='RBACtest', auth='123456TESTauth&!', priv='123456TESTencr&!',authP="sha",privP="aes",snmpengineid="800005230137620012")

    result = nms.ReceiveAndResponseInform()
    print(result)