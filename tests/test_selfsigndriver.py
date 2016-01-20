#   (c) Copyright 2015 Hewlett-Packard Development Company, L.P.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import re
import tempfile
import unittest

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
