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

import datetime
import logging
import os.path

import x509

LOG = logging.getLogger(__name__)


class CertWatcher(object):

    def __init__(self, key_path, cert_path, common_name, ca_driver,
                 on_refresh_success=None, on_refresh_failure=None,
                 refresh_window=None):
        if not os.path.isfile(key_path):
            raise Exception("key needs to exist")
        self.key_path = key_path
        self.cert_path = cert_path
        self.ca_driver = ca_driver
        self.on_refresh_success = on_refresh_success
        self.on_refresh_failure = on_refresh_failure
        self.common_name = common_name
        self.refresh_window = refresh_window

    @property
    def key(self):
        return open(self.key_path).read()

    @property
    def cert(self):
        return open(self.cert_path).read()

    def get_expire_date(self):
        return x509.get_expire_date(self.cert)

    def seconds_until_expiry(self):
        diff = self.get_expire_date() - datetime.datetime.now()
        return diff.total_seconds()

    def _replace_cert(self, cert_contents):
        LOG.info("Replacing certificate at %s" % self.cert_path)
        cert = open(self.cert_path, "w")
        cert.write(cert_contents)
        cert.close()

    def _will_be_expired(self, date):
        return date > self.get_expire_date()

    def _expires_in_window(self):
        now = datetime.datetime.now()
        if not self.refresh_window:
            LOG.debug("No refresh window set, assuming expired")
            return True
        window = now + datetime.timedelta(0, self.refresh_window)
        if self._will_be_expired(window):
            LOG.info("%s is expired inside window of %s"
                     % (self.cert_path, self.refresh_window))
            return True
        LOG.info("Certificate valid within window of %s seconds"
                 % self.refresh_window)
        return False

    def _cert_exists(self):
        if not os.path.isfile(self.cert_path):
            LOG.info("No cert found at %s" % self.cert_path)
            return False
        return True

    def is_invalid_cert(self):
        return not self._cert_exists() or self._expires_in_window()

    def check_and_update(self):
        LOG.info('Checking validity of certificate %s' % self.cert_path)
        if self.is_invalid_cert():
            csr = x509.generate_csr(self.key, self.common_name)
            cert = None
            try:
                cert = self.ca_driver.sign(csr)
            except Exception as e:
                LOG.exception("Could not retrieve cert\n%s", e)
            if cert:
                self._replace_cert(cert)
                self.on_refresh_success()
            else:
                self.on_refresh_failure()
