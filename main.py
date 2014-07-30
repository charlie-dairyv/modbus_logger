from __future__ import print_function
import serial
import simSerial
import Queue
import threading
import logging
import modbus_tk
import modbus_tk.modbus_rtu as tkRtu
import modbus_tk.defines as cst
# ---- module stuff -----
import ModelDevice as Device
import Model
from random import random
from time import sleep


# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='logga.log',
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

# Now, define a couple of other loggers which might represent areas in your
# application:

logger1 = logging.getLogger('myapp.area1')
logger2 = logging.getLogger('myapp.area2')


#test serial
portNbr = 4
baudrate = 9600

#----- MAIN -----

testDevice = Device.Device(random)
testDummy = Device.Dummy(random)
testModel = Model.Model()


testModel.add_device(testDummy, testDummy.getPV)
testModel.clock.subscribe(testModel.printme)

logger.debug(testModel.clock.callbacks)
testModel.start()

while True:
    sleep(5)
    print(len(testModel.data))