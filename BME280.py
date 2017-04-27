'''
This is a Library for the BME280 humidity, temperature and pressure sensor. It is only supported on the I2C Bus and will not support the SPI bus connection.

As expected, the software is written in Python and is for use with the Onion Omega2.

No Warranty is given for its use.

'''

#Relevant files to import

from OmegaExpansion import onionI2C

import time

#BME280 Default Address
# addr = 0x76

# Operating Modes Temp
T_OSample_1 = 1
T_OSample_2 = 2
T_OSample_4 = 3
T_OSample_8 = 4
T_OSample_16 = 5

# Operating Modes Pressure
P_OSample_1 = 1
P_OSample_2 = 2
P_OSample_4 = 3
P_OSample_8 = 4
P_OSample_16 = 5

# Operating Modes Humidity
H_OSample_1 = 1
H_OSample_2 = 2
H_OSample_4 = 3
H_OSample_8 = 4
H_OSample_16 = 5

# BME280 Registers

BME280_REGISTER_DIG_T1 = 0x88  # Trimming parameter registers
BME280_REGISTER_DIG_T2 = 0x8A
BME280_REGISTER_DIG_T3 = 0x8C

BME280_REGISTER_DIG_P1 = 0x8E
BME280_REGISTER_DIG_P2 = 0x90
BME280_REGISTER_DIG_P3 = 0x92
BME280_REGISTER_DIG_P4 = 0x94
BME280_REGISTER_DIG_P5 = 0x96
BME280_REGISTER_DIG_P6 = 0x98
BME280_REGISTER_DIG_P7 = 0x9A
BME280_REGISTER_DIG_P8 = 0x9C
BME280_REGISTER_DIG_P9 = 0x9E

BME280_REGISTER_DIG_H1 = 0xA1
BME280_REGISTER_DIG_H2 = 0xE1
BME280_REGISTER_DIG_H3 = 0xE3
BME280_REGISTER_DIG_H4 = 0xE4
BME280_REGISTER_DIG_H5 = 0xE5
BME280_REGISTER_DIG_H6 = 0xE6
BME280_REGISTER_DIG_H7 = 0xE7

BME280_REGISTER_CHIPID = 0xD0
BME280_REGISTER_VERSION = 0xD1
BME280_REGISTER_SOFTRESET = 0xE0

BME280_REGISTER_CONTROL_HUM = 0xF2
BME280_REGISTER_CONTROL = 0xF4
BME280_REGISTER_CONFIG = 0xF5
BME280_REGISTER_PRESSURE_DATA = 0xF7
BME280_REGISTER_TEMP_DATA = 0xFA
BME280_REGISTER_HUMIDITY_DATA = 0xFD

class BME280(object):
    def __init__(self, addr=0x76, tMode=T_OSample_1, pMode=P_OSample_1, hMode=H_OSample_1):
        #Check if the Modes are valid
        if tMode not in [T_OSample_1, T_OSample_2, T_OSample_4,
                        T_OSample_8, T_OSample_16]:
            raise ValueError(
                'Unexpected Temperature mode value {0}.  Set mode to one of BME280_ULTRALOWPOWER, BME280_STANDARD, BME280_HIGHRES, or BME280_ULTRAHIGHRES'.format(mode))
        self._tMode = tMode
        if pMode not in [P_OSample_1, P_OSample_2, P_OSample_4,
                        P_OSample_8, P_OSample_16]:
            raise ValueError(
                'Unexpected Pressure mode value {0}.  Set mode to one of BME280_ULTRALOWPOWER, BME280_STANDARD, BME280_HIGHRES, or BME280_ULTRAHIGHRES'.format(mode))
        self._pMode = pMode
        if hMode not in [H_OSample_1, H_OSample_2, H_OSample_4,
                        H_OSample_8, H_OSample_16]:
            raise ValueError(
                'Unexpected Humidity mode value {0}.  Set mode to one of BME280_ULTRALOWPOWER, BME280_STANDARD, BME280_HIGHRES, or BME280_ULTRAHIGHRES'.format(mode))
        self._hMode = hMode

        
        #I2C Bus init
        self._i2c = onionI2C.OnionI2C()

        #I2C Addr init
        self._addr = addr

        self._load_calibration()
        self._bme280_Setup()
        #self._i2c.writeByte(0x76, 0xF4, 0x3F)
        self.t_fine =0.0


    def _load_calibration(self):

        # BME280 address, 0x76(118)
        # Read data back from 0x88(136), 24 bytes
        b1 = self._i2c.readBytes(self._addr, 0x88, 24)

        # Convert the data
        # Temp coefficents
        self.dig_T1 = b1[1] * 256 + b1[0]
        self.dig_T2 = b1[3] * 256 + b1[2]
        if self.dig_T2 > 32767 :
            self.dig_T2 -= 65536
        self.dig_T3 = b1[5] * 256 + b1[4]
        if self.dig_T3 > 32767 :
            self.dig_T3 -= 65536

        # Pressure coefficents
        self.dig_P1 = b1[7] * 256 + b1[6]
        self.dig_P2 = b1[9] * 256 + b1[8]
        if self.dig_P2 > 32767 :
            self.dig_P2 -= 65536
        self.dig_P3 = b1[11] * 256 + b1[10]
        if self.dig_P3 > 32767 :
            self.dig_P3 -= 65536
        self.dig_P4 = b1[13] * 256 + b1[12]
        if self.dig_P4 > 32767 :
            self.dig_P4 -= 65536
        self.dig_P5 = b1[15] * 256 + b1[14]
        if self.dig_P5 > 32767 :
            self.dig_P5 -= 65536
        self.dig_P6 = b1[17] * 256 + b1[16]
        if self.dig_P6 > 32767 :
            self.dig_P6 -= 65536
        self.dig_P7 = b1[19] * 256 + b1[18]
        if self.dig_P7 > 32767 :
            self.dig_P7 -= 65536
        self.dig_P8 = b1[21] * 256 + b1[20]
        if self.dig_P8 > 32767 :
            self.dig_P8 -= 65536
        self.dig_P9 = b1[23] * 256 + b1[22]
        if self.dig_P9 > 32767 :
            self.dig_P9 -= 65536

        # BME280 address, 0x76(118)
        # Read data back from 0xA1(161), 1 byte
        b1 = self._i2c.readBytes(self._addr, 0xA1, 1)
        self.dig_H1 = b1[0]

        # BME280 address, 0x76(118)
        # Read data back from 0xE1(225), 7 bytes
        b1 = self._i2c.readBytes(self._addr, 0xE1, 7)

        # Convert the data
        # Humidity coefficents
        self.dig_H2 = b1[1] * 256 + b1[0]
        if self.dig_H2 > 32767 :
            self.dig_H2 -= 65536
        self.dig_H3 = (b1[2] &  0xFF)
        self.dig_H4 = (b1[3] * 16) + (b1[4] & 0xF)
        if self.dig_H4 > 32767 :
            self.dig_H4 -= 65536
        self.dig_H5 = (b1[4] / 16) + (b1[5] * 16)
        if self.dig_H5 > 32767 :
            self.dig_H5 -= 65536
        self.dig_H6 = b1[6]
        if self.dig_H6 > 127 :
            self.dig_H6 -= 256
        
    def _bme280_Setup(self):
        hMeas = self._hMode
        self._i2c.writeByte(self._addr, BME280_REGISTER_CONTROL_HUM, hMeas)
        meas = self._tMode << 5 | self._pMode << 2 | 1
        self._i2c.writeByte(self._addr, BME280_REGISTER_CONTROL, meas)


        sleep_time = 0.00125 + 0.0023 * (1 << self._tMode)
        sleep_time = sleep_time + 0.0023 * (1 << self._pMode) + 0.000575
        sleep_time = sleep_time + 0.0023 * (1 << self._hMode) + 0.000575
        time.sleep(sleep_time)  # Wait the required time

        '''# BME280 address, 0x76(118)
        # Select control humidity register, 0xF2(242)
        #		0x01(01)	Humidity Oversampling = 1
        self._i2c.writeByte(self._addr, 0xF2, 0x01)
        # BME280 address, 0x76(118)
        # Select Control measurement register, 0xF4(244)
        #		0x27(39)	Pressure and Temperature Oversampling rate = 1
        #					Normal mode
        self._i2c.writeByte(self._addr, 0xF4, 0x27)
        # BME280 address, 0x76(118)
        # Select Configuration register, 0xF5(245)
        #		0xA0(00)	Stand_by time = 1000 ms
        self._i2c.writeByte(self._addr, 0xF5, 0xA0)
        time.sleep(0.5)'''
    
    def read_raw_temp(self):
        # BME280 address, 0x76(118)
        # Read data back from 0xF7(247), 8 bytes
        # Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
        # Temperature xLSB, Humidity MSB, Humidity LSB
        data = self._i2c.readBytes(self._addr, 0xF7, 8)

        # Convert pressure and temperature data to 19-bits
        adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16
               
        return adc_t

    def read_raw_pressure(self):
        # BME280 address, 0x76(118)
        # Read data back from 0xF7(247), 8 bytes
        # Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
        # Temperature xLSB, Humidity MSB, Humidity LSB
        data = self._i2c.readBytes(self._addr, 0xF7, 8)

        # Convert pressure and temperature data to 19-bits
        adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
             
        return adc_p

    def read_raw_humidity(self):
        # BME280 address, 0x76(118)
        # Read data back from 0xF7(247), 8 bytes
        # Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
        # Temperature xLSB, Humidity MSB, Humidity LSB
        data = self._i2c.readBytes(self._addr, 0xF7, 8)

        # Convert the humidity data
        adc_h = data[6] * 256 + data[7]       
        return adc_h


    def read_temperatureC(self):
        UT = float(self.read_raw_temp())
        var1 = ((UT) / 16384.0 - (self.dig_T1) / 1024.0) * (self.dig_T2)
        var2 = (((UT) / 131072.0 - (self.dig_T1) / 8192.0) * ((UT)/131072.0 - (self.dig_T1)/8192.0)) * (self.dig_T3)
        self.t_fine = (var1 + var2)
        tempC = (var1 + var2) / 5120.0
        tempF = tempC * 1.8 + 32
        return tempC
    
    def read_temperatureF(self):
        UT = float(self.read_raw_temp())
        var1 = ((UT) / 16384.0 - (self.dig_T1) / 1024.0) * (self.dig_T2)
        var2 = (((UT) / 131072.0 - (self.dig_T1) / 8192.0) * ((UT)/131072.0 - (self.dig_T1)/8192.0)) * (self.dig_T3)
        self.t_fine = (var1 + var2)
        tempC = (var1 + var2) / 5120.0
        tempF = tempC * 1.8 + 32
        return tempF

    def read_pressure(self):
        adc = self.read_raw_pressure()
        var1 = (self.t_fine / 2.0) - 64000.0
        var2 = var1 * var1 * (self.dig_P6) / 32768.0
        var2 = var2 + var1 * (self.dig_P5) * 2.0
        var2 = (var2 / 4.0) + ((self.dig_P4) * 65536.0)
        var1 = ((self.dig_P3) * var1 * var1 / 524288.0 + ( self.dig_P2) * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * (self.dig_P1)
        p = 1048576.0 - adc
        p = (p - (var2 / 4096.0)) * 6250.0 / var1
        var1 = (self.dig_P9) * p * p / 2147483648.0
        var2 = p * (self.dig_P8) / 32768.0
        pressure = p + (var1 + var2 + (self.dig_P7)) / 16.0
        return pressure

    def read_humidity(self):
        adc = self.read_raw_humidity()
        var_H = ((self.t_fine) - 76800.0)
        var_H = (adc - (self.dig_H4 * 64.0 + self.dig_H5 / 16384.0 * var_H)) * (self.dig_H2 / 65536.0 * (1.0 + self.dig_H6 / 67108864.0 * var_H * (1.0 + self.dig_H3 / 67108864.0 * var_H)))
        humidity = var_H * (1.0 -  self.dig_H1 * var_H / 524288.0)
        if humidity > 100.0 :
            humidity = 100.0
        elif humidity < 0.0 :
            humidity = 0.0
        return humidity

