# -----------------------------------------------------------------------------
# Hardware config.

import configparser

configFilePath = '/etc/pycnc.conf'


configParser = configparser.RawConfigParser()
configParser.read(configFilePath)

# Mixed settings.
STEPPER_PULSE_LENGTH_US = configParser.getint('CONTROL', 'STEPPER_PULSE_LENGTH_US')
STEPPER_MAX_ACCELERATION_MM_PER_S2 = configParser.getint('CONTROL', 'STEPPER_MAX_ACCELERATION_MM_PER_S2')
SPINDLE_MAX_RPM = configParser.getint('CONTROL', 'SPINDLE_MAX_RPM')


# Workplace physical size.
TABLE_SIZE_X_MM = configParser.getint('WORKPLACE', 'TABLE_SIZE_X_MM')
TABLE_SIZE_Y_MM = configParser.getint('WORKPLACE', 'TABLE_SIZE_Y_MM')
TABLE_SIZE_Z_MM = configParser.getint('WORKPLACE', 'TABLE_SIZE_Z_MM')

TABLE_SIZE_X_MIN_MM = configParser.getint('WORKPLACE', 'TABLE_SIZE_X_MIN_MM')
TABLE_SIZE_Y_MIN_MM = configParser.getint('WORKPLACE', 'TABLE_SIZE_Y_MIN_MM')
TABLE_SIZE_Z_MIN_MM = configParser.getint('WORKPLACE', 'TABLE_SIZE_Z_MIN_MM')

# Maximum velocity for each axis in millimeter per minute.
MAX_VELOCITY_MM_PER_MIN_X = configParser.getint('AXIS', 'MAX_VELOCITY_MM_PER_MIN_X')
MAX_VELOCITY_MM_PER_MIN_Y = configParser.getint('AXIS', 'MAX_VELOCITY_MM_PER_MIN_Y')
MAX_VELOCITY_MM_PER_MIN_Z = configParser.getint('AXIS', 'MAX_VELOCITY_MM_PER_MIN_Z')
MAX_VELOCITY_MM_PER_MIN_E = configParser.getint('AXIS', 'MAX_VELOCITY_MM_PER_MIN_E')
MIN_VELOCITY_MM_PER_MIN   = configParser.getint('AXIS', 'MIN_VELOCITY_MM_PER_MIN')

# Average velocity for endstop calibration procedure
CALIBRATION_VELOCITY_MM_PER_MIN = configParser.getint('AXIS', 'CALIBRATION_VELOCITY_MM_PER_MIN')

# Stepper motors steps per millimeter for each axis.
STEPPER_PULSES_PER_MM_X = configParser.getint('AXIS', 'STEPPER_PULSES_PER_MM_X')
STEPPER_PULSES_PER_MM_Y = configParser.getint('AXIS', 'STEPPER_PULSES_PER_MM_Y')
STEPPER_PULSES_PER_MM_Z = configParser.getint('AXIS', 'STEPPER_PULSES_PER_MM_Z')
STEPPER_PULSES_PER_MM_E = configParser.getint('AXIS', 'STEPPER_PULSES_PER_MM_E')

# Invert axises direction, by default(False) high level means increase of
# position. For inverted(True) axis, high level means decrease of position.
STEPPER_INVERTED_X = configParser.getboolean('AXIS', 'STEPPER_INVERTED_X')
STEPPER_INVERTED_Y = configParser.getboolean('AXIS', 'STEPPER_INVERTED_Y')
STEPPER_INVERTED_Z = configParser.getboolean('AXIS', 'STEPPER_INVERTED_Z')
STEPPER_INVERTED_E = configParser.getboolean('AXIS', 'STEPPER_INVERTED_E')

# Invert zero end stops switches. By default(False) low level on input pin
# means that axis in zero position. For inverted(True) end stops, high level
# means zero position.
ENDSTOP_INVERTED_X = configParser.getboolean('AXIS', 'ENDSTOP_INVERTED_X')
ENDSTOP_INVERTED_Y = configParser.getboolean('AXIS', 'ENDSTOP_INVERTED_Y')
ENDSTOP_INVERTED_Z = configParser.getboolean('AXIS', 'ENDSTOP_INVERTED_Z')

EXTRUDER_MAX_TEMPERATURE = configParser.getint('TEMPERATURE', 'EXTRUDER_MAX_TEMPERATURE')
BED_MAX_TEMPERATURE = configParser.getint('TEMPERATURE', 'BED_MAX_TEMPERATURE')
MIN_TEMPERATURE = configParser.getint('TEMPERATURE', 'MIN_TEMPERATURE')


# -----------------------------------------------------------------------------
# Pins configuration.
# Enable pin for all steppers, low level is enabled.
STEPPERS_ENABLE_PIN = configParser.getint('CONTROL', 'STEPPERS_ENABLE_PIN')

STEPPER_STEP_PIN_X  = configParser.getint('AXIS', 'STEPPER_STEP_PIN_X')
STEPPER_DIR_PIN_X   = configParser.getint('AXIS', 'STEPPER_DIR_PIN_X')
ENDSTOP_PIN_X       = configParser.getint('AXIS', 'ENDSTOP_PIN_X')

STEPPER_STEP_PIN_Y  = configParser.getint('AXIS', 'STEPPER_STEP_PIN_Y')
STEPPER_DIR_PIN_Y   = configParser.getint('AXIS', 'STEPPER_DIR_PIN_Y')
ENDSTOP_PIN_Y       = configParser.getint('AXIS', 'ENDSTOP_PIN_Y')

STEPPER_STEP_PIN_Z  = configParser.getint('AXIS', 'STEPPER_STEP_PIN_Z')
STEPPER_DIR_PIN_Z   = configParser.getint('AXIS', 'STEPPER_DIR_PIN_Z')
ENDSTOP_PIN_Z       = configParser.getint('AXIS', 'ENDSTOP_PIN_Z')

STEPPER_STEP_PIN_E  = configParser.getint('AXIS', 'STEPPER_STEP_PIN_E')
STEPPER_DIR_PIN_E   = configParser.getint('AXIS', 'STEPPER_DIR_PIN_E')

SPINDLE_PWM_PIN     = configParser.getint('CONTROL', 'SPINDLE_PWM_PIN')
FAN_PIN             = configParser.getint('CONTROL', 'FAN_PIN')
EXTRUDER_HEATER_PIN = configParser.getint('CONTROL', 'EXTRUDER_HEATER_PIN')
BED_HEATER_PIN      = configParser.getint('CONTROL', 'BED_HEATER_PIN')

EXTRUDER_TEMPERATURE_SENSOR_CHANNEL = configParser.getint('CONTROL', 'EXTRUDER_TEMPERATURE_SENSOR_CHANNEL')
BED_TEMPERATURE_SENSOR_CHANNEL = configParser.getint('CONTROL', 'BED_TEMPERATURE_SENSOR_CHANNEL')


# -----------------------------------------------------------------------------
#  Behavior config

# Run command immediately after receiving and stream new pulses, otherwise
# buffer will be prepared firstly and then command will run.
# Before enabling this feature, please make sure that board performance is
# enough for streaming pulses(faster then real time).
INSTANT_RUN = configParser.getboolean('CONTROL', 'INSTANT_RUN')

# If this parameter is False, error will be raised on command with velocity
# more than maximum velocity specified here. If this parameter is True,
# velocity would be decreased(proportional for all axises) to fit the maximum
# velocity.
AUTO_VELOCITY_ADJUSTMENT = configParser.getboolean('CONTROL', 'AUTO_VELOCITY_ADJUSTMENT')

# Automatically turn on fan when extruder is heating, boolean value.
AUTO_FAN_ON = configParser.getboolean('CONTROL', 'AUTO_FAN_ON')

EXTRUDER_PID = {"P": 0.059161177519,
                "I": 0.00206217171374,
                "D": 0.206217171374}
BED_PID = {"P": 0.226740848076,
           "I": 0.00323956215053,
           "D": 0.323956215053}
