#!/usr/bin/python

from OmegaExpansion import onionI2C
import time

"""
Get the luminosity readings.
"""
i2c = onionI2C.OnionI2C()

addr = 0x23
i2c.writeByte(addr, 0x00, 0x00)  # make sure device is in a clean state
i2c.writeByte(addr, 0x01, 0x01)  # power up
i2c.writeByte(addr, 0x11, 0x11)  # set measurement mode
time.sleep(0.12)
data = i2c.readbytes(addr,0x11,2)
lux = str((data[1] + (256 * data[0])) / 1.2)

print(lux)
