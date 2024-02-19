import os
import time
import gevent
import inspect
import threading
import statistics
from functools import wraps
from seldom_atx.utils import cache
from seldom_atx.logging import log
from seldom_atx.running.config import Seldom, AppConfig, OUTPUT_DIR, DataBase, AppDecorator
from seldom_atx.u2driver import u2
from seldom_atx.utils.app._performance import MySoloX, TidevicePerf
from seldom_atx.wdadriver import make_screenrecord
from seldom_atx.running.config import Platform
from seldom_atx.utils.app import _duration, _common
from seldom_atx.utils.sqlite import SQLiteDB


class SeldomDecorator:
    """
    Performance: 获取性能数据
    Effect: 截图对比
    Duration: 耗时计算
    GetLog: 获取设备日志
    """
    Performance = 'Performance'
    Effect = 'Effect'
    Duration = 'Duration'
    GetLog = 'GetLog'


decorator_list = [SeldomDecorator.Performance, SeldomDecorator.Duration, SeldomDecorator.Effect,
                  SeldomDecorator.GetLog]


def start_recording():
    """用例执行过程中用于启动录屏的标识"""
    AppDecorator.record = True
    time.sleep(2)


def stop_recording():
    """若不主动调用，则自动在用例结束时停止"""
    AppDecorator.record = False


def run_testcase(func, *args, **kwargs):
    """Execute decorated test case"""
    try:
        func(*args, **kwargs)
    except Exception as e:
        AppDecorator.CASE_ERROR.append(f"{e}")
        log.error(f'❌ Error in run_testcase: {e}.')
    if AppDecorator.record and Seldom.platform_name == 'Android':
        time.sleep(1)
        u2.stop_recording()
    elif AppDecorator.record and Seldom.platform_name == 'iOS':
        AppDecorator.record = False
        if AppDecorator.iOS_perf_obj is not None:
            AppDecorator.iOS_perf_obj.stop()
    AppDecorator.threadLock = False
    AppDecorator.log = False


def get_log(log_path):
    """Get logs for Android devices"""
    try:
        AppDecorator.log = True
        # while not os.path.exists(run_path):
        #     time.sleep(1)
        if Seldom.platform_name == Platform.Android:
            u2.write_log(log_path)
    except Exception as e:
        AppDecorator.LOGS_ERROR.append(f"{e}")
        log.error(f'❌ Error in get_log: {e}.')


def get_perf():
    """Obtain mobile device performance data"""
    try:
        if Seldom.platform_name == Platform.Android:
            perf = MySoloX(pkg_name=Seldom.app_package)
            new_cpu = gevent.spawn(perf.get_cpu)
            new_mem = gevent.spawn(perf.get_mem)
            new_fps = gevent.spawn(perf.get_fps)
            gevent.joinall([new_cpu, new_mem, new_fps])
            cache.set({'CPU_INFO': new_cpu.value})
            cache.set({'MEM_INFO': new_mem.value})
            cache.set({'FPS_INFO': new_fps.value})
        elif Seldom.platform_name == Platform.iOS:
            AppDecorator.iOS_perf_obj = TidevicePerf()
            AppDecorator.iOS_perf_obj.start()
    except Exception as e:
        AppDecorator.PERF_ERROR.append(f"{e}")
        log.error(f"❌ Error in get_perf: {e}.")


def start_record(video_path, run_path):
    while not os.path.exists(run_path):
        time.sleep(1)
    while AppDecorator.threadLock and Seldom.driver:
        if AppDecorator.record:
            try:
                if Seldom.platform_name == 'iOS':
                    with make_screenrecord(output_video_path=video_path):
                        while AppDecorator.record:
                            time.sleep(1)
                elif Seldom.platform_name == 'Android':
                    u2.start_recording(video_path)
            except Exception as e:
                AppDecorator.RECORD_ERROR.append(f"{e}")
                log.error(f"❌ Error in start_record: {e}.")
            break
        time.sleep(1.5)


def App(RunList: list = [], start_path: str = None, stop_path: str = None, duration_times: int = 1,
        duration_threshold: float = 10000,
        mem_threshold: float = 10000):
    """
    APP性能装饰器
    :param RunList: 需要执行的组件
    :param start_path: 开始帧的位置
    :param stop_path: 结束帧的位置
    :param duration_times: 耗时的用例执行次数
    :param duration_threshold: 耗时的阈值(s)
    :param mem_threshold: 内存的阈值(MB)
    """

    def my_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sql = SQLiteDB()
            func_name = func.__name__
            func_desc = func.__doc__
            # 获取被装饰函数所在的模块文件路径
            func_fileName = os.path.split(inspect.getsourcefile(func))[1]
            # 获取被装饰函数所在的类名
            func_className = args[0].__class__.__name__
            func_folderName = os.path.basename(os.path.dirname(os.path.abspath(func.__code__.co_filename)))
            current_outputFolder = AppConfig.PERF_RUN_FOLDER = os.path.join(str(OUTPUT_DIR), AppConfig.RUN_TIME,
                                                                            func_folderName, func_className,
                                                                            func_name)
            os.makedirs(current_outputFolder, exist_ok=True)
            if SeldomDecorator.Duration in RunList and not start_path and not stop_path:
                raise FileNotFoundError('当需要计算耗时时,开始帧和结束帧为必填!')
            AppConfig.REPORT_IMAGE = []
            duration_list = []
            cpu_base64_list = []
            mem_base64_list = []
            fps_base64_list = []
            bat_base64_list = []
            flo_base64_list = []
            start_frame_list = []
            stop_frame_list = []
            run_times = AppConfig.DURATION_TIMES if SeldomDecorator.Duration in RunList and duration_times == 1 else duration_times
            for current_times in range(run_times):
                AppDecorator.threadLock = True
                AppDecorator.record = False
                # 录屏保存的路径
                video_path = os.path.join(current_outputFolder, f'{func_name}_{current_times}.mp4')
                # Android日志保存的路径
                log_path = os.path.join(current_outputFolder, f'{func_name}_{current_times}.log')
                # 分帧保存的文件夹
                frame_folder = os.path.join(current_outputFolder, f'{func_name}_{current_times}')
                # 识别的关键帧保存的文件夹
                key_frame_folder = os.path.join(frame_folder, 'key_frame')
                # 性能数据图表的路径
                perf_path = os.path.join(current_outputFolder, f'{func_name}_perf_{current_times}')
                if SeldomDecorator.Performance in RunList:
                    os.makedirs(perf_path, exist_ok=True)
                if SeldomDecorator.Duration in RunList:
                    os.makedirs(key_frame_folder, exist_ok=True)
                do_list = []
                for run in RunList:
                    if run == SeldomDecorator.Duration:
                        do_list.append(gevent.spawn())
                    elif run == SeldomDecorator.Performance:
                        do_list.append(gevent.spawn(get_perf))
                    elif run == SeldomDecorator.Effect:
                        do_list.append(gevent.spawn())
                    elif run == SeldomDecorator.GetLog and Seldom.platform_name == Platform.Android:
                        log_thread = threading.Thread(target=get_log, args=log_path)
                        log_thread.start()
                    else:
                        raise ValueError(f'Unsupported run: {run}')
                do_list.append(gevent.spawn(run_testcase, func, *args, **kwargs))
                gevent.joinall(do_list)
                if AppDecorator.CASE_ERROR:
                    log.error(f'{AppDecorator.CASE_ERROR}')
                    assert False, f'{AppDecorator.CASE_ERROR}'
                if SeldomDecorator.Duration in RunList:
                    _duration.extract_frames(video_file=video_path, output_dir=frame_folder)
                    if not AppDecorator.RECORD_ERROR:
                        start_frame_path = _duration.find_best_frame(start_path, frame_folder, is_start=True)
                        start_frame = int(os.path.split(start_frame_path)[1].split('.')[0][-6:])

                        stop_frame_path = _duration.find_best_frame(stop_path, frame_folder, is_start=False)
                        stop_frame = int(os.path.split(stop_frame_path)[1].split('.')[0][-6:])
                        duration = round((stop_frame - start_frame) / AppConfig.FPS, 2)
                        duration_list.append(duration)
                        start_frame_list.append(_common.image_to_base64(start_frame_path))
                        stop_frame_list.append(_common.image_to_base64(stop_frame_path))
                if SeldomDecorator.Performance in RunList and not AppDecorator.PERF_ERROR:
                    cpu_info = cache.get('CPU_INFO')
                    cpu_image_path = os.path.join(perf_path, f'{func_name}_CPU.jpg')
                    cpu_base64_list.append(
                        _common.draw_chart(cpu_info[1], cpu_info[0], ['appCpuRate', 'sysCpuRate'],
                                           jpg_name=cpu_image_path,
                                           label_title='CPU'))
                    mem_info = cache.get('MEM_INFO')
                    mem_image_path = os.path.join(perf_path, f'{func_name}_MEM.jpg')
                    mem_base64_list.append(
                        _common.draw_chart(mem_info[1], mem_info[0], ['totalPass', 'nativePass', 'dalvikPass'],
                                           jpg_name=mem_image_path, label_title='Memory'))
                    fps_info = cache.get('FPS_INFO')
                    fps_image_path = os.path.join(perf_path, f'{func_name}_FPS.jpg')
                    if fps_info is not None:
                        fps_base64_list.append(
                            _common.draw_chart(fps_info[1], fps_info[0], ['fps', 'jank'], jpg_name=fps_image_path,
                                               label_title='Fps'))
            if SeldomDecorator.Performance in RunList and not AppDecorator.PERF_ERROR:
                photo_list = cpu_base64_list + mem_base64_list + fps_base64_list + flo_base64_list \
                             + bat_base64_list + start_frame_list + stop_frame_list
                AppConfig.REPORT_IMAGE.extend(photo_list)
            duration_avg = 0 if not duration_list else round(statistics.mean(duration_list), 2)
            # duration_avg = round(statistics.mean(duration_list), 2) if not duration_list else 0
            memory_max = max(
                [tup[0] for tup in cache.get('MEM_INFO')[1]]) if SeldomDecorator.Performance in RunList else 0
            assert_result = 1
            if memory_max > mem_threshold:
                assert_result = -1
            if duration_avg > duration_threshold:
                assert_result = -1

            result_dict = {DataBase.PERF_TIME: AppConfig.RUN_TIME,
                           DataBase.PERF_Device: Seldom.platform_name,
                           DataBase.PERF_DeviceName: Seldom.device_id,
                           DataBase.PERF_TestCasePath: f"{func_fileName} --> {func_className}",
                           DataBase.PERF_TestCaseName: func_name,
                           DataBase.PERF_TestCaseDesc: func_desc,
                           DataBase.PERF_DurationTimes: duration_times,
                           DataBase.PERF_DurationList: str(duration_list),
                           DataBase.PERF_DurationAvg: duration_avg,
                           DataBase.PERF_MemoryMax: memory_max,
                           DataBase.PERF_RunList: str(RunList),
                           DataBase.PERF_RESULT: assert_result}
            print(result_dict)
            sql.insert_data(table=DataBase.PERF_TABLE, data=result_dict)
            sql.close()
            if memory_max > mem_threshold:
                assert False, memory_max
            if duration_avg > duration_threshold:
                assert False, duration_avg

        return wrapper

    return my_decorator

# def AppPerf(MODE, duration_times: int = None, mem_threshold: int = 800,
#             duration_threshold: int = 100, write_excel: bool = True, get_logs: bool = True):
#     """性能数据装饰器"""
#
#     def my_decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             # --------------------------初始化--------------------------
#             frame_path = None  # 分帧文件夹路径
#             start_path = None  # 开始关键帧路径
#             stop_path = None
#             perf_path = None  # 性能文件夹路径
#             App.iOS_perf_obj = None
#             testcase_name = func.__name__
#             testcase_desc = func.__doc__
#             testcase_file_name = os.path.split(inspect.getsourcefile(func))[1]  # 获取被装饰函数所在的模块文件路径
#             testcase_class_name = args[0].__class__.__name__  # 获取被装饰函数所在的类名
#             testcase_folder_name = os.path.basename(os.path.dirname(os.path.abspath(func.__code__.co_filename)))
#             cache.set({'TESTCASE_NAME': testcase_name})
#             cache.set({'TESTCASE_CLASS_NAME': testcase_class_name})
#             run_times = 1
#             if AppConfig.PERF_OUTPUT_FOLDER is None:
#                 AppConfig.PERF_OUTPUT_FOLDER = os.path.join(os.getcwd(), "reports")
#             testcase_base_path = os.path.join(AppConfig.PERF_OUTPUT_FOLDER, testcase_folder_name, AppConfig.RUN_TIME,
#                                               testcase_class_name, testcase_name)
#             if not os.path.exists(testcase_base_path):
#                 os.makedirs(testcase_base_path)
#             keyframes_path = os.path.join(AppConfig.PERF_OUTPUT_FOLDER, f'{Seldom.platform_name}KeyFrames')
#             if not os.path.exists(keyframes_path):
#                 os.makedirs(keyframes_path)
#             if MODE == RunType.NOTHING:
#                 log.info(f'Do nothing mode:{testcase_name}')
#             elif MODE == RunType.DEBUG:
#                 log.info(f'Recording and framing mode:{testcase_name}')
#             elif MODE == RunType.DURATION:
#                 log.info(f'Calculation time consumption mode:{testcase_name}')
#                 run_times = duration_times if duration_times is not None else AppConfig.DURATION_TIMES
#                 log.info('Please ensure that there are no testcase with the same name!')
#                 start_path = os.path.join(keyframes_path, f'{testcase_name}_start.jpg')  # 开始帧的位置
#                 stop_path = os.path.join(keyframes_path, f'{testcase_name}_stop.jpg')  # 结束帧的位置
#                 if not os.path.exists(start_path) or not os.path.exists(stop_path):
#                     log.error(
#                         f'如果是首次运行用例：{testcase_name}\n'
#                         f'1.请先使用@AppPerf(MODE=RunType.DEBUG)模式执行一遍\n'
#                         f'2.生成分帧后再挑出关键帧放置在该位置\n'
#                         f'3.然后再执行@AppPerf(MODE=RunType.DURATION)模式！')
#                     raise FileNotFoundError(f'{start_path}___or___{stop_path}')
#             elif MODE == RunType.STRESS:
#                 log.info(f'Stress test mode:{testcase_name}')
#             else:
#                 raise ValueError
#             AppConfig.REPORT_IMAGE = []
#             duration_list = []
#             cpu_base64_list = []
#             mem_base64_list = []
#             fps_base64_list = []
#             bat_base64_list = []
#             flo_base64_list = []
#             start_frame_list = []
#             stop_frame_list = []
#             testcase_assert = True
#             for i in range(run_times):
#                 run_path = AppConfig.PERF_RUN_FOLDER = testcase_base_path
#                 video_path = os.path.join(run_path, f'{testcase_name}_{i}.mp4')  # 录屏文件路径
#                 log_path = os.path.join(run_path, f'{testcase_name}_{i}.txt')
#                 Common.CASE_ERROR = []
#                 Common.PERF_ERROR = []
#                 Common.LOGS_ERROR = []
#                 if MODE in [RunType.DEBUG, RunType.DURATION]:
#                     frame_path = os.path.join(testcase_base_path, f'{testcase_name}_frame_{i}')
#                     if not os.path.exists(frame_path):
#                         os.makedirs(frame_path)
#                 if MODE in [RunType.DURATION, RunType.STRESS]:
#                     perf_path = os.path.join(testcase_base_path, f'{testcase_name}_jpg_{i}')
#                     if not os.path.exists(perf_path):
#                         os.makedirs(perf_path)
#                 else:
#                     if not os.path.exists(run_path):
#                         os.makedirs(run_path)
#                 App.threadLock = True
#                 Common.record = False
#
#                 # --------------------------执行用例--------------------------
#                 if get_logs and Seldom.platform_name == 'Android':
#                     log_thread = threading.Thread(target=get_log, args=(log_path, run_path))
#                     log_thread.start()
#                 do_list = [gevent.spawn(run_testcase, func, *args, **kwargs),
#                            gevent.spawn(start_record, video_path, run_path)]
#                 if MODE in [RunType.DURATION, RunType.STRESS]:  # 判断是否开启性能数据获取，开启的话就在协程队列中增加get_perf执行
#                     do_list.append(gevent.spawn(get_perf))
#                 gevent.joinall(do_list)
#                 if Common.CASE_ERROR:
#                     log.error(f'{Common.CASE_ERROR}')
#                     assert False, f'{Common.CASE_ERROR}'
#                 # --------------------------录屏文件分帧--------------------------
#                 if MODE in [RunType.DEBUG, RunType.DURATION] and Common.RECORD_ERROR == []:
#                     log.info("✅ 正在进行录屏分帧.")
#                     Common.extract_frames(video_path, frame_path)
#                     log.info("✅ 录屏分帧结束.")
#                 # --------------------------寻找关键帧--------------------------
#                 if MODE == RunType.DURATION and Common.RECORD_ERROR == []:
#                     log.info("🌝 Start searching for the most similar start frame.")
#                     start_frame_path = Common.find_best_frame(start_path, frame_path)
#                     start_frame = int(os.path.split(start_frame_path)[1].split('.')[0][-6:])
#                     log.info(f"Start frame:[{start_frame}].")
#                     log.info("🌚 Start searching for the most similar end frame.")
#                     stop_frame_path = Common.find_best_frame(stop_path, frame_path, is_start=False)
#                     stop_frame = int(os.path.split(stop_frame_path)[1].split('.')[0][-6:])
#                     log.info(f"Stop frame:[{stop_frame}].")
#                     # --------------------------计算耗时--------------------------
#                     duration = round((stop_frame - start_frame) / AppConfig.FPS, 2)
#                     log.info(f"🌈 [{testcase_name}]Func time consume[{duration}]s.")
#                     duration_list.append(duration)
#                     start_frame_list.append(Common.image_to_base64(start_frame_path))
#                     stop_frame_list.append(Common.image_to_base64(stop_frame_path))
#                     if run_times != 1:
#                         if Seldom.platform_name == 'Android':
#                             u2.launch_app(stop=True)
#                         elif Seldom.platform_name == 'iOS':
#                             wda_.launch_app(stop=True)
#
#                 # --------------------------性能图像保存在本地并转换为base64--------------------
#                 if MODE in [RunType.DURATION, RunType.STRESS] and Common.PERF_ERROR == []:
#                     # CPU
#                     cpu_info = cache.get('CPU_INFO')
#                     cpu_image_path = os.path.join(perf_path, f'{testcase_name}_CPU_{i}.jpg')
#                     cpu_base64_list.append(
#                         Common.draw_chart(cpu_info[1], cpu_info[0], ['appCpuRate', 'sysCpuRate'],
#                                           jpg_name=cpu_image_path,
#                                           label_title='CPU'))
#                     # MEM
#                     mem_info = cache.get('MEM_INFO')
#                     mem_image_path = os.path.join(perf_path, f'{testcase_name}_MEM_{i}.jpg')
#                     mem_base64_list.append(
#                         Common.draw_chart(mem_info[1], mem_info[0], ['totalPass', 'nativePass', 'dalvikPass'],
#                                           jpg_name=mem_image_path, label_title='Memory'))
#                     # 帧率
#                     fps_info = cache.get('FPS_INFO')
#                     fps_image_path = os.path.join(perf_path, f'{testcase_name}_FPS_{i}.jpg')
#                     if fps_info is not None:
#                         fps_base64_list.append(
#                             Common.draw_chart(fps_info[1], fps_info[0], ['fps', 'jank'], jpg_name=fps_image_path,
#                                               label_title='Fps'))
#             # --------------------------图片回写报告--------------------------
#             if MODE in [RunType.DURATION, RunType.STRESS] and Common.PERF_ERROR == []:
#                 photo_list = cpu_base64_list + mem_base64_list + fps_base64_list + flo_base64_list \
#                              + bat_base64_list + start_frame_list + stop_frame_list
#                 AppConfig.REPORT_IMAGE.extend(photo_list)
#                 # --------------------------数据回写表格--------------------------
#                 mode = 'DurationTest' if MODE == RunType.DURATION else 'StressTest'
#                 file_class_name = f"{testcase_file_name} --> {testcase_class_name}"
#                 in_excel_times = AppConfig.STRESS_TIMES if MODE == RunType.STRESS else run_times
#                 test_case_data = {'Time': AppConfig.RUN_TIME, 'TestCasePath': file_class_name,
#                                   'TestCaseName': testcase_name,
#                                   'TestCaseDesc': testcase_desc, 'Device': Seldom.platform_name,
#                                   'Times': in_excel_times, 'MODE': mode}
#                 # --------------------------耗时或内存阈值断言--------------------------
#                 if MODE == RunType.DURATION:
#                     max_duration_res = round(statistics.mean(duration_list), 2)
#                     log.success("🌈 Average time consumption of functions[{:.2f}]s.".format(max_duration_res))
#                     if max_duration_res > duration_threshold:
#                         max_duration_res = f"{run_times}次平均耗时：{max_duration_res}s," \
#                                            f"设定阈值：{duration_threshold}s."
#                         testcase_assert = False
#                         log.warning(max_duration_res)
#                     test_case_data.update({'DurationList': str(duration_list), 'DurationAvg': max_duration_res})
#                     if testcase_assert is False:
#                         assert False, max_duration_res
#                 elif MODE == RunType.STRESS:
#                     max_mem_res = max([tup[0] for tup in cache.get('MEM_INFO')[1]])
#                     if max_mem_res > mem_threshold:
#                         max_mem_res = f"最大内存：{max_mem_res},设定阈值：{mem_threshold}."
#                         testcase_assert = False
#                         log.warning(max_mem_res)
#                     test_case_data.update({'MemMax': max_mem_res})
#                     if testcase_assert is False:
#                         assert False, max_mem_res
#                 if write_excel:
#                     AppConfig.WRITE_EXCEL.append(test_case_data)
#
#         return wrapper
#
#     return my_decorator
