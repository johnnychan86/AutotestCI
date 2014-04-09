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


class TaskManager(object):
    def __init__(self, devices):
        self.devices = devices
        self.params = []
        self.results = []
 
    def one_for_all(self, tp, cases, target, version, timeout=0):
        if not self.devices:
            print "No device available"
            return

        time_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        for d in self.devices:
            param = {'time_stamp': time_stamp,
                     'type': tp,
                     'device': d,
                     'timeout': timeout,
                     'cases': cases,
                     'target': target,
                     'version': version}
            self.params.append(param)

    def add_test(self, tp, device, cases, target, version, timeout=0):
        time_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        param = {'time_stamp': time_stamp,
                 'type': tp,
                 'device': device,
                 'timeout': timeout,
                 'cases': cases,
                 'target': target,
                 'version': version}
        self.params.append(param)
 
    def get_tests(self):
        return self.params

    def get_results(self):
        return self.results

    def start_test(self):
        self.tm = ThreadManager(self.devices)
        for param in self.params:
            if param['type'] == 'monkey':
                task = MonkeyTask(param)
            elif param['type'] == 'robotium':
                task = RobotiumTask(param)
            self.tm.add_job(task)

        self.tm.wait_for_complete()
        self.results = self.tm.get_all_results()
        self.save_results()

    def save_results(self):
        for x in self.results:
            f = open(os.path.join(self.output, '%s.txt' % x['device']), 'a+')
            f.write("Device: %s\n" % x['device'])
            f.write("info: \n")
            for r in x['results']:
                f.write(r['case'] + '\n')
                f.writelines(r['result'])
                f.write('-' * 100 + '\n')
            f.close()


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

if __name__ == "__main__":
    pass
