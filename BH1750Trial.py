
from OmegaExpansion import onionI2C

import time



DELAY_HMODE = 0.18  # 180ms in H-mode
DELAY_LMODE = 0.024  # 24ms in L-mode


class BH1750(object):

    PowerDown = 0x00
    PowerOn = 0x01
    Reset = 0x07
    Cont_HRES1 = 0x10
    Cont_HRES2 = 0x11
    Cont_LRES = 0x13
    SINGLE_HRES1 = 0x20
    SINGLE_HRES2 = 0x21
    SINGLE_LRES = 0x23


    def __init__(self, mode=SINGLE_HRES1, addr=0x23):
        if mode not in [Cont_HRES1, Cont_HRES2, Cont_LRES,
                        SINGLE_HRES1, SINGLE_HRES2, SINGLE_LRES]:
            raise ValueError(
                'Unexpected sample mode value {0}.  Set mode to one of XXX'.format(mode))
        Delay = 0.0
        if mode == Cont_LRES:
            Delay = DELAY_LMODE
        elif mode == SINGLE_LRES:
            Delay = DELAY_LMODE
        else Delay = DELAY_HMODE

        self.mode = mode

        self.i2c = onionI2C.OnionI2C()

        self.addr = addr
        


    def luxsample(self):

        """0x01

            Performs a single sampling. returns the result in lux

        """

        i2c.write(i2c.addr, PowerDown)  # make sure device is in a clean state
        i2c.write(i2c.addr, PowerOn)  # power up
        i2c.write(i2c.addr, self.mode)  # set measurement mode

        time.sleep(Delay)

        raw = i2c.readBytes(i2c.addr, 2)
        i2c.write(i2c.addr, PowerDown)  # power down again

        # we must divide the end result by 1.2 to get the lux
        return ((raw[0] << 24) | (raw[1] << 16)) // 78642
