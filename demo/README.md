## seldom-atx demo

通过 demo 帮助你快速了解seldom-atx的使用。

### 准备工作

* 目录树：

```shell
./demo
├── README.md
├── __init__.py
├── confrun.py  # 运行配置钩子函数
├── reports     # 测试报告
├── test_data   # 测试数据
└── test_dir    # 测试用例
    ├── __init__.py
    └── test_demo_Android.py  # app Android 自动化用例
    └── test_demo_iOS.py  # app iOS 自动化用例
```


* 请安装 seldom-atx 最新版本。

```shell
> pip install -U git+https://github.com/SeldomQA/seldom-atx.git
```
* 可以通过初始化命令生成一个demo实例：
```shell
> seldom_atx --project demoName
```


### 使用方法

seldom_atx 支持 `confrun.py` 配置运行钩子函数，并推荐你使用这种方式。

| 函数             | 类型      | 说明                                                        |
|----------------|---------|-----------------------------------------------------------|
| start_run()    | fixture | 运行测试之前执行                                                  |
| end_run()      | fixture | 运行测试之后执行                                                  |
| platform_name() | app     | app的设备类型，例如：Android或iOS                                   |
| app_package()   | app     | app的包名，例如：com.android.settings                            |
| device_id()     | app     | app的设备ID或UDID，例如：f5ede5e3                                 |
| debug()        | general | 是否开启debug模式：True/False                                    |
| rerun()        | general | 用例失败/错误重跑，默认：0                                            |
| report()       | general | 指定报告生成地址，例如： `/User/tech/xxx.html`、  `/User/tech/xxx.xml` |
| timeout()      | general | 全局运行超时时间，默认：10                                            |
| title()        | general | 测试报告标题：html报告                                             |
| tester()       | general | 测试人员名字：html报告                                             |
| description()  | general | 测试报告描述：html报告                                             |
| language()     | general | 测试报告语言：html报告，类型： `en`、`zh-CN`                            |
| whitelist()    | general | 运行用例白名单                                                   |
| blacklist()    | general | 运行用例黑名单                                                   |


__特殊配置__

特殊配置是针对不同的测试类型设置的配置。

* app UI 自动化测试

```python
# confrun.py

def platform_name():
    """
    app UI test
    between Android and iOS
    """
    return "Android"


def app_package():
    """
    app UI test
    test app package name
    """
    return "com.android.settings"


def device_id():
    """
    app UI test
    Android: device id
    iOS: udid
    """
    return "f5ede5e3"


def duration_times():
    """耗时性能测试用例重复次数"""
    return 3
```

运行测试：

```shell
> seldom_atx --path test_dir/
```

__通用配置__

通用配置是不管运行什么类型的测试都适用的配置。

```python
# confrun.py

def debug():
    """
    debug mod
    """
    return False


def rerun():
    """
    error/failure rerun times
    """
    return 0


def report():
    """
    setting report path
    Used:
    return "d://mypro/result.html"
    return "d://mypro/result.xml"
    """
    return None


def timeout():
    """
    setting timeout
    """
    return 10


def title():
    """
    setting report title
    """
    return "seldom_atx test report"


def tester():
    """
    setting report tester
    """
    return "bugmaster"


def description():
    """
    setting report description
    """
    return ["windows", "jenkins"]


def language():
    """
    setting report language
    return "en"
    return "zh-CN"
    """
    return "en"


def whitelist():
    """test label white list"""
    return []


def blacklist():
    """test label black list"""
    return []
```

