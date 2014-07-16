#!/usr/bin/python

import serial, time
import modbus_tk.defines as tkCst
import modbus_tk.modbus_rtu as tkRtu
import modbus_tk.modbus as modbus
import logging
from SOLOregisters import holding_registers as SOLOregister
slavesArr = [1,2,3,4,5,6,7,8]
iterSp = 2
regsSp = 100
#portNbr = 21
#portName = '/dev/cu.usbserial-A603IXGL'
#baudrate = 153600

ser = serial.Serial(
	port='/dev/tty.usbserial-A603IXGL',
	baudrate=9600,
	parity=serial.PARITY_EVEN,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS
)

ModbusExceptions = {'1':"ILLEGAL_FUNCTION",
'2':"ILLEGAL_DATA_ADDRESS",
'3':"ILLEGAL_DATA_VALUE",
'4':"SLAVE_DEVICE_FAILURE",
'5':"COMMAND_ACKNOWLEDGE",
'6':"SLAVE_DEVICE_BUSY",
'8':"MEMORY_PARITY_ERROR"}

#SOLOregister = {"PV":4096,
#    "LED_STATUS":4138}

# set up logging to file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='logga.log',
                    filemode='w')

timeoutSp=0.018 + regsSp*.001
logging.info("----- Starting new run -----")
logging.info("timeout: %s [s]" % timeoutSp)


ser.flush()
tkmc = tkRtu.RtuMaster(ser)
tkmc.set_timeout(timeoutSp)

errCnt = 0
startTs = time.time()
for i in range(iterSp):
  for slaveId in slavesArr:
    try:
        reply = tkmc.execute(slaveId, tkCst.READ_HOLDING_REGISTERS, SOLOregister["PV"],1)
        print "Unit %s: %s" % (slaveId, reply)
        logging.info("Unit %s: %s" % (slaveId, reply))
    except modbus.ModbusInvalidResponseError, e:
        errCnt += 1
        logging.warning("Unit %s: Modbus Invalid Response Error: %s" % (slaveId,e))
    except modbus.ModbusError, e:
        exception = ModbusExceptions[e.get_exception_code]
        logging.warning("Unit %s: Modbus Exception: %s" % (slaveId, exception))
    except Exception, e:
        print "Unexpcted Error: ", e
        logging.error("---- Terminating:  Unhandled Error: ",e)
        raise
    finally:
        ser.flush()
stopTs = time.time()
timeDiff = stopTs  - startTs
print("modbus-tk:\ttime to read %s x %s (x %s regs): %.3f [s] / %.3f [s/req]" % (len(slavesArr),iterSp, regsSp, timeDiff, timeDiff/iterSp))
if errCnt >0:
    print("   !modbus-tk:\terrCnt: %s; last tb: %s" % (errCnt, e))
tkmc.close()

