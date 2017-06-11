import os
import mmap
import struct
import re
import fcntl
import array
import atexit
import ctypes

# Raspberry Pi registers
# https://www.raspberrypi.org/wp-content/uploads/2012/02/BCM2835-ARM-Peripherals.pdf
RPI1_PERI_BASE = 0x20000000
RPI2_3_PERI_BASE = 0x3F000000
# detect board version
with open("/proc/cpuinfo", "r") as f:
    d = f.read()
    r = re.search("^Revision\s+:\s+(.+)$", d, flags=re.MULTILINE)
    h = re.search("^Hardware\s+:\s+(.+)$", d, flags=re.MULTILINE)
    RPI_1_REVISIONS = ['0002', '0003', '0004', '0005', '0006', '0007', '0008',
                       '0009', '000d', '000e', '000f', '0010', '0011', '0012',
                       '0013', '0014', '0015', '900021', '900032']
    if h is None:
        raise ImportError("This is not raspberry pi board.")
    elif r.group(1) in RPI_1_REVISIONS:
        PERI_BASE = RPI1_PERI_BASE
    elif "BCM2" in h.group(1):
        PERI_BASE = RPI2_3_PERI_BASE
    else:
        raise ImportError("Unknown board.")
PAGE_SIZE = 4096
GPIO_REGISTER_BASE = 0x200000
GPIO_INPUT_OFFSET = 0x34
GPIO_SET_OFFSET = 0x1C
GPIO_CLEAR_OFFSET = 0x28
GPIO_FSEL_OFFSET = 0x0
GPIO_PULLUPDN_OFFSET = 0x94
GPIO_PULLUPDNCLK_OFFSET = 0x98
PHYSICAL_GPIO_BUS = 0x7E000000 + GPIO_REGISTER_BASE

# registers and values for DMA
DMA_BASE = 0x007000
DMA_CS = 0x00
DMA_CONBLK_AD = 0x04
DMA_TI_NO_WIDE_BURSTS = 1 << 26
DMA_TI_SRC_INC = 1 << 8
DMA_TI_DEST_INC = 1 << 4
DMA_SRC_IGNORE = 1 << 11
DMA_DEST_IGNORE = 1 << 7
DMA_TI_TDMODE = 1 << 1
DMA_TI_WAIT_RESP = 1 << 3
DMA_TI_SRC_DREQ = 1 << 10
DMA_TI_DEST_DREQ = 1 << 6
DMA_CS_RESET = 1 << 31
DMA_CS_ABORT = 1 << 30
DMA_CS_DISDEBUG = 1 << 28
DMA_CS_END = 1 << 1
DMA_CS_ACTIVE = 1 << 0
DMA_TI_PER_MAP_PWM = 5
DMA_TI_PER_MAP_PCM = 2
DMA_TI_PER_MAP = (lambda x: x << 16)
DMA_TI_TXFR_LEN_YLENGTH = (lambda y: (y & 0x3fff) << 16)
DMA_TI_TXFR_LEN_XLENGTH = (lambda x: x & 0xffff)
DMA_TI_STRIDE_D_STRIDE = (lambda x: (x & 0xffff) << 16)
DMA_TI_STRIDE_S_STRIDE = (lambda x: x & 0xffff)
DMA_CS_PRIORITY = (lambda x: (x & 0xf) << 16)
DMA_CS_PANIC_PRIORITY = (lambda x: (x & 0xf) << 20)

# hardware PWM controller registers
PWM_BASE = 0x0020C000
PHYSICAL_PWM_BUS = 0x7E000000 + PWM_BASE
PWM_CTL = 0x00
PWM_DMAC = 0x08
PWM_RNG1 = 0x10
PWM_RNG2 = 0x20
PWM_FIFO = 0x18
PWM_CTL_MODE1 = 1 << 1
PWM_CTL_MODE2 = 1 << 9
PWM_CTL_PWEN1 = 1 << 0
PWM_CTL_PWEN2 = 1 << 8
PWM_CTL_CLRF = 1 << 6
PWM_CTL_USEF1 = 1 << 5
PWM_CTL_USEF2 = 1 << 13
PWM_DMAC_ENAB = 1 << 31
PWM_DMAC_PANIC = (lambda x: x << 8)
PWM_DMAC_DREQ = (lambda x: x)

# clock manager module
CM_BASE = 0x00101000
CM_PCM_CNTL = 0x98
CM_PCM_DIV = 0x9C
CM_PWM_CNTL = 0xA0
CM_PWM_DIV = 0xA4
CM_PASSWORD = 0x5A << 24
CM_CNTL_ENABLE = 1 << 4
CM_CNTL_BUSY = 1 << 7
CM_SRC_OSC = 1   # 19.2 MHz
CM_SRC_PLLC = 5  # 1000 MHz
CM_SRC_PLLD = 6  # 500 MHz
CM_SRC_HDMI = 7  # 216 MHz
CM_DIV_VALUE = (lambda x: x << 12)


class PhysicalMemory(object):
    # noinspection PyArgumentList,PyArgumentList
    def __init__(self, phys_address, size=PAGE_SIZE):
        """ Create object which maps physical memory to Python's mmap object.
        :param phys_address: based address of physical memory
        """
        self._size = size
        phys_address -= phys_address % PAGE_SIZE
        fd = self._open_dev("/dev/mem")
        self._memmap = mmap.mmap(fd, size, flags=mmap.MAP_SHARED,
                                 prot=mmap.PROT_READ | mmap.PROT_WRITE,
                                 offset=phys_address)
        self._close_dev(fd)
        atexit.register(self.cleanup)

    def cleanup(self):
        self._memmap.close()

    @staticmethod
    def _open_dev(name):
        fd = os.open(name, os.O_SYNC | os.O_RDWR)
        if fd < 0:
            raise IOError("Failed to open " + name)
        return fd

    @staticmethod
    def _close_dev(fd):
        os.close(fd)

    def write_int(self, address, int_value):
        ctypes.c_uint32.from_buffer(self._memmap, address).value = int_value

    def write(self, address, fmt, data):
        struct.pack_into(fmt, self._memmap, address, *data)

    def read_int(self, address):
        return ctypes.c_uint32.from_buffer(self._memmap, address).value

    def get_size(self):
        return self._size


class CMAPhysicalMemory(PhysicalMemory):
    IOCTL_MBOX_PROPERTY = ctypes.c_long(0xc0046400).value

    def __init__(self, size):
        """ This class allocates continuous memory with specified size, lock it
            and provide access to it with Python's mmap. It uses RPi video
            buffers to allocate it (/dev/vcio).
        :param size: number of bytes to allocate
        """
        size = (size + PAGE_SIZE - 1) // PAGE_SIZE * PAGE_SIZE
        self._vcio_fd = self._open_dev("/dev/vcio")
        # allocate memory
        self._handle = self._send_data(0x3000c, [size, PAGE_SIZE, 0xC])
        if self._handle == 0:
            raise OSError("No memory to allocate with /dev/vcio")
        # lock memory
        self._bus_memory = self._send_data(0x3000d, [self._handle])
        if self._bus_memory == 0:
            # memory should be freed in __del__
            raise OSError("Failed to lock memory with /dev/vcio")
        # print("allocate {} at {} (bus {})".format(size,
        #       hex(self.get_phys_address()), hex(self.get_bus_address())))
        super(CMAPhysicalMemory, self).__init__(self.get_phys_address(), size)
        atexit.register(self.free)

    def free(self):
        """Release and free allocated memory
        """
        self._send_data(0x3000e, [self._handle])  # unlock memory
        self._send_data(0x3000f, [self._handle])  # free memory
        self._close_dev(self._vcio_fd)

    def _send_data(self, request, args):
        data = array.array('I')
        data.append(24 + 4 * len(args))  # total size
        data.append(0)                   # process request
        data.append(request)             # request id
        data.append(4 * len(args))       # size of the buffer
        data.append(4 * len(args))       # size of the data
        data.extend(args)                # arguments
        data.append(0)                   # end mark
        fcntl.ioctl(self._vcio_fd, self.IOCTL_MBOX_PROPERTY, data, True)
        return data[5]

    def get_bus_address(self):
        return self._bus_memory

    def get_phys_address(self):
        return self._bus_memory & ~0xc0000000


class DMAProto(object):
    def __init__(self, memory_size, dma_channel):
        """ This class provides basic access to DMA and creates buffer for
            control blocks.
        """
        self._DMA_CHANNEL = dma_channel
        # allocate buffer for control blocks
        self._phys_memory = CMAPhysicalMemory(memory_size)
        # prepare dma registers memory map
        self._dma = PhysicalMemory(PERI_BASE + DMA_BASE)

    def _run_dma(self):
        """ Run DMA module from created buffer.
        """
        address = 0x100 * self._DMA_CHANNEL
        self._dma.write_int(address + DMA_CS, DMA_CS_END)
        self._dma.write_int(address + DMA_CONBLK_AD,
                            self._phys_memory.get_bus_address())
        cs = DMA_CS_PRIORITY(7) | DMA_CS_PANIC_PRIORITY(7) | DMA_CS_DISDEBUG
        self._dma.write_int(address + DMA_CS, cs)
        cs |= DMA_CS_ACTIVE
        self._dma.write_int(address + DMA_CS, cs)

    def _stop_dma(self):
        """ Stop DMA
        """
        address = 0x100 * self._DMA_CHANNEL
        cs = self._dma.read_int(address + DMA_CS)
        cs |= DMA_CS_ABORT
        self._dma.write_int(address + DMA_CS, cs)
        cs &= ~DMA_CS_ACTIVE
        self._dma.write_int(address + DMA_CS, cs)
        cs |= DMA_CS_RESET
        self._dma.write_int(address + DMA_CS, cs)

    def is_active(self):
        """ Check if DMA is working. Method can check if single sequence
            still active or cycle sequence is working.
        :return: boolean value
        """
        address = 0x100 * self._DMA_CHANNEL
        cs = self._dma.read_int(address + DMA_CS)
        if cs & DMA_CS_ACTIVE == DMA_CS_ACTIVE:
            return True
        return False
