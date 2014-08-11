import os, pty, serial, sys, logging, errno
from timeout import timeout

class simSerial(object):
    def __init__(self, port=None, baudrate=9600, timeout=None, logger=None, *args, **kwargs):
        self.master, slave = pty.openpty()
        self.s_name = os.ttyname(slave)
        self.ser = serial.Serial(self.s_name)
        self.baudrate = baudrate
        self.ser.setTimeout(timeout)

        loggername = 'simSerial{0}'.format(self.s_name[-2:])
        self.logger = logger or logging.getLogger(loggername)
        self.logger.info('Initializing simSerial at {0}'.format(self.s_name))

    @property
    def name(self):
        return self.s_name


    def write(self, data):
        """Parameters: data to send
        Returns: Number of bytes written
        """
        self.ser.write(data)
        return sys.getsizeof(data)

#    @timeout(1,os.strerror(errno.ETIMEDOUT))
    def read(self, size=1):
        """Parameters: number of bytes to read
        Returns: Bytes read from the port."""
        return os.read(self.master,size)

    def portstr(self):
        return self.name

    def isOpen(self):
        return True

    def close(self):
        pass

    def flushInput(self):
        self.ser.flushInput()

    def flushOutput(self):
        self.ser.flushOutput()

    def flush(self):
        self.ser.flush()

    @property
    def timeout(self):
        return self.ser.getTimeout()

    @timeout.setter
    def timeout(self, value):
        self.logger.debug("Timeout set to {0}".format(value))
        self.ser.setTimeout(value)
