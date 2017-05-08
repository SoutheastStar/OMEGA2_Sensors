from OmegaExpansion import onionI2C
from bitstring import BitArray
import time

LSM_ACC_ADDR = 0x19

CTRL_REG1_A = 0x20
CTRL_REG4_A = 0x23
OUT_X_L_A = 0x28
OUT_X_H_A = 0x29
OUT_Y_L_A = 0x2A
OUT_Y_H_A = 0x2B
OUT_Z_L_A = 0x2C
OUT_Z_H_A = 0x2D


POWER_ON = 0b10010111           # ON LSM303 ACC. and 1.344 KHz mode
SCALE_A_2G = 0b00001000         # +/- 2 G scale, and HR
SCALE_A_4G = 0b00011000         # +/- 4 G scale, and HR
SCALE_A_8G = 0b00101000         # +/- 8 G scale, and HR
SCALE_A_16G = 0b00111000        # +/-16 G scale, and HR

LSM_MAG_ADDR = 0x1E

CRA_REG_M = 0x00
CRB_REG_M = 0x01
MR_REG_M = 0x02
OUT_X_L_M = 0x03
OUT_X_H_M = 0x04
OUT_Y_L_M = 0x05
OUT_Y_H_M = 0x06
OUT_Z_L_M = 0x07
OUT_Z_H_M = 0x08

DATA_RATE = 0b00011000          # Temp. Sen. Disable and 75H output rate
CONV_MODE = 0b00000000          # Continuous conversion mode

SCALE_M_13G = 0b00100000        # +/- 1.3 Gauss scale
SCALE_M_19G = 0b01000000        # +/- 1.9 Gauss scale
SCALE_M_25G = 0b01100000        # +/- 2.5 Gauss scale
SCALE_M_40G = 0b10000000        # +/- 4.0 Gauss scale
SCALE_M_47G = 0b10100000        # +/- 4.7 Gauss scale
SCALE_M_56G = 0b11000000        # +/- 5.6 Gauss scale
SCALE_M_81G = 0b11100000        # +/- 8.1 Gauss scale

class LSM303(object):
    def __init__(self, SCALE_A = SCALE_A_8G, LSM_ACC_ADDR = 0x19, SCALE_M = SCALE_M_81G, LSM_MAG_ADDR = 0x1E):
        if SCALE_A not in [SCALE_A_2G, SCALE_A_4G, SCALE_A_8G, SCALE_A_16G]:
            raise ValueError(
                'Unexpected Temperature mode value {0}.  Set mode to one of XXXX'.format(mode))
        self._Scale_A = SCALE_A
        if SCALE_M not in [SCALE_M_13G, SCALE_M_19G, SCALE_M_25G, SCALE_M_40G, SCALE_M_47G, SCALE_M_56G, SCALE_M_81G]:
            raise ValueError(
                'Unexpected Temperature mode value {0}.  Set mode to one of XXXX'.format(mode))
        self._Scale_M = SCALE_M

        #I2C Bus init
        self._i2c = onionI2C.OnionI2C()

        self.setup_acc()
        self.setup_mag()


    def setup_acc(self):
        self._i2c.writeByte(LSM_ACC_ADDR, CTRL_REG1_A, POWER_ON)
        self._i2c.writeByte(LSM_ACC_ADDR, CTRL_REG4_A, self._Scale_A)

        if(self._Scale_A == SCALE_A_2G):
            self._SA = (-2.0/32768.0)
        if(self._Scale_A == SCALE_A_4G):
            self._SA = (-4.0/32768.0)
        if(self._Scale_A == SCALE_A_8G):
            self._SA = (-8.0/32768.0)
        if(self._Scale_A == SCALE_A_16G):
            self._SA = (-16.0/32768.0)
        return self._SA


    def get_acc(self):
        ax1 = self._i2c.readBytes(LSM_ACC_ADDR, OUT_X_H_A, 1)
        ax2 = self._i2c.readBytes(LSM_ACC_ADDR, OUT_X_L_A, 1)
        ax = 256*ax1[0]+ ax2[0]

        ay1 = self._i2c.readBytes(LSM_ACC_ADDR, OUT_Y_H_A, 1)
        ay2 = self._i2c.readBytes(LSM_ACC_ADDR, OUT_Y_L_A, 1)
        ay = 256*ay1[0] + ay2[0]

        az1 = self._i2c.readBytes(LSM_ACC_ADDR, OUT_Z_H_A, 1)
        az2 = self._i2c.readBytes(LSM_ACC_ADDR, OUT_Z_L_A, 1)
        az = 256*az1[0] + az2[0]

        return [self._SA*ax,self._SA*ay,self._SA*az]

    def setup_mag(self):
        self._i2c.writeByte(LSM_MAG_ADDR, CRA_REG_M, DATA_RATE)
        self._i2c.writeByte(LSM_MAG_ADDR, CRB_REG_M, self._Scale_M)
        self._i2c.writeByte(LSM_MAG_ADDR, MR_REG_M, CONV_MODE)

        if(self._Scale_M == SCALE_M_13G):
            self._SM = (1.3/32768.0)
        if(self._Scale_M == SCALE_M_19G):
            self._SM = (1.9/32768.0)
        if(self._Scale_M == SCALE_M_25G):
            self._SM = (2.5/32768.0)
        if(self._Scale_M == SCALE_M_40G):
            self._SM = (4.0/32768.0)
        if(self._Scale_M == SCALE_M_47G):
            self._SM = (4.7/32768.0)
        if(self._Scale_M == SCALE_M_56G):
            self._SM = (5.6/32768.0)
        if(self._Scale_M == SCALE_M_81G):
            self._SM = (8.1/32768.0)

        return self._SM

    def get_mag(self):
        mx1 = self._i2c.readBytes(LSM_MAG_ADDR, OUT_X_H_M, 1)
        mx2 = self._i2c.readBytes(LSM_MAG_ADDR, OUT_X_L_M, 1)
        self._mx = 256*mx1[0] + mx2[0]

        my1 = self._i2c.readBytes(LSM_MAG_ADDR, OUT_Y_H_M, 1)
        my2 = self._i2c.readBytes(LSM_MAG_ADDR, OUT_Y_L_M, 1)
        self._my = 256*my1[0] + my2[0]

        mz1 = self._i2c.readBytes(LSM_MAG_ADDR, OUT_Z_H_M, 1)
        mz2 = self._i2c.readBytes(LSM_MAG_ADDR, OUT_Z_L_M, 1)
        self._mz = 256*mz1[0] + mz2[0]

        return [self._SM*self._mx,self._SM*self._my,self._SM*self._mz]

    def getHeading(self):
        float heading = 180*math.atan2(self._SM*self._my, self._SM*self._mx)/math.pi
        if(heading < 0):
            heading += 360

        return heading

    
        
        
