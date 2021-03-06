import logging
import Queue
from collections import namedtuple
import sys
import time



logger = logging.getLogger(__name__)


EventData = namedtuple('EventData',['time', 'device', 'value'])

class Event(object):
    def __str__(self):
        return self.__dict__.__str__()

class Observable(object):
    def __init__(self):
        self.callbacks = []

    def subscribe(self, callback, parent=None):
        logger.debug("Subscibing %s to %s" % (callback, self))
        self.callbacks.append(callback)


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
            try:
                fn(e)
            except e:
                logger.error("Firing %s has produced the error: %s" % (fn,e))
                raise

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
                logger.warning("Unexpected error: %s" % sys.exc_info()[0])
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


            try:
                if hasattr(fn.im_self,'record'): #and fn.im_class.record == True:
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
            #logger.debug("Processing from queue:\t %s" % self.data._asdict())
            self.fire(**self.data._asdict())     #**{"data":self.data}
            self.inputQueue.task_done()

    def dispatch_all(self, quantity=0):
            if quantity==0 or type(quantity) != int:
                logger.debug("Dispatching %s items from output queue" % self.inputQueue.qsize())
                quantity = self.inputQueue.qsize()
            for i in range(quantity):
                self.dispatch_item()