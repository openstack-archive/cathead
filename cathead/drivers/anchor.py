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

import requests

from cathead import cadriver
from cathead import x509

LOG = logging.getLogger(__name__)


class AnchorDriver(cadriver.CaDriver):

    def __init__(self, host, port,
                 user, secret, root='default', scheme='http'):
        self.host = host
        self.port = port
        self.user = user
        self.secret = secret
        self.scheme = scheme
        self.root = root

    def sign(self, csr):
        urlscheme = "{scheme}://{host}:{port}/v1/sign/{root}"
        url = urlscheme.format(**self.__dict__)
        LOG.info("Sending CSR to %s" % url)
        params = {"user": self.user,
                  "secret": self.secret,
                  "encoding": "pem",
                  "csr": csr,
                  "root": self.root}
        r = requests.post(url, data=params)
        cert = r.text
        LOG.debug("Received from Anchor server:\n%s" % cert)
        if self._is_valid_cert(cert):
            return cert
        else:
            LOG.info("Received invalid certificate from Anchor")

    def _is_valid_cert(self, cert):
        try:
            expire = x509.get_expire_date(cert)
            return expire > datetime.datetime.now()
        except Exception as e:
            LOG.info("invalid cert, failed check date with:\n%s", e)
            return False
