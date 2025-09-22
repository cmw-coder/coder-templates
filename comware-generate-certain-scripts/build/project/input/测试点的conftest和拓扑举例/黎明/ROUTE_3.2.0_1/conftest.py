from pytest import fixture
from pytest_atf import *
from pytest_atf.atf_globalvar import globalVar as gl

# --------用户修改区 -------------------
# 不要删除setup/teardown的装饰器

# 用于声明脚本共用的变量或方法，不能修改类名。
# 变量或方法都要定义为类属性，不要定义为实例属性。
class CVarsAndFuncs:
    '''
    测试背景：
    3台设备组网，DUT1、DUT2建立ISIS 1的邻居，DUT2和DUT3建立ISIS 1的邻居，三台设备均配置成L2，三台设备的v6地址族下均配置multi-topology，在DUT3上配置一个loopback，loopback下配置一条ipv6路由，使能isisv6
    '''
    pass
    

level = 3
topo = r'ROUTE_3.2.0_1.topox'


@atf_time_stats("ATFSetupTime")
@atf_adornment
def setup():
    #在DUT2上启动ISIS进程，接口使能ISISv6，ISIS下配置分拓扑
    gl.DUT2.send(f'''
            ctrl+z
            system-view
            isis 1
			cost-style wide
			is-level level-2
            network-entity 10.0000.0000.0002.00
			address-family ipv6
			multi-topology
            interface {gl.DUT2.port1.intf}
            isis ipv6 enable 1
			interface {gl.DUT2.port2.intf}
            isis ipv6 enable 1
            ''')
    #在DUT1上启动ISIS进程，接口使能ISISv6，ISIS下配置分拓扑
    gl.DUT1.send(f'''
            ctrl+z
            system-view
            isis 1
			cost-style wide
			is-level level-2
            network-entity 10.0000.0000.0001.00
			address-family ipv6
			multi-topology
            interface {gl.DUT1.port1.intf}
            isis ipv6 enable 1
            ''')
    #在DUT3上启动ISIS进程，接口使能ISISv6，ISIS下配置分拓扑
    gl.DUT3.send(f'''
            ctrl+z
            system-view
            isis 1
			cost-style wide
			is-level level-2
            network-entity 10.0000.0000.0003.00
			address-family ipv6
			multi-topology
            interface {gl.DUT3.port1.intf}
            isis ipv6 enable 1
			interface loopback 1
            ipv6 address 3::3/128
            isis ipv6 enable 1
            ''')

@atf_time_stats("ATFTeardownTime")
@atf_adornment
def teardown():
    #DUT1、DUT2、DUT3清除配置
    gl.DUT2.send(f'''
            ctrl+z
            system-view
            undo isis 1
            y
            ''')
    gl.DUT1.send(f'''
            ctrl+z
            system-view
            undo isis1
            y
            ''')
    gl.DUT3.send(f'''
            ctrl+z
            system-view
            undo isis 1
            y
            undo interface loopback 1
            ''')

# ---------END-----------

@fixture(scope="package", autouse=True)
def my_fixture_setup_and_teardown():
    atf_topo_map(topo, level)
    try:
        setup()
        yield
    finally:
        teardown()
        atf_topo_unmap()

@fixture(scope="package")
def VarsAndFuncs():
    return CVarsAndFuncs