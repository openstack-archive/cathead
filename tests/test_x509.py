import datetime
import re
import unittest

import mock
import oslo_concurrency.processutils

from cathead import x509


class X509TestCase(unittest.TestCase):

    @mock.patch.object(oslo_concurrency.processutils, 'execute')
    def test_get_expire_date(self, mock_execute):
        mock_execute.return_value = (("notBefore=Dec 19 03:18:43 2014 GMT\n"
                                      "notAfter=Dec 19 15:18:43 2014 GMT\n"
                                      "issuer= /C=UK/O=hp/CN=CertAuthority\n"
                                      "subject= /CN=192.0.2.26\n"),)
        expected_date = datetime.datetime(2014, 12, 19, 15, 18, 43)

        self.assertEqual(x509.get_expire_date('-'), expected_date)

    def test_generate_csr(self):
        key = x509.generate_key()
        csr = x509.generate_csr(key, "secert cert auth")
        match = re.search("^-----BEGIN CERTIFICATE REQUEST-----"
                          ".*"
                          "-----END CERTIFICATE REQUEST-----",
                          csr, re.MULTILINE | re.DOTALL)
        self.assertTrue(match)

    def test_generate_key(self):
        key = x509.generate_key()
        match = re.search("^-----BEGIN RSA PRIVATE KEY-----"
                          ".*"
                          "-----END RSA PRIVATE KEY-----",
                          key, re.MULTILINE | re.DOTALL)
        self.assertTrue(match)

    def test_generate_cert(self):
        key = x509.generate_key()
        csr = x509.generate_csr(key, "unknown")
        cert = x509.generate_cert(key, csr)
        match = re.search("^-----BEGIN CERTIFICATE-----"
                          ".*"
                          "-----END CERTIFICATE-----",
                          cert, re.MULTILINE | re.DOTALL)
        self.assertTrue(match)
