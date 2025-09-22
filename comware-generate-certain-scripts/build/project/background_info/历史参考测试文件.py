# *-* encoding: utf-8 *-*

# 如下库必须导入，可根据需要导入其它库
from pytest_atf import *
from pytest_atf.atf_globalvar import globalVar as gl
from atf_log.logger import logger
import re

# 脚本对应用例的信息，case_no 必须与用例编号对应
module = 'BGP_20.1.5.9'
case_no = '1.2.1.1.1.1.1,1.2.1.1.1.1.2'

# 脚本标识，每个标识必须使用 "pytest.mark." 声明，可选
pytestmark = [pytest.mark.FUN, pytest.mark.weight6]

# 修订从此处开始拷贝，重复信息请删除，包括 ''' '''符号
'''
==========================================项目详细信息START=============================================
 项目流水号           : NVxx

 项目名称             : xx

 脚本开发作者         : 姓名/工号

 脚本开发时间         : yyyy-mm-dd

 AIGC生成代码量       : 491

 生产耗时(人时)       : xx

 主测功能命令         :
    % bgp % i

 辅助功能命令         :
    % bgp % 

===========================================项目详细信息END==============================================
'''

class TestClass:
    '''
    组件信息:
        ROUTE
    
    分支信息:
        B75 
        
    场景名称:
        BGP L3VP over MPLS场景化

    场景说明:
        DUT1、DUT2、DUT3、DUT4菱形组网环境下，各设备接口全部使能ISIS，配置MPLS标签,其中DUT1与DUT2、DUT3通过LoopBack 0口建立L3VPN IBGP邻居，
    DUT4作为双归属CE引入本地LoopBack 1双栈地址。如无需双归属组网，删除DUT3设备配置即可验证BGP L3VPN over MPLS基本功能。组网中可通过修改TestClass.
    VRF切换组网场景。

    组网拓扑:
        ROUTE_4.12.0_1.topox

    开发作者:
        邵祥涌 22141
    '''

    @classmethod
    def setup_class(cls):
        '''
        场景化组网初始配置
        '''
        #DUT1设备通过IGP协议与DUT2、DUT3建立IBGP邻居，并配置MPLS
        gl.DUT1.send(f'''
            #
            ctrl+z
            sys
            #
            ip vpn-instance 1
            route-distinguisher 100:1
            vpn-target 100:1 import-extcommunity
            vpn-target 100:1 export-extcommunity
            #
            isis 1
            cost-style wide
            network-entity 10.0000.0000.1000.00
            #
            address-family ipv4 unicast
            #
            address-family ipv6 unicast
            #
            interface LoopBack0
            ip address 1.1.1.1 255.255.255.255
            isis enable 1
            ipv6 address 1::1/128
            isis ipv6 enable 1
            #
            interface LoopBack1
            ip binding vpn-instance 1
            ip address 11.11.11.11 255.255.255.255
            ipv6 address 11::11/128
            #
            mpls lsr-id 1.1.1.1
            #
            mpls ldp
            #
            interface {gl.DUT1.PORT1.intf}
            isis enable 1
            isis ipv6 enable 1
            mpls enable
            mpls ldp enable
            #
            interface {gl.DUT1.PORT3.intf}
            isis enable 1
            isis ipv6 enable 1
            mpls enable
            mpls ldp enable
            #
            bgp 1
            router-id 1.1.1.1
            peer 2.2.2.2 as-number 1
            peer 2.2.2.2 connect-interface LoopBack0
            peer 3.3.3.3 as-number 1
            peer 3.3.3.3 connect-interface LoopBack0
            peer 2::2 as-number 1
            peer 2::2 connect-interface LoopBack0
            peer 3::3 as-number 1
            peer 3::3 connect-interface LoopBack0
            #
            address-family vpnv4
            pic
            peer 2.2.2.2 enable
            peer 3.3.3.3 enable
            #
            address-family vpnv6
            pic
            peer 2.2.2.2 enable
            peer 3.3.3.3 enable
            #
            ip vpn-instance 1
            address-family ipv4 unicast
            import-route direct
            address-family ipv6 unicast
            import-route direct
            #
            

        ''')

        #DUT2设备通过IGP协议与DUT1建立IBGP邻居，与DUT4建立EBGP邻居，配置MPLS
        gl.DUT2.send(f'''
            #
            ctrl+z
            sys
            #
            ip vpn-instance 1
            route-distinguisher 100:1
            vpn-target 100:1 import-extcommunity
            vpn-target 100:1 export-extcommunity
            #
            isis 1
            cost-style wide
            network-entity 10.0000.0000.2000.00
            #
            address-family ipv4 unicast
            #
            address-family ipv6 unicast
            #
            interface LoopBack0
            ip address 2.2.2.2 255.255.255.255
            isis enable 1
            ipv6 address 2::2/128
            isis ipv6 enable 1
            #
            interface LoopBack1
            ip binding vpn-instance 1
            ip address 22.22.22.22 255.255.255.255
            ipv6 address 22::22/128
            #
            mpls lsr-id 2.2.2.2
            #
            mpls ldp
            #
            interface {gl.DUT2.PORT1.intf}
            mpls enable
            mpls ldp enable
            isis enable 1
            isis ipv6 enable 1
            #
            interface {gl.DUT2.PORT3.intf}
            isis ipv6 enable 1
            #
            interface {gl.DUT2.PORT4.intf}
            ip binding vpn-instance 1
            y
            ip address {gl.DUT2.PORT4.ip} {gl.DUT2.PORT4.mask}
            ipv6 address {gl.DUT2.PORT4.ip6} {gl.DUT2.PORT4.masklen6}
            #
            bgp 1
            router-id 2.2.2.2
            peer 1.1.1.1 as-number 1
            peer 1.1.1.1 connect-interface LoopBack0
            peer 1::1 as-number 1
            peer 1::1 connect-interface LoopBack0
            #
            address-family vpnv4
            peer 1.1.1.1 enable
            #
            address-family vpnv6
            peer 1.1.1.1 enable
            #
            ip vpn-instance 1
            peer {gl.DUT4.PORT2.ip} as-number 4
            peer {gl.DUT4.PORT2.ip6} as-number 4
            #
            address-family ipv4 unicast
            import-route direct
            peer {gl.DUT4.PORT2.ip} enable
            #
            address-family ipv6 unicast
            peer {gl.DUT4.PORT2.ip6} enable
            import-route direct
            #
        ''')

        #DUT3设备通过IGP协议与DUT1建立IBGP邻居，DUT4建立EBGP邻居，并配置MPLS
        gl.DUT3.send(f'''
            #
            ctrl+z
            sys
            #
            ip vpn-instance 1
            route-distinguisher 100:1
            vpn-target 100:1 import-extcommunity
            vpn-target 100:1 export-extcommunity
            #
            isis 1
            cost-style wide
            network-entity 10.0000.0000.3000.00
            #
            address-family ipv4 unicast
            #
            address-family ipv6 unicast
            #
            interface LoopBack0
            ip address 3.3.3.3 255.255.255.255
            isis enable 1
            ipv6 address 3::3/128
            isis ipv6 enable 1
            #
            interface LoopBack1
            ip binding vpn-instance 1
            ip address 33.33.33.33 255.255.255.255
            ipv6 address 33::33/128
            #
            mpls lsr-id 3.3.3.3
            #
            mpls ldp
            #
            interface {gl.DUT3.PORT1.intf}
            isis enable 1
            isis ipv6 enable 1
            mpls enable
            mpls ldp enable
            #
            interface {gl.DUT3.PORT3.intf}
            isis ipv6 enable 1
            #
            interface {gl.DUT3.PORT4.intf}
            ip binding vpn-instance 1
            y
            ip address {gl.DUT3.PORT4.ip} {gl.DUT3.PORT4.mask}
            ipv6 address {gl.DUT3.PORT4.ip6} {gl.DUT3.PORT4.masklen6}
            #
            bgp 1
            router-id 3.3.3.3
            peer 1.1.1.1 as-number 1
            peer 1.1.1.1 connect-interface LoopBack0
            peer 1::1 as-number 1
            peer 1::1 connect-interface LoopBack0
            #
            address-family vpnv4
            peer 1.1.1.1 enable
            #
            address-family vpnv6
            peer 1.1.1.1 enable
            #
            ip vpn-instance 1
            peer {gl.DUT4.PORT4.ip} as-number 4
            peer {gl.DUT4.PORT4.ip6} as-number 4
            #
            address-family ipv4 unicast
            import-route direct
            peer {gl.DUT4.PORT4.ip} enable
            #
            address-family ipv6 unicast
            import-route direct
            peer {gl.DUT4.PORT4.ip6} enable
            #
        ''')

        #DUT4设备与DUT2、DUT3建立EBGP邻居，并传递路由
        gl.DUT4.send(f'''
            #
            ctrl+z
            sys
            #
            interface LoopBack0
            ip address 4.4.4.4 255.255.255.255
            ipv6 address 4::4/128
            #
            interface LoopBack1
            ip address 5.5.5.5 255.255.255.255
            ipv6 address 5::5/128
            #
            interface {gl.DUT4.PORT1.intf}
            
            #
            interface {gl.DUT4.PORT3.intf}
            
            #
            bgp 4
            router-id 4.4.4.4
            peer {gl.DUT2.PORT4.ip} as-number 1
            peer {gl.DUT3.PORT4.ip} as-number 1
            peer {gl.DUT2.PORT4.ip6} as-number 1
            peer {gl.DUT3.PORT4.ip6} as-number 1
            #
            address-family ipv4 unicast
            network 5.5.5.5 255.255.255.255
            peer {gl.DUT2.PORT4.ip} enable
            peer {gl.DUT3.PORT4.ip} enable
            #
            address-family ipv6 unicast
            network 5::5 128
            peer {gl.DUT2.PORT4.ip6} enable
            peer {gl.DUT3.PORT4.ip6} enable
            #
        ''')

    @classmethod
    def teardown_class(cls):
        '''
        场景化组网删除配置
        '''

        gl.DUT1.send(f'''
            #
            ctrl+z
            sys
            #
            undo ip vpn-instance 1
            #
            undo bgp 1
            y
            #
            undo isis 1
            y
            #
            undo interface LoopBack 0
            #
            undo mpls ldp
            y
            #
            undo interface LoopBack 1
            #
            undo mpls lsr-id
            #
            interface {gl.DUT1.PORT1.intf}
            undo mpls enable
            undo mpls ldp enable
            #
            interface {gl.DUT1.PORT3.intf}
            undo mpls enable
            undo mpls ldp enable
            #
            ''')

        gl.DUT2.send(f'''
            #
            ctrl+z
            sys
            #
            undo ip vpn-instance 1
            #
            undo bgp 1
            y
            #
            undo isis 1
            y
            #
            undo interface LoopBack 0
            #
            undo interface LoopBack 1
            #
            undo mpls ldp
            y
            #
            undo mpls lsr-id
            #
            interface {gl.DUT2.PORT1.intf}
            undo mpls enable
            undo mpls ldp enable
            #
            interface {gl.DUT2.PORT4.intf}
            ip address {gl.DUT2.PORT4.ip} {gl.DUT2.PORT4.mask}
            ipv6 address {gl.DUT2.PORT4.ip6} {gl.DUT2.PORT4.masklen6}
            #
            ''')

        gl.DUT3.send(f'''
            #
            ctrl+z
            sys
            #
            undo ip vpn-instance 1
            #
            undo bgp 1
            y
            #
            undo isis 1
            y
            #
            undo interface LoopBack 0
            #
            undo interface LoopBack 1
            #
            undo mpls ldp
            y
            #
            undo mpls lsr-id
            #
            interface {gl.DUT3.PORT1.intf}
            undo mpls enable
            undo mpls ldp enable
            #
            #
            interface {gl.DUT3.PORT4.intf}
            ip address {gl.DUT3.PORT4.ip} {gl.DUT3.PORT4.mask}
            ipv6 address {gl.DUT3.PORT4.ip6} {gl.DUT3.PORT4.masklen6}
            #
            ''')

        gl.DUT4.send(f'''
            #
            ctrl+z
            sys
            #
            undo bgp 4
            y
            #
            undo isis 1
            y
            #
            undo interface LoopBack 0
            undo interface LoopBack 1
            #
            ''')

    def test_step_1(self):
        '''
        初始配置检查
        '''
        gl.DUT1.CheckCommand('DUT1设备查询与DUT2/DUT3设备ISIS路由情况',
            cmd='display isis route',
            expect=[
                '2.2.2.2/32',
                '3.3.3.3/32',
            ],
            not_expect=[],
            stop_max_attempt=3,
            wait_fixed=30,
            failed_assist=[],
        )
        gl.DUT1.CheckCommand('DUT1设备PING CE设备',
            cmd='ping -vpn-instance 1 5.5.5.5',
            expect=[],
            not_expect=[
                '100.0% packet loss',
            ],
            stop_max_attempt=3,
            wait_fixed=30,
            failed_assist=[],
        )
        
        gl.DUT1.CheckCommand('DUT1设备PING CE设备V6路由',
            cmd='ping ipv6 -vpn-instance 1 5::5',
            expect=[],
            not_expect=[
                '100.0% packet loss',
            ],
            stop_max_attempt=3,
            wait_fixed=30,
            failed_assist=[],
        )
        gl.DUT2.CheckCommand('DUT2设备查询与DUT1设备BGP邻居建立情况',
                             cmd='dis bgp peer vpnv4 1.1.1.1 verbose',
                             expect=['BGP current state: Established',],
                             not_expect=[],
                             stop_max_attempt=3,
                             wait_fixed=30)

        gl.DUT2.CheckCommand('DUT2设备查询与DUT4设备BGP邻居建立情况',
                             cmd='dis bgp peer ipv4 vpn-instance 1',
                             expect=['Peers in established state: 1',],
                             not_expect=[],
                             stop_max_attempt=3,
                             wait_fixed=30)

        gl.DUT1.CheckCommand('DUT1设备查询与DUT2/DUT3设备LDP邻居建立情况',
                             cmd='dis mpls ldp peer',
                             expect=[('2.2.2.2','Operational'),
                             ('3.3.3.3','Operational'),],
                             not_expect=[],
                             stop_max_attempt=3,
                             wait_fixed=30)

        gl.DUT3.CheckCommand('DUT3设备查询与DUT4设备BGP邻居建立情况',
                             cmd='dis bgp peer ipv4 vpn-instance 1',
                             expect=['Peers in established state: 1',],
                             not_expect=[],
                             stop_max_attempt=3,
                             wait_fixed=30)

        gl.DUT1.CheckCommand('DUT1查看路由表中的VPN路由信息',
                             cmd='dis ip routing vpn-instance 1',
                             expect=[
                                '5.5.5.5',
                                ],
                             not_expect=[],
                             stop_max_attempt=3,
                             wait_fixed=30)

        gl.DUT4.CheckCommand('DUT4查看路由表中的路由信息',
                             cmd='dis ip routing ',
                             expect=[
                                '11.11.11.11',
                                ],
                             not_expect=[],
                             stop_max_attempt=3,
                             wait_fixed=30)

        gl.DUT1.CheckCommand('DUT1设备查询与DUT2/DUT3设备BGP VPNv4邻居建立情况',
            cmd='display bgp peer vpnv4',
            expect=[
                'Peers in established state: 2',
                ('2.2.2.2', 'Established'),
                ('3.3.3.3', 'Established'),
            ],
            not_expect=[],
            stop_max_attempt=3,
            wait_fixed=30,
            failed_assist=[],
        )

        gl.DUT1.CheckCommand('DUT1设备查看BGP vpnv4路由形成主备',
            cmd='display bgp routing vpnv4 5.5.5.5',
            expect=[
                'Paths:   2 available, 1 best',
                'VPN Backup route.',
            ],
            not_expect=[],
            stop_max_attempt=3,
            wait_fixed=30,
            failed_assist=[],
        )

        gl.DUT1.CheckCommand('DUT1设备查看BGP vpnv6路由形成主备',
            cmd='display bgp routing vpnv6 5::5 128',
            expect=[
                'Paths:   2 available, 1 best',
                'VPN Backup route.',
            ],
            not_expect=[],
            stop_max_attempt=3,
            wait_fixed=30,
            failed_assist=[],
        )



    def test_step_2(self):
        '''
        用例编号: 1.2.1.1.1.1.1
        测试步骤: 
        '''

        #-------------------------------------- [ 增加配置 默认值、中间值 ] ------------------------#
        # 下发配置
         
        # 检查结果

        #-------------------------------------- [ 修改配置 边界值 ] ------------------------#
        #不涉及
        #-------------------------------------- [ 删除配置 ] --------------------------------------#

        #------------------ -------------------- [ 恢复配置 ] --------------------------------------#

        #-------------------------------------- [ 震荡、reset ] -----------------------------------#

        #-------------------------------------- [ 流量、ping ] ------------------------------------#

    def test_step_3(self):
        '''
        用例编号: 40.01.01.04.01.01.31.07
            原子功能：
                % bgp-vpnv4 %filter-policy prefix-list STRING<1-63> export unr
                display bgp routing-table ipv4[Status codes,Network]
            预置背景：
                参考ROUTE_4.12.0_1.topox
                DUT1、DUT2、DUT3、DUT4菱形组网环境下,DUT4作为ce设备。其他设备作为PE设备且接口使能ISISv6并通告SRv6 Locator路由，并配置end sid标签,其中DUT1与DUT2、DUT3通过LoopBack 0口建立L3VPN IBGP邻居。在各设备上创建两个vpn实例，一个是RD相同的，另外一个是RD不同的。
                DUT2上引入私网EBGP路由、静态路由、直连路由、ISIS路由、OSPF路由、RIP路由、unr路由，除了unr路由是ipv4路由，其他路由均是双栈路由。
        测试步骤: 
            1、在DUT2设备上，对引入的unr路由信息，通过vpnv4发布时，使用前缀列表进行过滤，覆盖原子功能% bgp-vpnv4 %filter-policy prefix-list STRING<1-63> export unr, 
               在DUT1上通过检查命令display bgp routing-table ipv4[Status codes,Network]查看bgp私网路由表，只有符合过滤条件的静态路由以及其他协议引入的路由。
            2、若原子功能存在参数，则覆盖对原子功能参数进行增删改查和边界值，实施邻居震荡和reset进程操作，并进行ping流量的覆盖，结果符合预期。
            3、若原子功能不存在参数，则覆盖对原子功能进行增删查，实施邻居震荡和reset进程操作，并进行ping流量的覆盖，结果符合预期。
            4、使用指导：（用户手册中有说明。若没有，填无；若有，额外增加步骤，实施特定使用的简单组合测试）
        '''

        #-------------------------------------- [ 修改配置顺序、参数组合 ] ------------------------#

        #-------------------------------------- [ 修改配置 边界值、默认值 ] ------------------------#

        #-------------------------------------- [ 删除配置 ] --------------------------------------#

        #-------------------------------------- [ 恢复配置 ] --------------------------------------#

        #-------------------------------------- [ 震荡、reset ] -----------------------------------#

        #-------------------------------------- [ 流量、ping ] ------------------------------------#

    def test_step_4(self):
        '''
        用例编号: 40.01.01.04.01.01.31.08
            原子功能：
                % bgp-vpnv4 %filter-policy prefix-list STRING<1-63> export unr
				% bgp % refresh delay INTEGER<0-3000>
                display bgp routing-table ipv4[Status codes,Network]
            预置背景：
                参考ROUTE_4.12.0_1.topox
                DUT1、DUT2、DUT3、DUT4菱形组网环境下,DUT4作为ce设备。其他设备作为PE设备且接口使能ISISv6并通告SRv6 Locator路由，并配置end sid标签,其中DUT1与DUT2、DUT3通过LoopBack 0口建立L3VPN IBGP邻居。在各设备上创建两个vpn实例，一个是RD相同的，另外一个是RD不同的。
                DUT2上引入私网EBGP路由、静态路由、直连路由、ISIS路由、OSPF路由、RIP路由、unr路由，除了unr路由是ipv4路由，其他路由均是双栈路由。
        测试步骤: 
            1、在DUT2设备上，对引入的unr路由信息，通过vpnv4发布时，使用前缀列表进行过滤，覆盖原子功能% bgp-vpnv4 %filter-policy prefix-list STRING<1-63> export unr, 
               在DUT1上通过检查命令display bgp routing-table ipv4[Status codes,Network]查看bgp私网路由表，只有符合过滤条件的静态路由以及其他协议引入的路由。
			2、在DUT2设备上设置路由的刷新延迟时间，覆盖原子功能% bgp % refresh delay INTEGER<0-3000>，在DUT1上通过检查命令display bgp routing-table ipv4[Status codes,Network]查看bgp私网路由表，路由的刷新时间符合预期。
            3、对组合原子功能进行配置顺序颠倒（增删恢复操作）、关键参数修改组合（非全遍历，分析等价类），随后实施reset进程和震荡邻居操作，并进行基础业务ping流量的覆盖，结果符合预期要求
        '''

        #-------------------------------------- [ 增加配置 默认值、中间值 ] ------------------------#
        #-------------------------------------- [ 修改配置 边界值 ] ------------------------#
        #-------------------------------------- [ 删除配置 ] --------------------------------------#

        #------------------ -------------------- [ 恢复配置 ] --------------------------------------#

        #-------------------------------------- [ 震荡、reset ] -----------------------------------#

        #-------------------------------------- [ 流量、ping ] ------------------------------------#
