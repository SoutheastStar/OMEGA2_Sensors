#!/usr/bin/env python

# SDL_DS3231.py Python Driver Code
# now includes reading and writing the AT24C32 included on the SwitchDoc Labs 
# DS3231 / AT24C32 Module


#encoding: utf-8
 
from datetime import datetime
from OmegaExpansion import onionI2C

import time

def _bcd_to_int(bcd):
    """Decode a 2x4bit BCD to a integer.
    """
    out = 0
    for d in (bcd >> 4, bcd):
        for p in (1, 2, 4 ,8):
            if d & 1:
                out += p
            d >>= 1
        out *= 10
    return out / 10

def _bcdtoint(bcd1):
    """Decode a 1x8bit BCD to a integer.
    """
    out = 0
    for d in (bcd1 >> 8, bcd1):
        for p in (1, 2, 4, 8, 16, 32, 68, 128):
            if d & 1:
                out += p
            d >>= 1
        out *= 10
    return out / 10


def _int_to_bcd(n):
    """Encode a one or two digits number to the BCD.
    """
    bcd = 0
    for i in (n // 10, n % 10):
        for p in (8, 4, 2, 1):
            if i >= p:
                bcd += 1
                i -= p
            bcd <<= 1
    return bcd >> 1


class SDL_DS3231():
    _REG_SECONDS = 0x00
    _REG_MINUTES = 0x01
    _REG_HOURS = 0x02
    _REG_DAY = 0x03
    _REG_DATE = 0x04
    _REG_MONTH = 0x05
    _REG_YEAR = 0x06
    _REG_CONTROL = 0x0E
    _REG_TMSB = 0x11
    _REG_TLSB = 0x12



    ###########################
    # DS3231 Code
    ###########################
    def __init__(self, addr=0x68, at24c32_addr=0x56):
        self._i2c = onionI2C.OnionI2C()
        self._addr = addr
        self._at24c32_addr = at24c32_addr


    def _write(self, register, data):
        self._i2c.writeByte(self._addr, register, data)


    def _read(self, data):

        returndata = self._i2c.readBytes(self._addr, data, 1)
        return returndata[0]




    def _read_seconds(self):
        return _bcd_to_int(self._read(self._REG_SECONDS)& 0x7F)   # wipe out the oscillator on bit


    def _read_minutes(self):
        return _bcd_to_int(self._read(self._REG_MINUTES))


    def _read_hours(self):
        d = self._read(self._REG_HOURS)
        if (d == 0x64):
            d = 0x40
        return _bcd_to_int(d & 0x3F)


    def _read_day(self):
        return _bcd_to_int(self._read(self._REG_DAY))


    def _read_date(self):
        return _bcd_to_int(self._read(self._REG_DATE))


    def _read_month(self):
        return _bcd_to_int(self._read(self._REG_MONTH))
        


    def _read_year(self):
        return _bcd_to_int(self._read(self._REG_YEAR))


    def read_all(self):
        """Return a tuple such as (year, month, date, day, hours, minutes,
        seconds).
        """
        return (self._read_year(), self._read_month(), self._read_date(),
                self._read_day(), self._read_hours(), self._read_minutes(),
                self._read_seconds())


    def read_str(self):
        """Return a string such as 'YY-DD-MMTHH-MM-SS'.
        """
        return '%02d-%02d-%02dT%02d:%02d:%02d' % (self._read_year(),
                self._read_month(), self._read_date(), self._read_hours(),
                self._read_minutes(), self._read_seconds())


    def read_datetime(self, century=21, tzinfo=None):
        """Return the datetime.datetime object.
        """
        return datetime((century - 1) * 100 + self._read_year(),
                self._read_month(), self._read_date(), self._read_hours(),
                self._read_minutes(), self._read_seconds(), 0, tzinfo=tzinfo)


    def write_all(self, seconds=None, minutes=None, hours=None, day=None,
            date=None, month=None, year=None, save_as_24h=True):
        """Direct write un-none value.
        Range: seconds [0,59], minutes [0,59], hours [0,23],
               day [0,7], date [1-31], month [1-12], year [0-99].
        """
        if seconds is not None:
            if seconds < 0 or seconds > 59:
                raise ValueError('Seconds is out of range [0,59].')
            #seconds_reg = _int_to_bcd(seconds)
            self._write(self._REG_SECONDS, _int_to_bcd(seconds))#seconds_reg)

        if minutes is not None:
            if minutes < 0 or minutes > 59:
                raise ValueError('Minutes is out of range [0,59].')
            self._write(self._REG_MINUTES, _int_to_bcd(minutes))

        if hours is not None:
            if hours < 0 or hours > 23:
                raise ValueError('Hours is out of range [0,23].')
            self._write(self._REG_HOURS, _int_to_bcd(hours) ) # not  | 0x40 according to datasheet

        if year is not None:
            if year < 0 or year > 99:
                raise ValueError('Years is out of range [0,99].')
            self._write(self._REG_YEAR, _int_to_bcd(year))

        if month is not None:
            if month < 1 or month > 12:
                raise ValueError('Month is out of range [1,12].')
            self._write(self._REG_MONTH, _int_to_bcd(month))

        if date is not None:
            if date < 1 or date > 31:
                raise ValueError('Date is out of range [1,31].')
            self._write(self._REG_DATE, _int_to_bcd(date))

        if day is not None:
            if day < 1 or day > 7:
                raise ValueError('Day is out of range [1,7].')
            self._write(self._REG_DAY, _int_to_bcd(day))


    def write_datetime(self, dt):
        """Write from a datetime.datetime object.
        """
        self.write_all(dt.second, dt.minute, dt.hour,
                dt.isoweekday(), dt.day, dt.month, dt.year % 100)


    def write_now(self):
        """Equal to DS3231.write_datetime(datetime.datetime.now()).
        """
        self.write_datetime(datetime.now())



    def get_temp(self):
        byte_tmsb = _bcdtoint(self._read(self._REG_TMSB))
        byte_tlsb = _bcdtoint(self._read(self._REG_TLSB))
        if byte_tlsb == 192:
            tlsb = 0.75
        elif byte_tlsb == 128:
            tlsb = 0.50
        elif byte_tlsb == 64:
            tlsb = 0.25
        else:
            tlsb = 0.00                
        return byte_tmsb + tlsb

    ###########################
    # AT24C32 Code
    ###########################

    # def set_current_AT24C32_address(self,address):
    #  a0=address%256;
    #  a1=address/256;
    #  self._bus.write_i2c_block_data(self._at24c32_addr,a1,[a0])

  
    def read_AT24C32_byte(self, address):
        return self._i2c.readBytes(self._at24c32_addr, address, 1)


    def write_AT24C32_byte(self, address, value):
        self._i2c.writeBytes(self._at24c32_addr,address,value)
        time.sleep(0.20)
