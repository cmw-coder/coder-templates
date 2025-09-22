.. _topics-NETCONF测试:


NETCONF测试
================
NETCONF是基于XML格式的网络管理协议，与被测设备的交互是通过发送/接收XML格式的信息完成。

框架提供了over ssh和over soap两种交互方式，由 ``gl.DUT.new_netconf`` 方法建立与netconf server(即被测设备)的连接，返回netconf client对象（如连接失败则返回None），后续操作均基于该对象的方法。另外该对象会自动赋值给 ``gl.DUT.netconf``。


new_netconf支持的参数如下：
  - ``host``: netconf server的地址，必选参数，字符串类型，支持Ipv4/Ipv6地址
  - ``port`` ：netconf server的端口号，必选参数，整型类型
  - ``user`` ：netconf server的登录用户名，必选参数，字符串类型
  - ``pwd`` ：netconf server的登录密码，必选参数，字符串类型
  - ``over`` ：netconf server的类型，必选参数，字符串类型，只支持ssh/soap，大小写敏感


示例如下

.. code-block:: python
    :linenos:

    # 创建基于 ssh 的 netconf client并进行连接
    object = gl.DUT.new_netconf(host='100.1.1.1', port=830, user='netconf_user', pwd='123_abc_456!', over='ssh')

    # 创建基于 ssh 的 netconf client并进行连接，使用ipv6地址
    object = gl.DUT.new_netconf(host='22003:100::D', port=830, user='netconf_user', pwd='123_abc_456!', over='ssh')

    # 创建基于 soap 的 netconf client并进行连接
    object = gl.DUT.new_netconf(host='100.1.1.1', port=80, user='netconf_user', pwd='123_abc_456!', over='soap')

    # 创建基于 soap 的 netconf client并进行连接，使用ipv6地址
    object = gl.DUT.new_netconf(host='22003:100::D', port=80, user='netconf_user', pwd='123_abc_456!', over='soap')

    # 创建 netconf client并进行连接，不使用默认的端口
    object = gl.DUT.new_netconf(host='100.1.1.1', port=880, user='netconf_user', pwd='123_abc_456!', over='ssh')
    object = gl.DUT.new_netconf(host='22003:100::D', port=8080, user='netconf_user', pwd='123_abc_456!', over='soap')
    

netconf client对象提供如下方法：
    - ``send`` ：完成与netconf server的交互，XML交互信息和手工测试工具Netconf Browser/Soap UI保持一致，over soap方式的认证信息由框架自动补充。
    - ``CheckNetconf`` ：用于检查netconf server的应答，是否符合预期。



----------------
send方法
----------------
send方法会自动处理应答xml，获取内容层xml信息，并保存到 ``gl.DUT.netconf.reply_xml`` 属性， 其返回值为删除名字空间的内容层xml信息。
当为get操作时，还会将应答信息由xml格式转化为字典格式，方便用户使用，字典格式的应答信息保存在 ``gl.DUT.netconf.reply_dict`` 属性。


示例如下（ **本示例基于S6520-16S-SI** ）

.. code-block:: python
    :linenos:

    # 创建netconf对象并连接
    object = gl.DUT.new_netconf(host='100.1.1.1', port=830, user='netconf_user', pwd='123_abc_456!', over='ssh')

    # 配置ospf 2，其route id为2.2.2.2
    req_xml = '''<edit-config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <target>
            <running/>
        </target>
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <OSPF xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="create">
                <Instances>
                    <Instance>
                        <Name>2</Name>
                        <RouterId>2.2.2.2</RouterId>
                    </Instance>
                </Instances>
            </OSPF>
        </config>
    </edit-config>
    '''

    # 下发配置
    object.send(req_xml)

    #打印应答xml，值为<ok/>
    print(object.reply_xml)


    # 删除ospf 2
    req_xml = '''<edit-config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <target>
            <running/>
        </target>
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <OSPF xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="delete">
                <Instances>
                    <Instance>
                        <Name>2</Name>
                    </Instance>
                </Instances>
            </OSPF>
        </config>
    </edit-config>
    '''

    # 下发配置
    object.send(req_xml)

    #打印应答xml，值为<ok/>
    print(object.reply_xml)


    # 获取端口的配置
    req_xml = '''<rpc message-id="100" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0">
    <get-config>
        <source>
            <running/>
        </source>
        <filter type="subtree">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <Ifmgr>
                <Interfaces>
                    <Interface/>
                    </Interfaces>
                </Ifmgr>
            </top>
        </filter>
    </get-config>
    </rpc>'''

    # 下发配置
    object.send(req_xml)

    #打印应答xml，值为端口配置的xml格式信息
    print(object.reply_xml)

    # 打印应答xml格式信息转化成的字典
    print(object.reply_dict)

    # netconf断开
    object.disconnect()


------------------
CheckNetconf方法
------------------
CheckNetconf用于下发netconf请求，并根据用户设置的参数，进行检查

``CheckNetconf`` 方法支持的参数如下：
  - ``desc``: 检查的描述信息，位置参数，类型为字符串
  - ``req_xml`` ：下发的netconf请求xml，必选参数，支持支持rpc层、内容层xml或soapui的请求xml
  - ``expect`` ：期望存在的信息，可选参数，支持包含字符串、元组的列表
  - ``expect_xml`` ：期望netconf的响应xml，可选参数，字符串类型，默认为空，支持支持rpc层、内容层xml或soapui的响应xml
  - ``expect_cli`` ：期望<cli>节点值，可选参数，字符串类型，默认为空，只有edit-config操作有效
  - ``ignore_value`` ：忽略节点值检查，只检查节点tag，，可选参数，默认False，仅对参数expect_xml有效
  - ``stop_max_attempt`` ：最大检查次数，如果检查结果正确则提前跳出，默认为1
  - ``wait_fixed`` ：检查两次检查的间隔时间，单位为秒， 默认为0


示例如下（ **本示例基于MSR56** ）

.. code-block:: python
    :linenos:

    # 创建netconf对象并连接
    object = gl.DUT.new_netconf(host='100.1.1.1', port=80, user='netconf_user', pwd='123_abc_456!', over='soap')

    req_xml = '''<get>
        <filter type="subtree">
        <top xmlns="http://www.h3c.com/netconf/data:1.0">
            <FileSystem>
            <RecycleBin>
                <RecycleBinFile>
                <Medium>slot1#cfa0:</Medium>
                </RecycleBinFile>
            </RecycleBin>
            </FileSystem>
        </top>
        </filter>
        </get>'''

    expect_xml = '''<data>
                    <top>
                        <FileSystem>
                            <RecycleBin>
                                <RecycleBinFile>
                                    <Medium>slot1#cfa0:</Medium>
                                    <TrashFiles>
                                        <FileName>testdir/2.cfg</FileName>
                                    </TrashFiles>
                                    <TrashFiles>
                                        <FileName>xxx.cfg</FileName>
                                    </TrashFiles>
                                    <TrashFiles>
                                        <FileName>tcl_sync.tcl</FileName>
                                    </TrashFiles>
                                    <TrashFiles>
                                        <FileName>file0</FileName>
                                    </TrashFiles>
                                </RecycleBinFile>
                            </RecycleBin>
                        </FileSystem>
                    </top>
                </data>'''

    object.CheckNetconf('检查netconf响应信息与期望xml相同，req_xml支持rpc层、内容层xml或soapui的请求xml', 
                            req_xml, expect_xml=expect_xml)
        
    object.CheckNetconf('检查netconf响应信息与期望xml相同，只检查节点，忽略节点值', 
                        req_xml, expect_xml=expect_xml, ignore_value=True)
    
    object.CheckNetconf('expect_xml和expect参数同时设置时，只有expect参数生效', 
                        req_xml, expect_xml=expect_xml, ignore_value=True, 
                        expect=['<FileName>2.cfg</FileName>', ('<FileName>',1)])
    
    object.CheckNetconf('expect参数类型为列表，其元素类型支持字符串和元组',
                        req_xml, expect=['<FileName>2.cfg</FileName>', ('<FileName>',4)])
    
    object.CheckNetconf('为字符串时，代表节点信息，通过冒号指定索引，从1开始，默认为1',
                        req_xml, expect=['<FileName>1.cfg</FileName>', '<FileName>2.cfg</FileName>:2'])
    
    object.CheckNetconf('为元组时，代表检查同tag的节点出现的次数，包含2个元素，第一个为标签名称(带<>)，第二个为预期出现次数',
                        req_xml, expect=[('<FileName>',4)])

    object.CheckNetconf('为元组时，也可以检查同tag的节点和同值出现的次数，包含2个元素，第一个为标签名称和值(<tag>value</tag>)，第二个为预期出现次数',
                        req_xml, expect=[('<FileName>1.cfg</FileName>',4)])
    
    object.CheckNetconf('Check类接口支持重试操作，检查成功时跳出。此示例表示最多重试3次，每次间隔5秒',
                        req_xml, expect=['<FileName>2.cfg</FileName>', ('<FileName>',4)],
                        stop_max_attempt=3, wait_fixed=5)

    req_xml = '''<edit-config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <target>
                <running/>
            </target>
            <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                <OSPF xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="create">
                    <Instances>
                        <Instance>
                            <Name>2</Name>
                            <RouterId>2.2.2.2</RouterId>
                        </Instance>
                    </Instances>
                </OSPF>
            </config>
        </edit-config>'''

    object.CheckNetconf('expect_cli参数类型为字符串，用于检查<cli>节点值，检查时忽略每条命令行前后的空格，但命令行顺序必须一致',
                        req_xml, expect_cli='ospf 2 router-id 2.2.2.2')

    # 断开netconf连接
    object.disconnect()
