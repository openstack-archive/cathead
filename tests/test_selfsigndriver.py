import re
import unittest
import tempfile

from cathead.drivers import selfsign
from cathead import x509


class SelfSignDriverTestCase(unittest.TestCase):

    def test_sign(self):
        key = x509.generate_key()
        keyfile = tempfile.NamedTemporaryFile()
        keyfile.write(key)
        keyfile.flush()
        driver = selfsign.SelfSignDriver(keyfile.name)
        csr = x509.generate_csr(key, '192')
        cert = driver.sign(csr)
        match = re.search("^-----BEGIN CERTIFICATE-----"
                          ".*"
                          "-----END CERTIFICATE-----",
                          cert, re.MULTILINE | re.DOTALL)
        self.assertTrue(match)
