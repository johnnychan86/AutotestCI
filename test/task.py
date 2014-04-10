# -*- coding: utf-8 -*-  
'''
Created on 2013-11-15

@author: juliochen
'''
import os
import time
import subprocess
import logging

from utils import util

class Task(object):
    device_log_path = '/mnt/sdcard/autotest'
    
    def __init__(self, param):
        self.results = {}
        self.results['results'] = []
        self.param = param
        self.time_stamp = param['time_stamp']
        self.device = param['device']
        self.log_path = "./logs/" + param['time_stamp']
        self.log_path = util.get_path(self.log_path)
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

    def run(self):
        self.output = os.path.join(self.log_path, self.param['device'])
        os.mkdir(self.output)

    def pull_log(self, device, souce, dest):
        cmd = '%s/ %s' % (souce, dest)
        res =util.adb_runner(device, cmd, key_cmd='pull', timeout=120)
        for r in res:
            print r

class RobotiumTask(Task):
    device_logcat = '/mnt/sdcard/logcat'

    def __init__(self, param, time_stamp='', log=True):
        Task.__init__(self, param, time_stamp)
        self.timeout = param['timeout']
        self.log = log

    def clear_device_log(self, pth):
        res = util.adb_runner(self.param['device'], 'rm %s/*' % pth)
        for r in res:
            print r

    def pull_logcat(self, device, base_path, log):
        cmd = '%s/%s %s' % (
            self.device_logcat, log, os.path.join(base_path, log))
        res = util.adb_runner(device, cmd, key_cmd='pull')
        for r in res:
            print r

    def logcat(self, device, output):
        cmd = ("adb -s %s logcat -v threadtime -f %s/logcat.log -r 1024 -n 2" % 
               (device, output))
        proc = subprocess.Popen(cmd, shell=False)
        return proc

    def test(self):
        for case in self.param['case']:
            cmd = util.make_instrument_cmd(
                self.param["device"], case, self.param['target'])
            r = os.popen(cmd).readlines()
            self.results["device"] = self.param["device"]
            self.results['results'].append({'case': case, 'result': r})
            time.sleep(2)

    def run(self):
        Task.run()
        util.adb_runner(self.param['device'], 'mkdir %s' % self.device_log_path)
        util.adb_runner(self.param['device'], 'mkdir %s' % self.device_logcat)
        proc = None
        if self.time_stamp and self.log:
            proc = self.logcat(self.param['device'], self.device_log_path)

        start =time.time()
        if self.timeout:
            begin = time.time()
            current = time.time()
            while current < begin + self.timeout:
                self.test()
                current = time.time()
        else:
            self.test()

        #TODO
        #self.results['time_consum'] = time.time() - start
        if self.log:
            self.pull_log(self.param['device'], self.device_log_path, self.output)

        #pull logcat files
        if proc:
            proc.terminate()
            proc.wait()

            os.mkdir(os.path.join(output, 'logcat'))
            self.pull_logcat(self.param['device'], 
                             os.path.join(output, 'logcat'),
                             'logcat.log')
            for x in range(2):
                self.pull_logcat(self.param['device'],
                                 os.path.join(output, 'logcat'),
                                 'logcat.log.' + str(x + 1))
            self.clear_device_log(self.device_log_path)



class MonkeyTask(Task):    
    def __init__(self, param):
        Task.__init__(self, param)
        self.timeout = param['timeout']
            
    def sdcard_detect(self):
        cmd = 'ls %s' % self.device_log_path.replace('autotest', '')
        res = util.adb_runner(self.param['device'], cmd)
        print res
        for r in res:
            if 'Permission denied' in r:
                self.device_log_path = self.device_log_path.replace('/mnt', '')
        
    def push(self, device, src, dest):
        cmd = '%s %s' % (src, dest)
        res = util.adb_runner(device, cmd, key_cmd='push')
        if res[1]:
            logging.error(res[1])
        
            
    def run(self):
        Task.run()
        
        util.adb_runner(self.param['device'], 'mkdir %s' % self.device_log_path)
        self.clear_device_log()
        
        shell = util.make_monkey_shell(self.param['case'], self.param['device'],
                               self.device_log_path, self.param['target'])
        #push shell to device
        self.push(self.param['device'], shell, '%s/monkey.sh' % self.device_log_path)
        
        start = time.time()
        out, err = util.adb_runner(self.param['device'], 
                        '/system/bin/sh %s/monkey.sh' % self.device_log_path,
                        timeout=self.timeout)
        
        #if err:
        #    logger.error(err)
        self.pull_log(self.param['device'], self.device_log_path, self.output)
        #for i in range(len(self.param['case'])):
        #    self.pull_log(self.param['device'], output, 'log_%s.log' % str(i))
            
        self.clear_device_log()
        #TODO
        self.results[self.param['device']] = time.time() - start

