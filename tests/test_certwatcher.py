import datetime
import tempfile
import unittest

import freezegun
import mock

from cathead import certwatch
import cathead.x509


class CertWatcherTestCase(unittest.TestCase):

    @mock.patch.object(cathead.x509, 'get_expire_date')
    def test_expires_in_window(self, mock_get_expire_date):
        key = tempfile.NamedTemporaryFile()
        cert = tempfile.NamedTemporaryFile()
        watcher = certwatch.CertWatcher(key.name, cert.name,
                                        "common name", None,
                                        refresh_window=40)
        mock_get_expire_date.return_value = datetime.datetime(2014, 12, 19,
                                                              15, 18, 53)
        with freezegun.freeze_time("2014-12-19 15:18:10"):
            self.assertFalse(watcher._expires_in_window())

        with freezegun.freeze_time("2014-12-19 15:18:14"):
            self.assertTrue(watcher._expires_in_window())

    @mock.patch.object(cathead.x509, 'get_expire_date')
    @mock.patch.object(cathead.x509, 'generate_csr')
    def test_check_and_update(self, mock_generate_csr, mock_get_expire_date):
        mock_get_expire_date.return_value = datetime.datetime(2014, 12, 19,
                                                              15, 18, 53)
        mock_generate_csr.return_value = "hello csr"

        callback = mock.Mock()
        key = tempfile.NamedTemporaryFile()
        cert = tempfile.NamedTemporaryFile()
        watcher = certwatch.CertWatcher(key.name, cert.name, 'common_name',
                                        None, on_refresh_success=callback,
                                        refresh_window=40)

        watcher.ca_driver = mock.Mock()
        watcher.ca_driver.sign.return_value = "hello cert"

        watcher.check_and_update()

        self.assertEqual("hello cert", cert.file.read())
        watcher.ca_driver.called_once_with("hello csr")
        callback.assert_called_once_with()
