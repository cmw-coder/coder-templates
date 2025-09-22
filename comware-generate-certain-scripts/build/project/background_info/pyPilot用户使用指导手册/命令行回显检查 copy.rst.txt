.. _topics-命令行回显检查:


命令行回显检查
================
命令行回显检查是非常重要的检查手段，其实现方法多种多样，为了简化脚本开发复杂度、提升脚本可读性，框架提供CheckCommand方法对回显信息进行检查。


CheckCommand
---------------

CheckCommand方法支持对命令行回显或debug信息进行检查，其功能如下：

- 支持同时检查多个字段，各字段可以期望存在或不存在，各字段可以是与、或关系
- 支持指定在回显信息中检查范围

先看两个示例，了解CheckCommand方法：

1. 观察如下回显信息

::

    <Sysname>display interface Ethernet0/1
    Ethernet0/1 current state: UP
    Line protocol current state: UP
    Description: Ethernet0/1 Interface
    The Maximum Transmit Unit is 1500
    Internet Address is 11.91.255.79/24 Primary
    IP Packet Frame Type: PKTFMT_ETHNT_2,  Hardware Address: 5866-ba85-59cf
    IPv6 Packet Frame Type: PKTFMT_ETHNT_2,  Hardware Address: 5866-ba85-59cf

- 期望 ``Line protocol current state: UP`` 和 ``Internet Address is 11.91.255.79/24`` 同时存在（忽略各字符间的空格差异），代码如下：

.. code-block:: python
    :linenos:

    gl.DUT.CheckCommand('检查端口信息，预期链路状态UP，IP地址正确', cmd=f'display interface Ethernet0/1', 
                    expect=['Line protocol current state: UP', 'Internet Address is 11.91.255.79/24'], 
                    is_strict=False, relationship='and', stop_max_attempt=3, wait_fixed=2)
                    


2. 观察如下debug信息

::

    <H3C>
    # --------------------------------------- #
    <H3C>*Jan 17 21:01:26:328 2013 H3C IPFW/7/IPFW_PACKET: 
    Receiving, interface = Vlan-interface100, version = 4, headlen = 20, tos = 0,
    pktlen = 110, pktid = 1, offset = 0, ttl = 64, protocol = 0,
    checksum = 34880, s = 13.38.108.1, d = 13.38.108.2
    channelID = 0, vpn-InstanceIn = 0, vpn-InstanceOut = 0.
    prompt: Receiving IP packet.

    *Jan 17 21:01:26:328 2013 H3C IPFW/7/IPFW_PACKET: 
    Delivering, interface = Vlan-interface100, version = 4, headlen = 20, tos = 0,
    pktlen = 110, pktid = 1, offset = 0, ttl = 64, protocol = 0,
    checksum = 34880, s = 13.38.108.1, d = 13.38.108.2
    channelID = 0, vpn-InstanceIn = 0, vpn-InstanceOut = 0.
    prompt: IP packet is delivering up.


- 期望debug信息中包含ipv4报文信息：version、源/目的ip，并且其值正确

.. code-block:: python
    :linenos:
    :emphasize-lines: 1

    gl.RT.CheckCommand('检查debug信息是否包含ipv4相关信息', cmd=gl.RT.get_buffer,
                             expect=['version = 4', f's = {gl.TM.PORT1.ip}', f'd = {gl.RT.PORT1.ip}'],
                             stop_max_attempt=3, wait_fixed=5)


``CheckCommand`` 方法支持的参数如下：
  - ``desc``: 检查的描述信息，位置参数，类型为字符串
  - ``cmd`` ：下发的命令行，必选参数，支持字符串类型或get_buffer方法，为字符串时代表要下发的命令行，get_buffer方法为获取缓冲区内容
  - ``timeout``：等待回显的最大时间，单位为秒，可选参数，整型，默认值为15秒。只有当回显时间特别长时，才需要设置。当cmd为get_buffer方法时不生效
  - ``expect、not_expect`` ：期望存在（不存在）的信息，可选参数，支持字符串、正则表达式编译对象、只包含字符串类型元素的元组或包含这3类元素的的列表
  - ``expect_count`` ：期望存在的信息出现的次数，可选参数，整型，默认为1，对expect中的所有元素生效，不支持对expect其中一个元素设置expect_count
  - ``is_strict`` ：对字符串检查生效，可选参数，默认False，表示忽略期望信息中各字符间的空格，True代表按期望信息进行检查
  - ``relationship`` ：代表期望存在（不存在）的信息的关系，可选参数，支持and/or，默认为and，表示期望的信息都存在，OR表示期望的信息存在任意一个都可以
  - ``starts、ends`` ：分别为检查范围开始和结束标识，可选参数，字符串类型，默认检查范围为全部回显信息，否则为回显信息中第一次找到starts和第一次找到ends之间的回显信息
  - ``stop_max_attempt`` ：最大检查次数，如果检查结果正确则提前跳出，默认为1
  - ``wait_fixed`` ：检查两次检查的间隔时间，单位为秒， 默认为0
  - ``failed_assist`` ：检查失败后的辅助信息打印，可选参数，字符串或列表类型，当检查结果为失败后会作为命令行下发给设备并记录回显，当检查结果正确则不做任何处理

-------------
通用检查示例
-------------

观察如下回显信息

::

    <Sysname>display ospf 1 lsdb network
    
            OSPF Process 1 with Router ID 192.168.1.1
                    Link State Database
    
                            Area: 0.0.0.0
    
        Type      : Network
        LS ID     : 192.168.0.2
        Adv Rtr   : 192.168.2.1
        LS age    : 922
        Len       : 32
        Options   :  E
        Seq#      : 80000003
        Checksum  : 0x8d1b
        Net mask  : 255.255.255.0
        Attached router    192.168.1.1
        Attached router    192.168.2.1

                            Area: 0.0.0.1
    
        Type      : Network
        LS ID     : 192.168.1.2
        Adv Rtr   : 192.168.1.2
        LS age    : 782
        Len       : 32
        Options   :  NP
        Seq#      : 80000003
        Checksum  : 0x2a77
        Net mask  : 255.255.255.0
        Attached router    192.168.1.1
        Attached router    192.168.1.2

检查

- 期望 ``Area: 0.0.0.0`` 和 ``LS ID:192.168.0.2`` 都存在，期望 ``Area: 0.0.0.1`` 和 ``LS ID:192.168.1.2`` 都不存在，忽略各字符间的空格差异


.. code-block:: python
    :linenos:
    
    gl.DUT.CheckCommand('检查ospf lsdb信息，期望ls id正确', cmd=f'display ospf 1 lsdb network', 
                    expect=['Area: 0.0.0.0', f'LS ID:192.168.0.2'], 
                    not_expect=['Area: 0.0.0.1', f'LS ID:192.168.1.2'], 
                    stop_max_attempt=3, wait_fixed=2)


- 期望 ``LS ID:192.168.0.2`` 信息属于Area：0.0.0.0，而不属于Area: 0.0.0.1，这类情况使用正则表达式解决

.. code-block:: python
    :linenos:

    pattern = re.compile(r'Area: 0.0.0.0(?!Area:).*LS ID\s+: 192.168.0.2', re.S)
    gl.DUT.CheckCommand('期望LS ID:192.168.0.2信息在Area：0.0.0.0里', cmd=f'display ospf 1 lsdb network', 
                    expect=pattern, 
                    stop_max_attempt=3, wait_fixed=2)

.. note:: 使用正则表达式时，CheckCommand直接使用compile对象进行search操作，不会添加额外处理（如忽略大小写），所以需要用户保证compile对象的完整性

---------------
行信息检查示例
---------------
观察如下回显信息

::

    <Sysname> display ip routing-table fast-reroute
    
    Destinations : 2        Routes : 2
    
    Destination/Mask   Proto   Pre Cost        NextHop         Interface
    3.3.3.3/32         Static  60  0           1.1.1.2         Vlan11
    4.4.4.4/32         Static  60  0           1.1.1.2         Vlan11

检查

- 期望目的地址为3.3.3.3/32的下一跳为1.1.1.2，期望不存在目的地址为4.4.4.4/32的路由条目，这类情况使用元组，检查规则为同一行内包含元组所有元素，并且元组各元素可以不连续

.. code-block:: python
    :linenos:
    
    gl.DUT.CheckCommand('期望目的地址为3.3.3.3/32的下一跳为1.1.1.2，期望不存在目的地址为4.4.4.4/32的路由条目', 
                    cmd=f'display ip routing-table fast-reroute', 
                    expect=[('3.3.3.3/32', '1.1.1.2')], 
                    not_expect=[('4.4.4.4/32',)],
                    stop_max_attempt=3, wait_fixed=2 )

----------------
指定检查范围示例
----------------
观察如下回显信息

::

    <Sysname>display interface Eth0/1
    Ethernet0/1 current state: UP
    Line protocol current state: UP
    Description: Ethernet0/1 Interface
    The Maximum Transmit Unit is 1500
    Internet Address is 11.91.255.79/24 Primary
    IP Packet Frame Type: PKTFMT_ETHNT_2,  Hardware Address: 5866-ba85-59cf
    IPv6 Packet Frame Type: PKTFMT_ETHNT_2,  Hardware Address: 5866-ba85-59cf
    Media type is twisted pair, loopback not set, promiscuous mode not set
    100Mb/s, Full-duplex, link type is autonegotiation
    Output flow-control is disabled, input flow-control is disabled
    Output queue : (Urgent queuing : Size/Length/Discards)  0/100/0
    Output queue : (Protocol queuing : Size/Length/Discards)  0/500/0
    Output queue : (FIFO queuing : Size/Length/Discards)  0/75/0
    Last clearing of counters: 19:35:46  Sat 02/04/2023
        Last 300 seconds input rate 0.00 bytes/sec, 0 bits/sec, 0.00 packets/sec
        Last 300 seconds output rate 0.00 bytes/sec, 0 bits/sec, 0.00 packets/sec
        Input: 126 packets, 1793 bytes, 26 buffers
            100 broadcasts, 26 multicasts, 0 pauses
            0 errors, 0 runts, 0 giants
            0 crc, 0 align errors, 0 overruns
            0 dribbles, 0 drops, 0 no buffers
        Output:92 packets, 6959 bytes, 92 buffers
            0 broadcasts, 0 multicasts, 0 pauses
            0 errors, 0 underruns, 0 collisions
            0 deferred, 0 lost carriers

检查

- 期望Input中broadcasts报文数量为100，使用字符串检查，配合指定查找范围

.. code-block:: python
    :linenos:

    gl.DUT.CheckCommand('期望Input中broadcasts报文数量为100', cmd=f'display interface Ethernet 0/1', 
                    expect=['100 broadcasts'], 
                    starts='Input:', ends='Output:', 
                    stop_max_attempt=3, wait_fixed=2 )


CheckPing
-------------
CheckPing方法用于进行ping操作，并检查通过率，支持大于等于、小于等于关系的检查。

``CheckPing`` 方法支持的参数如下：
  - ``desc``: 检查的描述信息，位置参数，类型为字符串
  - ``dst_address`` ：目的地址，字符串类型，必选参数，如 138.1.1.1
  - ``src_address``：源地址，字符串类型，如 10.1.1.1
  - ``count`` ：ping的次数，整型int，默认为5
  - ``size`` ：数据包的大小，整型int
  - ``waitmiliseconds`` ：等待时间，整型int
  - ``ttl`` ：最大ttl值，整型int
  - ``vrf_name`` ：vrf名称，字符串类型，如 vrf_general
  - ``pass_rate`` ：预期通过率，整型int，介于0 - 100，代表百分比，如80代表通过率为80%


.. code-block:: python
    :linenos:

    # 通过率设置错误，超过范围，执行后报出错误
    gl.DUT_1.CheckPing('预计可以ping通', gl.RT.PORT3.ip, pass_rate=120, stop_max_attempt=12, wait_fixed=3)

    # 设置ping次数，并且通过率不低于80，就算检查通过
    gl.DUT_1.CheckPing('预计可以ping通', gl.RT.PORT3.ip, count=10, pass_rate=80)

    # 设置ping使用的源地址
    gl.DUT_1.CheckPing('预计可以ping通', gl.RT.PORT3.ip, src_address=gl.DUT_1.PORT1.ip, pass_rate=100)

    # 预期ping不通
    gl.DUT_1.CheckPing('预计ping不通', gl.RT.PORT3.ip, pass_rate=0, stop_max_attempt=2, wait_fixed=3)


补充
-----
上述方法是设备类对象下的方法，只能对单台设备的单条命令行的回显进行检查，其它场景（如检查不同设备间命令行回显关系）的命令行检查，需要用户在 ``atf_assert`` 中实现检查逻辑，使用规则见：
:doc:`../用户指导手册/定制检查` 