"""
seldom_atx CLI
"""
import os
import sys
import ssl
import json
import click
import seldom_atx
from seldom_atx import Seldom, AppConfig, DataBase
from seldom_atx import SeldomTestLoader
from seldom_atx import TestMainExtend
from seldom_atx.logging import log, log_cfg
from seldom_atx.utils import file
from seldom_atx.utils import cache
from seldom_atx.running.loader_hook import loader
from seldom_atx import __version__

PY3 = sys.version_info[0] == 3

ssl._create_default_https_context = ssl._create_unverified_context


@click.command()
@click.version_option(version=__version__, help="Show version.")
@click.option("-P", "--project", help="Create an Seldom automation test project.")
@click.option('-cc', "--clear-cache", default=False, help="Clear all caches of seldom_atx.")
@click.option("-p", "--path", help="Run test case file path.")
@click.option("-c/-nc", "--collect/--no-collect", default=False, help="Collect project test cases. Need the `--path`.")
@click.option("-l", "--level", default="data",
              type=click.Choice(['data', 'method']),
              help="Parse the level of use cases. Need the --path.")
@click.option("-j", "--case-json", default=None, help="Test case files. Need the `--path`.")
@click.option("-e", "--env", default=None, help="Set the Seldom run environment `Seldom.env`.")
@click.option("-d/-nd", "--debug/--no-debug", default=False, help="Debug mode. Need the `--path`.")
@click.option("-rr", "--rerun", default=0, type=int,
              help="The number of times a use case failed to run again. Need the `--path`.")
@click.option("-r", "--report", default=None, help="Set the test report for output. Need the `--path`.")
@click.option("-m", "--mod", help="Run tests modules, classes or even individual test methods from the command line.")
@click.option("-ll", "--log-level",
              type=click.Choice(['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR']),
              help="Set the log level.")
def main(project, clear_cache, path, collect, level, case_json, env, debug, rerun, report, mod,
         log_level):
    """
    seldom_atx CLI.
    """

    if project:
        create_scaffold(project)
        return 0

    if clear_cache:
        cache.clear()

    if log_level:
        log_cfg.set_level(level=log_level)

    # check hook function(confrun.py)
    debug = loader("debug") if loader("debug") is not None else debug
    rerun = loader("rerun") if loader("rerun") is not None else rerun
    report = loader("report") if loader("report") is not None else report
    timeout = loader("timeout") if loader("timeout") is not None else 10
    Seldom.platform_name = platform_name = loader("platform_name") if loader("platform_name") is not None else None
    Seldom.app_package = app_package = loader("app_package") if loader("app_package") is not None else None
    Seldom.device_id = device_id = loader("device_id") if loader("device_id") is not None else None
    title = loader("title") if loader("title") is not None else "Seldom Test Report"
    tester = loader("tester") if loader("tester") is not None else "Anonymous"
    description = loader("description") if loader("description") is not None else "Test case execution"
    language = loader("language") if loader("language") is not None else "en"
    whitelist = loader("whitelist") if loader("whitelist") is not None else []
    blacklist = loader("blacklist") if loader("blacklist") is not None else []
    AppConfig.DURATION_TIMES = loader("duration_times") if loader(
        "duration_times") is not None else AppConfig.DURATION_TIMES

    if path:
        Seldom.env = env
        if collect is True and case_json is not None:
            click.echo(f"Collect use cases for the {path} directory.")

            if os.path.isdir(path) is True:
                click.echo(f"add env Path: {os.path.dirname(path)}.")
                file.add_to_path(os.path.dirname(path))

            SeldomTestLoader.collectCaseInfo = True
            loader("start_run")
            main_extend = TestMainExtend(path=path)
            case_info = main_extend.collect_cases(json=True, level=level, warning=True)
            case_path = os.path.join(os.getcwd(), case_json)

            with open(case_path, "w", encoding="utf-8") as json_file:
                json_file.write(case_info)
            click.echo(f"save them to {case_path}")
            return 0

        if collect is False and case_json is not None:
            click.echo(f"Read the {case_json} case file to the {path} directory for execution")

            if os.path.exists(case_json) is False:
                click.echo(f"The run case file {case_json} does not exist.")
                return 0

            if os.path.isdir(path) is False:
                click.echo(f"The run cae path {case_json} does not exist.")
                return 0

            click.echo(f"add env Path: {os.path.dirname(path)}.")
            file.add_to_path(os.path.dirname(path))

            loader("start_run")
            with open(case_json, encoding="utf-8") as json_file:
                case = json.load(json_file)
                path, case = reset_case(path, case)
                main_extend = TestMainExtend(
                    path=path, debug=debug, timeout=timeout,
                    platform_name=platform_name, device_id=device_id, app_package=app_package,
                    report=report, title=title, tester=tester, description=description,
                    rerun=rerun, language=language,
                    whitelist=whitelist, blacklist=blacklist)
                main_extend.run_cases(case)
            loader("end_run")
            return 0

        loader("start_run")
        seldom_atx.main(
            path=path, debug=debug, timeout=timeout,
            platform_name=platform_name, device_id=device_id, app_package=app_package,
            report=report, title=title, tester=tester, description=description,
            rerun=rerun, language=language,
            whitelist=whitelist, blacklist=blacklist)
        loader("end_run")
        return 0

    if mod:
        file_dir = os.getcwd()
        sys.path.insert(0, file_dir)
        loader("start_run")
        seldom_atx.main(
            case=mod, debug=debug, timeout=timeout,
            platform_name=platform_name, device_id=device_id, app_package=app_package,
            report=report, title=title, tester=tester, description=description,
            rerun=rerun, language=language,
            whitelist=whitelist, blacklist=blacklist)
        loader("end_run")
        return 0


def create_scaffold(project_name: str) -> None:
    """
    create scaffold with specified project name.
    """
    if os.path.isdir(project_name):
        log.info(f"Folder {project_name} exists, please specify a new folder name.")
        return

    log.info(f"Start to create new test project: {project_name}")
    log.info(f"CWD: {os.getcwd()}\n")

    def create_folder(path):
        os.makedirs(path)
        log.info(f"created folder: {path}")

    def create_file(path, file_content=""):
        with open(path, 'w', encoding="utf-8") as py_file:
            py_file.write(file_content)
        msg = f"created file: {path}"
        log.info(msg)

    def create_table(db_object, table_name: str):
        table_attr = get_table_attribute(table_name)
        if not table_attr:
            raise ValueError(f"未找到 '{table_name}' 的表定义")
        fields_definitions = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        fields_definitions += [f"{field_name} {field_type}" for field_name, field_type in table_attr.items()]
        fields_sql = ", ".join(fields_definitions)
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({fields_sql});"
        db_object.execute_sql(sql)
        log.info(f"创建数据表：{table_name}")

    def get_table_attribute(table_name: str):
        tables_attr = {

            DataBase.ELE_TABLE: {DataBase.ELE_NAME: DataBase.TYPE_TEXT,
                                 DataBase.ELE_BY: DataBase.TYPE_TEXT,
                                 DataBase.ELE_VALUE: DataBase.TYPE_TEXT,
                                 DataBase.ELE_PAGE: DataBase.TYPE_TEXT},
            DataBase.CONFIG_TABLE: {DataBase.CONFIG_KEY: DataBase.TYPE_TEXT,
                                    DataBase.CONFIG_VALUE: DataBase.TYPE_TEXT},
            DataBase.PERF_TABLE: {DataBase.PERF_Device: DataBase.TYPE_TEXT,
                                  DataBase.PERF_DeviceName: DataBase.TYPE_TEXT,
                                  DataBase.PERF_TestCasePath: DataBase.TYPE_TEXT,
                                  DataBase.PERF_TestCaseName: DataBase.TYPE_TEXT,
                                  DataBase.PERF_TestCaseDesc: DataBase.TYPE_TEXT,
                                  DataBase.PERF_RunList: DataBase.TYPE_TEXT,
                                  DataBase.PERF_MemoryMax: DataBase.TYPE_TEXT,
                                  DataBase.PERF_DurationTimes: DataBase.TYPE_TEXT,
                                  DataBase.PERF_DurationList: DataBase.TYPE_TEXT,
                                  DataBase.PERF_DurationAvg: DataBase.TYPE_TEXT,
                                  DataBase.PERF_TIME: DataBase.TYPE_TEXT,
                                  DataBase.PERF_RESULT: DataBase.TYPE_TEXT}
        }

        return tables_attr.get(table_name)

    test_data = '''{
 "bing":  [
    ["case1", "seldom_atx"],
    ["case2", "poium"],
    ["case3", "XTestRunner"]
 ]
}

'''
    test_demo_Android = '''import seldom_atx
from seldom_atx.utils import AppPerf, RunType, start_recording
from seldom_atx import TestCaseU2
from seldom_atx import label


@label('Android')
class TestDemo(TestCaseU2):
    """
    Test Android Demo
    """

    def start(self):
        self.launch_app(stop=True)

    def end(self):
        self.close_app()

    @AppPerf(MODE=RunType.DEBUG)
    def test_demo(self):
        """
        test MIUI settings
        """
        start_recording()
        self.click(resourceId="android:id/title", text="蓝牙")
        self.click(resourceId="com.android.settings:id/refresh_anim")
        self.assertElement(resourceId="android:id/title", text="蓝牙设置")
        self.sleep(1)


if __name__ == '__main__':
    # Android 用例配置
    seldom_atx.main(
        device_id="f5ede5e3",
        app_package="com.android.settings",
        platform_name="Android",
        debug=True)
'''
    test_demo_iOS = '''import seldom_atx
from seldom_atx.utils import AppPerf, RunType, start_recording
from seldom_atx import TestCaseWDA
from seldom_atx import label


@label('iOS')
class TestDemo(TestCaseWDA):
    """
    Test iOS Demo
    """

    def start(self):
        self.launch_app(stop=True)

    def end(self):
        self.close_app()

    @AppPerf(MODE=RunType.DEBUG)
    def test_demo(self):
        """
        test iOS settings
        """
        start_recording()
        self.swipe_up_find(name='General')
        self.click(name='General')
        self.click(name='About')
        self.get_text(className='XCUIElementTypeStaticText', index=3)
        self.assertElement(name='NAME_CELL_ID')
        self.sleep(1)


if __name__ == '__main__':
    # iOS 用例配置
    seldom_atx.main(
        device_id="bfaaa7b76fe378fb64332ebab762bb36dc77d3c3",
        app_package="com.apple.Preferences",
        platform_name="iOS",
        debug=True)
    '''
    run_test = '''"""
seldom_atx confrun.py hooks function
"""


def start_run():
    """
    Test the hook function before running
    """
    ...


def end_run():
    """
    Test the hook function after running
    """
    ...


def debug() -> bool:
    """
    debug mod
    """
    return False


def rerun() -> int:
    """
    error/failure rerun times
    """
    return 1


def report():
    """
    setting report path
    Used:
    return "d://mypro/result.html"
    return "d://mypro/result.xml"
    """
    return None


def timeout() -> int:
    """
    setting timeout
    """
    return 120


def title() -> str:
    """
    setting report title
    """
    return "seldom_atx test report"


def tester() -> str:
    """
    setting report tester
    """
    return "Cobb"


def description():
    """
    setting report description
    """
    return ["windows", "Android"]


def language() -> str:
    """
    setting report language
    return "en"
    return "zh-CN"
    """
    return "zh-CN"


def whitelist() -> list:
    """test label white list"""
    return []


def blacklist() -> list:
    """test label black list"""
    return []


def duration_times() -> int:
    """耗时性能测试用例重复次数"""
    return 3


def platform_name() -> str:
    """
    app UI test
    between Android and iOS
    """
    # return "iOS"
    return "Android"


def app_package() -> str:
    """
    app UI test
    test app package name
    """
    # return "com.apple.Preferences"
    return "com.android.settings"


def device_id() -> str:
    """
    app UI test
    Android: device id
    iOS: udid
    """
    # return "bfaaa7b76fe378fb64332ebab762bb36dc77d3c3"
    return "f5ede5e3"
'''
    requirements = '''solox==2.7.5
git+https://github.com/SeldomQA/seldom-atx.git
uiautomator2[image]==2.16.23
'''

    create_folder(project_name)
    create_folder(os.path.join(project_name, "test_dir"))
    create_folder(os.path.join(project_name, "reports"))
    create_folder(os.path.join(project_name, "test_data"))
    create_file(os.path.join(project_name, "test_data", "data.json"), test_data)
    create_file(os.path.join(project_name, "test_dir", "__init__.py"))
    create_file(os.path.join(project_name, "test_dir", "test_demo_Android.py"), test_demo_Android)
    create_file(os.path.join(project_name, "test_dir", "test_demo_iOS.py"), test_demo_iOS)
    create_file(os.path.join(project_name, "confrun.py"), run_test)
    create_file(os.path.join(project_name, "requirements.txt"), requirements)

    db_dir_path = os.path.join(project_name, "database")
    create_folder(db_dir_path)
    from seldom_atx.utils.sqlite import SQLiteDB
    db_file_path = os.path.join(db_dir_path, DataBase.DB_NAME)
    db = SQLiteDB(db_path=db_file_path)
    create_table(db, DataBase.CONFIG_TABLE)
    create_table(db, DataBase.ELE_TABLE)
    create_table(db, DataBase.PERF_TABLE)


def reset_case(path: str, cases: list) -> [str, list]:
    """
    Reset the use case data
    :param path: case base path
    :param cases: case data
    """
    if len(cases) == 0:
        return path, cases

    for case in cases:
        if "." not in case["file"]:
            return path, cases

    case_start = cases[0]["file"].split(".")[0]
    for case in cases:
        if case["file"].startswith(f"{case_start}.") is False:
            break
    else:
        path = os.path.join(path, case_start)
        for case in cases:
            case["file"] = case["file"][len(case_start) + 1:]
        return path, cases

    return path, cases


if __name__ == '__main__':
    main()
