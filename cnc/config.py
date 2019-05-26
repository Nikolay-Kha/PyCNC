# -----------------------------------------------------------------------------
# Hardware config.

import configparser

configFilePath = '/etc/pycnc.conf'


configParser = configparser.RawConfigParser()
configParser.read(configFilePath)

# Mixed settings.
STEPPER_PULSE_LENGTH_US = configParser.getint('control', 'stepper_pulse_length_us')
STEPPER_MAX_ACCELERATION_MM_PER_S2 = configParser.getint('control', 'stepper_max_acceleration_mm_per_s2')
SPINDLE_MAX_RPM = configParser.getint('control', 'spindle_max_rpm')


# Workplace physical size.
TABLE_SIZE_X_MM = configParser.getint('workplace', 'table_size_x_mm')
TABLE_SIZE_Y_MM = configParser.getint('workplace', 'table_size_y_mm')
TABLE_SIZE_Z_MM = configParser.getint('workplace', 'table_size_z_mm')

TABLE_SIZE_X_MIN_MM = configParser.getint('workplace', 'table_size_x_min_mm')
TABLE_SIZE_Y_MIN_MM = configParser.getint('workplace', 'table_size_y_min_mm')
TABLE_SIZE_Z_MIN_MM = configParser.getint('workplace', 'table_size_z_min_mm')

# Maximum velocity for each axis in millimeter per minute.
MAX_VELOCITY_MM_PER_MIN_X = configParser.getint('axis', 'max_velocity_mm_per_min_x')
MAX_VELOCITY_MM_PER_MIN_Y = configParser.getint('axis', 'max_velocity_mm_per_min_y')
MAX_VELOCITY_MM_PER_MIN_Z = configParser.getint('axis', 'max_velocity_mm_per_min_z')
MAX_VELOCITY_MM_PER_MIN_E = configParser.getint('axis', 'max_velocity_mm_per_min_e')
MIN_VELOCITY_MM_PER_MIN   = configParser.getint('axis', 'min_velocity_mm_per_min')

# Average velocity for endstop calibration procedure
CALIBRATION_VELOCITY_MM_PER_MIN = configParser.getint('axis', 'calibration_velocity_mm_per_min')

# Stepper motors steps per millimeter for each axis.
STEPPER_PULSES_PER_MM_X = configParser.getint('axis', 'stepper_pulses_per_mm_x')
STEPPER_PULSES_PER_MM_Y = configParser.getint('axis', 'stepper_pulses_per_mm_y')
STEPPER_PULSES_PER_MM_Z = configParser.getint('axis', 'stepper_pulses_per_mm_z')
STEPPER_PULSES_PER_MM_E = configParser.getint('axis', 'stepper_pulses_per_mm_e')

# Invert axises direction, by default(False) high level means increase of
# position. For inverted(True) axis, high level means decrease of position.
STEPPER_INVERTED_X = configParser.getboolean('axis', 'stepper_inverted_x')
STEPPER_INVERTED_Y = configParser.getboolean('axis', 'stepper_inverted_y')
STEPPER_INVERTED_Z = configParser.getboolean('axis', 'stepper_inverted_z')
STEPPER_INVERTED_E = configParser.getboolean('axis', 'stepper_inverted_e')

# Invert zero end stops switches. By default(False) low level on input pin
# means that axis in zero position. For inverted(True) end stops, high level
# means zero position.
ENDSTOP_INVERTED_X = configParser.getboolean('axis', 'endstop_inverted_x')
ENDSTOP_INVERTED_Y = configParser.getboolean('axis', 'endstop_inverted_y')
ENDSTOP_INVERTED_Z = configParser.getboolean('axis', 'endstop_inverted_z')

EXTRUDER_MAX_TEMPERATURE = configParser.getint('temperature', 'extruder_max_temperature')
BED_MAX_TEMPERATURE = configParser.getint('temperature', 'bed_max_temperature')
MIN_TEMPERATURE = configParser.getint('temperature', 'min_temperature')


# -----------------------------------------------------------------------------
# Pins configuration.
# Enable pin for all steppers, low level is enabled.
STEPPERS_ENABLE_PIN = configParser.getint('control', 'steppers_enable_pin')

STEPPER_STEP_PIN_X  = configParser.getint('axis', 'stepper_step_pin_x')
STEPPER_DIR_PIN_X   = configParser.getint('axis', 'stepper_dir_pin_x')
ENDSTOP_PIN_X       = configParser.getint('axis', 'endstop_pin_x')

STEPPER_STEP_PIN_Y  = configParser.getint('axis', 'stepper_step_pin_y')
STEPPER_DIR_PIN_Y   = configParser.getint('axis', 'stepper_dir_pin_y')
ENDSTOP_PIN_Y       = configParser.getint('axis', 'endstop_pin_y')

STEPPER_STEP_PIN_Z  = configParser.getint('axis', 'stepper_step_pin_z')
STEPPER_DIR_PIN_Z   = configParser.getint('axis', 'stepper_dir_pin_z')
ENDSTOP_PIN_Z       = configParser.getint('axis', 'endstop_pin_z')

STEPPER_STEP_PIN_E  = configParser.getint('axis', 'stepper_step_pin_e')
STEPPER_DIR_PIN_E   = configParser.getint('axis', 'stepper_dir_pin_e')

SPINDLE_PWM_PIN     = configParser.getint('control', 'spindle_pwm_pin')
FAN_PIN             = configParser.getint('control', 'fan_pin')
EXTRUDER_HEATER_PIN = configParser.getint('control', 'extruder_heater_pin')
BED_HEATER_PIN      = configParser.getint('control', 'bed_heater_pin')

EXTRUDER_TEMPERATURE_SENSOR_CHANNEL = configParser.getint('control', 'extruder_temperature_sensor_channel')
BED_TEMPERATURE_SENSOR_CHANNEL = configParser.getint('control', 'bed_temperature_sensor_channel')


# -----------------------------------------------------------------------------
#  Behavior config

# Run command immediately after receiving and stream new pulses, otherwise
# buffer will be prepared firstly and then command will run.
# Before enabling this feature, please make sure that board performance is
# enough for streaming pulses(faster then real time).
INSTANT_RUN = configParser.getboolean('control', 'instant_run')

# If this parameter is False, error will be raised on command with velocity
# more than maximum velocity specified here. If this parameter is True,
# velocity would be decreased(proportional for all axises) to fit the maximum
# velocity.
AUTO_VELOCITY_ADJUSTMENT = configParser.getboolean('control', 'auto_velocity_adjustment')

# Automatically turn on fan when extruder is heating, boolean value.
AUTO_FAN_ON = configParser.getboolean('control', 'auto_fan_on')

EXTRUDER_PID = {"P": 0.059161177519,
                "I": 0.00206217171374,
                "D": 0.206217171374}
BED_PID = {"P": 0.226740848076,
           "I": 0.00323956215053,
           "D": 0.323956215053}
