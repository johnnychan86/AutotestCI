# -*- coding: utf-8 -*- 
'''
Created on 2014-2-27

@author: juliochen
'''
import os
import logging

from utils import util
from utils import logging_manager


class Initializer(object):
    def __init__(self):
        self.devices = []
    
    def adb_service_init(self):
        cmd = "adb start-server"
        reply = os.popen(cmd).readlines()
        
    def get_device_list(self):
        self.devices = util.load_devices()
        return self.devices
    
    def install_package(self, package, devices, override=False):
        logger.info("Installing package %s..." % package.pkg_name)
        failed = []
        for d in devices:
            logger.info('Installing package on %s' % d)
            if not package.install(d, override):
                failed.append(d)
                
        return failed
   
    def uninstall_package(self, package, devices):
        logger.info("Clearing old package...")
        for d in devices:
            package.uninstall(d)
    
    def install_packages(self, devices, packages, clear=True):
        for pkg in packages:
            if clear:
                self.uninstall_package(pkg, devices)
                self.install_package(pkg, devices)
            else:
                self.install_package(pkg, devices, True)
                
    def process_login(self, login_package, case):
        self.uninstall_package(login_package)
        self.install_package(login_package)

        logging.info("Prcessing login...")
        task_manager = TaskManager(util.load_devices())


    
