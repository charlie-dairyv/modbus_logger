import logging
import threading
from threading import Thread
import time
import csv
import datetime
import sys
import traceback
import Queue
import modbus_tk.defines as tkCst
from collections import namedtuple
import SOLOregisters


class Event(object):
    pass


class Observable(object):
    def __init__(self):
        self.callbacks = []

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def unsubscribe(self, callback):
        self.callbacks.remove(callback)

    def fire(self, **attrs):
        e = Event()
        e.source = self
        for k, v in attrs.iteritems():
            #attach attributes passed to fire() to event
            setattr(e, k, v)
        for fn in self.callbacks:
            #pass event (w/ attrs) to functions
            return fn(e)

class Heartbeat(Observable):
    def __init__(self, interval=1, **kwargs):
        super(Heartbeat, self).__init__()
        self.interval = interval
        self.kwargs = kwargs
    #TODO Move threading code inside of class
    def run(self):
        while True:
            try:
                self.fire(**self.kwargs)
            except:
                print '\aa Process subscribed to Heartbeat has raised an exception\n'
                print "Unexpected error:", sys.exc_info()[0]
                raise
            finally:
                time.sleep(self.interval)

class RecordingHeartbeat(Heartbeat):
    def __init__(self, output_q=Queue.Queue(),interval=1, **kwargs):
        super(RecordingHeartbeat, self).__init__()
        self.interval = interval
        self.kwargs = kwargs
    #TODO Move threading code inside of class
    def run(self):
        while True:
            try:
                reply = self.fire(**self.kwargs)
                if reply is not bool:
                    timeAndReply = time.time(), reply
                    #self.output.append(timeAndReply)
                    #self.output_q.put(timeAndReply)

            except:
                raise
            finally:
                time.sleep(self.interval)


class QueueDispatcher(Observable):
    def __init__(self, queue_to_empty):
        super(QueueDispatcher, self).__init__(self)
        self.inputQueue = queue_to_empty

    def dispatch_item(self):
            self.data = self.inputQueue.get()
            self.fire(data)
            self.inputQueue.task_done()

    def dispatch_all(self, quantity=0):
            if quantity==0: quantity = inputQueue.qsize()
            for i in range():
                self.dispatch_item()

class Model(object):
    def __init__(self):
        self.clock = RecordingHeartbeat()
        self.devices = []

    def add_device(self,device,function):
        self.devices.append(device)
        self.clock.subscribe(function)

    def start(self):
        self.clock.run()
