"""
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
    return ["windows", "jenkins"]


def language() -> str:
    """
    setting report language
    return "en"
    return "zh-CN"
    """
    return "zh-CN"


def whitelist() -> list:
    """test label white list"""
    return ['init']


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
