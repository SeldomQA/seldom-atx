import seldom_atx
from seldom_atx.utils import AppPerf, RunType, start_recording
from seldom_atx import TestCaseU2
from seldom_atx import label


@label('Android')
class TestDemo(TestCaseU2):
    """
    Test Android Demo
    """

    def start(self):
        self.launch_app(stop=True)

    def end(self):
        self.close_app()

    @AppPerf(MODE=RunType.DEBUG)
    def test_demo(self):
        """
        test MIUI settings
        """
        start_recording()
        self.click(resourceId="android:id/title", text="蓝牙")
        self.click(resourceId="com.android.settings:id/refresh_anim")
        self.assertElement(resourceId="android:id/title", text="蓝牙设置")
        self.sleep(1)


if __name__ == '__main__':
    # Android 用例配置
    seldom_atx.main(
        device_id="f5ede5e3",
        app_package="com.android.settings",
        platform_name="Android",
        debug=True)
