"""
seldom_atx main
"""
import os
import re
import ast
import json as sys_json
import inspect
import unittest
import webbrowser
from typing import Dict, List, Any
from XTestRunner import HTMLTestRunner
from XTestRunner import XMLTestRunner
from seldom_atx.logging import log
from seldom_atx.logging import log_cfg
from seldom_atx.logging.exceptions import SeldomException
from seldom_atx.running.DebugTestRunner import DebugTestRunner
from seldom_atx.running.config import Seldom, BrowserConfig, AppConfig
from seldom_atx.running.loader_extend import seldomTestLoader
from seldom_atx.testdata.conversion import write_to_excel

INIT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "__init__.py")
_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open(INIT_FILE, 'rb') as f:
    VERSION = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

SELDOM_STR = f"""
              __    __              
   ________  / /___/ /___  ____ ____ 
  / ___/ _ \/ / __  / __ \/ __ ` ___/
 (__  )  __/ / /_/ / /_/ / / / / / /
/____/\___/_/\__,_/\____/_/ /_/ /_/ + openatx v{VERSION}
-----------------------------------------
                             @itest.info
"""
DEVICE_LIST = ['Android', 'iOS']


class TestMain:
    """
    Reimplemented Seldom Runner, Support for Web and API
    """
    TestSuits = []

    def __init__(
            self,
            path: str = None,
            case: str = None,
            debug: bool = False,
            timeout: int = 10,
            device_id: str = None,
            platform_name: str = None,
            app_package: str = None,
            report: str = None,
            title: str = "Seldom ATX Test Report",
            tester: str = "Anonymous",
            description: [str or list] = "Test case execution",
            rerun: int = 0,
            language: str = "en",
            whitelist: list = [],
            blacklist: list = [],
            open: bool = True,
            auto: bool = True):
        """
        runner test case
        :param path:
        :param case:
        :param title:
        :param tester:
        :param description:
        :param debug:
        :param timeout:
        :param device_id:
        :param platform_name:
        :param app_package:
        :param report:
        :param rerun:
        :param language:
        :param whitelist:
        :param blacklist:
        :param open:
        :param auto:
        :return:
        """
        print(SELDOM_STR)
        self.path = path
        self.case = case
        self.report = report
        self.title = BrowserConfig.REPORT_TITLE = title
        self.tester = tester
        self.description = description
        self.debug = debug
        self.rerun = rerun
        self.language = language
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.open = open
        self.auto = auto
        Seldom.platform_name = platform_name
        Seldom.device_id = device_id
        Seldom.app_package = app_package

        if Seldom.platform_name not in DEVICE_LIST:
            raise TypeError(f"platform_name [{app_package}] must be between iOS and Android.")

        if isinstance(timeout, int) is False:
            raise TypeError(f"Timeout {timeout} is not integer.")

        if isinstance(debug, bool) is False:
            raise TypeError(f"Debug {debug} is not Boolean type.")

        Seldom.timeout = timeout
        Seldom.debug = debug

        if self.case is not None:
            self.TestSuits = seldomTestLoader.loadTestsFromName(self.case)

        elif self.path is None:
            stack_t = inspect.stack()
            ins = inspect.getframeinfo(stack_t[1][0])
            file_dir = os.path.dirname(os.path.abspath(ins.filename))
            file_path = ins.filename
            if "\\" in file_path:
                this_file = file_path.split("\\")[-1]
            elif "/" in file_path:
                this_file = file_path.split("/")[-1]
            else:
                this_file = file_path
            self.TestSuits = seldomTestLoader.discover(file_dir, this_file)
        else:
            if len(self.path) > 3:
                if self.path[-3:] == ".py":
                    if "/" in self.path:
                        path_list = self.path.split("/")
                        path_dir = self.path.replace(path_list[-1], "")
                        self.TestSuits = seldomTestLoader.discover(path_dir, pattern=path_list[-1])
                    elif "\\" in self.path:
                        path_list = self.path.split("\\")
                        path_dir = self.path.replace(path_list[-1], "")
                        self.TestSuits = seldomTestLoader.discover(path_dir, pattern=path_list[-1])
                    else:
                        self.TestSuits = seldomTestLoader.discover(os.getcwd(), pattern=self.path)
                else:
                    self.TestSuits = seldomTestLoader.rediscover(self.path)
            else:
                self.TestSuits = seldomTestLoader.discover(self.path)

        if self.auto is True:
            self.run(self.TestSuits)

    def run(self, suits) -> None:
        """
        run test case
        """
        if self.debug is False:
            for filename in os.listdir(os.getcwd()):
                if filename == "reports":
                    break
            else:
                os.mkdir(os.path.join(os.getcwd(), "reports"))

            report_folder = AppConfig.PERF_OUTPUT_FOLDER = os.path.join(os.getcwd(), "reports")

            if (self.report is None) and (BrowserConfig.REPORT_PATH is not None):
                report_path = BrowserConfig.REPORT_PATH
            else:
                report_path = BrowserConfig.REPORT_PATH = os.path.join(report_folder, self.report)

            with open(report_path, 'wb') as fp:
                if report_path.split(".")[-1] == "xml":
                    runner = XMLTestRunner(output=fp, logger=log_cfg, rerun=self.rerun,
                                           blacklist=self.blacklist, whitelist=self.whitelist)
                    runner.run(suits)
                else:
                    runner = HTMLTestRunner(stream=fp, title=self.title, tester=self.tester,
                                            description=self.description,
                                            rerun=self.rerun, logger=log_cfg,
                                            language=self.language, blacklist=self.blacklist, whitelist=self.whitelist)
                    runner.run(suits)
            if AppConfig.WRITE_EXCEL:
                write_to_excel(data=AppConfig.WRITE_EXCEL,
                               filename=os.path.join(report_folder, f'{os.path.basename(report_path)[:26]}.xlsx'))

            log.success(f"generated html file: file:///{report_path}")
            log.success(f"generated log file: file:///{BrowserConfig.LOG_PATH}")
            if self.open is True:
                webbrowser.open_new(f"file:///{report_path}")
        else:
            runner = DebugTestRunner(
                blacklist=self.blacklist,
                whitelist=self.whitelist,
                verbosity=2)
            runner.run(suits)
            log.success("A run the test in debug mode without generating HTML report!")


class TestMainExtend(TestMain):
    """
    TestMain tests class extensions.
    1. Collect use case information and return to the list
    2. Execute the use cases based on the use case list
    """

    def __init__(
            self,
            path: str = None,
            debug: bool = False,
            timeout: int = 10,
            device_id: str = None,
            platform_name: str = None,
            app_package: str = None,
            report: str = None,
            title: str = "Seldom Test Report",
            tester: str = "Anonymous",
            description: str = "Test case execution",
            rerun: int = 0,
            language="en",
            whitelist: list = [],
            blacklist: list = []):

        if path is None:
            raise FileNotFoundError("Specify a file path")

        super().__init__(path=path, debug=debug, timeout=timeout,
                         device_id=device_id, platform_name=platform_name, app_package=app_package, report=report,
                         title=title, tester=tester,
                         description=description, rerun=rerun, language=language,
                         whitelist=whitelist, blacklist=blacklist, open=False, auto=False)

    def collect_cases(self, json: bool = False, level: str = "data", warning: bool = False) -> Any:
        """
        Return the collected case information.
        SeldomTestLoader.collectCaseInfo = True
        :param json: Return JSON format
        :param level: Parse the level of use cases:
                * data: Each piece of test data is parsed into a use case.
                * method: Each method is resolved into a use case
        :param warning: Whether to collect warning information
        """
        if level not in ["data", "method"]:
            raise ValueError("level value error.")

        cases = seldomTestLoader.collectCaseList

        if level == "method":
            # Remove the data-driven use case end number
            cases_backup_one = []
            for case in cases:
                case_name = case["method"]["name"]
                if "_" not in case_name:
                    cases_backup_one.append(case)
                else:
                    try:
                        int(case_name.split("_")[-1])
                    except ValueError:
                        cases_backup_one.append(case)
                    else:
                        case_name_end = case_name.split("_")[-1]
                        case["method"]["name"] = case_name[:-(len(case_name_end) + 1)]
                        cases_backup_one.append(case)

            # Remove duplicate use cases
            cases_backup_two = []
            case_full_list = []
            for case in cases_backup_one:
                case_full = f'{case["file"]}.{case["class"]["name"]}.{case["method"]["name"]}'
                if case_full not in case_full_list:
                    case_full_list.append(case_full)
                    cases_backup_two.append(case)

            cases = cases_backup_two

        if warning is True:
            self._load_testsuite(warning=True)

        if json is True:
            return sys_json.dumps(cases, indent=2, ensure_ascii=False)

        return cases

    def _load_testsuite(self, warning: bool = False) -> Dict[str, List[Any]]:
        """
        load test suite and convert to mapping
        :param warning: Whether to collect warning information
        """
        mapping = {}

        exception_info = ""
        for suits in self.TestSuits:
            for cases in suits:
                if isinstance(cases, unittest.suite.TestSuite) is False:
                    if warning is True:
                        exception_info = exception_info + str(cases._exception) + "\n"
                    continue

                for case in cases:
                    file_name = case.__module__
                    class_name = case.__class__.__name__

                    key = f"{file_name}.{class_name}"
                    if mapping.get(key, None) is None:
                        mapping[key] = []

                    mapping[key].append(case)

        if warning is True:
            collect_file = os.path.join(os.path.dirname(BrowserConfig.REPORT_PATH), "collect_warning.log")
            with open(collect_file, "w", encoding="utf-8") as file:
                file.write(exception_info)

        return mapping

    def run_cases(self, data: list) -> None:
        """
        run list case
        :param data: test case list
        :return:
        """
        if isinstance(data, list) is False:
            raise TypeError("Use cases must be lists.")

        if len(data) == 0:
            log.error("There are no use cases to execute")
            return

        suit = unittest.TestSuite()

        case_mapping = self._load_testsuite()
        for d in data:
            d_file = d.get("file", None)
            d_class = d.get("class").get("name", None)
            d_method = d.get("method").get("name", None)
            if (d_file is None) or (d_class is None) or (d_method is None):
                raise SeldomException(
                    """Use case format error, please refer to:
                    https://seldomqa.github.io/platform/platform.html""")

            cases = case_mapping.get(f"{d_file}.{d_class}", None)
            if cases is None:
                continue

            for case in cases:
                method_name = str(case).split(" ")[0]
                if "_" not in method_name:
                    if method_name == d_method:
                        suit.addTest(case)
                else:
                    try:
                        int(method_name.split("_")[-1])
                    except ValueError:
                        if method_name == d_method:
                            suit.addTest(case)
                    else:
                        if method_name.startswith(d_method):
                            suit.addTest(case)

        self.run(suit)


main = TestMain

if __name__ == '__main__':
    main()
