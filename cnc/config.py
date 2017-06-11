# Hardware limitations config
STEPPER_PULSE_LENGTH_US = 2
STEPPER_MAX_VELOCITY_MM_PER_MIN = 1800  # mm per min
STEPPER_MAX_ACCELERATION_MM_PER_S2 = 200  # mm per sec^2

STEPPER_PULSES_PER_MM_X = 400
STEPPER_PULSES_PER_MM_Y = 400
STEPPER_PULSES_PER_MM_Z = 400
STEPPER_PULSES_PER_MM_E = 80

TABLE_SIZE_X_MM = 200
TABLE_SIZE_Y_MM = 300
TABLE_SIZE_Z_MM = 48

SPINDLE_MAX_RPM = 10000

# Pins config
STEPPER_STEP_PIN_X = 16
STEPPER_STEP_PIN_Y = 20
STEPPER_STEP_PIN_Z = 21
STEPPER_STEP_PIN_E = 25

STEPPER_DIR_PIN_X = 13
STEPPER_DIR_PIN_Y = 19
STEPPER_DIR_PIN_Z = 26
STEPPER_DIR_PIN_E = 8

SPINDLE_PWM_PIN = 7

ENDSTOP_PIN_X = 12
ENDSTOP_PIN_Y = 6
ENDSTOP_PIN_Z = 5

# Hardware behavior config
# Run command immediately after receiving and stream new pulses, otherwise
# buffer will be prepared firstly and then command will run.
# Before enabling this feature, please make sure that board performance is
# enough for streaming pulses(faster then real time).
INSTANT_RUN = True
