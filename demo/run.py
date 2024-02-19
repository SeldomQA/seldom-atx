import seldom_atx

"""
说明：
path： 指定测试目录。
device_id： 设备ID
platform_name： Android或iOS
app_package： 被测APP的包名
title： 指定测试项目标题。
tester： 指定测试人员。
description： 指定测试环境描述。
debug： debug模式，设置为True不生成测试用例。
rerun： 测试失败重跑
"""

if __name__ == '__main__':
    # Android case 配置
    seldom_atx.main(path="test_dir/test_demo_Android.py",
                    device_id='92d48b97',
                    platform_name='Android',
                    app_package='com.magicv.airbrush',
                    title="seldom自带 APP demo",
                    tester="Cobb",
                    debug=False,
                    rerun=0)
