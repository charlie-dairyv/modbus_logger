from random import random, randint
from ConfigParser import SafeConfigParser
import SOLOregisters
import collections
import modbus_tk.defines as MBUS
from modbus_tk.modbus import ModbusInvalidResponseError
import sys
import struct

import logging
logger = logging.getLogger(__name__)


class Device(object):
    """device to be regularly polled for process data"""
    def __init__(self, socketfn, name=None):
        #give it someway to connect to real device
        self._execute = socketfn
        self._name = name


    def getPV(self,*args, **kwargs):
        #Should return process value for this device as a dict
        #Each key in the dict should describe it's value
        #for single value devices, the key is usually the device name
        return {self.name, None}

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



    def __poll(self, max_attempts=10):
        #Note:  this is not thread-safe
        tries = 0
        success = False
        while tries < max_attempts and success != True:
            try:
                poll_reply = self._execute(self.address,
                                            self.query['function_code'],
                                            self.query['starting_register'] + self.address_offset,
                                            self.query['registers_to_read'])
                success = True
            except ModbusInvalidResponseError, e:
                logger.warning(e)
                poll_reply = None
                tries += 1
            except:
                poll_reply = None
                tries += 1


        return poll_reply

    def getPV(self,*args,**kwargs):
        # reply = tkmc.execute(slaveId, MBUS.READ_HOLDING_REGISTERS, SOLOregister["PV"],1)
        self.query['function_code']     = MBUS.READ_HOLDING_REGISTERS
        self.query['starting_register'] = self.registers["PV"]
        self.query['registers_to_read'] = 1

        value = self.__poll()
        reply = {}
        try:
            reply[self.name] = value[0] #unpack tuples and lists if possible
        except:
            reply[self.name] = value
        
        return reply

    def getNamedRegister(self, reg_name, num_of_registers=1):
        self.query['function_code']     = MBUS.READ_HOLDING_REGISTERS
        self.query['starting_register'] = self.registers[reg_name]
        self.query['registers_to_read'] = num_of_registers
        return self.__poll()

    def getRegisterAddress(self, reg_number, num_of_registers=1):
        self.query['function_code']     = MBUS.READ_HOLDING_REGISTERS
        self.query['starting_register'] = reg_number
        self.query['registers_to_read'] = num_of_registers
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
        decimal_position = self.getNamedRegister('Decimal Point Position')
        self.decimal_correction = 1. / pow(10,decimal_position)

    @property
    def name(self):
        if self._name is None:
            return "Solo4848 #%s" % self.address
        else:
            return self._name

    def getPV(self,*args,**kwargs):
        reply = super(SOLO4848, self).getPV(args, kwargs)
        corrected_value = reply[self.name] * self.decimal_correction
        reply[self.name] = corrected_value
        return reply


class micromotion2700series(ModbusSlaveDevice):
    def __init__(self,modbusExecuteFunc, SlaveID):
        super(micromotion2700series, self).__init__(modbusExecuteFunc, SlaveID, registers = {}, address_offset=0)
        self.registers = {
            'Mass flow rate':1,
            'Density':2,
            'Temperature':3,
            'Volume flow rate':4,
            'Mass total':7,
            'Volume total':8,
            'Mass inventory':9,
            'Volume inventory':10,
            'Mass flow rate scale factor':28,
            'Density scale factor':29,
            'Temperature scale factor':30,
            'Volume flow rate scale factor':31,
            'Mass inventory scale factor':36
            }


    @property
    def name(self):
        if self._name is None:
            return "Series2700 #%s" % self.address
        else:
            return self._name

    def getPV(self, *args, **kwargs):
        reply = {}
        queries = ["Mass flow rate", 'Density', 'Temperature']
        for each in queries:
            data = self.get_named_PV(each, *args, **kwargs)
            reply.update(data)
        return reply


    def get_named_PV(self, PV_name, scale_factor='Auto', scale_factor_name=None, *args, **kwargs):
        try:
            value = self.getRegisterAddress(self.registers[PV_name], 1)[0]
        except:
            value = None
            traceback.print_exc()

        try:
            scale_factor_name = PV_name + " scale factor"
            scale = self.getRegisterAddress(self.registers[scale_factor_name], 1)[0]
        except:
            scale = 1
            traceback.print_exc()

        reply = {PV_name: self.scale_process_value(value, scale)}
        return reply

    def scale_process_value(self, process_value, scale_value):
        try:
            float_value = float(process_value) / float(scale_value)
        except:
            #revise this section!!! Needs better error handling
            float_value = process_value
        return float_value


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
            reply = {self.name: self._execute()}
            return reply

def MakeDevicesfromCfg(cfgfile, exec_fucntion):
    "returns a dict of devices initialized from the cfg file and function to reach physical media"
    devices = {}
    parser = SafeConfigParser()

    try:
        parser.read(cfgfile)
    except:
        logger.warning("There was an error opening the device config file %s: \n%s" % (cfgfile,sys.exc_info()[0]))
        raise

    #TODO: load values into dict, pop req'd values to init device, append rest to device.__dict__
    for device_id in parser.sections():
        device_name = parser.get(device_id, 'name')
        device_address = parser.get(device_id, 'address')
        type_of_device = parser.get(device_id, 'type')
        try:
            is_enabled = parser.get(device_id, 'enable')
        except:
            is_enabled = 'True'

        #TODO: modify to load paramams from dvc (cfg type) file
        if is_enabled == 'True':
            new_device = ModbusSlaveDevice(exec_fucntion, device_address, registers = SOLOregisters.holding_registers, name=device_name)
            devices[device_id] = new_device

    return devices
