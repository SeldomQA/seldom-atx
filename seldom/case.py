"""
seldom test case
"""
import time
import wda
import uiautomator2
import unittest
from seldom.u2driver import U2Driver
from seldom.wdadriver import WDADriver
from seldom.running.config import Seldom, AppConfig
from seldom.logging import log
from seldom.logging.exceptions import NotFindElementError


class TestCase(unittest.TestCase, U2Driver, WDADriver):
    """seldom TestCase class"""

    def start_class(self):
        """
        Hook method for setting up class fixture before running tests in the class.
        """
        pass

    def end_class(self):
        """
        Hook method for deconstructing the class fixture after running all tests in the class.
        """
        pass

    @classmethod
    def setUpClass(cls):
        cls().start_class()

    @classmethod
    def tearDownClass(cls):
        cls().end_class()

    def start(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        pass

    def end(self):
        """
        Hook method for deconstructing the test fixture after testing it.
        """
        pass

    def setUp(self):
        self.images = []
        # lunch app
        if (Seldom.app_server is None) and (Seldom.app_info.get('platformName') == 'Android'):
            """lunch uiautomator2"""
            Seldom.driver = uiautomator2.connect_usb(Seldom.app_info.get('deviceName'))
        elif (Seldom.app_server is None) and (Seldom.app_info.get('platformName') == 'iOS'):
            """lunch facebook-wda"""
            Seldom.driver = wda.USBClient(udid=Seldom.app_info.get('udid'))
        self.start()

    def tearDown(self):
        self.end()
        # close app
        if (Seldom.app_server is not None) and (Seldom.app_info is not None):
            Seldom.driver.quit()
        elif (Seldom.app_server is None) and (Seldom.app_info is not None):
            """upload performance related chart data"""
            self.images = AppConfig.REPORT_IMAGE

    @property
    def driver(self):
        """
        return browser driver (web)
        """
        return Seldom.driver

    def assertElement(self, index: int = 0, msg: str = None, **kwargs) -> None:
        """
        Asserts whether the element exists.

        Usage:
        self.assertElement(css="#id")
        """
        log.info("👀 assertElement.")
        if msg is None:
            msg = "No element found"
        try:
            if Seldom.app_info.get('platformName') == 'Android':
                self.get_elements_u2(index=index, **kwargs)
            elif Seldom.app_info.get('platformName') == 'iOS':
                self.get_element_wda(index=index, **kwargs)
            elem = True
        except NotFindElementError:
            elem = False

        self.assertTrue(elem, msg=msg)

    def assertNotElement(self, index: int = 0, msg: str = None, **kwargs) -> None:
        """
        Asserts if the element does not exist.

        Usage:
        self.assertNotElement(css="#id")
        """
        log.info("👀 assertNotElement.")
        if msg is None:
            msg = "Find the element"

        timeout_backups = Seldom.timeout
        Seldom.timeout = 2
        try:
            if Seldom.app_info.get('platformName') == 'Android':
                self.get_elements_u2(index=index, **kwargs)
            elif Seldom.app_info.get('platformName') == 'iOS':
                self.get_element_wda(index=index, **kwargs)
            elem = True
        except NotFindElementError:
            elem = False

        Seldom.timeout = timeout_backups

        self.assertFalse(elem, msg=msg)

    def xSkip(self, reason):
        """
        Skip this test.
        :param reason:
        Usage:
        if data is None:
            self.xSkip("data is None.")
        """
        self.skipTest(reason)

    def xFail(self, msg):
        """
        Fail immediately, with the given message
        :param msg:
        Usage:
        if data is None:
            self.xFail("This case fails.")
        """
        self.fail(msg)

    @staticmethod
    def sleep(sec: int) -> None:
        """
        Usage:
            self.sleep(seconds)
        """
        log.info(f"💤️ sleep: {sec}s.")
        time.sleep(sec)
