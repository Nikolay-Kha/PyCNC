import os
import fcntl
import struct
import time
import atexit
import threading

ADS111x_ADDRESS = 0x48
I2C_SLAVE = 0x0703


class __I2CDev(object):
    def __init__(self):
        self._os_close = os.close
        # Initialize i2c interface and register it for closing on exit.
        self._dev = os.open("/dev/i2c-1", os.O_SYNC | os.O_RDWR)
        if self._dev < 0:
            raise ImportError("i2c device not found")
        else:
            if fcntl.ioctl(self._dev, I2C_SLAVE, ADS111x_ADDRESS) < 0:
                self._close()
                raise ImportError("Failed to set up i2c address")
            else:
                atexit.register(self._close)

    def _close(self):
        self._os_close(self._dev)

    def write(self, data):
        os.write(self._dev, data)

    def read(self, n):
        return os.read(self._dev, n)

i2c = __I2CDev()

# mutex for multi threading requests
lock = threading.Lock()


def measure(channel):
    """
    Measure voltage on chip input.
    Raises OSError(Errno 121) "Remote I/O error" on reading error.
    Thread safe.
    :param channel: chip channel to use.
    :return: Voltage in Volts.
    """
    global i2c
    if channel < 0 or channel > 3:
        raise ValueError("Wrong channel")
    lock.acquire()
    # configure
    data = struct.pack(">BH",
                       0x01,  # config register
                       # single shot mode, +-4.096V, AINN = GND
                       ((0b100 | channel) << 12) | 0x8380
                       )
    i2c.write(data)
    # wait for conversion
    while True:
        i2c.write(struct.pack("B", 0x01))
        if struct.unpack(">H", i2c.read(2))[0] & 0x8000 != 0:
            break
        time.sleep(0.0001)
    # read result
    i2c.write(struct.pack("B", 0x00))  # conversion register
    v = struct.unpack(">h", i2c.read(2))[0]
    lock.release()
    return v / 8000.0  # / 32768.0 * 4.096 according to specified range


# check if ads111x is connected
try:
    measure(0)
except OSError:
    raise ImportError("ads111x is not connected")


# for test purpose
if __name__ == "__main__":
    while True:
        for i in range(0, 4):
            print(str(i), measure(i))
        print("-----------------------------")
        time.sleep(0.5)
