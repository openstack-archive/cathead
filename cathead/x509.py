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
import tempfile

from oslo_concurrency import processutils

LOG = logging.getLogger(__name__)


def generate_key():
    return processutils.execute("openssl", "genrsa", "2048")[0]


def generate_cert(key, csr):
    key_file = _create_temp_file(key)
    csr_file = _create_temp_file(csr)
    return processutils.execute("openssl", "x509", "-req", "-days",
                                "365", "-in", csr_file.name, "-signkey",
                                key_file.name)[0]


def get_expire_date(cert):
    # open cert with openssl and parse
    cert_file = _create_temp_file(cert)
    out = processutils.execute("openssl", "x509", "-in", cert_file.name,
                               "-dates", "-issuer", "-noout", "-subject")
    strdate = out[0].split("\n")[1].split("=")[1]
    return datetime.datetime.strptime(strdate, "%b %d %H:%M:%S %Y %Z")


def generate_csr(key, common_name,
                 country="", organisation=""):
    LOG.debug("Generating CSR")
    key_file = _create_temp_file(key)
    out = processutils.execute("openssl", "req", "-new", "-key", key_file.name,
                               "-subj",
                               "/C=%s/O=%s/CN=%s" %
                               (country, organisation, common_name))
    return out[0]


def _create_temp_file(contents):
    temp_file = tempfile.NamedTemporaryFile()
    temp_file.file.write(contents)
    temp_file.flush()
    return temp_file
