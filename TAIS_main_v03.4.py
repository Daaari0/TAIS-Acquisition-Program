# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 10:45:50 2025

@author: Dario
"""
# TAIS_main_v03.4.py

from decimal import Decimal, ROUND_HALF_UP
from GMT_Stage_pkg.EziDrivers.StageController import StageFullController

# Scope class and higher level function
from RnS_scope_pkg.RnS_Oscilloscope import RnS_Oscilloscope
from RnS_scope_pkg.RnS_manager import initialization

# Shutter controller
from Shutters_pkg.shutters_control import shutter
# Acquisition logic
from Tais_manager import acquire_signal

# Utils
from Utilities_pkg.input_manager import ask_User, set_stage_coordinates
from Utilities_pkg.math_functions import (stage_grid_size,
                                          format_duration,
                                          decimal_range,
                                          expected_time)
from Utilities_pkg.filetools import select_folder, save_data_csv
from Utilities_pkg.utils import preprocess_parameters


Scope = None
StageController = None


def main():
    # %% == SETTINGS SCOPE ==
    display_status = 'ON'  # Decide whether or not see the display in remote, it makes it slower, ON | OFF
    signal_channel = 'CHAN1'
    trigger_channel = 'CHAN3'
    LASER_REPETITION_RATE_Hz = 10e+3  # important to estimate the time of acquisition
    BANDWIDTH_MHz = 20  # Valid options: '20', '50', '100', '200', '350', 'FULL'
    ACQ_MODE = 'AVER'   # Valid options: SAMPle | PDETect | ENVelope | AVERage, thogh sample doesnt work
    NUM_AVERAGE = int(10e+3)  # for 'RUN' acq, namely no segmentation
    VOLTS_per_DIV = 1e-3
    TIME_DIV = 10e-6  # 5e-6 is 5µs/div
    OFFSET_VOLTS = 197e-3  # if manual settings is used
    TRIGGER_LEVEL = -1.6e-3  # trigger level in volts
    
    isSEGM_RUN = True if NUM_AVERAGE >= 10000 else False  # better FALSE for num_average less than 10k

    # TODO: add metadata infos
    experiment_info ={
        'sample': 'FMN',
        'solvent': 'H2O',
        'asorbance at 473': '0.0005',
        'pump laser': '473',
        'probe laser': '640',
        'comment': 'OD=1 on 640CW, none on 473Hz'
        }

    # %% === User-defined scan bounds ===

    x_bounds = [6, 8.5]
    z_bounds = [5.5, 14]
    step_sizes = [0.5, 0.5]  # x and z

    # %%  STAGE INIT
    com_port = 4  # 4 for picoQ, 3 my PC
    move_speed = 50000

    settings = {
        "display_status": display_status,
        "signal_channel": signal_channel,
        "trigger_channel": trigger_channel,
        "LASER_REPETITION_RATE_Hz": LASER_REPETITION_RATE_Hz,
        "BANDWIDTH_MHz": BANDWIDTH_MHz,
        "ACQ_MODE": ACQ_MODE,
        "NUM_AVERAGE": NUM_AVERAGE,
        "VOLTS_per_DIV": VOLTS_per_DIV,
        "TIME_DIV": TIME_DIV,
        "OFFSET_VOLTS": OFFSET_VOLTS,
        "TRIGGER_LEVEL": TRIGGER_LEVEL,
        "isSEGM_RUN": isSEGM_RUN,
    }

    print('\n🛠 Stage initialization...')
    StageController = StageFullController(com_port)

    input('\n Press ENTER to start stage calibration - ⚠️ Stage will move!')
    print('🚧 Stage moving...')
    upper_x, upper_z = StageController.initialize()

    print('\nThe stage upper limits are:\n' +
          f'\t\t ↔️X={upper_x} mm\n' +
          f'\t\t ↕️Z={upper_z} mm')

    print('\nMake sure the defined upper bounds are within the limits')

    # === Double Check scan bounds while running ===
    check = False
    while not check:
        print('\nStage ranges are:\n' +
              f'x = {x_bounds}\n' +
              f'z = {z_bounds}\n' +
              f'steps = {step_sizes}\n')

        print('Which corresponds to:')
        points_x, points_z, points_total = stage_grid_size(x_bounds, z_bounds, step_sizes)
        print(f"\n{points_x} x {points_z} = {points_total} pixels")

        acq_time = expected_time(points_total, NUM_AVERAGE, LASER_REPETITION_RATE_Hz)
        print(f'It will take at least {format_duration(acq_time)} ')
        check = ask_User('\n Happy with the ranges?')
        if not check:
            x_bounds, z_bounds, step_sizes = set_stage_coordinates()

    # %% SCOPE INIT

    # Connect
    scope = RnS_Oscilloscope(
        'USB0::0x0AAD::0x0197::1335.5050k04-200414::INSTR')

    # Initialization parameters and channels settings
    print('🛠 Scope initialization...')
    initialization(scope, settings)

    # %%
    try:
        wantToSave = ask_User('\nDo you want to save all the raw signals?')
        if wantToSave:
            folder_path = select_folder()
        else:
            folder_path = None

        # %% "BASELINE" (pump laser only) acquisition

        YesReference = ask_User(
            '\n Do you want to adcquire a "reference" (only pump laser ON) signal?\n\t')

        if YesReference:
            stage_XZ = (1, 1)

            data, acq_info, settings = acquire_signal(scope,
                                                      StageController,
                                                      move_speed,
                                                      settings,
                                                      wantToSave=wantToSave,
                                                      folder_path=folder_path,
                                                      stage_XZ=stage_XZ,
                                                      reference=YesReference,
                                                      plot_verbose=True
                                                      )
            # Saving Ref
            if wantToSave:
                params = preprocess_parameters(scope,
                                               settings,
                                               acq_info,
                                               data,
                                               folder_path,
                                               stage_XZ
                                               )
                params.update(experiment_info)
                save_data_csv(data, params, directory=folder_path, reference=YesReference)
                print('💾 Ref. data saved.')
        else:
            pass

        # %% ACQUISITION LOOP on stage position
        print('\n🔁📡  Starting loop acquisition...\n')
        points_scanned = 0
        # Generate list of x positions
        x_line = decimal_range(x_bounds[0], x_bounds[1], step_sizes[0])

        for j, z in enumerate(decimal_range(z_bounds[0], z_bounds[1], step_sizes[1])):
            target_z = z

            if j > 0:
                # After first z value, to ensure bidirectional X scan it flips the order each time
                x_line = x_line[::-1]

            for x in x_line:
                target_x = x
                stage_XZ = (target_x, target_z)
                data, acq_info, settings = acquire_signal(scope,
                                                          StageController,
                                                          move_speed,
                                                          settings,
                                                          wantToSave=wantToSave,
                                                          folder_path=folder_path,
                                                          stage_XZ=stage_XZ,
                                                          reference=False,
                                                          plot_verbose=True
                                                          )

                points_scanned += 1
                print(f'\n\t** Scanned {points_scanned/points_total * 100:.1f} % ' +
                      'points so far **\n')

                # Saving Data
                if wantToSave:
                    params = preprocess_parameters(scope,
                                                   settings,
                                                   acq_info,
                                                   data,
                                                   folder_path,
                                                   stage_XZ)

                    save_data_csv(data, params, directory=folder_path)
                    print('💾 Data saved.')

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.\n")
    finally:
        print('\n---------------------------')
        scope.disconnect()
        print("🔌❌  Scope disconnected.")

        StageController.close()
        print("🔌❌  Stage disconnected.")

        print("🛑 Both Shutters Closed.")
        # Reset to safe state
        shutter('pump', 'off')
        shutter('probe', 'off')

        print("\n\t✅ Finished.")


if __name__ == '__main__':
    main()