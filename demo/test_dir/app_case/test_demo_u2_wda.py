import seldom_atx
from seldom_atx.utils.perf import AppPerf, RunType, start_recording
from seldom_atx.wdadriver import WDAElement
from seldom_atx import TestCaseWDA
from seldom_atx.utils import file


class Element:
    edit = WDAElement(label='编辑照片和视频', value='编辑照片和视频')


class TestDemo(TestCaseWDA):
    """
    Test Demo
    """

    @AppPerf(MODE=RunType.DEBUG)
    def test_demo(self):
        """
        test flyme bbs search
        """
        self.sleep(5)
        self.launch_app()
        start_recording()
        self.sleep(3)
        self.click(elem=Element.edit, index=0)
        self.assertElement(label='最近项目')
        self.sleep(1)


if __name__ == '__main__':
    from seldom_atx import AppConfig
    AppConfig.PERF_OUTPUT_FOLDER = file.join(file.dir, "reports")

    # Android 用例配置
    seldom_atx.main(
        device_id="f5ede5e3",
        app_package="com.magicv.airbrush",
        platform_name="Android",
        debug=True)

    # iOS 用例配置
    seldom_atx.main(
        device_id="bfaaa7b76fe378fb64332ebab762bb36dc77d3c3",
        app_package="com.magicv.AirBrush",
        platform_name="iOS",
        debug=True)
