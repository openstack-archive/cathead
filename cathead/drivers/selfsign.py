# Copyright 2015 Tom Cammann
# All Rights Reserved.
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

import os.path

from cathead import cadriver
from cathead import x509


class SelfSignDriver(cadriver.CaDriver):

    def __init__(self, ca_key_file, check_key_file=True):
        if check_key_file and not os.path.isfile(ca_key_file):
            raise Exception("Key %s not found" % ca_key_file)
        self.ca_key_file = ca_key_file

    def sign(self, csr):
        return x509.generate_cert(open(self.ca_key_file).read(), csr)
