import tidevice
from datetime import datetime
from tidevice._perf import DataType
from seldom_atx.utils.solox.apm import Memory, CPU, FPS
from seldom_atx.utils import cache
from seldom_atx.logging import log
from seldom_atx.running.config import Seldom
from seldom_atx.running.loader_hook import loader
from seldom_atx.running.config import AppDecorator


class MySoloX:
    """Only Android perf driver"""

    def __init__(self, pkg_name, device_id=None):
        device_id = device_id if device_id is not None else Seldom.device_id

        # if platform == Seldom.platform_name:
        #     wait_times = 0
        #     while wait_times <= 20:
        #         if u2.wait_app() != 0:
        #             break
        #         wait_times += 1
        #         log.info(f'❗ Unable to obtain pid,retry...{wait_times}.')
        #         time.sleep(0.5)
        self.mem = Memory(pkgName=pkg_name, deviceId=device_id)
        self.cpu = CPU(pkgName=pkg_name, deviceId=device_id)
        self.fps = FPS(pkgName=pkg_name, deviceId=device_id)

    def get_mem(self):
        """get mem info"""
        mem_list = []
        time_list = []
        try:
            while AppDecorator.threadLock:
                mem_res = self.mem.getAndroidMemory()
                now_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                log.trace(f'{now_time} : MEM{mem_res}')
                mem_list.append(tuple(mem_res))
                time_list.append(now_time)
        except Exception as e:
            cache.set({'PERF_ERROR': f"Error in get_mem: {e}"})

        return time_list, mem_list

    def get_cpu(self):
        """get cpu info"""
        cpu_list = []
        time_list = []
        try:
            while AppDecorator.threadLock:
                cpu_res = self.cpu.getAndroidCpuRate()
                now_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                log.trace(f'{now_time} : CPU{cpu_res}')
                cpu_list.append(tuple(cpu_res))
                time_list.append(now_time)
        except Exception as e:
            cache.set({'PERF_ERROR': f"Error in get_cpu: {e}"})

        return time_list, cpu_list

    def get_fps(self):
        """get fps info"""
        fps_list = []
        time_list = []
        try:
            while AppDecorator.threadLock:
                fps_res = self.fps.getAndroidFps()
                now_time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                log.trace(f'{now_time} : FPS{fps_res}')
                fps_list.append(tuple(fps_res))
                time_list.append(now_time)
        except Exception as e:
            cache.set({'PERF_ERROR': f"Error in get_fps: {e}"})

        return time_list, fps_list


class TidevicePerf:
    """Only iOS perf driver"""

    def __init__(self):
        self.t = tidevice.Device(udid=(loader("device_id") if loader("deviceId") is not None else None))
        self.perf = tidevice.Performance(self.t, [DataType.CPU, DataType.MEMORY, DataType.FPS])
        self.mem_list = []
        self.mem_time_list = []
        self.cpu_list = []
        self.cpu_time_list = []
        self.fps_list = []
        self.fps_time_list = []

    def callback(self, _type, value: dict):
        if _type.value == 'cpu':
            log.trace(f'cpu:{value}')
            self.cpu_time_list.append(
                str(((datetime.fromtimestamp(value['timestamp'] / 1000)).strftime('%H:%M:%S.%f'))[:-3]))
            self.cpu_list.append((round(value['value'], 2), round(value['sys_value'], 2)))
        elif _type.value == 'memory':
            log.trace(f'mem:{value}')
            self.mem_time_list.append(
                str(((datetime.fromtimestamp(value['timestamp'] / 1000)).strftime('%H:%M:%S.%f'))[:-3]))
            self.mem_list.append((round(value['value'], 2), 0, 0))
        elif _type.value == 'fps':
            log.trace(f'fps:{value}')
            self.fps_time_list.append(
                str(((datetime.fromtimestamp(value['timestamp'] / 1000)).strftime('%H:%M:%S.%f'))[:-3]))
            self.fps_list.append((value['value'], 0))

    def start(self, pkg_name=None):
        pkg_name = pkg_name if pkg_name is not None else Seldom.app_package
        self.mem_list = []
        self.mem_time_list = []
        self.cpu_list = []
        self.cpu_time_list = []
        self.fps_list = []
        self.fps_time_list = []
        self.perf.start(bundle_id=pkg_name, callback=self.callback)

    def stop(self):
        self.perf.stop()
        cache.set({'CPU_INFO': (self.cpu_time_list, self.cpu_list)})
        cache.set({'MEM_INFO': (self.mem_time_list, self.mem_list)})
        cache.set({'FPS_INFO': (self.fps_time_list, self.fps_list)})
