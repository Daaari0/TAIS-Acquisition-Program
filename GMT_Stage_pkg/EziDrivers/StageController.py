# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 14:33:47 2025

@author: Dario
"""
# GMT_Stage_pkg/EziDrivers/StageController.py

import time
from decimal import Decimal, ROUND_HALF_UP
from .EziServoPlusR import EziServoPlusR


class StageFullController:
    def __init__(self, com_port, device_x=0, device_z=1, pulse_per_rev=10):
        self.device_x = device_x
        self.device_z = device_z
        self.pulse_per_rev = pulse_per_rev
        self.stage = EziServoPlusR(com_port)
        self.stage.connect()
        self._configure_stage()

    def _configure_stage(self):
        # Set pulse per revolution
        self.stage.setParameter(self.device_x, paramIndex=0, paramValue=self.pulse_per_rev)
        self.stage.setParameter(self.device_z, paramIndex=0, paramValue=self.pulse_per_rev)

        # Enable encoder direction tracking
        self.stage.setParameter(self.device_x, paramIndex=29, paramValue=1)
        self.stage.setParameter(self.device_z, paramIndex=29, paramValue=1)

    def initialize(self, move_speed=100000):
        # Define origin at lower limit
        self.stage.setOriginAtLowerLimit(self.device_x, move_speed)
        self.stage.setOriginAtLowerLimit(self.device_z, move_speed)

        # Move to origin
        self.stage.moveToOrigin(self.device_x)
        self.stage.moveToOrigin(self.device_z)

        # Move to upper limit and record max positions, convert them in millimiters
        self.stage.moveToLimit(self.device_x, move_speed, 1)
        upper_x = self.stage.getCommandPosition(self.device_x)
        upper_x_mm = self.pulses_to_mm(upper_x)

        self.stage.moveToLimit(self.device_z, move_speed, 1)
        upper_z = self.stage.getCommandPosition(self.device_z)
        upper_z_mm = self.pulses_to_mm(upper_z)


        return upper_x_mm, upper_z_mm

    def move_axis(self, axis, mm, speed):
        pulses = self.mm_to_pulses(mm)
        self.stage.moveToPosition(axis, pulses, speed)

    def move_axes(self, x_mm, z_mm, speed):
        x_pulses = self.mm_to_pulses(x_mm)
        z_pulses = self.mm_to_pulses(z_mm)
        self.stage.moveToPosition(self.device_x, x_pulses, speed)
        self.stage.moveToPosition(self.device_z, z_pulses, speed)

    def get_position_mm(self, axis):
        pulses = self.stage.getCommandPosition(axis)
        return pulses, self.pulses_to_mm(pulses)

    @staticmethod
    def pulses_to_mm(pulses):
        mm = pulses / 1e4
        return float(Decimal(str(mm)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP))

    @staticmethod
    def mm_to_pulses(mm):
        pulses = mm * 1e4
        return int(Decimal(pulses).to_integral_value(rounding=ROUND_HALF_UP))

    def close(self):
        self.stage.close()


if __name__ == '__main__':
    pass