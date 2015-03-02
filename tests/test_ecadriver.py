import unittest

from cathead import cadriver
from cathead.drivers import eca


class EcaDriverTestCase(unittest.TestCase):

    def test_sign(self):
        driver = eca.EcaDriver("host", "port", "user", "password")
        self.assertTrue(isinstance(driver, cadriver.CaDriver))
