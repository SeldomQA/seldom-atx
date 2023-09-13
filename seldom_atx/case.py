"""
seldom_atx test case
"""
import time
import wda
import uiautomator2
import unittest
from seldom_atx.u2driver import U2Driver
from seldom_atx.wdadriver import WDADriver
from seldom_atx.running.config import Seldom, AppConfig
from seldom_atx.logging import log
from seldom_atx.logging.exceptions import NotFindElementError


class TestCase(unittest.TestCase):
    """seldom_atx TestCase class"""

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
        self.start()

    def tearDown(self):
        self.end()
        """upload performance related chart data"""
        self.images = AppConfig.REPORT_IMAGE

    @property
    def driver(self):
        """
        return browser driver (web)
        """
        return Seldom.driver

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


class TestCaseU2(TestCase, U2Driver):
    """u2-api TestCase class"""

    @classmethod
    def setUpClass(cls):
        Seldom.driver = uiautomator2.connect_usb(Seldom.deviceId)
        cls().start_class()

    def assertElement(self, index: int = 0, msg: str = None, **kwargs) -> None:
        """Asserts whether the element exists."""
        log.info("👀 assertElement.")
        if msg is None:
            msg = "No element found"
        try:
            self.get_elements(index=index, **kwargs)
            elem = True
        except NotFindElementError:
            elem = False

        self.assertTrue(elem, msg=msg)

    def assertNotElement(self, index: int = 0, msg: str = None, **kwargs) -> None:
        """Asserts if the element does not exist."""
        log.info("👀 assertNotElement.")
        if msg is None:
            msg = "Find the element"

        timeout_backups = Seldom.timeout
        Seldom.timeout = 2
        try:
            self.get_elements(index=index, **kwargs)
            elem = True
        except NotFindElementError:
            elem = False

        Seldom.timeout = timeout_backups

        self.assertFalse(elem, msg=msg)


class TestCaseWDA(TestCase, WDADriver):
    """wda-api TestCase class"""

    @classmethod
    def setUpClass(cls):
        Seldom.driver = wda.USBClient(udid=Seldom.deviceId)
        cls().start_class()

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
            self.get_element(index=index, **kwargs)
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
            self.get_element(index=index, **kwargs)
            elem = True
        except NotFindElementError:
            elem = False

        Seldom.timeout = timeout_backups

        self.assertFalse(elem, msg=msg)
