import seldom

"""
说明：
path： 指定测试目录。
app_info： 启动app配置,
app_server： server 地址。
title： 指定测试项目标题。
tester： 指定测试人员。
description： 指定测试环境描述。
debug： debug模式，设置为True不生成测试用例。
rerun： 测试失败重跑
"""

if __name__ == '__main__':
    # uiautomator2 case 配置
    desired_caps = {
        'deviceName': 'JEF_AN20',
        'platformName': 'Android',
        'appPackage': 'com.meizu.flyme.flymebbs',
    }
    seldom.main(path="./test_dir/app_case",
                app_info=desired_caps,
                title="seldom自带 APP demo",
                tester="Cobb",
                debug=True,
                rerun=0)
