# -*- coding: utf-8 -*-
"""Netconf自动化测试脚本 - NQA/UdpJitterEntries元素测试."""
# pylint: disable=no-member,line-too-long,too-many-lines,trailing-newlines
# pylint: disable=anomalous-backslash-in-string,f-string-without-interpolation
# pylint: disable=consider-using-f-string,unused-variable,too-many-branches
# pylint: disable=too-many-statements
import re
import pytest
from pytest_atf.atf_globalvar import globalVar as gl
from pytest_atf import atf_assert, atf_wait, atf_logs  # pylint: disable=unused-import
# 脚本对应用例的信息，case_no 必须与用例编号对应
MODULE = 'Netconf'
case_no = 'T85_P11001','T85_P10995','T85_P11005'

# 脚本标识，每个标识必须使用 "pytest.mark." 声明，可选
pytestmark = [pytest.mark.FUN, pytest.mark.weight6]
# 修订从此处开始拷贝，重复信息请删除，包括 ''' '''符号

'''

#==========================项目详细信息START============================================
# 项目流水号           : 主线任务
#
# 项目名称             : NQA/UdpJitterEntries元素测试
#
# 脚本开发作者         : Claude Code
#
# 脚本开发时间         : 2025/10/13
#
# AIGC生成代码量（行） ：200+
#
# 生产耗时（人时）     ：1
#
#==========================项目详细信息END==============================================


======================================脚本涉及到的关键功能命令行Start======================================



======================================脚本涉及到的关键功能命令行End========================================


=========================================脚本开发详细信息Start=============================================


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
        gl.DUT1.send('''
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
        # PC--<PORT1>---------<PORT1>--DUT1
        # 创建netconf对象并连接
        TestClass.object = gl.DUT1.new_netconf(
            host=gl.DUT1.PORT1.ip, port=80, user='comware_test', pwd='comware_test', over='soap')

        # 正则表达式获取接口索引示例，具体看版本是否支持
        ifmgr_message = gl.DUT1.send(
            f'ctrl+z\nsys\nprobe\ndisplay system internal ifmgr list | '
            f'include {gl.DUT1.PORT1.intf}')
        TestClass.DUT1_PORT1_ifindex = re.search(r'index:(\d+)', ifmgr_message).group(1)

        # getStringValue获取接口索引示例，具体看版本是否支持
        # TestClass.DUT1_PORT1_ifindex=gl.DUT1.getStringValue(
        #     cmd=f'display interface {gl.DUT1.PORT1.intf}',
        #     target=['Interface index',],match='first', rule=2)
        # TestClass.DUT1_PORT1_ifindex=gl.DUT1.getStringValue(
        #     cmd=f'ctrl+z\nsys\nprobe\ndisplay system internal ifmgr interface '
        #     f'name {gl.DUT1.PORT1.intf}',
        #     target=['Interface index',],match='first', rule=2)

    @classmethod
    def teardown_class(cls):
        '''
        清除netconf脚本初始配置
        '''
        #删除用户名
        gl.DUT1.send('''
            ctrl+z
            system-view
            undo netconf soap http enable
            undo netconf soap idle-timeout
            undo netconf ssh server enable
            undo netconf ssh server port
            undo local-user comware_test class manage
            password-control composition enable
            undo password-control length
            password-control complexity user-name check
        ''')

    @staticmethod
    def occurrences(rpc, expect_results, index_description, keep_rpc=True):
        """检查RPC响应中期望元素的出现次数.

        Args:
            rpc: RPC响应内容
            expect_results: 期望结果列表
            index_description: 测试点描述
            keep_rpc: 是否保留RPC信息

        Returns:
            tuple: (检查结果, 错误日志)
        """
        result = True
        error_logs = ''
        for expect_result in expect_results:
            expect_count = expect_result["count"]
            actual_count = rpc.count(expect_result["element"])
            if expect_count == actual_count:
                continue
            if (actual_count > 0) & (expect_result["is_strict"] == 0):
                continue
            result = False
            if error_logs == '':
                error_logs = error_logs + '=========错误信息打印开始=========\n'
                if keep_rpc is True:
                    error_log ='\n测试点信息: ' + index_description  + '\n\n设备实际返回报文: \n' + rpc + '\n\n'
                else:
                    error_log ='\n测试点信息: ' + index_description + '\n\n'
                error_logs = error_logs + error_log
                # print(error_log)
            error_log = (expect_result['description'] + ' 检查失败:\n             期望 ' +
                        expect_result['element'] + ' 出现次数 ' + str(expect_result['count']) +
                        ', 实现出现次数 ' + str(actual_count) + '\n\n')
            error_logs = error_logs + error_log
            # print(error_log)
        if error_logs != '':
            error_logs = error_logs + '=========错误信息打印结束=========\n'
        return result, error_logs

