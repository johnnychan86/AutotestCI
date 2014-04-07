# -*- coding: utf-8 -*-
'''
Created on 2014-03-31

@author: juliochen
'''
import device_mapper

class Device(object):
    def __init__(self, id):
        self.id = id
        self.model = self.get_model(id)
        self.system = self.get_sys(id)

    def reboot(self):
        #TODO
        pass

    def initialize(self):
        #TODO
        pass

    def get_model(self, id):
        return device_mapper.get_model(id)

    def get_sys(self):
        return device_mapper.get_os(id)

    def is_up(self, timeout=0):
        #TODO
        pass

