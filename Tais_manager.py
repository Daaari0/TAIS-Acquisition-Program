# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 10:42:23 2025

@author: Dario
"""
# Tais_manager.py

import time
from Shutters_pkg.shutters_control import shutter
from RnS_scope_pkg.RnS_manager import run_acquisition

from RnS_scope_pkg.RnS_scope_drivers.utils.visualization import plot_waveform


def acquire_signal(scope,
                   StageController,
                   move_speed,
                   settings,
                   wantToSave=False,
                   folder_path=None,
                   stage_XZ=(7, 14),
                   reference=False,
                   plot_verbose=True
                   ):
    signal_channel = settings["signal_channel"]
    LASER_REPETITION_RATE_Hz = settings["LASER_REPETITION_RATE_Hz"]
    NUM_AVERAGE = settings["NUM_AVERAGE"]
    VOLTS_per_DIV = settings["VOLTS_per_DIV"]
    TIME_DIV = settings["TIME_DIV"]
    isSEGM_RUN = settings["isSEGM_RUN"]
    target_x, target_z = stage_XZ

    if reference:
        pump_status = 'ON'
        probe_status = 'OFF'
        plot_title = f'REF\nAverage of {int(NUM_AVERAGE)} Waveforms'
        data_type = 'reference'

    else:
        pump_status, probe_status = 'ON', 'ON'
        plot_title = f'Average of {int(NUM_AVERAGE)} Waveforms'
        data_type = 'signal'

    # MOVING STAGE
    StageController.move_axes(target_x, target_z, move_speed)
    print(f'📍  Current position: ({target_x}, {target_z}) ')
    shutter('pump', pump_status)
    shutter('probe', probe_status)

    time.sleep(0.1)  # wait for stage stabilization and opening shutter

    # ACQUISITION
    print('🔍 Autoffset...')
    # TODO: auto offest done in run acquisition to avoid opnening and closing the shutters only for that in cycles acq
    '''scope.auto_vertical_offset(channel=signal_channel, target_scale=VOLTS_per_DIV,
                               settle_time=0.2, verbose=False)# 200 * 1/LASER_REPETITION_RATE_Hz, verbose=False)'''

    print('\n⏳ Measuring...')
    data, acq_info, segmentation_info = run_acquisition(scope,
                                                        VOLTS_per_DIV,
                                                        isSEGM_RUN,
                                                        LASER_REPETITION_RATE_Hz,
                                                        signal_channel,
                                                        NUM_AVERAGE,
                                                        pump_status=pump_status,
                                                        probe_status=probe_status)

    settings['(num_cycles, segments_per_cycle)'] = segmentation_info

    print(f'\t {data_type} acquired.')
    if plot_verbose:
        plot_waveform(data, time_per_div=TIME_DIV, title=plot_title)
        print('📊 Plotted {data_type} data.')

    return data, acq_info, settings