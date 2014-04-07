# -*- coding: utf-8 -*-
'''
Created on 2013-11-15

@author: juliochen
'''
import os
import re

from utils import util
from utils import reporter
from failure import Crash
from failure import RCrash
from failure import ANR

class MonkeyLogParser(object):
    def __init__(self):
        pass

    def _search_crash(self, filename):
        f = open(filename, 'r')
        actions = []
        crash_info = []
        
        def has_trace(info):
            pass
        
        for line in f:
            pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} ')
            if pattern.match(line):
                line = pattern.split(line)[1]
            line = line.strip()
            if r'// Sending event #' in line:
                if crash_info:
                    self.crashes.append(Crash(crash_info, actions,
                                              self.param, filename))
                    crash_info = []
                actions = []
                actions.append(line)
            elif r'// CRASH: ' in line:
                if crash_info:
                    self.crashes.append(Crash(crash_info, actions,
                                              self.param, filename))
                    crash_info = []
                crash_info.append(line)
            elif 'ANR in ' in line:
                if crash_info:
                    self.crashes.append(Crash(crash_info, actions,
                                              self.param, filename))
                break
            elif crash_info:
                if line.startswith(r"//"):
                    crash_info.append(line)
                if re.match(r"//\s*$", line):
                    self.crashes.append(Crash(crash_info, actions,
                                              self.param, filename))
                    crash_info = []
                    actions = []
            elif actions:
                actions.append(line)
                
        if(crash_info):
            self.crashes.append(Crash(crash_info, actions,
                                      self.param, filename))
                
        f.close()
                
    def _search_anr(self, filename):
        f = open(filename, 'r')
        actions = []
        anr_info = []
        
        for line in f:
            pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} ')
            if pattern.match(line):
                line = pattern.split(line)[1]
            line = line.strip()
            if r'// Sending event #' in line:
                actions = []
                actions.append(line)
            elif 'ANR in ' in line:
                anr_info.append(line)
            elif anr_info:
                anr_info.append(line)
            elif actions:
                actions.append(line)
            if len(anr_info) > 100:
                anr_info.append('...')
                break
        f.close()
        if anr_info:
            self.anrs.append(ANR(anr_info, actions, self.param, filename))
