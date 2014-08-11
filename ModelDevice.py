from random import random, randint
from ConfigParser import SafeConfigParser
import SOLOregisters
import collections
import modbus_tk.defines as MBUS
from modbus_tk.modbus import ModbusInvalidResponseError

import logging
logger = logging.getLogger(__name__)


class Device(object):
    """device to be regularly polled for process data"""
    def __init__(self, socketfn, name=None):
        #give it someway to connect to real device
        self._execute = socketfn
        self._name = name


    def getPV(self,*args, **kwargs):
        #Should return process value for this device
        return None

    @property
    def name(self):
        if self._name is None:
            self._name = "Unnamed Device %s" % randint(0,255)
            return self._name
        else:
            return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class ModbusSlaveDevice(Device):
    def __init__(self,modbusExecuteFunc, SlaveID, name=None, registers={}, address_offset=-1, lock = None):
        """Manages a connection with A Modbus slave.
        Takes a modbus_tk.modbus.Master.execute function """
        super(ModbusSlaveDevice, self).__init__(modbusExecuteFunc, name=name)
        self.address  = int(SlaveID)
        self.registers = registers
        self.address_offset = address_offset
        self.record = True
        #if lock
        #TODO figure out if it makes sense to use lock at this level

        #setdefaults
        self.query = {'function_code':MBUS.READ_HOLDING_REGISTERS,
            'starting_register':None,
            'registers_to_read':0}
        logger.info("modbus slave device initiated at %s" % SlaveID)
        logger.info("Type of query.registers to read is %s" % type(self.query['registers_to_read']))



    def __poll(self):
        #Note:  this is not thread-safe
        try:
            poll_reply = self._execute(self.address,
                                        self.query['function_code'],
                                        self.query['starting_register'] + self.address_offset,
                                        self.query['registers_to_read'])
        except ModbusInvalidResponseError, e:
            logger.warning(e)
            poll_reply = None

        return poll_reply

    def getPV(self,*args,**kwargs):
        # reply = tkmc.execute(slaveId, MBUS.READ_HOLDING_REGISTERS, SOLOregister["PV"],1)
        self.query['function_code']     = MBUS.READ_HOLDING_REGISTERS
        self.query['starting_register'] = self.registers["PV"]
        self.query['registers_to_read'] = 1

        return self.__poll()

    def getNamedRegister(self, reg_name):
        self.query['function_code']     = MBUS.READ_HOLDING_REGISTERS
        self.query['starting_register'] = self.registers[reg_name]
        self.query['registers_to_read'] = 1
        return self.__poll()

    def getRegisterAddress(self, reg_number):
        self.query['function_code']     = MBUS.READ_HOLDING_REGISTERS
        self.query['starting_register'] = reg_number
        self.query['registers_to_read'] = 1
        return self.__poll()

    @property
    def name(self):
        if self._name is None:
            return "ModbusSlaveDevice %s" % self.address
        else:
            return self._name



    #TODO
    #   Add "currently in error state" flag
    #   Add get last error func



class SOLO4848(ModbusSlaveDevice):
    def __init__(self,modbusExecuteFunc, SlaveID):
        super(SOLO4848, self).__init__(self, modbusExecuteFunc, SlaveID, registers = SOLOregisters.holding_registers)

    @property
    def name(self):
        if self._name is None:
            return "Solo4848 #%s" % self.address
        else:
            return self._name




class Dummy(Device):
    """Thin class that just returns the value from socket function
    Returns a random int if no function is passed"""

    def __init__(self, socketfn=None):
        if socketfn is None:
            socketfn = random

        super(Dummy, self).__init__(socketfn)
        #self.__execute = socketfn
        self.record = True

    def getPV(self,*args,**kwargs):
        try:
            e.record = True
        finally:
            return self._execute()

def MakeDevicesfromCfg(cfgfile, exec_fucntion):
    "returns a dict of devices initialized from the cfg file and function to reach physical media"
    devices = {}
    parser = SafeConfigParser()
    parser.read(cfgfile)

    #TODO: load values into dict, pop req'd values to init device, append rest to device.__dict__
    for device_id in parser.sections():
        device_name = parser.get(device_id, 'name')
        device_address = parser.get(device_id, 'address')
        type_of_device = parser.get(device_id, 'type')

        #TODO: modify to load paramams from dvc (cfg type) file
        new_device = ModbusSlaveDevice(exec_fucntion, device_address, registers = SOLOregisters.holding_registers)
        devices[device_id] = new_device

    return devices