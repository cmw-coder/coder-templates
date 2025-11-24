.. _topics-XMLRPC远程测试:


XMLRPC远程测试
================================
XML-RPC（XML Remote Procedure Call）是一种远程过程调用（RPC）协议，它使用HTTP协议作为传输协议，使用XML作为消息编码格式。XML-RPC允许在不同的计算机上运行的程序通过网络进行通信和协作。它提供了一种简单的方法来调用远程服务器上的函数或方法，并返回结果。

本节中将对服务端和客户端的接口进行逐一介绍，最后给出脚本使用示例

--------------------------------
服务端接口介绍
--------------------------------


``open_program`` 用于打开指定程序，返回打开程序的pid用于关闭程序，支持1个参数：

- program_path: 要打开程序所在的绝对路径，必选参数，字符串类型


``close_program_by_pid`` 用于关闭程序，支持1个参数：

- pid: open_program打开程序的pid，必选参数，字符串类型


``enable_disable_network`` 用于启动或禁用指定名称的网卡，支持2个参数：

- adapter_name: 网卡名称，必选参数，字符串类型
- action: 对指定网卡的操作，启动为enable，禁用为disable，必选参数，字符串类型


``get_dns`` 用于获取服务端的dns信息，无入参


``get_dhcp_info`` 用于获取服务端的dhcp信息，无入参


``get_authentication`` 用于登陆网页需要认证登陆，支持4个参数：

- username : 认证用户名，必选参数，字符串类型
- password : 认证密码，必选参数，字符串类型
- driverpath : 服务端chromedriver所在绝对路径，chromedriver须与chrome浏览器版本相适配，必选参数，字符串类型
- url : 用户进行认证登陆是通过网页登陆进行认证，用户可以自定义传入url，可选参数，字符串类型，默认打开百度界面

.. note:: 服务端python文件必须以 **管理员身份** 运行，默认服务端开启端口 **8000** 




--------------------------------
客户端接口介绍
--------------------------------
客户端接口与服务端一一对应，用于用户在客户端调用服务端提供的接口


``OpenProgram`` 用于打开指定程序，返回打开程序的pid用于关闭程序，支持1个参数：

- abspath: 要打开服务端程序所在的绝对路径，必选参数，字符串类型


``CloseProgram`` 用于关闭程序，支持1个参数：

- pid: OpenProgram打开程序的pid，必选参数，字符串类型


``EnableDisableNetwork`` 用于启动或禁用指定名称的网卡，支持2个参数：

- adapter_name: 网卡名称，必选参数，字符串类型
- action: 对指定网卡的操作，启动为enable，禁用为disable，必选参数，字符串类型


``GetDns`` 用于获取服务端的dns信息，无入参


``GetDhcpInfo`` 用于获取服务端的dhcp信息，无入参


``Authentication`` 用于登陆网页需要认证登陆，支持4个参数：

- username : 认证用户名，必选参数，字符串类型
- password : 认证密码，必选参数，字符串类型
- driverpath : 服务端chromedriver所在绝对路径，chromedriver须与chrome浏览器版本相适配，必选参数，字符串类型
- url : 用户进行认证登陆是通过网页登陆进行认证，用户可以自定义传入url，可选参数，字符串类型，默认打开百度界面




--------------------------------
XMLRPC脚本示例
--------------------------------

.. note:: 示例脚本中用的绝对路径都是 **服务端** 应用的绝对路径，且客户端脚本执行前，需要先将服务端python文件以管理员身份运行，topox文件中服务器类型为XmlrpcServer


.. code-block:: python
    :linenos:

    import time
    from pytest_atf import *
    from pytest_atf.atf_globalvar import globalVar as gl


    class TestClass:
        '''
        测试目的：远程调用xmlrpc服务端接口
        作者：zhangsan/12345
        开发时间：2022.10.10
        修改记录：
        '''

        @classmethod
        def setup_class(cls):
            '''
            脚本初始配置
            '''
            pass


        @classmethod
        def teardown_class(cls):
            '''
            清除脚本初始配置
            '''

            pass


        def test_step_1(self):
            '''
            获取服务端的dhcp和dns信息
            '''

            dhcpinfo = gl.Server_0.GetDhcpInfo()
            dnsinfo = gl.Server_0.GetDns()


        def test_step_2(self):
            '''
            打开服务端指定程序，5s后关闭该程序
            '''
            # pid = gl.Server_0.OpenProgram("C:/Program Files (x86)/iNode/iNode Client/iNode Client.exe")
            pid = gl.Server_0.OpenProgram("C:/Program Files/XMind/XMind.exe")
            atf_logs(pid)

            atf_wait('等5s',5)

            gl.Server_0.CloseProgram(pid)


        def test_step_3(self):
            '''
            启动服务端指定网卡，5s后关闭
            '''
            gl.Server_0.EnableDisableNetwork("以太网3",'enable')
            atf_wait('等5s',5)
            gl.Server_0.EnableDisableNetwork("以太网3",'disable')
            

        def test_step_4(self):
            '''
            登陆网页进行认证
            '''
            gl.Server_0.Authentication("z24755",'xxxxxxxx','D:/Program Files (x86)/python38/chromedriver.exe')
            

