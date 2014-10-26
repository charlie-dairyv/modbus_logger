import logging
import threading
from threading import Thread
import csv
import traceback
import modbus_tk.defines as tkCst
import observables
#from collections import namedtuple
import csv
import datetime
#import time
#import SOLOregisters
#import Queue
#import sys


logger = logging.getLogger(__name__)


class Model(threading.Thread):
    """Takes data from devices each interval and moves it to it's internal data list"""
    def __init__(self, devices=[], dataset=[]):
        super(Model, self).__init__()
        self.clock = observables.RecordingHeartbeat()
        self.devices = devices
        self.data = dataset
        self.__data_dispatcher = observables.QueueDispatcher(self.clock.output)
        self.__data_dispatcher.subscribe(self.__append_to_data)
        self.clock.subscribe(self.__data_dispatcher.dispatch_all)
        self.data_lock = threading.Lock()
        self.daemon = True

        for name, device in self.devices.items():
            #TODO: Fix Model initiation
            #sloppy, device has to guess at which function to query
            self.clock.subscribe(device.getPV)

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
    def __init__(self,  devices=[], AutoName=True, targetfile=None, fieldnames=None):
        super(FileWriterModel, self).__init__(devices)
        if AutoName is True and targetfile is None:
            #"Names data file with todays date. Does not override a provided targetfile name"
            targetfile = autoname('isodate','csv')

        if fieldnames is None:
        #TODO get rid of this lazy hack
            self.fieldnames = ('time','device',"value")
        else:
            self.fieldnames = fieldnames

        self.file = CSVFileWriter(self.fieldnames, targetfile)
        self.add_data_handler(self.file.write_event)
        
    def autoname(self,style='isodate', extension='csv'):
        "returns new file name string with specified name style and extension."
        new_file_name = None
        if style = 'isodate':
            today =  datetime.date.today()
            name_string= today.strftime('%Y%m%d')
            
        
        new_file_name = name_string + '.' + extension
        return new_file_name



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
        with open(self.filename,'a') as csvfile:
            writer = csv.DictWriter(csvfile, self.fieldnames, delimiter='\t', restval= None, extrasaction='ignore')
            writer.writerow(event.__dict__)




