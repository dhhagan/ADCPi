__all__ = ['ADCPi']

class ADCPi:
	_address = 0x68
	_address2 = 0x69
	_config1 = 0x1C
	_currentchannel1 = 1
	_config2 = 0x1C
	_currentchannel2 = 1
	_bitrate = 18
	_pga = float(0.5)
	_lsb = 7.8125e-6

	# create a byte array and fill it with initial values to define the size
	_adcreading = bytearray()
	_adcreading.append(0x00)
	_adcreading.append(0x00)
	_adcreading.append(0x00)
	_adcreading.append(0x00)

	global _bus

	# local methods
	def _updatebyte(self, byte, bit, value):
		'''
			Internal method for setting the value of a single bit within a byte
		'''
		if value == 0:
			return byte & ~(1 << bit)
		elif value == 1:
			return byte | (1 << bit)

	def _checkbit(self, byte, bit):
		bitval = ((byte & (1 << bit)) != 0)
		
		return True if (bitval == 1) else False

	def _twos_comp(self, val, bits):
		if ((val & (1 << (bits - 1))) != 0):
			val = val - (1 << bits)
		return val

	def _setchannel(self, channel):
        ''' internal method for updating the config to the selected channel '''
        if channel < 5:
            if channel != self._currentchannel1:
                if channel == 1:
                    self._config1 = self._updatebyte(self._config1, 5, 0)
                    self._config1 = self._updatebyte(self._config1, 6, 0)
                    self._currentchannel1 = 1
                if channel == 2:
                    self._config1 = self._updatebyte(self._config1, 5, 1)
                    self._config1 = self._updatebyte(self._config1, 6, 0)
                    self._currentchannel1 = 2
                if channel == 3:
                    self._config1 = self._updatebyte(self._config1, 5, 0)
                    self._config1 = self._updatebyte(self._config1, 6, 1)
                    self._currentchannel1 = 3
                if channel == 4:
                    self._config1 = self._updatebyte(self._config1, 5, 1)
                    self._config1 = self._updatebyte(self._config1, 6, 1)
                    self._currentchannel1 = 4
        else:
            if channel != self._currentchannel2:
                if channel == 5:
                    self._config2 = self._updatebyte(self._config2, 5, 0)
                    self._config2 = self._updatebyte(self._config2, 6, 0)
                    self._currentchannel2 = 5
                if channel == 6:
                    self._config2 = self._updatebyte(self._config2, 5, 1)
                    self._config2 = self._updatebyte(self._config2, 6, 0)
                    self._currentchannel2 = 6
                if channel == 7:
                    self._config2 = self._updatebyte(self._config2, 5, 0)
                    self._config2 = self._updatebyte(self._config2, 6, 1)
                    self._currentchannel2 = 7
                if channel == 8:
                    self._config2 = self._updatebyte(self._config2, 5, 1)
                    self._config2 = self._updatebyte(self._config2, 6, 1)
                    self._currentchannel2 = 8
        return

    # init object with i2caddress, default is 0x68, 0x69 for ADCoPi board
    def __init__(self, bus, address=0x68, address2=0x69, rate=18):
        self._bus = bus
        self._address = address
        self._address2 = address2
        self.setBitRate(rate)

    def read_voltage(self, channel):
        # returns the voltage from the selected adc channel - channels 1 to
        # 8
        raw = self.read_raw(channel)
        if (self._signbit):
            return float(0.0)  # returned a negative voltage so return 0
        else:
            voltage = float(
                (raw * (self._lsb / self._pga)) * 2.448579823702253)
            return float(voltage)

    def read_raw(self, channel):
        # reads the raw value from the selected adc channel - channels 1 to 8
        h = 0
        l = 0
        m = 0
        s = 0

        # get the config and i2c address for the selected channel
        self._setchannel(channel)
        if (channel < 5):
            config = self._config1
            address = self._address
        else:
            config = self._config2
            address = self._address2

        # keep reading the adc data until the conversion result is ready
        while True:
            _adcreading = self._bus.read_i2c_block_data(address, config)
            if self._bitrate == 18:
                h = _adcreading[0]
                m = _adcreading[1]
                l = _adcreading[2]
                s = _adcreading[3]
            else:
                h = _adcreading[0]
                m = _adcreading[1]
                s = _adcreading[2]
            if self._checkbit(s, 7) == 0:
                break

        self._signbit = False
        t = 0.0
        # extract the returned bytes and combine in the correct order
        if self._bitrate == 18:
            t = ((h & 0b00000011) << 16) | (m << 8) | l
            self._signbit = bool(self._checkbit(t, 17))
            if self._signbit:
                t = self._updatebyte(t, 17, 0)

        if self._bitrate == 16:
            t = (h << 8) | m
            self._signbit = bool(self._checkbit(t, 15))
            if self._signbit:
                t = self._updatebyte(t, 15, 0)

        if self._bitrate == 14:
            t = ((h & 0b00111111) << 8) | m
            self._signbit = self._checkbit(t, 13)
            if self._signbit:
                t = self._updatebyte(t, 13, 0)

        if self._bitrate == 12:
            t = ((h & 0b00001111) << 8) | m
            self._signbit = self._checkbit(t, 11)
            if self._signbit:
                t = self._updatebyte(t, 11, 0)

        return t

    def set_pga(self, gain):
        """
        PGA gain selection
        1 = 1x
        2 = 2x
        4 = 4x
        8 = 8x
        """

        if gain == 1:
            self._config1 = self._updatebyte(self._config1, 0, 0)
            self._config1 = self._updatebyte(self._config1, 1, 0)
            self._config2 = self._updatebyte(self._config2, 0, 0)
            self._config2 = self._updatebyte(self._config2, 1, 0)
            self._pga = 0.5
        if gain == 2:
            self._config1 = self._updatebyte(self._config1, 0, 1)
            self._config1 = self._updatebyte(self._config1, 1, 0)
            self._config2 = self._updatebyte(self._config2, 0, 1)
            self._config2 = self._updatebyte(self._config2, 1, 0)
            self._pga = 1
        if gain == 4:
            self._config1 = self._updatebyte(self._config1, 0, 0)
            self._config1 = self._updatebyte(self._config1, 1, 1)
            self._config2 = self._updatebyte(self._config2, 0, 0)
            self._config2 = self._updatebyte(self._config2, 1, 1)
            self._pga = 2
        if gain == 8:
            self._config1 = self._updatebyte(self._config1, 0, 1)
            self._config1 = self._updatebyte(self._config1, 1, 1)
            self._config2 = self._updatebyte(self._config2, 0, 1)
            self._config2 = self._updatebyte(self._config2, 1, 1)
            self._pga = 4

        self._bus.write_byte(self._address, self._config1)
        self._bus.write_byte(self._address2, self._config2)
        return

    def setBitRate(self, rate):
        """
        sample rate and resolution
        12 = 12 bit (240SPS max)
        14 = 14 bit (60SPS max)
        16 = 16 bit (15SPS max)
        18 = 18 bit (3.75SPS max)
        """

        if rate == 12:
            self._config1 = self._updatebyte(self._config1, 2, 0)
            self._config1 = self._updatebyte(self._config1, 3, 0)
            self._config2 = self._updatebyte(self._config2, 2, 0)
            self._config2 = self._updatebyte(self._config2, 3, 0)
            self._bitrate = 12
            self._lsb = 0.0005
        if rate == 14:
            self._config1 = self._updatebyte(self._config1, 2, 1)
            self._config1 = self._updatebyte(self._config1, 3, 0)
            self._config2 = self._updatebyte(self._config2, 2, 1)
            self._config2 = self._updatebyte(self._config2, 3, 0)
            self._bitrate = 14
            self._lsb = 0.000125
        if rate == 16:
            self._config1 = self._updatebyte(self._config1, 2, 0)
            self._config1 = self._updatebyte(self._config1, 3, 1)
            self._config2 = self._updatebyte(self._config2, 2, 0)
            self._config2 = self._updatebyte(self._config2, 3, 1)
            self._bitrate = 16
            self._lsb = 0.00003125
        if rate == 18:
            self._config1 = self._updatebyte(self._config1, 2, 1)
            self._config1 = self._updatebyte(self._config1, 3, 1)
            self._config2 = self._updatebyte(self._config2, 2, 1)
            self._config2 = self._updatebyte(self._config2, 3, 1)
            self._bitrate = 18
            self._lsb = 0.0000078125

        self._bus.write_byte(self._address, self._config1)
        self._bus.write_byte(self._address2, self._config2)
        return