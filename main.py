#!/usr/bin/env

from __future__ import print_function
import serial
import simSerial
#import Queue
import threading
import logging
from ConfigParser import SafeConfigParser
import cmd
import sys

import modbus_tk
import modbus_tk.modbus_rtu as tkRtu
import modbus_tk.defines as cst

# ---- module stuff -----
import ModelDevice as Device
import Model
from random import random
from time import sleep

#--- Load main parameters from cfg file
parser = SafeConfigParser()

try:
    parser.read('main.cfg')
except:
    logger.warning("There was an error opening the config file %s: \n%s" % (cfgfile,sys.exc_info()[0]))
    logger.info("Using default parameters to initialize")

    parser.add_section('main')
    parser.set('main', 'log file', 'pilot.log')
    parser.set('main', 'device configuration', 'device.cfg')
finally:
    log_file = parser.get('main', 'log file')
    device_cfg_file = parser.get('main', 'device configuration')


#--- Set up Logging to File And Console
# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=log_file,
                    filemode='w')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)

# add the handler to the root logger
logger = logging.getLogger(__name__)
logger.addHandler(console)

# Now, we can log to the root logger, or any other logger. First the root...
logger.info('------Starting--------')


import plotly_frontend as pfront

#---  Set up Serial Port
logger.info('------Initializing--------')
try:
    ser = serial.Serial(
        port='/dev/tty.usbserial-A603IXGL',
        baudrate=9600,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
except OSError, e:
    logger.error("OSError: %s" % e)
    if e.__str__().find("[Errno 2]") == -1:
        raise e
    else:
        ser = simSerial.simSerial(port=4, baudrate=9600)
        logger.info("Specified serial port doesn't exist. Created simulated serial port at %s" % ser.name)


#--- Set up custom CMD console
class logger_console(cmd.Cmd):

    def do_EOF(self, line):
        return True

    def do_print(self, line):
        for each in myModel.data:
            print(each)

    def do_quit(self, line):
        return True

#--- Set up Modbus Interface
timeout = .02
ser.flush()
interface = tkRtu.RtuMaster(ser)
interface.set_timeout(timeout)


#----- MAIN -----
mydevices = Device.MakeDevicesfromCfg(device_cfg_file, interface.execute)
mydevices['FI13'] = Device.micromotion2700series(interface.execute,12)
logger.info("Created devices: %s" % mydevices)

myModel = Model.FileWriterModel(devices=mydevices, targetfile="test.csv")
logger.debug("Model initiated with devices: %s" % myModel.clock.callbacks)

#Create frontend
graph = pfront.plotly_frontend(mydevices.keys())
graph.create()
myModel.add_data_handler(graph.write_event)

console = logger_console()

if __name__ == '__main__':
    myModel.start()
    console.cmdloop()
