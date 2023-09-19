import seldom_atx
from seldom_atx.utils import AppPerf, RunType, start_recording
from seldom_atx import TestCaseWDA
from seldom_atx import label


@label('iOS')
class TestDemo(TestCaseWDA):
    """
    Test iOS Demo
    """

    def start(self):
        self.launch_app(stop=True)

    def end(self):
        self.close_app()

    @AppPerf(MODE=RunType.DEBUG)
    def test_demo(self):
        """
        test iOS settings
        """
        start_recording()
        self.swipe_up_find(name='General')
        self.click(name='General')
        self.click(name='About')
        self.get_text(className='XCUIElementTypeStaticText', index=3)
        self.assertElement(name='NAME_CELL_ID')
        self.sleep(1)


if __name__ == '__main__':
    # iOS 用例配置
    seldom_atx.main(
        device_id="bfaaa7b76fe378fb64332ebab762bb36dc77d3c3",
        app_package="com.apple.Preferences",
        platform_name="iOS",
        debug=True)
