# P9_19 --->  SCL (LSM303DLHC)
# P9_20 --->  SDA (LSM303DLHC)

import lsm303t
from time import sleep

print ('Press CTRL+C to stop')
print ('setup: lsm303 ...')
sleep(1.0)

sensor = lsm303t.LSM303()                     

while(True):
    a = sensor.get_acc()
    m = sensor.get_mag()
    head = sensor.getHeading()
    tiltHead = sensor.getTiltHeading()
    print ('--------------------------------------------------')	
    print ('ax = {0:.2f} g; ay = {1:.2f} g; az = {2:.2f} g.') .format(a[0],a[1],a[2])
    print ('mx = {0:.2f} gauss; my = {1:.2f} gauss; mz = {2:.2f} gauss.') .format(m[0],m[1],m[2])
    print ('Heading = {0:.2f} degrees.') .format(head)
    print ('Tilt Heading = {0:.2f} degrees.') .format(tiltHead)
    sleep(0.2)
