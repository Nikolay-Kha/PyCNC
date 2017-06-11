import time

from cnc.hal_raspberry import rpgpio
from cnc.pulses import *
from cnc.config import *

US_IN_SECONDS = 1000000

gpio = rpgpio.GPIO()
dma = rpgpio.DMAGPIO()
pwm = rpgpio.DMAPWM()

STEP_PIN_MASK_X = 1 << STEPPER_STEP_PIN_X
STEP_PIN_MASK_Y = 1 << STEPPER_STEP_PIN_Y
STEP_PIN_MASK_Z = 1 << STEPPER_STEP_PIN_Z
STEP_PIN_MASK_E = 1 << STEPPER_STEP_PIN_E


def init():
    """ Initialize GPIO pins and machine itself, including calibration if
        needed. Do not return till all procedures are completed.
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
    gpio.init(ENDSTOP_PIN_X, rpgpio.GPIO.MODE_INPUT_PULLUP)
    gpio.init(ENDSTOP_PIN_X, rpgpio.GPIO.MODE_INPUT_PULLUP)
    gpio.init(SPINDLE_PWM_PIN, rpgpio.GPIO.MODE_OUTPUT)
    gpio.clear(SPINDLE_PWM_PIN)

    # calibration
    gpio.set(STEPPER_DIR_PIN_X)
    gpio.set(STEPPER_DIR_PIN_Y)
    gpio.set(STEPPER_DIR_PIN_Z)
    pins = STEP_PIN_MASK_X | STEP_PIN_MASK_Y | STEP_PIN_MASK_Z
    dma.clear()
    dma.add_pulse(pins, STEPPER_PULSE_LENGTH_US)
    st = time.time()
    max_pulses_left = int(1.2 * max(STEPPER_PULSES_PER_MM_X,
                                    STEPPER_PULSES_PER_MM_Y,
                                    STEPPER_PULSES_PER_MM_Z) *
                          max(TABLE_SIZE_X_MM,
                              TABLE_SIZE_Y_MM,
                              TABLE_SIZE_Z_MM))
    try:
        while max_pulses_left > 0:
            if (STEP_PIN_MASK_X & pins) != 0 and gpio.read(ENDSTOP_PIN_X) == 0:
                pins &= ~STEP_PIN_MASK_X
                dma.clear()
                dma.add_pulse(pins, STEPPER_PULSE_LENGTH_US)
            if (STEP_PIN_MASK_Y & pins) != 0 and gpio.read(ENDSTOP_PIN_Y) == 0:
                pins &= ~STEP_PIN_MASK_Y
                dma.clear()
                dma.add_pulse(pins, STEPPER_PULSE_LENGTH_US)
            if (STEP_PIN_MASK_Z & pins) != 0 and gpio.read(ENDSTOP_PIN_Z) == 0:
                pins &= ~STEP_PIN_MASK_Z
                dma.clear()
                dma.add_pulse(pins, STEPPER_PULSE_LENGTH_US)
            if pins == 0:
                break
            dma.run(False)
            # limit velocity at ~10% of top velocity
            time.sleep((1 / 0.10) / (STEPPER_MAX_VELOCITY_MM_PER_MIN
                                     / 60 * max(STEPPER_PULSES_PER_MM_X,
                                                STEPPER_PULSES_PER_MM_Y,
                                                STEPPER_PULSES_PER_MM_Z)))
            max_pulses_left -= 1
            if st is not None:
                if time.time() - st > 2:
                    logging.critical("Calibration still in progress. Check if "
                                     "machine is moving.\nPress Ctrl+C to "
                                     "cancel calibration and proceed as is.")
                    st = None
        if pins != 0:
            logging.critical("Calibration has failed. You may proceed, but be "
                             "careful.")
    except KeyboardInterrupt:
        logging.critical("Calibration has canceled by user. Be careful.")


def spindle_control(percent):
    """ Spindle control implementation.
    :param percent: spindle speed in percent. If 0, stop the spindle.
    """
    logging.info("spindle control: {}%".format(percent))
    if percent > 0:
        pwm.add_pin(SPINDLE_PWM_PIN, percent)
    else:
        pwm.remove_pin(SPINDLE_PWM_PIN)


def move(generator):
    """ Move head to specified position
    :param generator: PulseGenerator object.
    """
    # wait if previous command still works
    while dma.is_active():
        time.sleep(0.001)

    # prepare and run dma
    dma.clear()
    prev = 0
    is_ran = False
    instant = INSTANT_RUN
    st = time.time()
    for direction, tx, ty, tz, te in generator:
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
        if not is_ran and instant:
            if k > 500000:  # wait at least 500 ms is uploaded
                if time.time() - st > 0.5:
                    logging.warn("Buffer preparing for instant run took more "
                                 "time then buffer time")
                    instant = False
                else:
                    dma.run_stream()
                    is_ran = True
    pt = time.time()
    if not is_ran:
        dma.run(False)
    else:
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
    pwm.remove_all()
