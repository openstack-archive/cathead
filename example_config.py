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

CONF = {
    'failure_refresh_timeout': 10,
    'drivers': [
        {
            'name': 'selfsign',
            'driver': 'cathead.drivers.selfsign.SelfSignDriver',
            'ca_key_file': 'ca.p.key',
        },
        {
            'name': 'anchor',
            'driver': 'cathead.drivers.anchor.AnchorDriver',
            'host': '192.168.99.100',
            'port': 5016,
            'user': 'woot',
            'secret': 'woot',
            'root': 'default'
        }
    ],
    'certs': [
        {
            'driver': 'anchor',
            'key': 'tmp/anchor-test.example.com.key',
            'cert': 'tmp/anchor-test.example.com.crt',
            'refresh_window': 1,
            'common_name': '127.0.0.1',
            'on_refresh_success': 'hello_system',
        }
    ],
    'actions': [
        {
            'name': 'hello_python',
            'type': 'python',
            'module': 'os',
            'command': 'write',
            'args': [2, 'hello world'],
        },
        {
            'name': 'hello_system',
            'type': 'system',
            'command': 'echo',
            'args': ['hello echo world'],
        },
    ]
}
