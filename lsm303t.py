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

        self.setup_acc(Scale_A)
        self.setup_mag(Scale_M)


    def setup_acc(self, SCALE):
        self._i2c.writeByte(LSM_ACC_ADDR, CTRL_REG1_A, POWER_ON)
        self._i2c.writeByte(LSM_ACC_ADDR, CTRL_REG4_A, SCALE)

        if(SCALE == SCALE_A_2G):
            S = (-2.0/32768.0)
        if(SCALE == SCALE_A_4G):
            S = (-4.0/32768.0)
        if(SCALE == SCALE_A_8G):
            S = (-8.0/32768.0)
        if(SCALE == SCALE_A_16G):
            S = (-16.0/32768.0)
        return S


    def get_acc(self, S):
        ax = 256*self._i2c.readBytes(LSM_ACC_ADDR, OUT_X_H_A, 1)+self._i2c.readBytes(LSM_ACC_ADDR, OUT_X_L_A, 1)
        if(ax >= 32768 ):
            ax = BitArray(bin(ax)).int

        ay = 256*self._i2c.readBytes(LSM_ACC_ADDR, OUT_Y_H_A, 1)+self._i2c.readBytes(LSM_ACC_ADDR, OUT_Y_L_A, 1)
        if(ay >= 32768 ):
            ay = BitArray(bin(ay)).int

        az = 256*self._i2c.readBytes(LSM_ACC_ADDR, OUT_Z_H_A, 1)+self._i2c.readBytes(LSM_ACC_ADDR, OUT_Z_L_A, 1)
        if(az >= 32768 ):
            az = BitArray(bin(az)).int
        return [S*ax,S*ay,S*az]

    def setup_mag(self, SCALE):
        self._i2c.writeByte(LSM_MAG_ADDR, CRA_REG_M, DATA_RATE)
        self._i2c.writeByte(LSM_MAG_ADDR, CRB_REG_M, SCALE)
        self._i2c.writeByte(LSM_MAG_ADDR, MR_REG_M, CONV_MODE)

        if(SCALE == SCALE_M_13G):
            S = (1.3/32768.0)
        if(SCALE == SCALE_M_19G):
            S = (1.9/32768.0)
        if(SCALE == SCALE_M_25G):
            S = (2.5/32768.0)
        if(SCALE == SCALE_M_40G):
            S = (4.0/32768.0)
        if(SCALE == SCALE_M_47G):
            S = (4.7/32768.0)
        if(SCALE == SCALE_M_56G):
            S = (5.6/32768.0)
        if(SCALE == SCALE_M_81G):
            S = (8.1/32768.0)

        return S

    def get_mag(self, S):
        mx = 256*self._i2c.readBytes(LSM_MAG_ADDR, OUT_X_H_M, 1)+self._i2c.readBytes(LSM_MAG_ADDR, OUT_X_L_M, 1)
        if(mx >= 32768 ):
            mx = BitArray(bin(mx)).int

        my = 256*self._i2c.readBytes(LSM_MAG_ADDR, OUT_Y_H_M, 1)+self._i2c.readBytes(LSM_MAG_ADDR, OUT_Y_L_M, 1)
        if(my >= 32768 ):
            my = BitArray(bin(my)).int

        mz = 256*self._i2c.readBytes(LSM_MAG_ADDR, OUT_Z_H_M, 1)+self._i2c.readBytes(LSM_MAG_ADDR, OUT_Z_L_M, 1)
        if(mz >= 32768 ):
            mz = BitArray(bin(mz)).int
        return [S*mx,S*my,S*mz]
