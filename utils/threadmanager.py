# -*- coding: utf-8 -*-
'''
'''
import Queue
from threading import Thread


class ThreadManager(object):
    '''
    Create and start threads.
    '''

    def __init__(self, devices, time_out=1):
        '''
        '''
        self.work_q = Queue.Queue()
        self.resutl_q = Queue.Queue()
        self.workers = []
        self.timeout = time_out
        self._recruitThreads(devices)
        
    def _recruitThreads(self, lst):
        for l in lst:
            worker = Runner(self.work_q, self.resutl_q, device)
            self.workers.append(worker)
            
    def wait_for_complete(self):
        '''
        Wait for all threads complete.
        '''
        while len(self.workers):
            worker = self.workers.pop()
            worker.join()
            if worker.isAlive() and not self.work_q.empty():
                self.workers.append(worker)
        print "Done!"
                
    def add_job(self, task):
        self.work_q.put(task)
        
    def get_all_results(self):
        results = []
        while True:
            try:
                results.append(self.resutl_q.get(timeout = self.timeout))
            except Queue.Empty:
                break
            
        return results
        

class Runner(Thread):
    timeout = 2
    
    def __init__(self, work_q, result_q, device):
        Thread.__init__(self)
        self.work_q = work_q
        self.result_q = result_q
        self.device = device
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:
            try:
                task = self.work_q.get(timeout = Runner.timeout)
                if self.device == task.device:
                    task.run()
                    self.result_q.put(task.results)
                else:
                    self.work_q.put(task)
            except Queue.Empty:
                break
                
