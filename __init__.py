
import math
import time

import board
import busio

from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15 import ads1015
from adafruit_ads1x15 import ads1115


ADS1015 = ads1015.ADS1015
ADS1115 = ads1115.ADS1115

P0 = 0
P1 = 1
P2 = 2
P3 = 3


ADDRESS = 0x48

class GasDetection:
 
    LOAD_RESISTANCE = 5

  
    CLEAN_AIR_FACTOR = 9.6

   
    CO_GAS = 0
    H2_GAS = 1
    CH4_GAS = 2
    LPG_GAS = 3
    PROPANE_GAS = 4
    ALCOHOL_GAS = 5
    SMOKE_GAS = 6

  
    CO_CURVE = [2.30775, 0.71569, -0.33539]
    H2_CURVE = [2.30776, 0.71895, -0.33539]
    CH4_CURVE = [2.30987, 0.48693, -0.37459]
    LPG_CURVE = [2.30481, 0.20588, -0.46621]
    PROPANE_CURVE = [2.30366, 0.23203, -0.46202]
    ALCOHOL_CURVE = [2.30704, 0.45752, -0.37398]
    SMOKE_CURVE = [2.30724, 0.53268, -0.44082]

   
    CALIBARAION_SAMPLE_NUMBER = 50
    CALIBRATION_SAMPLE_INTERVAL = 500

    
    READ_SAMPLE_NUMBER = 5
    READ_SAMPLE_INTERVAL = 50

    
    channel = None


    ro = None

    def __init__(self, convertor=ADS1115, pin=P0, address=ADDRESS, ro=None):
       
        i2c = busio.I2C(board.SCL, board.SDA)
        adc = convertor(i2c=i2c, address=address)

        self.channel = AnalogIn(adc, pin)

        if ro:
            self.ro = ro
        else:
            self.ro = self.calibrate()

    def __read(self, number=None, interval=None):
       

        number = number if number else self.READ_SAMPLE_NUMBER
        interval = interval if interval else self.READ_SAMPLE_INTERVAL

        rs = 0

        for _ in range(number):
            rs += self.__calculate_resistance(self.channel.voltage)
            time.sleep(interval / 1000)

        rs = rs / number

        return rs

    def __calculate_resistance(self, voltage, resistance=None):
     


        resistance = resistance if resistance else self.LOAD_RESISTANCE

        return float(resistance * (1023.0 - voltage) / float(voltage))

    def __calculate_percentage(self, ratio, curve):
      
        return math.pow(
            10,
            ((math.log(ratio) - curve[1]) / curve[2]) + curve[0]
        )

    def __calculate_gas_percentage(self, ratio, gas):
      

        if gas == self.CO_GAS:
            ppm = self.__calculate_percentage(ratio, self.CO_CURVE)
        elif gas == self.H2_GAS:
            ppm = self.__calculate_percentage(ratio, self.H2_CURVE)
        elif gas == self.CH4_GAS:
            ppm = self.__calculate_percentage(ratio, self.CH4_CURVE)
        elif gas == self.LPG_GAS:
            ppm = self.__calculate_percentage(ratio, self.LPG_CURVE)
        elif gas == self.PROPANE_GAS:
            ppm = self.__calculate_percentage(ratio, self.PROPANE_CURVE)
        elif gas == self.ALCOHOL_GAS:
            ppm = self.__calculate_percentage(ratio, self.ALCOHOL_CURVE)
        elif gas == self.SMOKE_GAS:
            ppm = self.__calculate_percentage(ratio, self.SMOKE_CURVE)
        else:
            ppm = 0

        return ppm

    def calibrate(self, number=None, interval=None, factor=None):
      

        number = number if number else self.CALIBARAION_SAMPLE_NUMBER
        interval = interval if interval else self.CALIBRATION_SAMPLE_INTERVAL
        factor = factor if factor else self.CLEAN_AIR_FACTOR

        rs = 0

        for _ in range(number):
            rs += self.__calculate_resistance(self.channel.voltage)
            time.sleep(interval / 1000)

        rs = rs / number

        return rs / factor

    def percentage(self):
      
        resistence = self.__read()
        ppm = {}

        ppm[self.CO_GAS] = self.__calculate_gas_percentage(
            resistence / self.ro, self.CO_GAS
        )

        ppm[self.H2_GAS] = self.__calculate_gas_percentage(
            resistence / self.ro, self.H2_GAS
        )

        ppm[self.CH4_GAS] = self.__calculate_gas_percentage(
            resistence / self.ro, self.CH4_GAS
        )

        ppm[self.LPG_GAS] = self.__calculate_gas_percentage(
            resistence / self.ro, self.LPG_GAS)

        ppm[self.PROPANE_GAS] = self.__calculate_gas_percentage(
            resistence / self.ro, self.PROPANE_GAS
        )

        ppm[self.ALCOHOL_GAS] = self.__calculate_gas_percentage(
            resistence / self.ro, self.ALCOHOL_GAS
        )

        ppm[self.SMOKE_GAS] = self.__calculate_gas_percentage(
            resistence / self.ro, self.SMOKE_GAS
        )

        return ppm
