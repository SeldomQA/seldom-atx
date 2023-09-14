import seldom_atx
from seldom_atx.utils.perf import AppPerf, RunType, start_recording


class Element:
    edit = {
        'label': '编辑照片和视频',
        'value': '编辑照片和视频'
    }


class TestDemo(seldom_atx.TestCaseWDA):
    """
    Test Demo
    """

    @AppPerf(MODE=RunType.DEBUG)
    def test_demo(self):
        """
        test flyme bbs search
        """
        # self.sleep(5)
        self.launch_app()
        start_recording()
        self.sleep(3)
        self.click(**Element.edit, index=0)
        self.assertElement(label='最近项目')
        self.sleep(1)
