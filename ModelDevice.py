from random import randint

class Device(object):
    """device to be regularly polled for process data"""
    def __init__(self, socketfn, name=None):
        #give it someway to connect to real device
        self.__execute = socketfn
        self.__name = name


    def getPV(self,*args, **kwargs):
        #Should return process value for this device
        return None

    @property
    def name(self):
        if self.__name is None:
            self.__name = "Unnamed Device %s" % randint(0,255)
            return self.__name
        else:
            return self.__name

    @name.setter
    def name(self, new_name):
        self.__name = new_name


class ModbusSlaveDevice(Device):
    def __init__(self,modbusExecuteFunc, SlaveID, name=None, registers={}, address_offset=-1):
        """Manages a connection with A Modbus slave.
        Takes a modbus_tk.modbus.Master.execute function """
        super(ModbusSlaveDevice, self).__init__(self, modbusExecuteFunc, name)
        self.address  = SlaveID
        self.registers = registers
        self.address_offset = address_offset
        self.record = True


        #setdefaults
        ModbusQuery = collections.namedtuple('ModbusQuery', 'function_code starting_register registers_to_read')
        self.query = ModbusQuery(function_code=tkCst.READ_HOLDING_REGISTERS,
            starting_register = None,
            registers_to_read=0)


    def __poll(self):
        #Note:  this is not thread-safe
        poll_reply = self.__execute(self.address,
                                    self.query.function_code,
                                    self.query.starting_register + self.address_offset,
                                    self.query.registers_to_read)
        return poll_reply

    def getPV(self,**kwargs):
        # reply = tkmc.execute(slaveId, tkCst.READ_HOLDING_REGISTERS, SOLOregister["PV"],1)
        self.query.function_code     = tkCst.READ_HOLDING_REGISTERS
        self.query.starting_register = self.registers["PV"]
        self.query.registers_to_read = 1
        return self.__poll()

    def getNamedRegister(self, reg_name):
        self.query.function_code     = tkCst.READ_HOLDING_REGISTERS
        self.query.starting_register = self.registers[reg_name]
        self.query.registers_to_read = 1
        return self.__poll()

    def getRegisterAddress(self, reg_number):
        self.query.function_code     = tkCst.READ_HOLDING_REGISTERS
        self.query.starting_register = reg_number
        self.query.registers_to_read = 1
        return self.__poll()

    @property
    def name(self):
        if self.__name is None:
            return "ModbusSlaveDevice %s" % self.address
        else:
            return self.__name

    #TODO
    #   Add "currently in error state" flag
    #   Add get last error func



class SOLO4848(ModbusSlaveDevice):
    def __init__(self,modbusExecuteFunc, SlaveID):
        super(SOLO4848, self).__init__(self, modbusExecuteFunc,SOLOregisters.holding_registers)

    @property
    def name(self):
        if self.__name is None:
            return "Solo4848 #%s" % self.address
        else:
            return self.__name




class Dummy(Device):
    #Thin class that just returns the value from socket function
    def __init__(self, socketfn):
        #super(Dummy, self).__init__(self, socketfn)  not sure why this doesn't work
        self.__execute = socketfn
        self.record = True

    def getPV(self,*args,**kwargs):
        try:
            e.record = True
        finally:
            return self.__execute()