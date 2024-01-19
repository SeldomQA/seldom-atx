#!/usr/bin/python
# encoding=utf-8
import os
import platform
import re
from logzero import logger
import socket
from tidevice._device import Device
from tidevice import Usbmux
from seldom_atx.utils.solox.adb import adb


class Platform:
    Android = 'Android'
    iOS = 'iOS'
    Mac = 'MacOS'
    Windows = 'Windows'


class Devices:

    def __init__(self, platform=Platform.Android):
        self.platform = platform
        self.adb = adb.adb_path

    def execCmd(self, cmd):
        """Execute the command to get the terminal print result"""
        r = os.popen(cmd)
        try:
            text = r.buffer.read().decode(encoding='gbk').replace('\x1b[0m', '').strip()
        except UnicodeDecodeError:
            text = r.buffer.read().decode(encoding='utf-8').replace('\x1b[0m', '').strip()
        finally:
            r.close()
        return text

    def filterType(self):
        """Select the pipe filtering method according to the system"""
        filtertype = ('grep', 'findstr')[platform.system() == Platform.Windows]
        return filtertype

    def getDeviceIds(self):
        """Get all connected device ids"""
        Ids = list(os.popen(f"{self.adb} devices").readlines())
        deviceIds = []
        for i in range(1, len(Ids) - 1):
            id, state = Ids[i].strip().split()
            if state == 'device':
                deviceIds.append(id)
        return deviceIds

    def getDevicesName(self, deviceId):
        """Get the device name of the Android corresponding device ID"""
        try:
            devices_name = os.popen(f'{self.adb} -s {deviceId} shell getprop ro.product.model').readlines()[0].strip()
        except Exception:
            devices_name = os.popen(f'{self.adb} -s {deviceId} shell getprop ro.product.model').buffer.readlines()[
                0].decode("utf-8").strip()
        return devices_name

    def getDevices(self):
        """Get all Android devices"""
        DeviceIds = self.getDeviceIds()
        Devices = [f'{id}({self.getDevicesName(id)})' for id in DeviceIds]
        logger.info('Connected devices: {}'.format(Devices))
        return Devices

    def getIdbyDevice(self, deviceinfo, platform):
        """Obtain the corresponding device id according to the Android device information"""
        if platform == Platform.Android:
            deviceId = re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", deviceinfo)
            if deviceId not in self.getDeviceIds():
                raise Exception('no device found')
        else:
            deviceId = deviceinfo
        return deviceId

    def getSdkVersion(self, deviceId):
        version = adb.shell(cmd='getprop ro.build.version.sdk', deviceId=deviceId)
        return version

    def getPid(self, deviceId, pkgName):
        """Get the pid corresponding to the Android package name"""
        try:
            sdkversion = self.getSdkVersion(deviceId)
            if sdkversion and int(sdkversion) < 26:
                result = os.popen(f"{self.adb} -s {deviceId} shell ps | {self.filterType()} {pkgName}").readlines()
                processList = ['{}:{}'.format(process.split()[1], process.split()[8]) for process in result]
            else:
                result = os.popen(f"{self.adb} -s {deviceId} shell ps -ef | {self.filterType()} {pkgName}").readlines()
                processList = ['{}:{}'.format(process.split()[1], process.split()[7]) for process in result]
            for i in range(len(processList)):
                if processList[i].count(':') == 1:
                    index = processList.index(processList[i])
                    processList.insert(0, processList.pop(index))
                    break
            if len(processList) == 0:
                # self.getPid(deviceId=deviceId,pkgName=pkgName)
                logger.warning('{}: no pid found'.format(pkgName))
        except Exception as e:
            processList = []
            logger.exception(e)
        return processList

    def checkPkgname(self, pkgname):
        flag = True
        replace_list = ['com.google']
        for i in replace_list:
            if i in pkgname:
                flag = False
        return flag

    def getPkgname(self, deviceId):
        """Get all package names of Android devices"""
        pkginfo = os.popen(f"{self.adb} -s {deviceId} shell pm list packages --user 0")
        pkglist = [p.lstrip('package').lstrip(":").strip() for p in pkginfo]
        if pkglist.__len__() > 0:
            return pkglist
        else:
            pkginfo = os.popen(f"{self.adb} -s {deviceId} shell pm list packages")
            pkglist = [p.lstrip('package').lstrip(":").strip() for p in pkginfo]
            return pkglist

    def getDeviceInfoByiOS(self):
        """Get a list of all successfully connected iOS devices"""
        deviceInfo = [udid for udid in Usbmux().device_udid_list()]
        logger.info('Connected devices: {}'.format(deviceInfo))
        return deviceInfo

    def getPkgnameByiOS(self, udid):
        """Get all package names of the corresponding iOS device"""
        d = Device(udid)
        pkgNames = [i.get("CFBundleIdentifier") for i in d.installation.iter_installed(app_type="User")]
        return pkgNames

    def get_pc_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            logger.error('get local ip failed')
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def get_device_ip(self, deviceId):
        content = os.popen(f"{self.adb} -s {deviceId} shell ip addr show wlan0").read()
        logger.info(content)
        math_obj = re.search(r'inet\s(\d+\.\d+\.\d+\.\d+).*?wlan0', content)
        if math_obj and math_obj.group(1):
            return math_obj.group(1)
        return None

    def getCurrentActivity(self, deviceId):
        result = adb.shell(cmd='dumpsys window | {} mCurrentFocus'.format(self.filterType()), deviceId=deviceId)
        if result.__contains__('mCurrentFocus'):
            activity = str(result).split(' ')[-1].replace('}', '')
            return activity
        else:
            raise Exception('no activity found')

    def getStartupTimeByAndroid(self, activity, deviceId):
        result = adb.shell(cmd='am start -W {}'.format(activity), deviceId=deviceId)
        return result

    def getStartupTimeByiOS(self, pkgname):
        try:
            import ios_device
        except ImportError:
            logger.error('py-ios-devices not found, please run [pip install py-ios-devices]')
        result = self.execCmd('pyidevice instruments app_lifecycle -b {}'.format(pkgname))
        return result
