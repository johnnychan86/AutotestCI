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

logger = logging.getLogger('E')

class Task(object):
    device_log_path = '/mnt/sdcard/autotest'
    
    def __init__(self, param, time_stamp=''):
        self.results = {}
        self.results['results'] = []
        self.param = param
        self.time_stamp = time_stamp

    def run(self):
        print "Not implemented"

class RobotiumTask(Task):
    device_log_path = '/mnt/sdcard/autotest'
    device_crash = '/mnt/sdcard/crash'

    def __init__(self, param, time_stamp=''):
        Task.__init__(self, param, time_stamp)
        self.log_path = util.get_path(
            os.path.join('./logs/', time_stamp))

    def clear_device_log(self, pth):
        res = util.adb_runner(self.param['device'], 'rm %s/*' % pth)
        
        if res[1]:
            logger.error(res[1])

    def pull_logcat(self, device, base_path, log):
        cmd = '%s/%s %s' % (
            self.device_log_path, log, os.path.join(base_path, log))
        res = util.adb_runner(device, cmd, key_cmd='pull')
        if res[1]:
            logger.error(res[1])

    def pull_crashlog(self, device, base_path, log):
        cmd = '%s/%s %s' % (self.device_crash, 
                            log, os.path.join(base_path, log))
        util.adb_runner(device, cmd, key_cmd='pull')
        
    def logcat(self, device, output):
        cmd = ("adb -s %s logcat -v threadtime -f %s/logcat.log -r 1024 -n 2" % 
               (device, output))
        proc = subprocess.Popen(cmd, shell=False)
        return proc

    def run(self):
        util.adb_runner(self.param['device'], 'mkdir %s' % self.device_log_path)
        proc = None
        if self.time_stamp:
            output = os.path.join(self.log_path, self.param['device'])
            os.mkdir(output)
            proc = self.logcat(self.param['device'], self.device_log_path)

        for case in self.param['case']:
            cmd = util.make_instrument_cmd(
                self.param["device"], case, self.param['target'])
            r = os.popen(cmd).readlines()
            self.results["device"] = self.param["device"]
            self.results['results'].append({'case': case, 'result': r})
            time.sleep(2)

        
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
    def __init__(self, param, time_stamp, timeout=None):
        Task.__init__(self, param, time_stamp)
        self.time_stamp = time_stamp
        self.timeout = timeout
#         self.sdcard_detect()
        
        self.log_path = "./logs/" + time_stamp
        self.log_path = util.get_path(self.log_path)
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)
            
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
            logger.error(res[1])
        
            
    def run(self):
        output = os.path.join(self.log_path, self.param['device'])
        os.mkdir(output)
        
        util.adb_runner(self.param['device'], 'mkdir %s' % self.device_log_path)
        self.clear_device_log()
        
        shell = util.make_monkey_shell(self.param['case'], self.param['device'],
                               self.device_log_path, self.param['target'])
        #push shell to phone
        self.push(self.param['device'], shell, '%s/monkey.sh' % self.device_log_path)
        
        start = time.time()
        out, err = util.adb_runner(self.param['device'], 
                        '/system/bin/sh %s/monkey.sh' % self.device_log_path)
        
        if err:
            logger.error(err)
        for i in range(len(self.param['case'])):
            self.pull_log(self.param['device'], output, 'log_%s.log' % str(i))
            
        self.clear_device_log()
        self.results[self.param['device']] = time.time() - start

