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

import logging

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers import background

import certwatch

LOG = logging.getLogger(__name__)


class Scheduler(object):

    def __init__(self):
        self._scheduler = background.BackgroundScheduler()
        self._scheduler.configure(daemon=True)
        self.job_dict = {}
        self._scheduler.start()

    def is_tracked(self, key_path):
        return key_path in self.job_dict

    def _remove_job(self, key_path):
        try:
            self._scheduler.remove_job(key_path)
        except JobLookupError:
            LOG.info("No scheduled job for %s, creating new job", key_path)

    def _create_success_callback(self, key_path, callback):
        def success_callback():
            job_info = self.job_dict[key_path]
            self._remove_job(key_path)
            watcher = job_info['watcher']
            seconds = watcher.seconds_until_expiry()
            new_interval = seconds - seconds / 5
            self._scheduler.add_job(watcher.check_and_update, 'interval',
                                    seconds=new_interval, id=key_path)
            if callback:
                try:
                    callback()
                except Exception as e:
                    LOG.exception(e)
        return success_callback

    def _create_failure_callback(self, key_path):
        def failure_callback():
            job_info = self.job_dict[key_path]
            self._remove_job(key_path)
            watcher = job_info['watcher']
            self._scheduler.add_job(watcher.check_and_update,
                                    'interval', seconds=10, id=key_path)
        return failure_callback

    def add_cert_watch(self, driver, key_path, cert_path,
                       common_name, on_refresh_success=None,
                       jitter=0, refresh_window=None):
        if self.is_tracked(key_path):
            raise Exception("Already tracking certificate")

        on_success = self._create_success_callback(key_path,
                                                   on_refresh_success)
        on_failure = on_failure = self._create_failure_callback(key_path)
        watcher = certwatch.CertWatcher(key_path, cert_path, common_name,
                                        driver, on_refresh_success=on_success,
                                        on_refresh_failure=on_failure)

        self.job_dict[key_path] = {'watcher': watcher}
        watcher.check_and_update()

    def wait(self):
        self._scheduler._thread.join()
