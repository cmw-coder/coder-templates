.. _topics-GRPC测试:


GRPC测试
================
我司的Telemetry技术采用gRPC协议将数据从设备推送给网管的采集器，设备支持Dial-in模式和Dial-out模式。

Dial-in模式：
 - 设备作为gRPC服务器，采集器作为gRPC客户端。由采集器主动向设备发起gRPC连接并订阅需要采集的数据信息。其支持GET、gNMI、CLI等3种操作。

Dial-out模式：
 - 设备作为gRPC客户端，采集器作为gRPC服务器。设备主动和采集器建立gRPC连接，将设备上配置的订阅数据推送给采集器。

框架提供了相关接口处理两种模块的信息交互。


.. list-table:: Dial-in方法说明
   :widths: 20 20 30 30
   :header-rows: 1

   * - 操作描述
     - 方法名称
     - 参数说明
     - 返回值说明
   * - gRPC dialin模式下登陆设备
     - grpc_dialin_Login
     - - host      必选参数，字符串类型，gRPC server的地址
       - port      必选参数，字符串类型，gRPC server的端口号
       - user      必选参数，字符串类型，登陆用户名
       - pwd       必选参数，字符串类型，登陆密码
     - 成功返回True，失败返回False
   * - gRPC dialin模式下登出设备
     - grpc_dialin_Logout
     - 无
     - 成功返回True，失败返回False
   * - gRPC dialin模式下向设备下发配置
     - grpc_dialin_CliConfig
     - - cmdline   必选参数，字符串类型，下发命令行
     - 成功返回True，失败返回False
   * - gRPC dialin模式下获取设备相关信息
     - grpc_dialin_DisplayCmdTextOutput
     - - cmdline   必选参数，字符串类型，下发命令行
     - 成功返回命令下发后的返回信息，失败返回False
   * - gRPC dialin模式下订阅事件流
     - grpc_dialin_SubscribeByStreamName
     - - stream_name   必选参数，字符串类型，流名称
     - 成功返回True，失败返回False
   * - gRPC dialin模式下获取事件结果
     - grpc_dialin_GetEventReport
     - 无
     - 成功返回事件报告对象，失败返回False
   * - gRPC dialin模式下检查事件报告
     - grpc_dialin_ChkSyslogReportInfo
     - - event_report_obj   必选参数，object对象，事件报告对象
       - stream_name        必选参数，字符串类型，流名称
     - 成功返回True，失败返回False


.. list-table:: Dial-out方法说明
   :widths: 20 20 30 30
   :header-rows: 1

   * - 操作描述
     - 方法名称
     - 参数说明
     - 返回值说明
   * - gRPC dialout模式下启动gRPC server
     - grpc_dialout_StartServer
     - - server_ip      必选参数，字符串类型，服务器地址
       - server_port    必选参数，字符串类型，服务器端口号
     - 成功返回True，失败返回False，设备推送的事件信息保存

       在CLocalHost.grpc_dialout_received_info_list变量里
   * - gRPC dialout模式下关闭gRPC server
     - grpc_dialout_StopServer
     - 无
     - 成功返回True，失败返回False


示例如下

.. code-block:: python
    :linenos:

    # DUT设备作为gRPC服务器，LocalHost启动采集器
    cmds = '''
        ctrl+zsystem-view
        grpc enable
        local-user test
        password simple 12345asdfg
        authorization-attribute user-role network-admin
        service-type https'''
    gl.DUT.send(cmds)

    # 采集器登录
    gl.PC.grpc_dialin_Login(host='192.168.1.1', port=50021, user='test', pwd='12345asdfg')

    # 查看设备arp表项
    arp_table = gl.PC.grpc_dialin_DisplayCmdTextOutput('display arp')
    print(arp_table)

    # 订阅Ifmgr流日志
    gl.PC.grpc_dialin_SubscribeByStreamName('Ifmgr')

    # 下发配置shutdown/undo shutdown vlan101接口，触发Ifmgr订阅事件，获取事件日志并检查
    reportobj = gl.PC.grpc_dialin_GetEventReport()
    cmds =  '''
        interface loopback 0
        shutdown
        undo shutdown
    '''
    gl.PC.grpc_dialin_CliConfig(cmds)
    gl.PC.grpc_dialin_ChkSyslogReportInfo(reportobj,'Ifmgr')

    # 采集器登出
    gl.PC.grpc_dialin_Logout()


    # DUT配置gRPC功能，启动grpc服务
    cmds = f'''
        telemetry
        sensor-group 1
        sensor path ifmgr/interfaces
        quit
        destination-group 1
        ipv4-address {gl.PC.PORT1.ip} port 50051
        quit
        subscription 1
        sensor-group 1 sample-interval 5
        destination-group 1
        '''
    gl.DUT.send(cmds)
    gl.PC.grpc_dialout_StartServer(gl.PC.PORT1.ip,'50051')


    # PC关闭grpc服务
    gl.PC.grpc_dialout_StopServer()

