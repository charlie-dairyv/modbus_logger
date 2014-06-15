#!/usr/bin/python

import serial
import modbus_tk.defines as tkCst
import modbus_tk.modbus_rtu as tkRtu

slavesArr = [2]
iterSp = 100
regsSp = 10
portNbr = 21
portName = 'com22'
baudrate = 153600

timeoutSp=0.018 + regsSp*0
#print "timeout: %s [s]" % timeoutSp

tkmc = tkRtu.RtuMaster(serial.Serial(port=portNbr, baudrate=baudrate))
tkmc.set_timeout(timeoutSp)

errCnt = 0
startTs = time.time()
for i in range(iterSp):
  for slaveId in slavesArr:
    try:
        tkmc.execute(slaveId, tkCst.READ_HOLDING_REGISTERS, 0,regsSp)
    except:
        errCnt += 1
        tb = traceback.format_exc()
stopTs = time.time()
timeDiff = stopTs  - startTs
print("modbus-tk:\ttime to read %s x %s (x %s regs): %.3f [s] / %.3f [s/req]" % (len(slavesArr),iterSp, regsSp, timeDiff, timeDiff/iterSp))
if errCnt >0:
    print("   !modbus-tk:\terrCnt: %s; last tb: %s" % (errCnt, tb))
tkmc.close()

