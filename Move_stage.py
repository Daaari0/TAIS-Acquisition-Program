# -*- coding: utf-8 -*-
"""
Created on Thu Nov 27 15:12:54 2025

@author: dario
"""

# Move_stage.py

from GMT_Stage_pkg.EziDrivers.StageController import StageFullController

def main():
    com_port = 4
    move_speed = 50000

    try:
        StageController = StageFullController(com_port)
        upper_x, upper_z = StageController.initialize()

        print(f'\nMax positions:')
        print(f' X: {StageController.pulses_to_mm(upper_x)} mm')
        print(f' Z: {StageController.pulses_to_mm(upper_z)} mm')

        while True:
            target_x = float(input('\nTarget position in mm for x axis?\t'))
            StageController.move_axis(StageController.device_x, target_x, move_speed)
            x_pulses, x_mm = StageController.get_position_mm(StageController.device_x)
            print(f'x position: {x_pulses} pulses = {x_mm} mm')
    
            target_z = float(input('\nTarget position in mm for z axis?\t'))
            StageController.move_axis(StageController.device_z, target_z, move_speed)
            z_pulses, z_mm = StageController.get_position_mm(StageController.device_z)
            print(f'z position: {z_pulses} pulses = {z_mm} mm')

        '''or just
        StageController.move_axes(target_x, target_z, move_speed)
        '''

    except KeyboardInterrupt:
        print("\nInterrupted by user.\n")
    finally:
        StageController.close()
        print("\nStage disconnected.\n")


if __name__ == '__main__':
    main()