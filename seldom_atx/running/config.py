"""
Seldom configuration file
"""
import os


class Seldom:
    """
    Seldom browser driver
    """
    driver = None
    timeout = 30
    debug = False
    platform_name = None
    device_id = None
    app_package = None
    env = None


class BrowserConfig:
    """
    报告相关配置
    """
    REPORT_PATH = None
    REPORT_TITLE = "Seldom Test Report"
    LOG_PATH = None


class AppConfig:
    """
    Define run atx config
    """
    # 整个用例的执行时间
    RUN_TIME = None
    # 测试用例执行过程中的输出路径
    PERF_RUN_FOLDER = None
    # 每个用例执行过程中呈现在报告上的图片
    REPORT_IMAGE = []
    # 默认设定录屏的帧率为45
    FPS = 45
    # 默认设定录屏分帧只分帧前后5s的片段
    FRAME_SECONDS = 5
    # 默认全局的耗时重复次数
    DURATION_TIMES = 3


class AppDecorator:
    """
    不支持用户修改的参数
    """
    iOS_perf_obj = None
    # 协程锁标志
    threadLock = False
    # 日志的标志
    log = False
    # 录屏的标志
    record = False
    # 用例执行过程中的异常捕获
    CASE_ERROR = []
    # 性能获取过程中的异常捕获
    PERF_ERROR = []
    # 日志获取过程中的异常捕获
    LOGS_ERROR = []
    # 录屏获取过程中的异常捕获
    RECORD_ERROR = []


class Platform:
    """
    不支持修改的常量名
    """
    Android = 'Android'
    iOS = 'iOS'
    Mac = 'MacOS'
    Windows = 'Windows'


class DataBase:
    """
    不支持修改的常量名
    """
    DB_NAME = "seldom_atx.db"

    TYPE_TEXT = "TEXT"

    CONFIG_TABLE = 'config'
    CONFIG_KEY = 'key'
    CONFIG_VALUE = 'value'

    ELE_TABLE = 'element'
    ELE_NAME = 'name'
    ELE_BY = 'by'
    ELE_VALUE = 'value'
    ELE_PAGE = 'page'

    PERF_TABLE = 'perf'
    PERF_TIME = 'time'
    PERF_Device = 'device'
    PERF_DeviceName = 'device_name'
    PERF_TestCasePath = 'testcase_path'
    PERF_TestCaseName = 'testcase_name'
    PERF_TestCaseDesc = 'testcase_desc'
    PERF_DurationTimes = 'duration_times'
    PERF_DurationList = 'duration_list'
    PERF_DurationAvg = 'duration_avg'
    PERF_MemoryMax = 'memory_max'
    PERF_RunList = 'run_list'
    PERF_RESULT = 'result'


# 项目根目录
BASEDIR = os.getcwd()
# 数据库目录
DB_DIR = os.path.join(BASEDIR, "database")
# 输出目录
OUTPUT_DIR = os.path.join(BASEDIR, "output")
