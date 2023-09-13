import os
import time
import base64
from typing import Tuple
from datetime import datetime
from seldom_atx.logging import log
from seldom_atx.testdata import get_word
from seldom_atx.running.config import Seldom, AppConfig
from seldom_atx.logging.exceptions import NotFindElementError

__all__ = ["U2Driver", "U2Element", "u2"]

keycodes = {
    'HOME': 'home',
    'BACK': 'back',
    'LEFT': 'left',
    'ENTER': 'enter',
}

LOCATOR_LIST = {
    'resourceId': "resourceId",
    'name': "name",
    'xpath': "xpath",
    'text': 'text',
    'className': "className",
}


class U2Element:
    """元素类"""

    def __init__(self, **kwargs) -> None:
        """元素初始化检查"""
        if not kwargs:
            raise ValueError("Please specify a locator.")
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

    def get_elements(self, index: int = None, empty: bool = False, timeout: float = None):
        """获取元素"""
        try:
            if self.desc:
                self.desc = f'desc={self.desc}'
            else:
                self.desc = ', '.join([f"{k}={v}" for k, v in self.kwargs.items()])
            if timeout:
                u2.implicitly_wait(timeout=timeout, noLog=True)
            if index:
                if 'xpath' in self.kwargs:
                    elems = Seldom.driver.xpath(**self.kwargs).all()[index]
                else:
                    elems = Seldom.driver(**self.kwargs)[index]
            else:
                if 'xpath' in self.kwargs:
                    elems = Seldom.driver.xpath(**self.kwargs)
                else:
                    elems = Seldom.driver(**self.kwargs)
            if timeout:
                u2.implicitly_wait(timeout=Seldom.timeout, noLog=True)
        except Exception as e:
            if empty is False:
                raise NotFindElementError(f"❌ Find error: {self.desc} -> {e}.")
            else:
                return []
        if not empty:
            self.find_elem_info = f"Find element: {self.desc}."
        return elems

    @property
    def info(self):
        """return element info"""
        return self.find_elem_info

    @property
    def warn(self):
        """return element warn"""
        return self.find_elem_warn


class U2Driver:
    """Android驱动"""

    @staticmethod
    def implicitly_wait(timeout: float = None, noLog: bool = False) -> None:
        """设置元素隐式等待"""

        if not timeout:
            timeout = Seldom.timeout
        Seldom.driver.implicitly_wait(timeout)
        if not noLog:
            log.info(f'✅ Set implicitly wait -> {timeout}s.')

    @staticmethod
    def install_app(app_path: str) -> None:
        """安装指定应用"""

        os.system(f'adb install -g {app_path}')
        log.info(f'✅ {app_path} -> Install APP.')

    @staticmethod
    def remove_app(package_name: str = None) -> None:
        """卸载指定应用"""

        if not package_name:
            package_name = Seldom.appPackage
        Seldom.driver.app_uninstall(package_name)
        log.info(f'✅ {package_name} -> Remove APP.')

    @staticmethod
    def launch_app(package_name: str = None, stop: bool = False) -> None:
        """启动指定应用"""

        if not package_name:
            package_name = Seldom.appPackage
        log.info(f'✅ {package_name} -> Launch APP, STOP={stop}.')
        Seldom.driver.app_start(package_name=package_name, stop=stop)

    @staticmethod
    def close_app(package_name: str = None) -> None:
        """关闭指定应用"""
        if not package_name:
            package_name = Seldom.appPackage
        log.info(f'✅ {package_name} -> Close APP.')
        Seldom.driver.app_stop(package_name)

    @staticmethod
    def close_app_all() -> None:
        """关闭所有应用"""
        Seldom.driver.app_stop_all()
        log.info('✅ Close all APP.')

    @staticmethod
    def clear_app(package_name: str = None) -> None:
        """清除APP数据"""
        if not package_name:
            package_name = Seldom.appPackage
        Seldom.driver.app_clear(package_name)
        log.info(f'✅ {package_name} -> Clear APP.')

    @staticmethod
    def wait_app(package_name: str = None) -> int:
        """等待APP运行"""
        if not package_name:
            package_name = Seldom.appPackage
        log.info(f'✅ {package_name} -> wait APP run.')
        pid = Seldom.driver.app_wait(package_name)
        return pid

    def set_text(self, text: str, clear: bool = False, enter: bool = False, click: bool = False, index: int = None,
                 **kwargs) -> None:
        """输入元素文本"""
        if clear is True:
            self.clear_text(index, **kwargs)
        if click is True:
            self.click(index, **kwargs)
            time.sleep(0.5)
        u2_elem = U2Element(**kwargs)
        elem = u2_elem.get_elements(index=index)
        log.info(f"✅ {u2_elem.info} -> input [{text}].")
        elem.set_text(text)
        if enter is True:
            elem.press('enter')

    @staticmethod
    def clear_text(index: int = None, **kwargs) -> None:
        """清空元素文本"""
        u2_elem = U2Element(**kwargs)
        elem = u2_elem.get_elements(index=index)
        log.info(f"✅ {u2_elem.info} -> clear input.")
        elem.clear_text()

    @staticmethod
    def click(index: int = None, **kwargs) -> None:
        """点击元素"""
        u2_elem = U2Element(**kwargs)
        elem = u2_elem.get_elements(index=index)
        elem.click()
        log.info(f"✅ {u2_elem.info} -> click.")

    @staticmethod
    def click_text(text: str, index: int = None) -> None:
        """点击文本元素"""
        u2_elem = U2Element(text=text)
        elem = u2_elem.get_elements(index=index)
        elem.click()
        log.info(f"✅ {u2_elem.info} -> click text.")

    @staticmethod
    def get_text(index: int = None, **kwargs) -> str:
        """获取元素文本"""
        u2_elem = U2Element(**kwargs)
        elem = u2_elem.get_elements(index=index)
        text = elem.get_text()
        log.info(f"✅ {u2_elem.info} -> text: {text}.")
        return text

    def get_text_page(self, stable=False):
        """
        获取页面所有元素的文本内容
        """
        if stable:
            self.wait_stable()
        try:
            texts = []
            for i in Seldom.driver.xpath('//android.widget.TextView|//android.widget.Button').all():
                texts.append(i.text.strip())
            log.info(f"✅ All text on the current page -> {texts}.")
            return texts
        except Exception as err:
            return err

    @staticmethod
    def get_display(index: int = None, timeout: float = 1.0, **kwargs) -> bool:
        """获取元素可见状态"""
        u2_elem = U2Element(**kwargs)
        elem = u2_elem.get_elements(index=index, empty=True, timeout=timeout)
        if not elem:
            return False
        else:
            result = elem.exists
            log.info(f"✅ {u2_elem.info} -> display: {result}.")
            return result

    def wait(self, timeout: int = Seldom.timeout, index: int = None, noLog: bool = False, **kwargs) -> bool:
        """等待元素出现"""
        u2_elem = U2Element(**kwargs)
        timeout_backups = Seldom.timeout
        Seldom.timeout = timeout
        if noLog is not True:
            log.info(f"⌛ {u2_elem.desc} -> wait element: {timeout}s.")
        try:
            u2_elem.get_elements(empty=kwargs.get('empty', False), index=index).wait(timeout=timeout)
            result = True
        except:
            if noLog is False:
                log.warning(f"❌ {u2_elem.desc} -> not exist.")
            self.save_screenshot(report=True)
            result = False
        Seldom.timeout = timeout_backups
        return result

    def wait_gone(self, timeout: int = None, index: int = None, **kwargs) -> bool:
        """等待元素消失"""
        if not timeout:
            timeout = Seldom.timeout
        u2_elem = U2Element(**kwargs)
        elem = u2_elem.get_elements(empty=kwargs.get('empty', False), index=index)
        log.info(f"⌛ {u2_elem.desc} -> wait gone: {timeout}s.")
        result = elem.wait_gone(timeout=timeout)
        if not result:
            log.warning(f'❌ {u2_elem.desc} -> wait gone failed.')
            self.save_screenshot(report=True)
        return result

    def wait_stable(self, interval: float = 1.0, retry: int = 10, timeout: float = 20.0) -> bool:
        """等待页面稳定"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            for _ in range(retry):
                first_snapshot = Seldom.driver.dump_hierarchy()
                time.sleep(interval)
                second_snapshot = Seldom.driver.dump_hierarchy()
                if first_snapshot == second_snapshot:
                    return True
                else:
                    log.info('⌛ Wait page stable...')
        self.save_screenshot(report=True)
        raise EnvironmentError("❌ Unstable page.")

    @staticmethod
    def start_recording(output: str = None, fps: int = None) -> None:
        """开始录屏"""
        if output is None:
            log.warning('Please set the storage location for screen recording')
            output = 'record.mp4'
        if fps is None:
            fps = AppConfig.FPS
        log.info(f"📷️ start_recording -> ({output}).")
        Seldom.driver.screenrecord(output, fps=fps)

    @staticmethod
    def stop_recording() -> None:
        """结束录屏"""
        log.info(f"📷️ record down.")
        Seldom.driver.screenrecord.stop()

    @staticmethod
    def save_screenshot(file_path: str = None, report: bool = False) -> None:
        """保存截图"""
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
    def write_log(save_path: str = None) -> None:
        """获取Android日志，并通过修改AppConfig.log=False来停止获取"""
        if not save_path:
            save_path = os.path.join(AppConfig.PERF_RUN_FOLDER,
                                     f'{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.txt')
        if not os.path.exists(save_path):
            open(save_path, "w").close()
        try:
            Seldom.driver.shell('logcat -c')
            cmd = Seldom.driver.shell(f"logcat", stream=True)
            log_list = []
            for line in cmd.iter_lines():
                try:
                    log_list.append(line.decode('utf-8'))
                except Exception as e:
                    log.error(f'❗ Error in read log: {e}, but skip!')
                if not AppConfig.log:
                    break
            if not AppConfig.log:
                cmd.close()
            with open(save_path, "w") as f:
                for item in log_list:
                    try:
                        f.write(item + "\n")
                    except Exception as e:
                        log.warning(f'❗ Error in write log: [{e}], but skip!')
            log.info(f'✅ Log saved in {save_path}')
        except Exception as e:
            raise Exception(f'❌ Error in write_log: {e}.')

    @staticmethod
    def open_quick_settings():
        """
        打开状态栏快速设置
        """
        Seldom.driver.open_quick_settings()
        log.info(f'✅ open quick settings.')

    @staticmethod
    def get_elements(**kwargs):
        """获取元素们对象"""
        u2_elem = U2Element(**kwargs)
        elems = u2_elem.get_elements(empty=True)
        if len(elems) == 0:
            log.warning(f"{u2_elem.warn}.")
        else:
            log.info(f"✅ {u2_elem.info}.")
        return elems

    @staticmethod
    def get_element(index: int = None, **kwargs):
        """获取元素对象"""
        u2_elem = U2Element(**kwargs)
        elem = u2_elem.get_elements(index=index)
        log.info(f"✅ {u2_elem.info}.")
        return elem

    @staticmethod
    def press(key: str) -> None:
        """按下key"""
        log.info(f'✅ Press key -> "{key}".')
        keycode = keycodes.get(key)
        Seldom.driver.press(keycode)

    @staticmethod
    def back() -> None:
        """按下物理返回键"""
        log.info("✅ Go back.")
        Seldom.driver.press(keycodes.get('back'))

    @staticmethod
    def home() -> None:
        """按下物理home键"""
        log.info("✅ Press home.")
        Seldom.driver.press(keycodes.get('home'))

    @staticmethod
    def size() -> dict:
        """获取屏幕尺寸"""
        size = Seldom.driver.window_size()
        log.info(f"✅ Screen resolution: {size}.")
        return size

    @staticmethod
    def tap(x: int, y: int) -> None:
        """按下坐标点"""
        log.info(f"✅ tap x={x},y={y}.")
        Seldom.driver.click(x=x, y=y)

    @staticmethod
    def swipe_up(times: int = 1, upper: bool = False, width: float = 0.5, start: float = 0.9,
                 end: float = 0.1) -> None:
        """向上滑动"""
        log.info(f"✅ swipe up {times} times.")

        if upper is True:
            start = (start / 2)

        for _ in range(times):
            Seldom.driver.swipe(width, start, width, end)
            if times != 1:
                time.sleep(1)

    def swipe_up_find(self, times: int = 15, upper: bool = False, index: int = None, **kwargs) -> None:
        """
        向上滑动寻找元素

        Usage:
        self.swipe_up_find_u2(elem=ElemObj)
        self.swipe_up_find_u2(text='login')
        """

        swipe_times = 0
        u2_elem = U2Element(index=index, **kwargs)
        log.info(f'✅ {u2_elem.desc} -> swipe to find.')
        while not self.get_display(**kwargs):
            self.swipe_up(upper=upper)
            swipe_times += 1
            if swipe_times > times:
                raise NotFindElementError(f"❌ Find element error: swipe {times} times no find -> {u2_elem.desc}.")

    @staticmethod
    def swipe_down(times: int = 1, upper: bool = False, width: float = 0.5, start: float = 0.1,
                   end: float = 0.9) -> None:
        """swipe down"""
        log.info(f"✅ swipe down {times} times.")

        if upper is True:
            end = (end / 2)

        for _ in range(times):
            Seldom.driver.swipe(width, start, width, end)
            if times != 1:
                time.sleep(1)

    @staticmethod
    def swipe_left(times: int = 1, upper: bool = False, height: float = 0.9, start: float = 0.9,
                   end: float = 0.1) -> None:
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
        self.swipe_left_find(elem=ElemObj)
        self.swipe_left_find(text='login')
        """

        swipe_times = 0
        u2_elem = U2Element(index=index, **kwargs)
        log.info(f'✅ {u2_elem.desc} -> swipe to find.')
        while not self.get_display(**kwargs):
            self.swipe_left(upper=upper, height=height)
            swipe_times += 1
            if swipe_times > times:
                raise NotFindElementError(f"❌ Find element error: swipe {times} times no find -> {u2_elem.desc}.")

    @staticmethod
    def swipe_right(times: int = 1, upper: bool = False, height: float = 0.9, start: float = 0.1,
                    end: float = 0.9) -> None:
        """swipe right"""
        log.info(f"✅ swipe right {times} times.")

        if upper is True:
            end = (end / 2)

        for _ in range(times):
            Seldom.driver.swipe(start, height, end, height)
            if times != 1:
                time.sleep(1)

    @staticmethod
    def swipe_points(start_point: Tuple[float, float], end_point: Tuple[float, float], duration: int = 0.1):
        Seldom.driver.swipe_points([start_point, end_point], duration=duration)
        log.info(f'✅ Swipe from {start_point} to {end_point}.')

    @staticmethod
    def screen_on() -> None:
        if not Seldom.driver.info.get('screenOn'):
            Seldom.driver.screen_on()
            log.info('✅ Screen ON.')

    @staticmethod
    def open_url(url) -> None:
        Seldom.driver.open_url(url)
        log.info(f'✅ Open {url}.')

    @staticmethod
    def icon_save(save_path: str = None, package_name: str = None) -> str:
        """
        save app icon
        """
        if not package_name:
            package_name = Seldom.appPackage
        if not save_path:
            save_path = os.path.join(AppConfig.PERF_OUTPUT_FOLDER, f'{package_name}.png')
        Seldom.driver.app_icon(package_name).save(save_path)
        log.info(f'✅ Icon saved: {save_path}.')
        return save_path

    @staticmethod
    def app_info(package_name: str = None) -> str:
        if not package_name:
            package_name = Seldom.appPackage
        info = Seldom.driver.app_info(package_name)
        log.info(f'✅ {package_name} -> info: {info}.')
        return info

    @staticmethod
    def push(file, path):
        """
        将文件推送到设备
        :param file: 电脑文件地址
        :param path: Android目标路径
        :return:
        """
        Seldom.driver.push(file, path)
        log.info(f'✅ Push file {file} to {path}.')

    @staticmethod
    def pull(file, path):
        """
        从设备中拉取文件
        :param file: 手机文件地址
        :param path: 电脑存放位置
        :return:
        """
        Seldom.driver.pull(file, path)
        log.info(f'✅ Pull file {file} to {path}.')

    @staticmethod
    def delete(path):
        """
        删除设备上的文件or文件夹
        :param path: 如果是一个文件则删除文件，如果是一个文件夹则删除文件夹下所有文件
        :return:
        """
        if Seldom.driver.shell(f'test -d "{path}" && echo "directory"').output.strip() == 'directory':
            Seldom.driver.shell(f'rm -rf {path}/*')
            log.info(f"✅ Directory {path} is deleted.")
        elif Seldom.driver.shell(f'test -f "{path}" && echo "file"').output.strip() == 'file':
            Seldom.driver.shell(f'rm {path}')
            log.info(f"✅ File {path} is deleted.")
        else:
            log.error(f"❌ Path {path} is not exist.")

    @staticmethod
    def func(func_name, **kwargs):
        """如果遇到没有封装的u2的api，可以使用本方法来调用."""
        try:
            function = getattr(Seldom.driver, func_name)
            log.info(f"✅ New func {func_name}({kwargs}).")
            return function(**kwargs)
        except Exception as e:
            raise ValueError(f'❌ {func_name} is error -> {e}.')

    @staticmethod
    def register_watch(args: list, name: str = None) -> str:
        """when all element exist than click"""
        if not name:
            name = get_word()
        watcher = Seldom.driver.watcher(name)
        value_list = []
        for elem in args:
            ele = U2Element(**elem)
            by, value = list(ele.kwargs.items())[0]
            if by == 'xpath':
                watcher.when(value)
                value_list.append(value)
            elif by == 'text':
                watcher.when(value)
                value_list.append(value)
            else:
                log.warning(f'❌ {by}={value} type must between "xpath" and "text".')
        if not value_list:
            raise ValueError(f'❌ Not right element be register!')
        else:
            log.info(f'✅ Register watch -> {name}={value_list}.')
            watcher.click()
            return name

    def start_watcher(self, args: list = None, name: str = None, time_interval: float = 0.5) -> str:
        name = self.register_watch(name=name, args=args)
        Seldom.driver.watcher.start(time_interval)
        log.info(f'✅ Start watch -> {name}.')
        return name

    @staticmethod
    def stop_all_watcher():
        Seldom.driver.watcher.stop()
        log.info(f'✅ Stop all watch.')

    @staticmethod
    def remove_watcher(name: str):
        Seldom.driver.watcher.remove(name)
        log.info(f'✅ Remove watch -> {name}.')


u2 = U2Driver()
