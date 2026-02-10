# -*- coding: utf-8 -*-
from pytest_atf import *
from pytest_atf.atf_globalvar import globalVar as gl
from atf_log.logger import logger
import re
import random
import ipaddress

# 脚本对应用例的信息，case_no 必须与用例编号对应
module = 'Netconf'
case_no = '1.1.1.6.1.1.7,1.1.1.6.1.1.8,1.1.1.6.1.1.9'

# 脚本标识，每个标识必须使用 "pytest.mark." 声明，可选
pytestmark = [pytest.mark.FUN, pytest.mark.weight6]

'''
==========================================项目详细信息START=============================================
 项目流水号           : NV202506270002 

 项目名称             : 【V9 Trunk】【园区核心交换机】园区交换机B70D064SP特性同步到V9 trunk----NQA&INQA&EMDI&NTP补齐 

 脚本开发作者         : 

 脚本开发时间         : 

 AIGC生成代码量(行)   : 

 生产耗时(人时)       : 
 
 主测功能命令         :


 主测功能节点         :NQA/StampInterfaceSession

===========================================项目详细信息END==============================================


=========================================脚本开发详细信息Start=============================================
脚本测试要点：

1. 基本操作测试
    get                 操作 -> 无配置时进行get/get-config/get-bulk/get-bulk-config操作，返回空数据
     
2. create操作测试
    create              操作 -> create下发全部配置成功
    get-config          操作 -> 验证create下发生效，缺省值不显示
    create              操作 -> 重复create NQA/StampInterfaceSession，返回配置已存在

3. delete操作测试, create后先删除配置
    delete              操作 -> delete删除配置成功
    get                 操作 -> 验证delete下发生效

4. merge操作测试
    merge               操作 -> merge下发全部配置成功
    get-config          操作 -> 验证merge下发生效，缺省值不显示
    merge               操作 -> 重复merge操作成功

5. replace操作测试
    replace             操作 -> replace操作下发值为false（默认值），成功
    get-config          操作 -> 验证replace下发生效，配置为空
    replace             操作 -> replace操作下发值为true，成功
    get-config          操作 -> 验证replace下发生效
    replace             操作 -> 重复replace操作成功

6. delete操作测试
    delete              操作 -> delete删除配置成功
    get                 操作 -> 验证delete下发生效
    delete              操作 -> 重复delete操作失败

7. 边界值测试
    replace             操作 -> 源端口最小值862，成功
    replace             操作 -> 源端口最大值65535，成功
    replace             操作 -> 源端口非法值861，失败
    replace             操作 -> 源端口非法值65536，失败
    replace             操作 -> 目的端口最小值862，成功
    replace             操作 -> 目的端口最大值65535，成功
	
8. remove操作测试
    remove              操作 -> remove删除配置成功（可删除默认值）
    get                 操作 -> 验证remove下发生效
    remove              操作 -> 重复remove操作成功

=========================================脚本开发详细信息  End=============================================
'''

class TestClass:
    '''
    Netconf功能测试
    '''
    
    @classmethod
    def setup_class(cls):
        '''
        netconf脚本初始配置
        '''
        #使能netconf并创建用户名
        gl.DUT1.send(f'''    
            ctrl+z
            system-view
            netconf soap http enable
            netconf soap idle-time 999
            netconf ssh server enable
            netconf ssh server port 830
            password-recovery enable
            undo password-control composition enable
            password-control length 4
            undo password-control complexity user-name check            
            local-user comware_test class manage
            password simple comware_test
            service-type ssh telnet http https
            authorization-attribute user-role network-admin
            authorization-attribute user-role network-operator
        ''')
        # 使用拓扑示例
        # PC--<PORT1>---------<PORT3>--DUT1--<PORT1>---------------<PORT1>--DUT2
        #                              DUT1--<PORT2>---------------<PORT2>--DUT2
        
        # 创建netconf对象并连接
        TestClass.object = gl.DUT1.new_netconf(host=gl.DUT1.PORT1.ip, port=23, user='comware_test', pwd='comware_test', over='soap')

        #自定义变量


        # 正则表达式获取接口索引示例，具体看版本是否支持
        ifmgr_message = gl.DUT1.send(f'ctrl+z\nsys\nprobe\ndisplay system internal ifmgr list | include {gl.DUT1.PORT1.intf}')
        TestClass.DUT1_PORT1_IFINDEX=re.search(r'index:(\d+)', ifmgr_message).group(1)
                
        # getStringValue获取接口索引示例，具体看版本是否支持
        # TestClass.DUT1_PORT1_ifindex=gl.DUT1.getStringValue(cmd=f'display interface {gl.DUT1.PORT1.intf}',target=['Interface index',],match='first', rule=2)
        # TestClass.DUT1_PORT1_ifindex=gl.DUT1.getStringValue(cmd=f'ctrl+z\nsys\nprobe\ndisplay system internal ifmgr interface name {gl.DUT1.PORT1.intf}',target=['Interface index',],match='first', rule=2)
        
    @classmethod
    def teardown_class(cls):
        '''
        清除netconf脚本初始配置
        '''
        #删除用户名
        gl.DUT1.send(f'''
            ctrl+z
            system-view
            undo netconf soap http enable
            undo netconf soap https enable
            undo netconf soap idle-timeout
            undo netconf ssh server enable
            undo netconf ssh server port
            undo local-user comware_test class manage
            password-control composition enable
            undo password-control length
            password-control complexity user-name check
        ''') 

    def generate_rand_string(strlen):
        ESCAPE_CHAR = [r'\\', r'\"', ]  # 转义字符
        SPECIAL_CHAR = ['!', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '@',
                        '[', ']', '^', '_', '`', '{', '|', '}', '~']  # 特殊字符
        NORMAL_CHAR = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                    'u',
                    'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                    'P',
                    'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8',
                    '9']  # 普通字符
        ALL_CHAR = NORMAL_CHAR
        random_str = ""
        while strlen:
            random_str = random_str +(random.sample(ALL_CHAR, 1))[0]#随机从候选字符挑选，构造随机字符串
            strlen = strlen - 1
        return random_str

    def generate_rand_ipv4_address():
        while True:
            ip = '.'.join(str(random.randint(100, 255)) for _ in range(4))
            if ipaddress.ip_address(ip):#返回合法ipv6地址，构造最大长度32位ipv4地址，每个字节都不为0
                return ip

    def generate_rand_ipv6_address():
        while True:
            ipv6 = ':'.join(''.join(random.choice('123456789ABCDEF') for _ in range(4)) for _ in range(8))
            if ipaddress.ip_address(ipv6):#返回合法ipv6地址，构造最大长度128位ipv6地址，每个字节都不为0
                return ipv6
    
    def occurrences(rpc, expect_results, index_description, keep_rpc = True):
        # 如果想显示返回RPC信息，请将结果置为keep_rpc = True
        result = True
        error_logs = ''
        for expect_result in expect_results:
            expect_count = expect_result["count"]
            actual_count = rpc.count(expect_result["element"])
            if expect_count == actual_count:
                continue
            else:
                if (actual_count > 0) & (expect_result["is_strict"] == 0):
                    continue
                else:
                    result = False
                    if error_logs == '':
                        error_logs = error_logs + '=========================================错误信息打印开始===========================================\n'
                        if keep_rpc == True:
                            error_log ='\n测试点信息: ' + index_description  + '\n\n设备实际返回报文: \n' + rpc + '\n\n'
                        else:
                            error_log ='\n测试点信息: ' + index_description + '\n\n'
                        error_logs = error_logs + error_log
                        # print(error_log)
                    error_log = expect_result['description'] + ' 检查失败:\n             期望 ' + expect_result['element'] + ' 出现次数 ' + str(expect_result['count']) + ', 实现出现次数 ' + str(actual_count) + '\n\n'
                    error_logs = error_logs + error_log
                    # print(error_log)
        if error_logs != '':
            error_logs = error_logs + '=========================================错误信息打印结束===========================================\n'
        return result, error_logs


    def test_step_1(self):
        '''
        测试点编号1: 1、无配置时进行get\get-config\get-bulk\get-bulk-config操作
        '''
        with atf_assert(f'''测试点编号1.1: 1.1 无配置时基于被测属性列，无指定索引列进行get操作，返回所有被测属性列''') as ars:
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                  <get>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/data:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession/>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step01", "is_strict":1 ,"count": 1, "element":"<data/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号1.1: 1.1 无配置时基于被测属性列，无指定索引列进行get操作，返回所有被测属性列''')
            if result is True:
                ars.append('True')
            else:
              atf_wait('检查失败',5)
              atf_logs(f'''failed:测试点编号1.1: 1.1 无配置时基于被测属性列，无指定索引列进行get操作，返回所有被测属性列, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号1.2: 1.2 无配置时基于被测属性列，无指定索引列进行get-config操作，返回所有被测属性列''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                  <get-config>
                    <source>
                      <running/>
                    </source>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession/>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step02", "is_strict":1 ,"count": 1, "element":"<data/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号1.2: 1.2 无配置时基于被测属性列，无指定索引列进行get-config操作，返回所有被测属性列''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号1.2: 1.2 无配置时基于被测属性列，无指定索引列进行get-config操作，返回所有被测属性列, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号1.3: 1.3 无配置时基于被测属性列，无指定索引列进行get-bulk操作，返回所有被测属性列''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <get-bulk>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/data:1.0" xmlns:web="http://www.h3c.com/netconf/base:1.0" xmlns:data="http://www.h3c.com/netconf/data:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession/>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get-bulk>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step03", "is_strict":1 ,"count": 1, "element":"<data/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号1.3: 1.3 无配置时基于被测属性列，无指定索引列进行get-bulk操作，返回所有被测属性列''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号1.3: 1.3 无配置时基于被测属性列，无指定索引列进行get-bulk操作，返回所有被测属性列, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号1.4: 1.4 无配置时基于被测属性列，无指定索引列进行get-bulk-config操作，返回所有被测属性列''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" xmlns:xxx="http://www.h3c.com/netconf/base:1.0" message-id="100">
                  <get-bulk-config>
                    <source>
                      <running/>
                    </source>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession/>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get-bulk-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step04", "is_strict":1 ,"count": 1, "element":"<data/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号1.4: 1.4 无配置时基于被测属性列，无指定索引列进行get-bulk-config操作，返回所有被测属性列''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号1.4: 1.4 无配置时基于被测属性列，无指定索引列进行get-bulk-config操作，返回所有被测属性列, 下面打印详细错误信息:\n{error_logs}\n''','error')

    def test_step_2(self):
        '''
        测试点编号2: 2、create操作测试
        '''
        with atf_assert(f'''测试点编号2.1: create下发全部配置成功''') as ars:
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="create">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable>true</Enable>
                              <SourcePort>1146</SourcePort>
                              <DestinationPort>862</DestinationPort>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step01", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号2.1: create下发全部配置成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号2.1: create下发全部配置成功, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号2.2: 通过get-config操作验证create下发生效,缺省值不显示''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                  <get-config>
                    <source>
                      <running/>
                    </source>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step02", "is_strict":1 ,"count": 1, "element":f"<IfName>{gl.DUT1.PORT1.intf}</IfName>", },
                {"description":"step03", "is_strict":1 ,"count": 1, "element":"<AddrFamily>ipv4</AddrFamily>", },
                {"description":"step04", "is_strict":1 ,"count": 1, "element":"<Enable>true</Enable>", },
                {"description":"step05", "is_strict":1 ,"count": 0, "element":"<SourcePort>1146</SourcePort>", },
                {"description":"step06", "is_strict":1 ,"count": 0, "element":"<DestinationPort>862</DestinationPort>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号2.2: 通过get-config操作验证create下发生效''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号2.2: 通过get-config操作验证create下发生效, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号2.3: 重复create失败''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="create">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable>true</Enable>
                              <SourcePort>1146</SourcePort>
                              <DestinationPort>862</DestinationPort>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step07", "is_strict":1 ,"count": 1, "element":"<error-tag>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号2.3: 重复create失败''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号2.3: 重复create失败, 下面打印详细错误信息:\n{error_logs}\n''','error')


    def test_step_3(self):
        '''
        测试点编号3: 3、delete操作测试, create后先删除配置
        '''
        with atf_assert(f'''测试点编号3.1: delete删除配置成功，delete不支持删除默认值，因而不删除SourcePort,DestinationPort''') as ars:
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="delete">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable/>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step01", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号3.1: delete删除配置成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号3.1: delete删除配置成功, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号3.2: 通过get操作验证delete下发生效''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                  <get>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/data:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession/>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step02", "is_strict":1 ,"count": 1, "element":"<data/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号3.2: 通过get-config操作验证delete下发生效''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号3.2: 通过get-config操作验证delete下发生效, 下面打印详细错误信息:\n{error_logs}\n''','error')

    def test_step_4(self):
        '''
        测试点编号4: 4、merge操作测试
        '''
        with atf_assert(f'''测试点编号4.1: merge操作下发全部配置成功''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="merge">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable>true</Enable>
                              <SourcePort>1146</SourcePort>
                              <DestinationPort>862</DestinationPort>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step01", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号4.1: merge操作下发全部配置成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号4.1: merge操作下发全部配置成功, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号4.2: 通过get-config操作验证merge下发生效，缺省值不显示''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                  <get-config>
                    <source>
                      <running/>
                    </source>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step02", "is_strict":1 ,"count": 1, "element":f"<IfName>{gl.DUT1.PORT1.intf}</IfName>", },
                {"description":"step03", "is_strict":1 ,"count": 1, "element":"<AddrFamily>ipv4</AddrFamily>", },
                {"description":"step04", "is_strict":1 ,"count": 1, "element":"<Enable>true</Enable>", },
                {"description":"step05", "is_strict":1 ,"count": 0, "element":"<SourcePort>1146</SourcePort>", },
                {"description":"step06", "is_strict":1 ,"count": 0, "element":"<DestinationPort>862</DestinationPort>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号4.2: 通过get-config操作验证merge下发生效''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号4.2: 通过get-config操作验证merge下发生效, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号4.3: 重复merge操作成功''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="merge">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable>true</Enable>
                              <SourcePort>1146</SourcePort>
                              <DestinationPort>862</DestinationPort>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step07", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号4.3: 重复merge操作成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号4.3: 重复merge操作成功, 下面打印详细错误信息:\n{error_logs}\n''','error')

    def test_step_5(self):
        '''
        测试点编号5: 5、replace操作测试
        '''
        with atf_assert(f'''测试点编号5.1: replace操作下发值为false。默认值，成功''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="replace">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable>false</Enable>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step01", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号5.1: replace操作下发值为false。默认值，成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号5.1: replace操作下发值为false。默认值，成功, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号5.2: 通过get-config操作验证replace下发生效，配置为空，缺省值不显示''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                  <get-config>
                    <source>
                      <running/>
                    </source>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step04", "is_strict":1 ,"count": 0, "element":"<Enable>false</Enable>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号5.2: 通过get-config操作验证replace下发生效，配置为空''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号5.2: 通过get-config操作验证replace下发生效，配置为空, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号5.3: replace操作下发值为true成功''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="replace">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable>true</Enable>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step05", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号5.3: replace操作下发值为true成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号5.3: replace操作下发值为true成功, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号5.4: 通过get-config操作验证replace下发生效''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                  <get-config>
                    <source>
                      <running/>
                    </source>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step06", "is_strict":1 ,"count": 1, "element":f"<IfName>{gl.DUT1.PORT1.intf}</IfName>", },
                {"description":"step07", "is_strict":1 ,"count": 1, "element":"<AddrFamily>ipv4</AddrFamily>", },
                {"description":"step08", "is_strict":1 ,"count": 1, "element":"<Enable>true</Enable>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号5.4: 通过get-config操作验证replace下发生效''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号5.4: 通过get-config操作验证replace下发生效, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号5.5: 重复下发''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="replace">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable>true</Enable>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step09", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号5.5: 重复下发''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号5.5: 重复下发, 下面打印详细错误信息:\n{error_logs}\n''','error')

    def test_step_6(self):
        '''
        测试点编号6: 6、delete操作测试
        '''
        with atf_assert(f'''测试点编号6.1: delete删除配置成功，delete不支持删除默认值，因而不删除SourcePort,DestinationPort''') as ars:
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="delete">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable/>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step01", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号6.1: delete删除配置成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号6.1: delete删除配置成功, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号6.2: 通过get操作验证delete下发生效''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                  <get>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/data:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession/>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step02", "is_strict":1 ,"count": 1, "element":"<data/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号6.2: 通过get-config操作验证delete下发生效''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号6.2: 通过get-config操作验证delete下发生效, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号6.3: 重复delete下发失败''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="delete">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable/>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step03", "is_strict":1 ,"count": 1, "element":"<error-tag>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号6.3: 重复delete下发失败''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号6.3: 重复delete下发失败, 下面打印详细错误信息:\n{error_logs}\n''','error')

    def test_step_7(self):
        '''
        测试点编号7: 7、remove操作测试
        '''
        with atf_assert(f'''测试点编号7.1: remove删除配置成功,remove可以删除默认值''') as ars:
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="remove">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable/>
                              <SourcePort/>
                              <DestinationPort/>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step01", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号7.1: remove删除配置成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号7.1: remove删除配置成功, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号7.2: 通过get操作验证remove下发生效''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                  <get>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/data:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession/>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step02", "is_strict":1 ,"count": 1, "element":"<data/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号7.2: 通过get-config操作验证remove下发生效''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号7.2: 通过get-config操作验证remove下发生效, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号7.3: 重复remove下发成功''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="remove">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable/>
                              <SourcePort/>
                              <DestinationPort/>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step03", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号7.3: 重复remove下发成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号7.3: 重复remove下发成功, 下面打印详细错误信息:\n{error_logs}\n''','error')

    def test_step_8(self):
        '''
        测试点编号8: 8、remove操作测试
        '''
        with atf_assert(f'''测试点编号8.1: remove删除配置成功,remove可以删除默认值''') as ars:
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="remove">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable/>
                              <SourcePort/>
                              <DestinationPort/>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step01", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号8.1: remove删除配置成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号8.1: remove删除配置成功, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号8.2: 通过get操作验证remove下发生效''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:web="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
                  <get>
                    <filter type="subtree">
                      <top xmlns="http://www.h3c.com/netconf/data:1.0">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession/>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </filter>
                  </get>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step02", "is_strict":1 ,"count": 1, "element":"<data/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号8.2: 通过get-config操作验证remove下发生效''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号8.2: 通过get-config操作验证remove下发生效, 下面打印详细错误信息:\n{error_logs}\n''','error')
        with atf_assert(f'''测试点编号8.3: 重复remove下发成功''') as ars:
            #---------------------- input   rpc -----------------------#
            TestClass.object.send(f'''
                <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:xc="http://www.h3c.com/netconf/base:1.0" message-id="101">
                  <edit-config>
                    <target>
                      <running/>
                    </target>
                    <error-option>rollback-on-error</error-option>
                    <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                      <top xmlns="http://www.h3c.com/netconf/config:1.0" xc:operation="remove">
                        <NQA>
                          <StampInterfaceSessions>
                            <StampInterfaceSession>
                              <IfName>{gl.DUT1.PORT1.intf}</IfName>
                              <AddrFamily>ipv4</AddrFamily>
                              <Enable/>
                              <SourcePort/>
                              <DestinationPort/>
                            </StampInterfaceSession>
                          </StampInterfaceSessions>
                        </NQA>
                      </top>
                    </config>
                  </edit-config>
                </rpc>
                ''')
            #--------------------- check  result ----------------------#
            expect_results=[
                #-------------------- include elements --------------------#
                {"description":"step03", "is_strict":1 ,"count": 1, "element":"<ok/>", },
            ]
            result, error_logs=TestClass.occurrences(TestClass.object.reply_xml, expect_results, f'''测试点编号8.3: 重复remove下发成功''')
            if result is True:
                ars.append('True')
            else:
                atf_wait('检查失败',5)
                atf_logs(f'''failed:测试点编号8.3: 重复remove下发成功, 下面打印详细错误信息:\n{error_logs}\n''','error')