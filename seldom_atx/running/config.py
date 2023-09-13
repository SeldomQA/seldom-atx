"""
Seldom configuration file
"""


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
    Define run browser config
    """
    NAME = None
    REPORT_PATH = None
    REPORT_TITLE = "Seldom Test Report"
    LOG_PATH = None

    # driver config
    options = None
    command_executor = ""
    executable_path = ""


class AppConfig:
    """
    Define run atx config
    """
    PERF_OUTPUT_FOLDER = None
    PERF_RUN_FOLDER = None
    REPORT_IMAGE = []
    WRITE_EXCEL = []
    FPS = 45
    FRAME_SECONDS = 5
    DURATION_TIMES = 3
    STRESS_TIMES = 3
    log = False
