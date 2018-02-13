#!/usr/bin/python

import minimalmodbus
import sys

value=['low','boost','bypass']

instrument = minimalmodbus.Instrument('/dev/ttyVMC1',0)
instrument.serial.baudrate = 19200
instrument.serial.bytesize = 8
instrument.serial.parity = 'E'
instrument.serial.stopbits = 1

try:
    result = instrument.read_register(15,0,3,False)
    print('{ "airflow_mode": "{}", "airflow_readable": "{}" }'.format(result,value[result]))
except ValueError as e:
    print('{ "error": "%s" }'%(e))
except TypeError as e:
    print('{ "error": "%s" }'%(e))
except IOError as e:
    print('{ "error": "%s" }'%(e))
