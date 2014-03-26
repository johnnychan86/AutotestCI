# -*- coding: utf-8 -*- 
'''
Created on 2014-2-27

@author: juliochen
'''
import os
import time
import subprocess
import platform
import httplib
import sys
import random

ROOT = r"D:\workspace\AutoTestCI"
root_path = os.path.abspath(os.path.dirname(sys.argv[0]))

def get_path(pth):
    
    if platform.system() == "Windows":
        r_path = pth.replace('/', "\\")
    else:
        r_path = pth
    
    return os.path.normpath(os.path.join(ROOT, r_path))

def load_devices():
    cmd = "adb start-server"
    os.popen(cmd)
    cmd = "adb devices"
    
    result = os.popen(cmd).readlines()
    del(result[0])
    return [x.strip().split('\t')[0]  for x in result if x.strip() != '']

def get_device_state(device):
    cmd = "adb devices"
    result = os.popen(cmd).readlines()
    del(result[0])
    
    for x in result:
        if device in x:
            return x.strip().split('\t')[1]

def adb_runner(device, params='', stdout=subprocess.PIPE,
               stderr=subprocess.PIPE, cmd='shell', timeout=None):
    cmd = "adb -s %s %s %s" % (device, cmd, params)
    
    if platform.system() == 'Linux':
        sh = True
    else:
        sh = False
    proc = subprocess.Popen(cmd, shell=sh, stdout=stdout,
                                 stderr=stderr)
    
    if timeout:
        begin = time.time()
        current = time.time()
        while current < begin + timeout:
            if proc.poll() is not None:
                break
            current = time.time()
        else:
            proc.terminate()
            proc.wait()
        return (proc.stdout.read(), proc.stderr.read())
    else:
        stdout, stderr = proc.communicate()
        return (stdout, stderr)

def make_monkey_cmd(cmd, device_store, stdout):
    cmd = '"%s > %s/%s 2>&1"' % (cmd, device_store, stdout)
    return cmd

def make_instrument_cmd(device, suite, pkg_name):
    cs = '.'.join([pkg_name, suite])
    cmd = "adb -s %s shell am instrument -e class %s \
    -w %s/android.test.InstrumentationTestRunner" % \
    (device, cs, pkg_name)
    
    return cmd

def make_monkey_shell(cmds, device, pth, package):
    shell_path = get_path('./res/monkey_%s.sh' % device)
    shell = open(shell_path, 'w+')
    cmds = [c.replace("package_name", package) for c in cmds]
    for c, i in zip(cmds, range(len(cmds))):
        cmd = c.replace('%pct%', str(random.randint(10, 90)))
        cmd = cmd.replace('%seed%', str(random.randint(1, 1000)))
        shell.write(cmd + ' > %s/log_%s.log 2>&1 \n' % (pth, str(i)))
        shell.write("am force-stop %s;sleep 2\n" % package)
    shell.close()
    return shell_path

def trigger_report():
    conn = httplib.HTTPConnection("mq.webdev.com")
    conn.request("GET", "/mobelcrash.php")
    res = conn.getresponse()
    print res.status, res.reason
    
