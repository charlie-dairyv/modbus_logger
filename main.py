import serial
import simSerial
import Queue
#import Threading
import logging
import modbus_tk
import modbus_tk.modbus_rtu as tkRtu
import modbus_tk.defines as cst



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
logger = logging.getLogger('pilot_app')
logger.addHandler(console)

# Now, we can log to the root logger, or any other logger. First the root...
logging.info('------Starting--------')

# Now, define a couple of other loggers which might represent areas in your
# application:

logger1 = logging.getLogger('myapp.area1')
logger2 = logging.getLogger('myapp.area2')


#test serial
portNbr = 4
baudrate = 9600

try:
    master = tkRtu.RtuMaster(simSerial.simSerial(port=portNbr, baudrate=baudrate))
    master.set_timeout(5.0)
    master.set_verbose(True)
    logger.info("connected")

    logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 100, 3))

except modbus_tk.modbus.ModbusError, e:
        logger.error("%s- Code=%d" % (e, e.get_exception_code()))