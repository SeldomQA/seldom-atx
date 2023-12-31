import base64
import os
import time
import contextlib
import io
import socket
import threading
from datetime import datetime
from typing import Tuple
import imageio
import tidevice
from seldom_atx.logging import log
from seldom_atx.logging.exceptions import NotFindElementError
from seldom_atx.running.config import Seldom, AppConfig
from seldom_atx.running.loader_hook import loader

__all__ = ["WDADriver", "WDAElement", "make_screenrecord", "wda_"]

keycodes = {
    'home': 'home',
    'back': 'back',
    'left': 'left',
    'enter': 'enter',
}

LOCATOR_LIST = {
    'id': "id",
    'name': "name",
    'xpath': "xpath",
    'text': "text",
    'className': "className",
    'value': "value",
    'label': "label"
}


class WDAObj:
    c = None  # device
    s = None  # session
    e = None  # element

    @staticmethod
    def t():
        t = tidevice.Device(udid=(loader("device_id") if loader(
            "device_id") is not None else Seldom.device_id if Seldom.device_id is not None else None))
        t.create_inner_connection()
        return t


class SocketBuffer:
    """
    Since I can't find a lib that can buffer socket read and write, so I write a one
    copy过来的方法：SocketBuffer 类是一个用于缓冲套接字读写操作的自定义实用工具类。
    它对原始套接字执行的操作进行封装，以便更方便地从套接字中读取数据或向套接字发送数据。
    """

    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._buf = bytearray()

    def _drain(self):
        _data = self._sock.recv(1024)
        if _data is None:
            raise IOError("socket closed")
        self._buf.extend(_data)
        return len(_data)

    def read_until(self, delimeter: bytes) -> bytes:
        """ return without delimeter """
        while True:
            index = self._buf.find(delimeter)
            if index != -1:
                _return = self._buf[:index]
                self._buf = self._buf[index + len(delimeter):]
                return _return
            self._drain()

    def read_bytes(self, length: int) -> bytes:
        while length > len(self._buf):
            self._drain()

        _return, self._buf = self._buf[:length], self._buf[length:]
        return _return

    def write(self, data: bytes):
        return self._sock.sendall(data)


class WDAElement:
    """facebook-wda element API"""

    def __init__(self, **kwargs) -> None:
        if not kwargs:
            raise ValueError("Please specify a locator")
        self.desc = None
        self.kwargs = kwargs
        for by, value in list(self.kwargs.items()):
            if LOCATOR_LIST.get(by) is None:
                setattr(self, by, value)
                del self.kwargs[by]
        if not self.kwargs:
            raise ValueError(f"No supported elements found.")
        self.find_elem_info = None
        self.find_elem_warn = None
        if self.desc:
            self.desc = f'desc={self.desc}'
        else:
            self.desc = ', '.join([f"{k}={v}" for k, v in self.kwargs.items()])

    def get_elements(self, index: int = 0, visible: bool = True, empty: bool = False, timeout: float = None):
        try:
            WDAObj.e = WDAObj.s(**self.kwargs, visible=visible, index=index).get(timeout=timeout)
        except Exception as e:
            if empty is False:
                raise NotFindElementError(f"❌ Find element error: {self.desc} -> {e}.")
            else:
                return []
        self.find_elem_info = f"Find element: {self.desc}"
        return WDAObj.e

    @property
    def info(self):
        """return element info"""
        return self.find_elem_info

    @property
    def warn(self):
        """return element warn"""
        return self.find_elem_warn


class WDADriver:
    """iOS驱动"""

    def __init__(self):
        WDAObj.c = Seldom.driver

    @staticmethod
    def implicitly_wait(timeout: float = None, noLog: bool = False):
        """set facebook-wda implicitly wait"""
        if not timeout:
            timeout = Seldom.timeout
        WDAObj.s.implicitly_wait(timeout)
        if not noLog:
            log.info(f'✅ Set implicitly wait -> {timeout}s.')

    def install_app(self, app_path: str):
        """Install the application found at `app_path` on the device.

        Args:
            app_path: the local or remote path to the application to install

        """
        os.system(f'tidevice --udid {Seldom.device_id} install {app_path}')
        log.info(f'✅ Install APP path -> {app_path}.')
        return self

    def remove_app(self, package_name: str):
        """Remove the specified application from the device.

        Args:
            package_name: the application id to be removed

        """
        if not package_name:
            package_name = Seldom.app_package
        os.system(f'tidevice uninstall {package_name}')
        log.info(f'✅ Remove APP -> {package_name}.')
        return self

    def launch_app(self, package_name: str = None, stop: bool = False):
        """Start on the device the application specified in the desired capabilities."""
        if not package_name:
            package_name = Seldom.app_package
        if stop:
            Seldom.driver.session().app_terminate(package_name)
        log.info(f'✅ Launch APP -> {package_name} STOP={stop}.')
        WDAObj.s = Seldom.driver.session(package_name)

        return self

    def close_app(self, package_name: str = None):
        """Stop the running application, specified in the desired capabilities, on
        the device.

        Returns:
            Union['WebDriver', 'Applications']: Self instance
        """
        if not package_name:
            package_name = Seldom.app_package
        log.info(f'✅ Close APP -> {package_name}.')
        Seldom.driver.session().app_terminate(package_name)

        return self

    def set_text(self, text: str, clear: bool = False, enter: bool = False, click: bool = False, index: int = 0,
                 **kwargs) -> None:
        """
        Operation input box.

        Usage:
            self.type(css="#el", text="selenium")
        """
        if clear is True:
            self.clear_text(index, **kwargs)
        if click is True:
            self.click(index, **kwargs)
            time.sleep(0.5)
        wda_elem = WDAElement(**kwargs)
        elem = wda_elem.get_elements(index)
        log.info(f"✅ {wda_elem.info} -> input '{text}'.")
        elem.set_text(text)
        if enter is True:
            elem.press('enter')

    @staticmethod
    def clear_text(index: int = 0, **kwargs) -> None:
        """
        Clear the contents of the input box.

        Usage:
            self.clear(css="#el")
        """
        wda_elem = WDAElement(**kwargs)
        elem = wda_elem.get_elements(index=index)
        log.info(f"✅ {wda_elem.info} -> clear input.")
        elem.clear_text()

    @staticmethod
    def click(index: int = 0, **kwargs) -> None:
        """
        It can click any text / image can be clicked
        Connection, check box, radio buttons, and even drop-down box etc..

        Usage:
            self.click(css="#el")
        """
        wda_elem = WDAElement(**kwargs)
        elem = wda_elem.get_elements(index=index)
        log.info(f"✅ {wda_elem.info} -> click.")
        elem.click()

    @staticmethod
    def click_text(text: str, index: int = 0) -> None:
        """
        Click the element by the text

        Usage:
            self.click_text("新闻")
        """
        wda_elem = WDAElement(text=text)
        elem = wda_elem.get_elements(index)
        log.info(f"✅ {wda_elem.info} -> click text.")
        elem.click()

    @staticmethod
    def get_text(index: int = 0, **kwargs) -> str:
        """
        Get element text information.

        Usage:
            self.get_text(css="#el")
        """
        wda_elem = WDAElement(**kwargs)
        elem = wda_elem.get_elements(index)
        text = elem.text
        log.info(f"✅ {wda_elem.info} -> get text: {text}.")
        return text

    @staticmethod
    def get_display(index: int = 0, **kwargs) -> bool:
        """获取当前某元素的可见状态"""
        wda_elem = WDAElement(**kwargs)
        result = WDAObj.s(**wda_elem.kwargs, visible=True, index=index).exists
        log.info(f"✅ {wda_elem.desc} -> exists: {result}.")
        return result

    def wait(self, timeout: int = 5, index: int = 0, noLog=False, **kwargs) -> bool:
        """等待某元素出现"""
        wda_elem = WDAElement(**kwargs)
        result = None
        if noLog is False:
            log.info(f"⌛ wait {wda_elem.desc} to exist: {timeout}s.")
        for _ in range(timeout):
            result = self.get_display(**wda_elem.kwargs, index=index, noLog=True)
            time.sleep(1)
            if result:
                break
        if not result:
            if noLog is False:
                log.warning(f"❗ Element {wda_elem.kwargs} not exist.")
            self.save_screenshot(report=True)
        return result

    def wait_gone(self, timeout: int = None, index: int = 0, **kwargs) -> bool:
        """等待元素消失"""
        if not timeout:
            timeout = Seldom.timeout
        wda_elem = WDAElement(**kwargs)
        log.info(f"⌛ wait {wda_elem.desc} gone: timeout={timeout}s.")
        try:
            result = WDAObj.s(**kwargs, visible=True, index=index).wait_gone(timeout=timeout)
        except Exception as e:
            raise e

        if not result:
            log.warning(f'❗ Wait {wda_elem.desc} gone failed.')
            self.save_screenshot(report=True)
        return result

    @staticmethod
    def save_screenshot(file_path: str = None, report: bool = False) -> None:
        """Saves a screenshots of the current window to a PNG image file."""
        screenshot = Seldom.driver.screenshot()
        if file_path is None:
            file_path = os.path.join(AppConfig.PERF_RUN_FOLDER,
                                     f'{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.png')

        log.info(f"📷️ screenshot -> ({file_path}).")
        screenshot.save(file_path)
        if report:
            with open(file_path, "rb") as image_file:
                image_bytes = image_file.read()
                base64_data = base64.b64encode(image_bytes)
                base64_string = base64_data.decode("utf-8")
            AppConfig.REPORT_IMAGE.extend([base64_string])

    @staticmethod
    def get_element(index: int = 0, **kwargs):
        """
        Get a set of elements

        Usage:
        elem = self.get_element(index=1, css="#el")
        elem.click()
        """
        wda_elem = WDAElement(**kwargs)
        elem = wda_elem.get_elements(index)
        log.info(f"✅ {wda_elem.info}.")
        return elem

    def press(self, key: str):
        """
        keyboard
        :param key: keyword name
        press_key("HOME")
        """
        log.info(f'✅ press key "{key}".')
        keycode = keycodes.get(key)
        Seldom.driver.press(keycode)
        return self

    def back(self):
        """go back"""
        log.info("✅ go back.")
        Seldom.driver.press(keycodes.get('back'))
        return self

    def home(self):
        """press home"""
        log.info("✅ press home.")
        Seldom.driver.press(keycodes.get('home'))
        return self

    @staticmethod
    def tap(x: int, y: int) -> None:
        """
        Tap on the coordinates
        :param x: x coordinates
        :param y: y coordinates
        :return:
        """
        log.info(f"✅ tap x={x},y={y}.")
        Seldom.driver.click(x=x, y=y)

    @staticmethod
    def swipe_up(times: int = 1, upper: bool = False, width: float = 0.5, start: float = 0.8,
                 end: float = 0.4) -> None:
        """
        swipe up
        """
        log.info(f"✅ Swipe up {times} times.")

        if upper is True:
            start = (start / 2)

        for _ in range(times):
            Seldom.driver.swipe(width, start, width, end)
            if times != 1:
                time.sleep(1)

    def swipe_up_find(self, times: int = 15, upper: bool = False, index: int = 0, **kwargs):

        swipe_times = 0
        wda_elem = WDAElement(**kwargs)
        log.info(f'✅ Swipe to find -> {wda_elem.desc}.')
        while not self.get_display(**kwargs, index=index):
            self.swipe_up(upper=upper)
            swipe_times += 1
            time.sleep(3.5)
            if swipe_times > times:
                raise NotFindElementError(f"❌ Find element error: swipe {times} times no find -> {wda_elem.desc}.")

    @staticmethod
    def swipe_down(times: int = 1, upper: bool = False, width: float = 0.5, start: float = 0.1,
                   end: float = 0.8) -> None:
        """
        swipe down
        """
        log.info(f"✅ Swipe down {times} times.")

        if upper is True:
            end = (end / 2)

        for _ in range(times):
            Seldom.driver.swipe(width, start, width, end)
            if times != 1:
                time.sleep(1)

    @staticmethod
    def swipe_left(times: int = 1, upper: bool = False, height: float = 0.9, start: float = 0.9,
                   end: float = 0.4) -> None:
        """swipe left"""
        log.info(f"✅ swipe left {times} times.")

        if upper is True:
            start = (start / 2)

        for _ in range(times):
            Seldom.driver.swipe(start, height, end, height)
            if times != 1:
                time.sleep(1)

    def swipe_left_find(self, times: int = 15, upper: bool = False, height: float = 0.9, index: int = None,
                        **kwargs) -> None:
        """
        向左滑动寻找元素

        Usage:
        self.swipe_left_find(text='login')
        """

        swipe_times = 0
        wda_elem = WDAElement(index=index, **kwargs)
        log.info(f'✅ {wda_elem.desc} -> swipe to find.')
        while not wda_elem.get_elements(index=index, empty=True, timeout=0.5):
            self.swipe_left(upper=upper, height=height)
            swipe_times += 1
            time.sleep(3.5)
            if swipe_times > times:
                raise NotFindElementError(f"❌ Find element error: swipe {times} times no find -> {wda_elem.desc}.")

    @staticmethod
    def swipe_right(times: int = 1, upper: bool = False, height: float = 0.9, start: float = 0.4,
                    end: float = 0.9) -> None:
        """swipe right"""
        log.info(f"✅ Swipe right {times} times.")

        if upper is True:
            end = (end / 2)

        for _ in range(times):
            Seldom.driver.swipe(start, height, end, height)
            if times != 1:
                time.sleep(1)

    @staticmethod
    def swipe_points(start_point: Tuple[float, float], end_point: Tuple[float, float], duration: int = 0.1):
        WDAObj.s.swipe(*start_point, *end_point, duration=duration)
        log.info(f'✅ Swipe from {start_point} to {end_point}.')

    @staticmethod
    def func(func_name, **kwargs):
        try:
            function = getattr(Seldom.driver, func_name)
            log.info(f"✅ New func {func_name}({kwargs}).")
            return function(**kwargs)
        except Exception as e:
            raise ValueError(f'❌ {func_name} is error -> {e}.')


wda_ = WDADriver()


@contextlib.contextmanager
def make_screenrecord(t=None, output_video_path='record.mp4'):
    """
    iOS录屏上下文管理器
    这里不指定帧率的话，默认只有10帧/s，但指定帧率视频容易变速
    """
    if t is None:
        t = WDAObj.t()

    # Read image from WDA mjpeg server
    pconn = t.create_inner_connection(9100)  # default WDA mjpeg server port
    sock = pconn.get_socket()
    buf = SocketBuffer(sock)
    buf.write(b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n")
    buf.read_until(b'\r\n\r\n')
    log.info(f"📷️ start_recording -> ({output_video_path}).")

    wr = imageio.get_writer(output_video_path)

    def _drain(stop_event, done_event):
        while not stop_event.is_set():
            # read http header
            length = None
            while True:
                line = buf.read_until(b'\r\n')
                if line.startswith(b"Content-Length"):
                    length = int(line.decode('utf-8').split(": ")[1])
                    break
            while True:
                if buf.read_until(b'\r\n') == b'':
                    break

            imdata = buf.read_bytes(length)
            im = imageio.imread(io.BytesIO(imdata))
            wr.append_data(im)
        done_event.set()

    stop_event = threading.Event()
    done_event = threading.Event()
    threading.Thread(name="screenrecord", target=_drain, args=(stop_event, done_event), daemon=True).start()
    yield
    stop_event.set()
    done_event.wait()
    wr.close()
    log.info(f"📷️ Record down.")
