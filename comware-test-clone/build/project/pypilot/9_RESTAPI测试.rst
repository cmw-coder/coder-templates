.. _topics-RESTAPI测试:


RESTAPI测试
================
Comware REST 是通过 REST over HTTP/HTTPs 访问设备，REST 报文放在HTTP 报文的正文中。HTTP 报文需要符
合HTTP 的报文格式要求，使用Comware REST功能需要先配置REST功能。

框架提供了 ``gl.DUT.new_restful_connection.send`` 方法完成交互，``gl.DUT.new_restful_connection.CheckRestful`` 方法完成返回值检查，REST连接和生命周期管理由框架自动管理。

--------------------------------
send方法
--------------------------------
``send`` 会主动建立rest会话，管理会话，用户不用自己建立会话，``send`` 主要用于发送rest请求，支持GET、POST、PUT、DELETE操作。


入参说明：

 - ``restapi``:  类型为元组的列表或单个元组，含义为下发api的集合，每个元组包含 一个api:uri（rest API）,action（操作类型）, payload（请求数据）。可以多api下发

 - ``timeout``:  类型为整型等待请求返回的最大时间，单位为秒，可选参数，整型，默认值为15s。一般不设置

返回值说明：

 - ``return_result``: 如果下发正常并且有返回数据，就是返回数据（json格式），如果下发正常但是没有返回数据，或者下发失败就是空json：{}，多api下发的时候返回值为最后一个api的返回值


	 1  如果命令下发成功并且有返回数据，则返回json格式数据(字典格式)

	 2  如果命令下发成功但没有返回数据，则返回空json：{}

	 3  如果命令下发失败，则返回空json：{}

示例如下：

.. code-block:: python
    :linenos:

    # 创建restapi对象
    rest_test = gl.DUT1.new_restful_connection(host = gl.DUT.PORT1.ip, user = 'restfuluser', pwd ='123456abc')

    # GET操作
    return_result = rest_test.send(restapi = ("/api/v1/Ifmgr/Interfaces?filter-condition=more%3AConfigDuplex%3D1%3BConfigSpeed%3D1&index=IfIndex%3D3&select-fields=Description","GET",''))

    # POST操作
    return_result = rest_test.send(restapi = ("/api/v1/action/VLAN/BatchVlans","POST",''))
    '''

    # PUT操作
    rest_payload ='''
    {
        "IfIndex":3,
        "Description": "Interface 3"
    }
    '''

    return_result = rest_test.send(restapi = ("/api/v1/Ifmgr/Interfaces?index=IfIndex%3D3","PUT",rest_payload))

    # DELETE操作
    return_result = rest_test.send(("/api/v1/Ifmgr/RailGroups","DELETE",''))

    # 多api下发
    return_result = rest_test.send([("/api/v1/Ifmgr/RailGroups","DELETE",''),
        ("/api/v1/Ifmgr/Interfaces?index=IfIndex%3D3","PUT",rest_payload),
        ("/api/v1/action/VLAN/BatchVlans","POST",''),
        ("/api/v1/Ifmgr/Interfaces?filter-condition=more%3AConfigDuplex%3D1%3BConfigSpeed%3D1&index=IfIndex%3D3&select-fields=Description","GET",''),
        ("/api/v1/action/VLAN/BatchVlans","POST",''),
    ])

    # 打印结果
    print(f"return_result:{return_result}  type:{type(return_result)}")

--------------------------------
CheckRestful方法
--------------------------------
``CheckRestful`` 支持对rest api返回值进行检查

基本用法与 ``CheckCommand`` 一致：继承了 ``CheckCommand`` 的检查方法（未支持表格检查，按行不连续字符串检查， 按分组检查），具体用法请参考6.1章节

针对Rest返回数据主要是json格式，``CheckRestful`` 在 ``CheckCommand`` 基础之上增加适合json数据的检查方式.

入参说明：
 - ``desc`` : 检查的描述信息，位置参数，类型为字符串
 - ``uri`` :rest API
 - ``action`` : 操作类型
 - ``payload`` : 请求数据
 - ``timeout`` ：等待请求返回的最大时间，单位为秒，可选参数，整型，目前默认值为15秒。只有当回显时间特别长时，才需要设置。
 - ``expect、not_expect`` ：期望存在（不存在）的信息，可选参数，支持字符串、正则表达式编译对象、只包含字符串类型元素的元组或包含这3类元素的的列表
 - ``expect_count`` ：期望存在的信息出现的次数，可选参数，整型，默认为1，对expect中的所有元素生效，不支持对expect其中一个元素设置expect_count
 - ``is_strict`` ：进行大小写检查，可选参数，默认False，对所有检查方式生效（正则表达式除外）
 - ``relationship`` ：代表期望存在（不存在）的信息的关系，可选参数，支持and/or，默认为and，表示期望的信息都存在，or表示期望的信息存在任意一个都可以
 - ``ignore_api_send_error`` ：忽略命令行下发是否失败，可选参数，布尔型，默认False，表示当命令行下发失败时，检查失败
 - ``stop_max_attempt`` ：最大检查次数，如果检查结果正确则提前跳出，默认为1
 - ``wait_fixed`` ：检查两次检查的间隔时间，单位为秒， 默认为0
 - ``failed_assist`` ：检查失败后的辅助信息打印，可选参数，字符串或列表类型，当检查结果为失败后会作为命令行下发给设备并记录回显，当检查结果正确则不做任何处理


示例如下（均为CheckRestful特有检查方式）


.. code-block:: python
    :linenos:

    # 1.单纯的状态码检查：如果只做状态码检查（只要求发送成功），请在expect里面填写'Not Content'即可
    rest_test.CheckRestful('状态码检查',
			uri = "/api/v1/Ifmgr/Interfaces?filter-condition=more%3AConfigDuplex%3D1%3BConfigSpeed%3D1&index=IfIndex%3D3&select-fields=Description", 
			action = "GET", 
			payload = '',
			expect=['Not Content'],
			timeout=15,
			stop_max_attempt=3, wait_fixed=5)
    # 2.json检查：
    # json检查采用的是JSON Path(语法)进行查询，具体语法可以参考：https://blog.csdn.net/diandianxiyu_geek/article/details/125751062
    # 书写形式为以 _json 开头的字符串，括号第一个值为JSON Path表达式，第二个为对应key的预期值

    # 2.1典型json-单层json：返回值举例如下：
        {"IfIndex":3,"Description":"Interface 3","ConfigSpeed":1,"ConfigDuplex":3}
    # CheckRestful写法如下：
    rest_test.CheckRestful('检查返回的单层json里面IfIndex键的值为3',
			uri = "/api/v1/Ifmgr/Interfaces?filter-condition=more%3AConfigDuplex%3D1%3BConfigSpeed%3D1&index=IfIndex%3D3&select-fields=Description", 
			action = "GET", 
			payload = '',
			expect=['_json($.IfIndex,3)'],
			timeout=15,
			stop_max_attempt=3, wait_fixed=5
	)

    # 2.2典型json-多层json：返回值举例如下：
        {
            "VlanInterface": {
               "Type": "1",
               "VlanList": "15",
               "VlanList1": 
               {
                "Type1": "1"
               }
            },
            "VlanInterface1": {
               "Type": "2",
               "VlanList": "11",
               "VlanList1": 
               {
                "Type1": 2
               }

            },
            "GroupMember": [
                {
                     "InterfaceName": "GigabitEthernet0/0/2",
                     "MemberIndex": 12
                },
                {
                     "InterfaceName": "GigabitEthernet0/0/4",
                     "MemberIndex": 20
                }
            ],
            "IfIndex":3
        }

        # expect如下：检查返回的多层json里面有VlanInterface.VlanList1.Type1的键（可能有多个）有1
        expect=['_json($.VlanInterface.VlanList1.Type1，1)'],

    # 2.3典型json-多层json并且嵌套列表：返回值举例如下：
        {
            "RailGroups":
                [
                    {
                        "RailGroup": [
                            {
                                "GroupName": "test",
                                "GroupIndex": 1,
                                "GroupMembers": [
                                    {
                                        "GroupMember": [
                                            {
                                                "InterfaceName": "GigabitEthernet0/0/1",
                                                "MemberIndex": 12
                                            },
                                            {
                                                "InterfaceName": "GigabitEthernet0/0/2",
                                                "MemberIndex": 13
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "GroupName": "test1",
                                "GroupIndex": 1,
                                "GroupMembers": [
                                    {
                                        "GroupMember": [
                                            {
                                                "InterfaceName": "GigabitEthernet0/0/2",
                                                "MemberIndex": 12
                                            },
                                            {
                                                "InterfaceName": "GigabitEthernet0/0/4",
                                                "MemberIndex": 20
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
        }
        # expect如下：
        # 这里采用的是过滤表达式，该表达式只能在GroupMember这层（判断的key上层）为列表的时候才能使用，使用过滤表达式后面的值填""就行，*代表检查列表的所有元素
          expect=['_json($.RailGroups[*].RailGroup[*].GroupMembers[*].GroupMember[?(@.InterfaceName =="GigabitEthernet0/0/1")],"")'],
        # 如果不采用过滤表达式，expect如下：
          expect=['_json($.RailGroups[*].RailGroup[*].GroupMembers[*].GroupMember[*].InterfaceName,"GigabitEthernet0/0/1")'],
        # 以上两种都是等价的

        # 过滤表达式范围检查举例：
          expect=['_json($.RailGroups[*].RailGroup[1].GroupMembers[*].GroupMember[?(@.MemberIndex<21 && @.MemberIndex>15)],""],


附录1：语法介绍

以如下json字符串进行语法介绍

.. code-block:: json

    {
        "store": {
            "book": [{
                    "category": "reference",
                    "author": "Nigel Rees",
                    "title": "Sayings of the Century",
                    "price": 8.95
                }, {
                    "category": "fiction",
                    "author": "Evelyn Waugh",
                    "title": "Sword of Honour",
                    "price": 12.99
                }, {
                    "category": "fiction",
                    "author": "Herman Melville",
                    "title": "Moby Dick",
                    "isbn": "0-553-21311-3",
                    "price": 8.99
                }
            ],
            "bicycle": {
                "color": "red",
                "price": 19.95
            }
        }
    }




.. list-table::
   :widths: 20 20 20
   :header-rows: 1

   * - jsonpath表达式
     - 含义
     - 查找结果
   * - $.store.book[*].author
     - 所有 book 的 author 节点
     - ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville']
   * - $..author
     - 所有 author 节点
     - ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville']
   * - $.store.*
     - store 下的所有节点，book 数组和 bicycle 节点
     - [[{'category': 'reference', 'author': 'Nigel Rees', 'title': 'Sayings of the Century', 'price': 8.95}, {'category': 'fiction', 'author': 'Evelyn Waugh', 'title': 'Sword of Honour', 'price': 12.99}, {'category': 'fiction', 'author': 'Herman Melville', 'title': 'Moby Dick', 'isbn': '0-553-21311-3', 'price': 8.99}], {'color': 'red', 'price': 19.95}]
   * - $.store..price
     - store 下的所有 price 节点
     - [8.95, 12.99, 8.99, 19.95]
   * - $..book[2]
     - 匹配第 2 个 book 节点
     - [{'category': 'fiction', 'author': 'Evelyn Waugh', 'title': 'Sword of Honour', 'price': 12.99}]
   * - $..book[?(@.isbn)]
     - 过滤含 isbn 字段的节点
     - [{'category': 'fiction', 'author': 'Herman Melville', 'title': 'Moby Dick', 'isbn': '0-553-21311-3', 'price': 8.99}]
   * - $..book[?(@.noexist)]
     - 找不到匹配项时返回False
     - False


以上能覆盖大部分的json返回值，如需更多的JSON Path表达式请看 https://blog.csdn.net/diandianxiyu_geek/article/details/125751062
