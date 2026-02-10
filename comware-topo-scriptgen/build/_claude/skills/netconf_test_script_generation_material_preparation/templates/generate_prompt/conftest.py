

from pytest import fixture
from pytest_atf import *
from pytest_atf.atf_globalvar import globalVar as gl

# --------用户修改区 -------------------
# 不要删除setup/teardown的装饰器

# 用于声明脚本共用的变量或方法，不能修改类名。
# 变量或方法都要定义为类属性，不要定义为实例属性。
class CVarsAndFuncs:
    pass
    

level = 3
topo = r'test_topo.topox'


@atf_time_stats("ATFSetupTime")
@atf_adornment
def setup():
    gl.DUT1.send('''
            ctrl+z
            system-view
            configuration replace file 1027.cfg
            n
        ''')
    #DUT配置开启IGMP-snooping功能(默认为enable)
    gl.DUT1.send(f'''

    '''
    )


@atf_time_stats("ATFTeardownTime")
@atf_adornment
def teardown():
    #DUT清除配置
    gl.DUT1.send(f'''

     '''
    )


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