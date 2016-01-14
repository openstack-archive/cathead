import unittest

from cathead import cadriver
from cathead.drivers import anchor


class AnchorDriverTestCase(unittest.TestCase):

    def test_sign(self):
        driver = anchor.AnchorDriver("host", "port", "user", "password",root="default")
        self.assertTrue(isinstance(driver, cadriver.CaDriver))

    #TODO(hyakuhei) functional tests - spin up anchor container maybe?
