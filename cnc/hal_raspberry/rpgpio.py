#!/usr/bin/env python

from .rpgpio_private import *

import time
import logging
import sys


class GPIO(object):
    MODE_OUTPUT = 1
    MODE_INPUT_NOPULL = 2
    MODE_INPUT_PULLUP = 3
    MODE_INPUT_PULLDOWN = 4

    def __init__(self):
        """ Create object which can control GPIO.
            This class writes directly to CPU registers and doesn't use any libs
            or kernel modules.
        """
        self._mem = PhysicalMemory(PERI_BASE + GPIO_REGISTER_BASE)

    def _pull_up_dn(self, pin, mode):
        p = self._mem.read_int(GPIO_PULLUPDN_OFFSET)
        p &= ~3
        if mode == self.MODE_INPUT_PULLUP:
            p |= 2
        elif mode == self.MODE_INPUT_PULLDOWN:
            p |= 1
        self._mem.write_int(GPIO_PULLUPDN_OFFSET, p)
        address = 4 * int(pin / 32) + GPIO_PULLUPDNCLK_OFFSET
        self._mem.write_int(address, 1 << (pin % 32))
        p = self._mem.read_int(GPIO_PULLUPDN_OFFSET)
        p &= ~3
        self._mem.write_int(GPIO_PULLUPDN_OFFSET, p)
        self._mem.write_int(address, 0)

    def init(self, pin, mode):
        """ Initialize or re-initialize GPIO pin.
        :param pin: pin number.
        :param mode: one of MODE_* variables in this class.
        """
        address = 4 * int(pin / 10) + GPIO_FSEL_OFFSET
        v = self._mem.read_int(address)
        v &= ~(7 << ((pin % 10) * 3))  # input value
        if mode == self.MODE_OUTPUT:
            v |= (1 << ((pin % 10) * 3))  # output value, base on input
            self._mem.write_int(address, v)
        else:
            self._mem.write_int(address, v)
            self._pull_up_dn(pin, mode)

    def set(self, pin):
        """ Set pin to HIGH state.
        :param pin: pin number.
        """
        address = 4 * int(pin / 32) + GPIO_SET_OFFSET
        self._mem.write_int(address, 1 << (pin % 32))

    def clear(self, pin):
        """ Set pin to LOW state.
        :param pin: pin number.
        """
        address = 4 * int(pin / 32) + GPIO_CLEAR_OFFSET
        self._mem.write_int(address, 1 << (pin % 32))

    def read(self, pin):
        """ Read pin current value.
        :param pin: pin number.
        :return: integer value 0 or 1.
        """
        address = 4 * int(pin / 32) + GPIO_INPUT_OFFSET
        v = self._mem.read_int(address)
        v &= 1 << (pin % 32)
        if v == 0:
            return 0
        return 1


# When DMAGPIO is an active with two channels simultaneously, delay time shifts
# a little bit, because all DMA channels query the same PWM(which is used as
# clock for delay). So, do not create two or more instances of DMAGPIO.
class DMAGPIO(DMAProto):
    _DMA_CONTROL_BLOCK_SIZE = 32

    def __init__(self):
        """ Create object which control GPIO pins via DMA(Direct Memory
            Access).
            This object allows to add arbitrary sequence of pulses to any GPIO
            outputs and run this sequence in background without using CPU since
            DMA is a separated hardware module.
            Note: keep this object out of garbage collector until it stops,
            otherwise memory will be unlocked and it could be overwritten by
            operating system.
        """
        super(DMAGPIO, self).__init__(30 * 1024 * 1024, 4)
        self.__current_address = 0

        # get helpers registers, this class uses PWM module to create precise
        # delays
        self._pwm = PhysicalMemory(PERI_BASE + PWM_BASE)
        self._clock = PhysicalMemory(PERI_BASE + CM_BASE)

        # pre calculated variables for control blocks
        self._delay_info = (DMA_TI_NO_WIDE_BURSTS | DMA_SRC_IGNORE
                            | DMA_TI_PER_MAP(DMA_TI_PER_MAP_PWM)
                            | DMA_TI_DEST_DREQ)
        self._delay_destination = PHYSICAL_PWM_BUS + PWM_FIFO
        self._delay_stride = 0

        self._pulse_info = (DMA_TI_NO_WIDE_BURSTS | DMA_TI_TDMODE
                            | DMA_TI_WAIT_RESP)
        self._pulse_destination = PHYSICAL_GPIO_BUS + GPIO_SET_OFFSET
        # YLENGTH is transfers count and XLENGTH size of each transfer
        self._pulse_length = (DMA_TI_TXFR_LEN_YLENGTH(2)
                              | DMA_TI_TXFR_LEN_XLENGTH(4))
        self._pulse_stride = (DMA_TI_STRIDE_D_STRIDE(12)
                              | DMA_TI_STRIDE_S_STRIDE(4))

    def add_pulse(self, pins_mask, length_us):
        """ Add single pulse at the current position.
            Note: GPIO pins are not initialized in this method and should be
            initialized in advance before running.
            :param pins_mask: bitwise mask of GPIO pins to trigger. Only for
                              first 32 pins.
            :param length_us: length in us.
        """
        next_cb = self.__current_address + 3 * self._DMA_CONTROL_BLOCK_SIZE
        if next_cb > self._phys_memory.get_size():
            raise MemoryError("Out of allocated memory.")
        next3 = next_cb + self._phys_memory.get_bus_address()
        next2 = next3 - self._DMA_CONTROL_BLOCK_SIZE
        next1 = next2 - self._DMA_CONTROL_BLOCK_SIZE

        source1 = next1 - 8  # last 8 bytes are padding, use it to store data
        length2 = length_us << 4  # * 16
        source3 = next3 - 8

        data = (
            # control block 1 - set
            self._pulse_info, source1, self._pulse_destination,
            self._pulse_length, self._pulse_stride, next1, pins_mask, 0,
            # control block 2 - delay
            self._delay_info, 0, self._delay_destination, length2,
            self._delay_stride, next2, 0, 0,
            # control block 3 - clear
            self._pulse_info, source3, self._pulse_destination,
            self._pulse_length, self._pulse_stride, next3, 0, pins_mask
                )
        self._phys_memory.write(self.__current_address, "24I", data)
        self.__current_address = next_cb

    def add_delay(self, delay_us):
        """ Add delay at the current position.
            :param delay_us: delay in us.
        """
        next_cb = self.__current_address + self._DMA_CONTROL_BLOCK_SIZE
        if next_cb > self._phys_memory.get_size():
            raise MemoryError("Out of allocated memory.")
        next1 = self._phys_memory.get_bus_address() + next_cb
        source = next1 - 8  # last 8 bytes are padding, use it to store data
        length = delay_us << 4  # * 16
        data = (
                self._delay_info, source, self._delay_destination, length,
                self._delay_stride, next1, 0, 0
               )
        self._phys_memory.write(self.__current_address, "8I", data)
        self.__current_address = next_cb

    def add_set_clear(self, pins_to_set, pins_to_clear):
        """ Change state of gpio pins.
        :param pins_to_set: bitwise mask which pins should be set.
        :param pins_to_clear: bitwise mask which pins should be clear.
        """
        next_cb = self.__current_address + self._DMA_CONTROL_BLOCK_SIZE
        if next_cb > self._phys_memory.get_size():
            raise MemoryError("Out of allocated memory.")
        next1 = self._phys_memory.get_bus_address() + next_cb
        source = next1 - 8  # last 8 bytes are padding, use it to store data
        data = (
                self._pulse_info, source, self._pulse_destination,
                self._pulse_length, self._pulse_stride, next1,
                pins_to_set, pins_to_clear
               )
        self._phys_memory.write(self.__current_address, "8I", data)
        self.__current_address = next_cb

    def finalize_stream(self):
        """ Mark last added block as the last one.
        """
        self._phys_memory.write_int(self.__current_address + 20
                                    - self._DMA_CONTROL_BLOCK_SIZE, 0)
        logging.info("DMA took {}MB of memory".
                     format(round(self.__current_address / 1024.0 / 1024.0, 2)))

    def run_stream(self):
        """ Run DMA module in stream mode, i.e. does'n finalize last block
            and do not check if there is anything to do.
        """
        # configure PWM hardware module which will clocks DMA
        self._pwm.write_int(PWM_CTL, 0)
        self._clock.write_int(CM_PWM_CNTL, CM_PASSWORD | CM_SRC_PLLD)  # disable
        while (self._clock.read_int(CM_PWM_CNTL) & CM_CNTL_BUSY) != 0:
            time.sleep(0.00001)  # 10 us, wait until BUSY bit is clear
        self._clock.write_int(CM_PWM_DIV,
                              CM_PASSWORD | CM_DIV_VALUE(5))  # 100MHz
        self._clock.write_int(CM_PWM_CNTL,
                              CM_PASSWORD | CM_SRC_PLLD | CM_CNTL_ENABLE)

        self._pwm.write_int(PWM_RNG1, 100)
        self._pwm.write_int(PWM_DMAC, PWM_DMAC_ENAB
                            | PWM_DMAC_PANIC(15) | PWM_DMAC_DREQ(15))
        self._pwm.write_int(PWM_CTL, PWM_CTL_CLRF)
        self._pwm.write_int(PWM_CTL, PWM_CTL_USEF1 | PWM_CTL_PWEN1)
        super(DMAGPIO, self)._run_dma()

    def run(self, loop=False):
        """ Run DMA module and start sending specified pulses.
        :param loop: If true, run pulse sequence in infinite loop. Otherwise
        """
        if self.__current_address == 0:
            raise RuntimeError("Nothing was added.")
        # fix 'next' field in previous control block
        if loop:
            self._phys_memory.write_int(self.__current_address + 20
                                        - self._DMA_CONTROL_BLOCK_SIZE,
                                        self._phys_memory.get_bus_address())
        else:
            self.finalize_stream()
        self.run_stream()

    def stop(self):
        """ Stop any DMA activities.
        """
        self._pwm.write_int(PWM_CTL, 0)
        super(DMAGPIO, self)._stop_dma()

    def clear(self):
        """ Remove any specified pulses. Doesn't affect currently running
            sequence.
        """
        self.__current_address = 0


class DMAPWM(DMAProto):
    _DMA_CONTROL_BLOCK_SIZE = 32
    _DMA_DATA_OFFSET = 24
    _TOTAL_NUMBER_OF_BLOCKS = 256

    def __init__(self):
        """ Initialise PWM. PWM has 8 bit resolution and fixed frequency
            (~11.5 KHz and may flow). Though duty cycle is quite precise and
            it uses the minimum amount of system resources (just one lite DMA
            channel without any anything else).
            That's why such PWM is best to use with collector motors, heaters
            and other non sensitive hardware.
            Implementation is super simple and uses lite DMA channel.
            Overall frequency depends on number of blocks.
            To adjust frequency, just write more byte per operation, use Wait
            Cycles in info field of control blocks.
        """
        super(DMAPWM, self).__init__(self._TOTAL_NUMBER_OF_BLOCKS
                                     * self._DMA_CONTROL_BLOCK_SIZE, 14)
        self._clear_pins = dict()
        # first control block always set pins
        self.__add_control_block(0, GPIO_SET_OFFSET)
        # fill control blocks
        for i in range(1, self._TOTAL_NUMBER_OF_BLOCKS):
                self.__add_control_block(i * self._DMA_CONTROL_BLOCK_SIZE,
                                         GPIO_CLEAR_OFFSET)
        # loop
        self._phys_memory.write_int((self._TOTAL_NUMBER_OF_BLOCKS - 1)
                                    * self._DMA_CONTROL_BLOCK_SIZE + 20,
                                    self._phys_memory.get_bus_address())
        self._gpio = PhysicalMemory(PERI_BASE + GPIO_REGISTER_BASE)

    def __add_control_block(self, address, offset):
        ba = self._phys_memory.get_bus_address() + address
        data = (
            DMA_TI_NO_WIDE_BURSTS | DMA_TI_WAIT_RESP
            | DMA_TI_DEST_INC | DMA_TI_SRC_INC,  # info
            ba + self._DMA_DATA_OFFSET,  # source, use padding for storing data
            PHYSICAL_GPIO_BUS + offset,  # destination
            4,  # length
            0,  # stride
            ba + self._DMA_CONTROL_BLOCK_SIZE,  # next control block
            0,  # padding, uses as data storage
            0  # padding
        )
        self._phys_memory.write(address, "8I", data)

    def add_pin(self, pin, duty_cycle):
        """ Add pin to PMW with specified duty cycle.
        :param pin: pin number to add.
        :param duty_cycle: duty cycle 0..100 which represent percents.
        """
        assert 0 <= duty_cycle <= 100
        self.remove_pin(pin)
        block_number = int(duty_cycle * self._TOTAL_NUMBER_OF_BLOCKS
                           / 100.0)
        if block_number == 0:
            self._gpio.write_int(GPIO_CLEAR_OFFSET, 1 << pin)
        elif block_number == self._TOTAL_NUMBER_OF_BLOCKS:
            self._gpio.write_int(GPIO_SET_OFFSET, 1 << pin)
            self._clear_pins[pin] = self._DMA_DATA_OFFSET
        else:
            value = self._phys_memory.read_int(self._DMA_DATA_OFFSET)
            value |= 1 << pin
            self._phys_memory.write_int(self._DMA_DATA_OFFSET, value)
            clear_address = (block_number * self._DMA_CONTROL_BLOCK_SIZE
                             + self._DMA_DATA_OFFSET)
            value = self._phys_memory.read_int(clear_address)
            value |= 1 << pin
            self._phys_memory.write_int(clear_address, value)
            self._clear_pins[pin] = clear_address
            if not self.is_active():
                super(DMAPWM, self)._run_dma()

    def remove_pin(self, pin):
        """ Remove pin from PWM
        :param pin: pin number to remove.
        """
        assert 0 <= pin < 32
        if pin in self._clear_pins.keys():
            address = self._clear_pins[pin]
            value = self._phys_memory.read_int(address)
            value &= ~(1 << pin)
            self._phys_memory.write_int(address, value)
            value = self._phys_memory.read_int(self._DMA_DATA_OFFSET)
            value &= ~(1 << pin)
            self._phys_memory.write_int(self._DMA_DATA_OFFSET, value)
            del self._clear_pins[pin]
            self._gpio.write_int(GPIO_CLEAR_OFFSET, 1 << pin)
        if len(self._clear_pins) == 0 and self.is_active():
            super(DMAPWM, self)._stop_dma()

    def remove_all(self):
        """ Remove all pins from PWM and stop it.
        """
        pins_list = self._clear_pins.keys()
        for pin in pins_list:
            self.remove_pin(pin)
        assert len(self._clear_pins) == 0


# for testing purpose
def main():
    pin = 21
    g = GPIO()
    g.init(pin, GPIO.MODE_INPUT_NOPULL)
    print("nopull " + str(g.read(pin)))
    g.init(pin, GPIO.MODE_INPUT_PULLDOWN)
    print("pulldown " + str(g.read(pin)))
    g.init(pin, GPIO.MODE_INPUT_PULLUP)
    print("pullup " + str(g.read(pin)))
    time.sleep(1)
    g.init(pin, GPIO.MODE_OUTPUT)
    g.set(pin)
    print("set " + str(g.read(pin)))
    time.sleep(1)
    g.clear(pin)
    print("clear " + str(g.read(pin)))
    time.sleep(1)
    cma = CMAPhysicalMemory(1*1024*1024)
    print(str(cma.get_size() / 1024 / 1024) + "MB of memory allocated at "
          + hex(cma.get_phys_address()))
    a = cma.read_int(0)
    print("was " + hex(a))
    cma.write_int(0, 0x12345678)
    a = cma.read_int(0)
    assert a == 0x12345678, "Memory isn't written or read correctly"
    print("now " + hex(a))
    del cma
    dg = DMAGPIO()
    dg.add_pulse(1 << pin, 200000)
    dg.add_delay(600000)
    dg.run(True)
    print("dmagpio is started")
    try:
        print("press enter to stop...")
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    dg.stop()
    g.clear(pin)
    print("dma stopped")
    pwm = DMAPWM()
    pwm.add_pin(pin, 20)
    print("pwm is started")
    try:
        print("press enter to stop...")
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    pwm.remove_pin(pin)
    print("pwm stopped")

if __name__ == "__main__":
    main()
