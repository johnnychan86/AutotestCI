# -*- coding: utf-8 -*- 
'''
Created on 2013-11-15

@author: juliochen
'''
import os
import util

class PackageError(Exception):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return Exception.__str__(self) + self.msg

class Apk(object):
    def __init__(self, store_path, pkg_name, version=''):
        
        self.path = util.get_path(store_path)
        self.pkg_name = pkg_name
        if version:
            self.version = version
        else:
            self.version = os.path.basename(self.path)
        
    def uninstall(self, device):
        cmd = "adb -s %s uninstall %s " % (device, self.pkg_name)
        ret = os.popen(cmd).readlines()
        for r in ret:
            if "Failure" in r:
                return False
        return True
    
    def install(self, device, override=False):
        op = '-r' if override else ''
        cmd = "adb -s %s install %s %s" % (device, op, self.path)
        ret = os.popen(cmd).readlines()

        if ret and "Failure" in ret[-2]:
            print("Failed install package on %s: %s" % (device, ret[-2]))
            return False
            #raise PackageError("Failed install package on %s" % d)
        
        return True
        