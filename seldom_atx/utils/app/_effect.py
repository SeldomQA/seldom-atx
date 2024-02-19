import time
from functools import wraps
import gevent
from seldom_atx import Seldom
from seldom_atx.logging import log
from seldom_atx.utils.app._duration import get_image_diff
from seldom_atx.u2driver import u2
from seldom_atx.wdadriver import wda_


class constant:
    isScreenshot = False
    isThreadLock = False
    distance = 0


def screenshot_and_compare(file_path, compare_image_path):
    """screenshot_and_compare"""
    if Seldom.platform_name == 'Android':
        u2.save_screenshot(file_path=file_path)
    elif Seldom.platform_name == 'iOS':
        wda_.save_screenshot(file_path=file_path)
    else:
        raise Exception('Unsupported platform')
    constant.distance = get_image_diff(image1_path=file_path, image2_path=compare_image_path)
    log.success(f'用例截图对比差异值为：{constant.distance}')
    return constant.distance


def start_screenshot():
    constant.isScreenshot = True


def listen_screenshot(file_path, compare_image_path):
    while constant.isThreadLock and Seldom.driver:
        if constant.isScreenshot:
            try:
                screenshot_and_compare(file_path, compare_image_path)
            except Exception as e:
                log.error(f"❌ Error in screenshot: {e}.")
            break
        time.sleep(1.5)


def run_testcase(func, *args, **kwargs):
    """Execute decorated test case"""
    try:
        func(*args, **kwargs)
    except Exception as e:
        log.error(f'❌ Error in run_testcase: {e}.')
    constant.isThreadLock = False


def IC(screenshot_path=None, compare_image_path=None):
    """用例截图对比装饰器"""

    def my_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if compare_image_path and screenshot_path is None:
                log.warning('使用IC装饰器时，请指定对比图像的路径')
            else:
                do_list = [gevent.spawn(run_testcase, func, *args, **kwargs),
                           gevent.spawn(listen_screenshot, screenshot_path, compare_image_path)]

                gevent.joinall(do_list)

        return wrapper

    return my_decorator
