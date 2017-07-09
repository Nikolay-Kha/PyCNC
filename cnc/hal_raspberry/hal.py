import time

from cnc.hal_raspberry import rpgpio
from cnc.pulses import *
from cnc.config import *
from cnc.sensors import thermistor

US_IN_SECONDS = 1000000

gpio = rpgpio.GPIO()
dma = rpgpio.DMAGPIO()
pwm = rpgpio.DMAPWM()

STEP_PIN_MASK_X = 1 << STEPPER_STEP_PIN_X
STEP_PIN_MASK_Y = 1 << STEPPER_STEP_PIN_Y
STEP_PIN_MASK_Z = 1 << STEPPER_STEP_PIN_Z
STEP_PIN_MASK_E = 1 << STEPPER_STEP_PIN_E


def init():
    """ Initialize GPIO pins and machine itself.
    """
    gpio.init(STEPPER_STEP_PIN_X, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_STEP_PIN_Y, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_STEP_PIN_Z, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_STEP_PIN_E, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_X, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_Y, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_Z, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPER_DIR_PIN_E, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(ENDSTOP_PIN_X, rpgpio.GPIO.MODE_INPUT_PULLUP)
    gpio.init(ENDSTOP_PIN_Y, rpgpio.GPIO.MODE_INPUT_PULLUP)
    gpio.init(ENDSTOP_PIN_Z, rpgpio.GPIO.MODE_INPUT_PULLUP)
    gpio.init(SPINDLE_PWM_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(FAN_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(EXTRUDER_HEATER_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(BED_HEATER_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.init(STEPPERS_ENABLE_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.clear(SPINDLE_PWM_PIN)
    gpio.clear(FAN_PIN)
    gpio.clear(EXTRUDER_HEATER_PIN)
    gpio.clear(BED_HEATER_PIN)
    gpio.clear(STEPPERS_ENABLE_PIN)


def spindle_control(percent):
    """ Spindle control implementation.
    :param percent: spindle speed in percent 0..100. If 0, stop the spindle.
    """
    logging.info("spindle control: {}%".format(percent))
    if percent > 0:
        pwm.add_pin(SPINDLE_PWM_PIN, percent)
    else:
        pwm.remove_pin(SPINDLE_PWM_PIN)


def fan_control(on_off):
    """
    Cooling fan control.
    :param on_off: boolean value if fan is enabled.
    """
    if on_off:
        logging.info("Fan is on")
        gpio.set(FAN_PIN)
    else:
        logging.info("Fan is off")
        gpio.clear(FAN_PIN)


def extruder_heater_control(percent):
    """ Extruder heater control.
    :param percent: heater power in percent 0..100. 0 turns heater off.
    """
    if percent > 0:
        pwm.add_pin(EXTRUDER_HEATER_PIN, percent)
    else:
        pwm.remove_pin(EXTRUDER_HEATER_PIN)


def bed_heater_control(percent):
    """ Hot bed heater control.
    :param percent: heater power in percent 0..100. 0 turns heater off.
    """
    if percent > 0:
        pwm.add_pin(BED_HEATER_PIN, percent)
    else:
        pwm.remove_pin(BED_HEATER_PIN)


def get_extruder_temperature():
    """ Measure extruder temperature.
    :return: temperature in Celsius.
    """
    return thermistor.get_temperature(EXTRUDER_TEMPERATURE_SENSOR_CHANNEL)


def get_bed_temperature():
    """ Measure bed temperature.
    :return: temperature in Celsius.
    """
    return thermistor.get_temperature(BED_TEMPERATURE_SENSOR_CHANNEL)


def disable_steppers():
    """ Disable all steppers until any movement occurs.
    """
    logging.info("disable steppers")
    gpio.set(STEPPERS_ENABLE_PIN)


def __calibrate_private(x, y, z, invert):
    if invert:
        stepper_inverted_x = not STEPPER_INVERTED_X
        stepper_inverted_y = not STEPPER_INVERTED_Y
        stepper_inverted_z = not STEPPER_INVERTED_Z
        endstop_inverted_x = not ENDSTOP_INVERTED_X
        endstop_inverted_y = not ENDSTOP_INVERTED_Y
        endstop_inverted_z = not ENDSTOP_INVERTED_Z
    else:
        stepper_inverted_x = STEPPER_INVERTED_X
        stepper_inverted_y = STEPPER_INVERTED_Y
        stepper_inverted_z = STEPPER_INVERTED_Z
        endstop_inverted_x = ENDSTOP_INVERTED_X
        endstop_inverted_y = ENDSTOP_INVERTED_Y
        endstop_inverted_z = ENDSTOP_INVERTED_Z
    if stepper_inverted_x:
        gpio.clear(STEPPER_DIR_PIN_X)
    else:
        gpio.set(STEPPER_DIR_PIN_X)
    if stepper_inverted_y:
        gpio.clear(STEPPER_DIR_PIN_Y)
    else:
        gpio.set(STEPPER_DIR_PIN_Y)
    if stepper_inverted_z:
        gpio.clear(STEPPER_DIR_PIN_Z)
    else:
        gpio.set(STEPPER_DIR_PIN_Z)
    pins = 0
    max_size = 0
    if x:
        pins |= STEP_PIN_MASK_X
        max_size = max(max_size, TABLE_SIZE_X_MM * STEPPER_PULSES_PER_MM_X)
    if y:
        pins |= STEP_PIN_MASK_Y
        max_size = max(max_size, TABLE_SIZE_Y_MM * STEPPER_PULSES_PER_MM_Y)
    if z:
        pins |= STEP_PIN_MASK_Z
        max_size = max(max_size, TABLE_SIZE_Z_MM * STEPPER_PULSES_PER_MM_Z)
    pulses_per_mm_avg = (STEPPER_PULSES_PER_MM_X + STEPPER_PULSES_PER_MM_Y
                         + STEPPER_PULSES_PER_MM_Z) / 3.0
    pulses_per_sec = CALIBRATION_VELOCITY_MM_PER_MIN / 60.0 * pulses_per_mm_avg
    end_time = time.time() + 1.2 * max_size / pulses_per_sec
    delay = int(1000000 / pulses_per_sec)
    last_pins = ~pins
    while time.time() < end_time:
        # check each axis end stop twice
        x_endstop = (STEP_PIN_MASK_X & pins) != 0
        y_endstop = (STEP_PIN_MASK_Y & pins) != 0
        z_endstop = (STEP_PIN_MASK_Z & pins) != 0
        # read each sensor three time
        for _ in range(0, 3):
            x_endstop = x_endstop and ((gpio.read(ENDSTOP_PIN_X) == 1)
                                       == endstop_inverted_x)
            y_endstop = y_endstop and ((gpio.read(ENDSTOP_PIN_Y) == 1)
                                       == endstop_inverted_y)
            z_endstop = z_endstop and ((gpio.read(ENDSTOP_PIN_Z) == 1)
                                       == endstop_inverted_z)
        if x_endstop:
            pins &= ~STEP_PIN_MASK_X
        if y_endstop:
            pins &= ~STEP_PIN_MASK_Y
        if z_endstop:
            pins &= ~STEP_PIN_MASK_Z
        if pins != last_pins:
            dma.stop()
            if pins == 0:
                return True
            last_pins = pins
            # Prepare chunk with 1 second buffer. It is needed to make sure
            # that if program unexpectedly stops, dma will continue work not
            # long then this buffer time.
            dma.clear()
            generate = 1000000
            while generate > 0:
                dma.add_pulse(pins, STEPPER_PULSE_LENGTH_US)
                dma.add_delay(delay)
                generate -= delay + STEPPER_PULSE_LENGTH_US
            dma.finalize_stream()
        if not dma.is_active():
            dma.run(False)
    return False


def calibrate(x, y, z):
    """ Move head to home position till end stop switch will be triggered.
    Do not return till all procedures are completed.
    :param x: boolean, True to calibrate X axis.
    :param y: boolean, True to calibrate Y axis.
    :param z: boolean, True to calibrate Z axis.
    :return: boolean, True if all specified end stops were triggered.
    """
    # enable steppers
    gpio.clear(STEPPERS_ENABLE_PIN)
    logging.info("hal calibrate, x={}, y={}, z={}".format(x, y, z))
    if not __calibrate_private(x, y, z, True):  # move from endstop switch
        return False
    return __calibrate_private(x, y, z, False)  # move to endstop switch


def move(generator):
    """ Move head to specified position
    :param generator: PulseGenerator object.
    """
    # Fill buffer right before currently running(previous sequence) dma
    # this mode implements kind of round buffer, but protects if CPU is not
    # powerful enough to calculate buffer in advance, faster then machine
    # moving. In this case machine would safely paused between commands until
    # calculation is done.

    # enable steppers
    gpio.clear(STEPPERS_ENABLE_PIN)
    # 4 control blocks per 32 bytes
    bytes_per_iter = 4 * dma.control_block_size()
    # prepare and run dma
    dma.clear()  # should just clear current address, but not stop current DMA
    prev = 0
    is_ran = False
    instant = INSTANT_RUN
    st = time.time()
    current_cb = 0
    k = 0
    k0 = 0
    for direction, tx, ty, tz, te in generator:
        if current_cb is not None:
            while dma.current_address() + bytes_per_iter >= current_cb:
                time.sleep(0.001)
                current_cb = dma.current_control_block()
                if current_cb is None:
                    k0 = k
                    st = time.time()
                    break  # previous dma sequence has stopped
        if direction:  # set up directions
            pins_to_set = 0
            pins_to_clear = 0
            if tx > 0:
                pins_to_clear |= 1 << STEPPER_DIR_PIN_X
            elif tx < 0:
                pins_to_set |= 1 << STEPPER_DIR_PIN_X
            if ty > 0:
                pins_to_clear |= 1 << STEPPER_DIR_PIN_Y
            elif ty < 0:
                pins_to_set |= 1 << STEPPER_DIR_PIN_Y
            if tz > 0:
                pins_to_clear |= 1 << STEPPER_DIR_PIN_Z
            elif tz < 0:
                pins_to_set |= 1 << STEPPER_DIR_PIN_Z
            if te > 0:
                pins_to_clear |= 1 << STEPPER_DIR_PIN_E
            elif te < 0:
                pins_to_set |= 1 << STEPPER_DIR_PIN_E
            dma.add_set_clear(pins_to_set, pins_to_clear)
            continue
        pins = 0
        m = None
        for i in (tx, ty, tz, te):
            if i is not None and (m is None or i < m):
                m = i
        k = int(round(m * US_IN_SECONDS))
        if tx is not None:
            pins |= STEP_PIN_MASK_X
        if ty is not None:
            pins |= STEP_PIN_MASK_Y
        if tz is not None:
            pins |= STEP_PIN_MASK_Z
        if te is not None:
            pins |= STEP_PIN_MASK_E
        if k - prev > 0:
            dma.add_delay(k - prev)
        dma.add_pulse(pins, STEPPER_PULSE_LENGTH_US)
        # TODO not a precise way! pulses will set in queue, instead of crossing
        # if next pulse start during pulse length. Though it almost doesn't
        # matter for pulses with 1-2us length.
        prev = k + STEPPER_PULSE_LENGTH_US
        # instant run handling
        if not is_ran and instant and current_cb is None:
            if k - k0 > 100000:  # wait at least 100 ms is uploaded
                nt = time.time() - st
                ng = (k - k0) / 1000000.0
                if nt > ng:
                    logging.warn("Buffer preparing for instant run took more "
                                 "time then buffer time"
                                 " {}/{}".format(nt, ng))
                    instant = False
                else:
                    dma.run_stream()
                    is_ran = True
    pt = time.time()
    if not is_ran:
        # after long command, we can fill short buffer, that why we may need to
        #  wait until long command finishes
        while dma.is_active():
            time.sleep(0.01)
        dma.run(False)
    else:
        # stream mode can be activated only if previous command was finished.
        dma.finalize_stream()

    logging.info("prepared in " + str(round(pt - st, 2)) + "s, estimated in "
                 + str(round(generator.total_time_s(), 2)) + "s")


def join():
    """ Wait till motors work.
    """
    logging.info("hal join()")
    # wait till dma works
    while dma.is_active():
        time.sleep(0.01)


def deinit():
    """ De-initialize hardware.
    """
    join()
    disable_steppers()
    pwm.remove_all()
    gpio.clear(SPINDLE_PWM_PIN)
    gpio.clear(FAN_PIN)
    gpio.clear(EXTRUDER_HEATER_PIN)
    gpio.clear(BED_HEATER_PIN)
