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
import csv


logger = logging.getLogger(__name__)

EventData = namedtuple('EventData',['time', 'device', 'value'])

class Event(object):
    pass


class Observable(object):
    def __init__(self):
        self.callbacks = []

    def subscribe(self, callback, parent=None):
        logger.debug("Subscibing %s to %s" % (callback, self))
        self.callbacks.append(callback)
        #logger.debug("Callbacks of %s:\n\t\t\t\t %s" % (self, self.callbacks))


    def unsubscribe(self, callback):
        self.callbacks.remove(callback)
        logger.debug("Callbacks of %s:\n\t\t\t\t %s" % (self, self.callbacks))


    def fire(self, **attrs):
        e = Event()
        e.source = self
        for k, v in attrs.iteritems():
            #attach attributes passed to fire() to event
            setattr(e, k, v)
        for fn in self.callbacks:
            #pass event (w/ attrs) to functions
            logger.debug("Firing %s" % fn)
            fn(e)

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
        self.output = output_q

    def fire(self, **attrs):
        e = Event()
        e.source = self
        for k, v in attrs.iteritems():
            #attach attributes passed to fire() to event
            setattr(e, k, v)
        for fn in self.callbacks:
            #pass event (w/ attrs) to functions
            reply = fn(e)
            logger.debug("fire recieved %s from \t%s" % (reply,fn))
            try:
                logger.debug("Record is %s" % fn.im_self.record)
            except:
                logger.debug("%s didn't have a record!" % fn.im_self)

            try:
                if hasattr(fn.im_self,'record'): #and fn.im_class.record == True:
                    logger.debug("starting to record!")
                    data = EventData(time.time(), fn.im_self,reply)
                    self.output.put(data)
                    logger.debug("Added to queue: %s,%s,%s" % data)
            except AttributeError:
                raise
            except:
                raise


class QueueDispatcher(Observable):
    def __init__(self, queue_to_empty):
        super(QueueDispatcher, self).__init__()
        self.inputQueue = queue_to_empty

    def dispatch_item(self):
            self.data = self.inputQueue.get()
            logger.debug("Processing from queue:\t %s" % self.data._asdict())
            self.fire(**self.data._asdict())     #**{"data":self.data}
            self.inputQueue.task_done()

    def dispatch_all(self, quantity=0):
            if quantity==0 or type(quantity) != int:
                logger.debug("Dispatching %s items from output queue" % self.inputQueue.qsize())
                quantity = self.inputQueue.qsize()
            for i in range(quantity):
                self.dispatch_item()

class Model(threading.Thread):
    """Takes data from devices each interval and moves it to it's internal data list"""
    def __init__(self, devices=[], dataset=[]):
        super(Model, self).__init__()
        self.clock = RecordingHeartbeat()
        self.devices = devices
        self.data = dataset
        self.__data_dispatcher = QueueDispatcher(self.clock.output)
        self.__data_dispatcher.subscribe(self.__append_to_data)
        self.clock.subscribe(self.__data_dispatcher.dispatch_all)
        self.data_lock = threading.Lock()
        self.daemon = True

    def __append_to_data(self, event_data):
        with self.data_lock:
            self.data.append(event_data)

    def add_device(self,device,function):
        self.devices.append(device)
        self.clock.subscribe(function)

    def run(self):
        self.clock.run()

    def printme(self, *args, **kwargs):
        logger.debug(self.data)

    def add_data_handler(self, new_data_handler):
        self.__data_dispatcher.subscribe(new_data_handler)

    #TODO :
    #def remove_data_handler(self, handler):

class FileWriterModel(Model):
    def __init__(self,  devices=[], targetfile=None, fieldnames=None):
        super(FileWriterModel, self).__init__(devices)
        self.add_data_handler(self.file.write_event)

        if fieldnames is None:
        #TODO get rid of this lazy hack
            self.fieldnames = ('time','device',"value")
        else:
            self.fieldnames
        self.file = CSVFileWriter(self.fieldnames, targetfile)



class CSVFileWriter(object):
    """ Attach it's write_event method to an Observable, processes events to a CSV file """
    #todo add filters! to this or dispatcher
    def __init__(self, field_names, targetfile=None):
        self.fieldnames = field_names
        if targetfile is not None:
            self.filename = targetfile
        else:
            pass
            #TODO add defaulting or error catching code here

    def write_event(self, event):
        """ takes an event write it to a csv file """
        logger.debug("write_event args: %s" % event.__dict__)
        with open(self.filename,'a') as csvfile:
            writer = csv.DictWriter(csvfile, self.fieldnames, delimiter='\t', restval= None, extrasaction='ignore')
            writer.writerow(event.__dict__)




