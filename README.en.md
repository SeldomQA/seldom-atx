# seldom-atx
seldom and openatx complete mobile automation test.

### Features

- [x] App automation testing framework
- [x] Provide scaffolding for quick creation of automated projects
- [x] Integrated`XTestRunner`test report, modern and aesthetically pleasing
- [x] Provide rich assertions
- [x] Provide powerful`data driven`
- [x] Supporting time-consuming calculations for APP functionality
- [x] Integrate the `SoloX` APP performance library to obtain performance during use case execution

### Install

```shell
pip install seldom-atx (Not yet published)
```

If you want to use it, you can install it using the github repository URL:

```shell
> pip install -U git+https://github.com/SeldomQA/seldom-atx.git@main
```


### 🤖 Quick Start

1、view help：

```shell
seldom_atx --help
Usage: seldom_atx [OPTIONS]

  seldom_atx CLI.

Options:
  --version                       Show version.
  -P, --project TEXT              Create an Seldom automation test project.
  -cc, --clear-cache BOOLEAN      Clear all caches of seldom.
  -p, --path TEXT                 Run test case file path.
  -c, --collect / -nc, --no-collect
                                  Collect project test cases. Need the
                                  `--path`.
  -l, --level [data|method]       Parse the level of use cases. Need the
                                  --path.
  -j, --case-json TEXT            Test case files. Need the `--path`.
  -e, --env TEXT                  Set the Seldom run environment `Seldom.env`.
  -d, --debug / -nd, --no-debug   Debug mode. Need the `--path`.
  -rr, --rerun INTEGER            The number of times a use case failed to run
                                  again. Need the `--path`.
  -r, --report TEXT               Set the test report for output. Need the
                                  `--path`.
  -m, --mod TEXT                  Run tests modules, classes or even
                                  individual test methods from the command
                                  line.
  -ll, --log-level [TRACE|DEBUG|INFO|SUCCESS|WARNING|ERROR]
                                  Set the log level.
  --help                          Show this message and exit.
```