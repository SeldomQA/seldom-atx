import datetime
import re
import time
from seldom_atx.logging import log
from seldom_atx.utils.solox.adb import adb
from seldom_atx.utils.solox.common import Devices, Platform
from seldom_atx.utils.solox.android_fps import FPSMonitor, TimeUtils

d = Devices()


class Target:
    CPU = 'cpu'
    Memory = 'memory'
    MemoryDetail = 'memory_detail'
    Battery = 'battery'
    Network = 'network'
    FPS = 'fps'
    GPU = 'gpu'


class CPU(object):

    def __init__(self, pkgName, deviceId, platform=Platform.Android, pid=None):
        self.pkgName = pkgName
        self.deviceId = deviceId
        self.platform = platform
        self.pid = pid
        if self.pid is None and self.platform == Platform.Android:
            self.pid = d.getPid(pkgName=self.pkgName, deviceId=self.deviceId)[0].split(':')[0]

    def getprocessCpuStat(self):
        """get the cpu usage of a process at a certain time"""
        cmd = 'cat /proc/{}/stat'.format(self.pid)
        result = adb.shell(cmd=cmd, deviceId=self.deviceId)
        r = re.compile("\\s+")
        toks = r.split(result)
        processCpu = float(toks[13]) + float(toks[14]) + float(toks[15]) + float(toks[16])
        return processCpu

    def getTotalCpuStat(self):
        """get the total cpu usage at a certain time"""
        cmd = 'cat /proc/stat |{} ^cpu'.format(d.filterType())
        result = adb.shell(cmd=cmd, deviceId=self.deviceId)
        totalCpu = 0
        lines = result.split('\n')
        for line in lines:
            toks = line.split()
            if toks[1] in ['', ' ']:
                toks.pop(1)
            for i in range(1, 8):
                totalCpu += float(toks[i])
        return float(totalCpu)

    def getCpuCores(self):
        """get Android cpu cores"""
        cmd = 'cat /sys/devices/system/cpu/online'
        result = adb.shell(cmd=cmd, deviceId=self.deviceId)
        try:
            nums = int(result.split('-')[1]) + 1
        except:
            nums = 1
        return nums

    def getSysCpuStat(self):
        """get the total cpu usage at a certain time"""
        cmd = 'cat /proc/stat |{} ^cpu'.format(d.filterType())
        result = adb.shell(cmd=cmd, deviceId=self.deviceId)
        r = re.compile(r"(?<!cpu\d+)")
        toks = r.findall(result)
        print(toks)
        idleCpu = float(toks[4])
        sysCpu = self.getTotalCpuStat() - idleCpu
        return sysCpu

    def getIdleCpuStat(self):
        """get the total cpu usage at a certain time"""
        cmd = 'cat /proc/stat |{} ^cpu'.format(d.filterType())
        result = adb.shell(cmd=cmd, deviceId=self.deviceId)
        ileCpu = 0
        lines = result.split('\n')
        for line in lines:
            toks = line.split()
            if toks[1] in ['', ' ']:
                toks.pop(1)
            ileCpu += float(toks[4])
        return ileCpu

    def getAndroidCpuRate(self):
        """get the Android cpu rate of a process"""
        try:
            processCpuTime_1 = self.getprocessCpuStat()
            totalCpuTime_1 = self.getTotalCpuStat()
            idleCputime_1 = self.getIdleCpuStat()
            time.sleep(0.5)
            processCpuTime_2 = self.getprocessCpuStat()
            totalCpuTime_2 = self.getTotalCpuStat()
            idleCputime_2 = self.getIdleCpuStat()
            appCpuRate = round(float((processCpuTime_2 - processCpuTime_1) / (totalCpuTime_2 - totalCpuTime_1) * 100),
                               2)
            sysCpuRate = round(float(((totalCpuTime_2 - idleCputime_2) - (totalCpuTime_1 - idleCputime_1)) / (
                    totalCpuTime_2 - totalCpuTime_1) * 100), 2)
        except Exception as e:
            appCpuRate, sysCpuRate = 0, 0
            if len(d.getPid(self.deviceId, self.pkgName)) == 0:
                log.error('[CPU] {} : No process found'.format(self.pkgName))
            else:
                log.exception(e)
        return appCpuRate, sysCpuRate


class Memory(object):
    def __init__(self, pkgName, deviceId, platform=Platform.Android, pid=None):
        self.pkgName = pkgName
        self.deviceId = deviceId
        self.platform = platform
        self.pid = pid
        if self.pid is None and self.platform == Platform.Android:
            self.pid = d.getPid(pkgName=self.pkgName, deviceId=self.deviceId)[0].split(':')[0]

    def getAndroidMemory(self):
        """Get the Android memory ,unit:MB"""
        try:
            cmd = 'dumpsys meminfo {}'.format(self.pid)
            output = adb.shell(cmd=cmd, deviceId=self.deviceId)
            m_total = re.search(r'TOTAL\s*(\d+)', output)
            if not m_total:
                m_total = re.search(r'TOTAL PSS:\s*(\d+)', output)
            m_swap = re.search(r'TOTAL SWAP PSS:\s*(\d+)', output)
            if not m_swap:
                m_swap = re.search(r'TOTAL SWAP (KB):\s*(\d+)', output)
            totalPass = round(float(float(m_total.group(1))) / 1024, 2)
            swapPass = round(float(float(m_swap.group(1))) / 1024, 2)
        except Exception as e:
            totalPass, swapPass = 0, 0
            if len(d.getPid(self.deviceId, self.pkgName)) == 0:
                log.error('[Memory] {} : No process found'.format(self.pkgName))
            else:
                log.exception(e)
        return totalPass, swapPass

    def getAndroidMemoryDetail(self):
        """Get the Android detail memory ,unit:MB"""
        try:
            cmd = 'dumpsys meminfo {}'.format(self.pid)
            output = adb.shell(cmd=cmd, deviceId=self.deviceId)
            m_java = re.search(r'Java Heap:\s*(\d+)', output)
            m_native = re.search(r'Native Heap:\s*(\d+)', output)
            m_code = re.search(r'Code:\s*(\d+)', output)
            m_stack = re.search(r'Stack:\s*(\d+)', output)
            m_graphics = re.search(r'Graphics:\s*(\d+)', output)
            m_private = re.search(r'Private Other:\s*(\d+)', output)
            m_system = re.search(r'System:\s*(\d+)', output)
            java_heap = round(float(float(m_java.group(1))) / 1024, 2)
            native_heap = round(float(float(m_native.group(1))) / 1024, 2)
            code_pss = round(float(float(m_code.group(1))) / 1024, 2)
            stack_pss = round(float(float(m_stack.group(1))) / 1024, 2)
            graphics_pss = round(float(float(m_graphics.group(1))) / 1024, 2)
            private_pss = round(float(float(m_private.group(1))) / 1024, 2)
            system_pss = round(float(float(m_system.group(1))) / 1024, 2)
            memory_dict = dict(
                java_heap=java_heap,
                native_heap=native_heap,
                code_pss=code_pss,
                stack_pss=stack_pss,
                graphics_pss=graphics_pss,
                private_pss=private_pss,
                system_pss=system_pss
            )
        except Exception as e:
            memory_dict = dict(
                java_heap=0,
                native_heap=0,
                code_pss=0,
                stack_pss=0,
                graphics_pss=0,
                private_pss=0,
                system_pss=0
            )
            if len(d.getPid(self.deviceId, self.pkgName)) == 0:
                log.error('[Memory Detail] {} : No process found'.format(self.pkgName))
            else:
                log.exception(e)
        return memory_dict

    def getProcessMemory(self):
        """Get the app memory"""
        totalPass, swapPass = self.getAndroidMemory()
        return totalPass, swapPass


class Battery(object):
    def __init__(self, deviceId, platform=Platform.Android):
        self.deviceId = deviceId
        self.platform = platform

    def getAndroidBattery(self):
        """Get android battery info, unit:%"""
        # Switch mobile phone battery to non-charging state
        self.recoverBattery()
        cmd = 'dumpsys battery set status 1'
        adb.shell(cmd=cmd, deviceId=self.deviceId)
        # Get phone battery info
        cmd = 'dumpsys battery'
        output = adb.shell(cmd=cmd, deviceId=self.deviceId)
        level = int(re.findall(u'level:\s?(\d+)', output)[0])
        temperature = int(re.findall(u'temperature:\s?(\d+)', output)[0]) / 10
        return level, temperature

    def recoverBattery(self):
        """Reset phone charging status"""
        cmd = 'dumpsys battery reset'
        adb.shell(cmd=cmd, deviceId=self.deviceId)


class Network(object):

    def __init__(self, pkgName, deviceId, platform=Platform.Android, pid=None):
        self.pkgName = pkgName
        self.deviceId = deviceId
        self.platform = platform
        self.pid = pid
        if self.pid is None and self.platform == Platform.Android:
            self.pid = d.getPid(pkgName=self.pkgName, deviceId=self.deviceId)[0].split(':')[0]

    def getAndroidNet(self, wifi=True):
        """Get Android send/recv data, unit:KB wlan0/rmnet0"""
        try:
            net = 'wlan0' if wifi else 'rmnet0'
            cmd = 'cat /proc/{}/net/dev |{} {}'.format(self.pid, d.filterType(), net)
            output_pre = adb.shell(cmd=cmd, deviceId=self.deviceId)
            if not wifi and not output_pre:
                for phone_net in ['rmnet_data0', 'rmnet_ipa0', 'ccmni0']:
                    cmd = f'cat /proc/{self.pid}/net/dev |{d.filterType()} {net}'
                    output_pre = adb.shell(cmd=cmd, deviceId=self.deviceId)
                    if output_pre:
                        net = phone_net
                        break
            m_pre = re.search(r'{}:\s*(\d+)\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*(\d+)'.format(net), output_pre)
            sendNum_pre = round(float(float(m_pre.group(2)) / 1024), 2)
            recNum_pre = round(float(float(m_pre.group(1)) / 1024), 2)
            time.sleep(0.5)
            output_final = adb.shell(cmd=cmd, deviceId=self.deviceId)
            m_final = re.search(r'{}:\s*(\d+)\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*(\d+)'.format(net),
                                output_final)
            sendNum_final = round(float(float(m_final.group(2)) / 1024), 2)
            recNum_final = round(float(float(m_final.group(1)) / 1024), 2)
            sendNum = round(float(sendNum_final - sendNum_pre), 2)
            recNum = round(float(recNum_final - recNum_pre), 2)
        except Exception as e:
            sendNum, recNum = 0, 0
            if len(d.getPid(self.deviceId, self.pkgName)) == 0:
                log.error('[Network] {} : No process found'.format(self.pkgName))
            else:
                log.exception(e)
        return sendNum, recNum

    def setAndroidNet(self, wifi=True):
        try:
            net = 'wlan0' if wifi else 'rmnet0'
            cmd = f'cat /proc/{self.pid}/net/dev |{d.filterType()} {net}'
            output_pre = adb.shell(cmd=cmd, deviceId=self.deviceId)
            if not wifi and not output_pre:
                for phone_net in ['rmnet_data0', 'rmnet_ipa0', 'ccmni0']:
                    cmd = f'cat /proc/{self.pid}/net/dev |{d.filterType()} {net}'
                    output_pre = adb.shell(cmd=cmd, deviceId=self.deviceId)
                    if output_pre:
                        net = phone_net
                        break
            m = re.search(r'{}:\s*(\d+)\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*(\d+)'.format(net), output_pre)
            sendNum = round(float(float(m.group(2)) / 1024), 2)
            recNum = round(float(float(m.group(1)) / 1024), 2)
        except Exception as e:
            sendNum, recNum = 0, 0
            if len(d.getPid(self.deviceId, self.pkgName)) == 0:
                log.error('[Network] {} : No process found'.format(self.pkgName))
            else:
                log.exception(e)
        return sendNum, recNum


class FPS(object):
    AndroidFPS = None

    @classmethod
    def getObject(cls, *args, **kwargs):
        if kwargs['platform'] == Platform.Android:
            if cls.AndroidFPS is None:
                cls.AndroidFPS = FPS(*args, **kwargs)
            return cls.AndroidFPS
        return FPS(*args, **kwargs)

    @classmethod
    def clear(cls):
        cls.AndroidFPS = None

    def __init__(self, pkgName, deviceId, platform=Platform.Android, surfaceview=True):
        self.pkgName = pkgName
        self.deviceId = deviceId
        self.platform = platform
        self.surfaceview = surfaceview
        self.apm_time = datetime.datetime.now().strftime('%H:%M:%S.%f')
        self.monitors = None

    def getAndroidFps(self):
        """get Android Fps, unit:HZ"""
        try:
            monitors = FPSMonitor(device_id=self.deviceId, package_name=self.pkgName, frequency=1,
                                  surfaceview=self.surfaceview, start_time=TimeUtils.getCurrentTimeUnderline())
            monitors.start()
            fps, jank = monitors.stop()
        except Exception as e:
            fps, jank = 0, 0
            if len(d.getPid(self.deviceId, self.pkgName)) == 0:
                log.error('[FPS] {} : No process found'.format(self.pkgName))
            else:
                log.exception(e)
        return fps, jank
