# seldom-atx
一款集成openatx的UI自动化测试框架

### Features

- [x] app测试框架
- [x] 提供脚手架快速创建自动化项目
- [x] 集成`XTestRunner`测试报告，现代美观
- [x] 提供丰富的断言
- [x] 提供强大的`数据驱动`
- [x] 支持APP功能耗时的计算
- [x] 集成`solox`APP性能库，获取用例执行中的性能

### Install

```shell
pip install seldom-atx(暂未发布)
```

如果您想使用它，可以使用github存储库url进行安装：

```shell
> pip install -U git+https://github.com/SeldomQA/seldom-atx.git@main
```


### 🤖 快速开始

1、查看帮助：

```shell
seldom_atx --help
Usage: seldom_atx [OPTIONS]

  seldom_atx CLI.

Options:
  --version                       显示版本.
  -P, --project TEXT              创建一个seldom_atx的自动化测试项目.
  -cc, --clear-cache BOOLEAN      清除seldom_atx的所有缓存.
  -p, --path TEXT                 运行测试用例文件路径.
  -c, --collect / -nc, --no-collect
                                  收集项目测试用例,需要`--path`.
  -l, --level [data|method]       分析用例级别,需要`--path`.
  -j, --case-json TEXT            测试用例文件,需要`--path`.
  -e, --env TEXT                  设置seldom_atx运行环境`Seldom.env`.
  -d, --debug / -nd, --no-debug   调试模式,需要`--path`.
  -rr, --rerun INTEGER            用例再次运行失败的次数,需要`--path`.
  -r, --report TEXT               设置要输出的测试报告,需要`--path`.
  -m, --mod TEXT                  从命令行运行测试模块,类甚至单个测试方法.
  -ll, --log-level [TRACE|DEBUG|INFO|SUCCESS|WARNING|ERROR]
                                  设置日志级别.
  --help                          显示此消息并退出.
```

2、创建项目：

```shell
> seldom_atx --project mypro
```

目录结构如下：

```shell
mypro/
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

* `test_dir/` 测试用例目录。
* `reports/` 测试报告目录。
* `confrun.py` 运行配置文件。

3、运行项目：

* ❌️ 在`pyCharm`中右键执行。
* ✔️ 通过命令行工具执行。

```shell
> seldom_atx --path test_dir/test_demo_Android.py # 运行 test_dir Android测试demo
```

4、查看报告

你可以到 `mypro\reports\` 目录查看测试报告。

## 🔬 Demo

> seldom-atx继承unittest单元测试框架，完全遵循unittest编写用例规范。

[demo](/demo) 提供了丰富实例，帮你快速了解seldom-atx的用法。

### 执行测试

```python
import seldom_atx

seldom_atx.main()  # 默认运行当前测试文件
seldom_atx.main(path="./")  # 当前目录下的所有测试文件
seldom_atx.main(path="./test_dir/")  # 指定目录下的所有测试文件
seldom_atx.main(path="./test_dir/test_demo_Android.py")  # 指定目录下的测试文件
```