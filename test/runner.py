# -*- coding: utf-8 -*-
'''
Created on 2013-11-15

@author: juliochen
'''
import os
import subprocess
import datetime
import time
import logging

from task import Task
from utils import util
import log_parser
from utils.threadmanager import ThreadManager

'''
Data structure:
{
device: deviceid,
case: [test_case, ...],
target: target package,
}
'''

logger = logging.getLogger("R")


class Monkey(object):

    def __init__(self, devices, package):
        self.devices = devices
        self.package = package
        self.mt_log = ''

    def one_for_all(self):
        if not self.devices:
            logger.warn("No device available")

        param = []
        for d in self.devices:
            param.append({'device': d,
                         'case': util.load_monkey_case('./res/monkey_cmd'),
                         'target': self.package.pkg_name,
                         'version': self.package.version})
        self.test(param)

    def parse_log(self, timestamp):
        log_path = os.path.join(util.get_path('./logs'), timestamp)

        if os.path.exists(log_path):
            pass

    def test(self, param):
        time_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.tm = ThreadManager(self.devices)
        for d in param:
            mk_task = MonkeyTask(d, time_stamp)
            self.tm.add_job(mk_task)

        self.tm.wait_for_complete()

        self.mt_log = log_parser.parse_monkey_log(
            time_stamp, self.tm.get_all_results(), param)


class Robotium(object):

    def __init__(self, devices, pkg):
        self.devices = devices
        self.test_pkg = pkg
        self.results = []
        self.current_case = None
        self.cases = []

    def add_case(self, case):
        self.cases.append(case)

    def install(self, device):
        # clear old package
        self.test_pkg.uninstall(device)
        self.test_pkg.install(device)

    def one_for_all(self):
        param = []
        for d in self.devices:
            param.append({'device': d, 'case': self.cases,
                         'target': self.test_pkg.pkg_name})
        self.test(param)
        self.save_results()

    def clear_screeshots(self):
        for device in self.devices:
            util.adb_runner(device, 'rm /mnt/sdcard/Robotium-Screenshots/*')

    def test(self, param):
        base_path = util.get_path('./logs/robotium')
        time_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.output = os.path.join(base_path, time_stamp)
        if not os.path.exists(self.output):
            os.makedirs(self.output)

        self.tm = ThreadManager(self.devices)
        for d in param:
            task = Task(d, time_stamp)
            self.tm.add_job(task)

        self.tm.wait_for_complete()
        self.results = self.tm.get_all_results()
        return self.results

    @staticmethod
    def make_instrument_cmd(device, suite, pkg_name):
        cs = '.'.join([pkg_name, suite])
        cmd = "adb -s %s shell am instrument -e class %s \
              -w %s/android.test.InstrumentationTestRunner" % \
              (device, cs, pkg_name)

        return cmd

    def pull_pics(self, path):
        pass

    def save_results(self):
        #f = open(os.path.join(pth, 'log_%s.txt' % self.current_case), 'a+')
        for x in self.results:
            sub_path = os.path.join(self.output, x['device'])
            if not os.path.exists(sub_path):
                os.makedirs(sub_path)
            self.pull_pics(sub_path)

            f = open(os.path.join(self.output, '%s.txt' % x['device']), 'a+')
            f.write("Device: %s\n" % x['device'])
            f.write("info: \n")
            for r in x['results']:
                f.write(r['case'] + '\n')
                f.writelines(r['result'])
                f.write('-' * 100 + '\n')
            f.close()

if __name__ == "__main__":
    Robotium.save_results()
