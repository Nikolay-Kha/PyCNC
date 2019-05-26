# This version uses new-style automatic setup/destroy/mapping
# Need to change /etc/webiopi

# Imports
import webiopi

# Enable debug output
webiopi.setDebug()



# Retrieve GPIO lib
GPIO = webiopi.GPIO

# -------------------------------------------------- #
# Constants definition                               #
# -------------------------------------------------- #
LED_GREEN   = 25

STEPPER_STEP_PIN_X  = 13
STEPPER_DIR_PIN_X   = 6
ENDSTOP_PIN_X       = 24

STEPPER_STEP_PIN_Y  = 21
STEPPER_DIR_PIN_Y   = 20
ENDSTOP_PIN_Y       = 23

STEPPER_STEP_PIN_Z  = 26
STEPPER_DIR_PIN_Z   = 19
ENDSTOP_PIN_Z       = 17



# -------------------------------------------------- #
# Convenient PWM Function                            #
# -------------------------------------------------- #
# Set the speed of two motors
# def set_speed(speed):
#     GPIO.pulseRatio(LS, speed)
#     GPIO.pulseRatio(RS, speed)


# -------------------------------------------------- #
# Blink Functions                                    #
# -------------------------------------------------- #
def blink_1():
    GPIO.output(LED_GREEN, GPIO.HIGH)
    webiopi.sleep(0.2)
    GPIO.output(LED_GREEN, GPIO.LOW)
    webiopi.sleep(0.1)

def blink_2():
    blink_1()
    blink_1()

def blink_3():
    blink_1()
    blink_1()
    blink_1()


# Called by WebIOPi at script loading
def setup():
    webiopi.debug("Basic script - Setup")
    # Setup GPIOs
    GPIO.setFunction(LED_GREEN, GPIO.OUT)
    GPIO.digitalWrite(LED_GREEN, GPIO.LOW)

    # X Axis
    GPIO.setFunction(STEPPER_STEP_PIN_X, GPIO.OUT)
    GPIO.setFunction(STEPPER_DIR_PIN_X, GPIO.OUT)
    GPIO.setFunction(ENDSTOP_PIN_X, GPIO.IN)

    # Y Axis
    GPIO.setFunction(STEPPER_STEP_PIN_Y, GPIO.OUT)
    GPIO.setFunction(STEPPER_DIR_PIN_Y, GPIO.OUT)
    GPIO.setFunction(ENDSTOP_PIN_Y, GPIO.IN)

    # Z Axis
    GPIO.setFunction(STEPPER_STEP_PIN_Z, GPIO.OUT)
    GPIO.setFunction(STEPPER_DIR_PIN_Z, GPIO.OUT)
    GPIO.setFunction(ENDSTOP_PIN_Z, GPIO.IN)


    # time.sleep(100)
    # GPIO.setFunction(LED_GREEN, GPIO.PWM)
    # GPIO.pwmWrite(LED_GREEN, 0.5)  # set to 50% ratio

    # GPIO.setFunction(LS, GPIO.PWM)
    # GPIO.setFunction(L1, GPIO.OUT)
    # GPIO.setFunction(L2, GPIO.OUT)
    #
    # GPIO.setFunction(RS, GPIO.PWM)
    # GPIO.setFunction(R1, GPIO.OUT)
    # GPIO.setFunction(R2, GPIO.OUT)



# Looped by WebIOPi
# def loop():
#
#     # webiopi.debug("Loop")
#     # Toggle LED each 0.2 seconds
#     value = not GPIO.digitalRead(LED_GREEN)
#     GPIO.digitalWrite(LED_GREEN, value)
#     webiopi.sleep(0.2)



# Called by WebIOPi at server shutdown
def destroy():
    # webiopi.debug("Basic script - Destroy")
    # Reset GPIO functions
    GPIO.setFunction(STEPPER_STEP_PIN_X, GPIO.IN)
    GPIO.setFunction(STEPPER_DIR_PIN_X, GPIO.IN)
    GPIO.setFunction(STEPPER_STEP_PIN_Y, GPIO.IN)
    GPIO.setFunction(STEPPER_DIR_PIN_Y, GPIO.IN)
    GPIO.setFunction(STEPPER_STEP_PIN_Z, GPIO.IN)
    GPIO.setFunction(STEPPER_DIR_PIN_Z, GPIO.IN)
    GPIO.setFunction(LED_GREEN, GPIO.IN)


# -------------------------------------------------- #
# Macro definition part                              #
# -------------------------------------------------- #
@webiopi.macro
def go_1():
    blink_1()

@webiopi.macro
def go_2():
    blink_2()

@webiopi.macro
def go_3():
    blink_3()

@webiopi.macro
def pwmMode():
    GPIO.setFunction(LED_GREEN, GPIO.PWM)
    GPIO.pwmWrite(LED_GREEN, 0.5)  # set to 50% ratio

@webiopi.macro
def onoffMode():
    GPIO.setFunction(LED_GREEN, GPIO.OUT)
    GPIO.digitalWrite(LED_GREEN, GPIO.LOW)

@webiopi.macro
def myMacroWithArgs(args):
    for n in range(0, int(args)):
        blink_1()

