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

import imp
import importlib
import logging
import sys

from oslo_concurrency import processutils

import scheduler


class Cathead(object):

    def __init__(self, config):
        self.config = config

    def start(self):
        self.setup_logging()
        self.parse_config()
        self.wait()

    def setup_logging(self):
        ch = logging.StreamHandler()
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(ch)

    def extract_drivers(self):
        drivers = {}
        for driver in self.config['drivers']:
            split = driver.pop('driver').split('.')
            module = importlib.import_module('.'.join(split[:-1]))
            name = driver.pop('name')
            drivers[name] = getattr(module, split[-1])(**driver)
        return drivers

    def parse_config(self):

        drivers = self.extract_drivers()
        actions = self.extract_actions()

        self._scheduler = scheduler.Scheduler()

        for cert in self.config['certs']:
            callback = self.create_cert_callback(cert['on_refresh_success'],
                                                 actions)

            scheduler_conf = {
                'driver': drivers[cert['driver']],
                'key_path': cert['key'],
                'cert_path': cert['cert'],
                'refresh_window': cert['refresh_window'],
                'common_name': cert['common_name'],
                'on_refresh_success': callback,
                'jitter': 0,
            }

            self._scheduler.add_cert_watch(**scheduler_conf)

        return self._scheduler

    def extract_actions(self):
        actions = {}
        for action in self.config['actions']:
            if action['type'] == 'python':

                def create_closure():
                    closure = action

                    def callback():
                        module = importlib.import_module(closure['module'])
                        getattr(module, closure['command'])(*closure['args'])
                    return callback
                actions[action['name']] = create_closure()
            elif action['type'] == 'system':
                # closure = action.copy()

                def create_closure():
                    closure = action

                    def callback():
                        command = [closure['command']]
                        command.extend(closure['args']
                                       if closure['args'] else [])
                        processutils.execute(*command)
                    return callback
                actions[action['name']] = create_closure()
        return actions

    def create_cert_callback(self, action, actions):
        def callback():
            on_success = action
            if isinstance(on_success, str):
                actions[on_success]()
            else:
                for func in on_success:
                    actions[func]()
        return callback

    def wait(self):
        self._scheduler.wait()

def main():
    if len(sys.argv) == 2:
        # sys.path.append(os.path.abspath(sys.argv[1]))
        # conf_module = importlib.import_module(sys.argv[1].split(".py")[0])
        # conf = __import__(sys.argv[1].split(".py")[0])
        (file, path, desc) = imp.find_module(sys.argv[1].split(".py")[0], ["."])
        conf_module = imp.load_module('', file, path, desc)
        Cathead(conf_module.CONF).start()
    else:
        print("Usage: cathead path/to/configy.py")
