# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 15:04:41 2025

@author: Dario

-same version of the 8.v03 of RnS scope folder, but with shutters enabled
"""
# RnS_scope_pkg\RnS_manager.py

import time
import math
import numpy as np
from pathlib import Path
from datetime import datetime

from RnS_scope_pkg.autosave import should_autosave, autosave_backup, get_daily_autosave_filename

from Utilities_pkg.input_manager import ask_User
from Utilities_pkg.filetools import select_folder, save_data_csv

from Shutters_pkg.shutters_control import shutter


def wait_until_previous_operation_done(scope):
    #FIXME: should be move to the class # RnS_scope_pkg\RnS_Oscilloscope.py for architeture consistency
    """ p1500 SCPI manual
    Query OPC status in the event status register
    If you activate a time-consuming operation and wait for completion with *OPC?, a time
    out could occur before the operation is finished and you do not receive the returned “1”. 
    In addition, the test program is blocked while waiting with *OPC?. It is not possible
    to process other (not interdependent) commands in the meantime or to communicate
    with other instruments. Thus, for time-consuming operations, you can avoid blocking the communication by
    sending the operation complete command *OPC:
    *CLS
    *OPC
    Afterwards you can poll the operation complete status in the event status register with
    *ESR?. This query returns the content of the event status register and afterwards clears the
    content. 

    *CLS    /   Clear status
    Sets the status byte (STB), the standard event register (ESR) and the EVENt part of
    the QUEStionable and the OPERation registers to zero. The command does not
    alter the mask and transition parts of the registers. It clears the output buffer.
    Usage:     Setting only

    *OPC   /    Operation complete
    Sets bit 0 in the event status register when all preceding commands have been execu
    ted. This bit can be used to initiate a service request. The query writes a "1" into the
    output buffer when all preceding commands have been executed, which is useful for
    command synchronization.

    The ESR is defined in IEEE 488.2. It can be compared with the EVENt part of a SCPI
    register. The event status register can be read out using command *ESR?.
    values: 0 is operation complete
            1 is not used
            2-5 different tupes of erros
            6 is user request
            7 turn on the intrument

            --info on p728  Manual
    """

    #scope.write("*CLS")  # set many flags zero #may hide unrelated errors, better not to use it this way
    scope.write("*OPC")  # arm completion flag
    # wait for acquisition to finish
    while True:
        # loop to check if the *OPC flag changed
        if int(scope.query("*ESR?")) & 1:
            break


# %% Signal and Trigger  settings all-in-one functions


def set_signal_channel_settings(scope,
                                channel='CHAN1',
                                coupling='DC',  # set DC 50 Ohm coupling
                                position_divs=0,
                                bandwidth='B20'):

    scope.set_coupling(channel=channel, coupling=coupling)
    scope.set_vertical_position(channel=channel, position_divs=position_divs)
    scope.set_bandwidth(channel=channel, bandwidth=bandwidth)


def set_trigger_settings(scope,
                         channel='CHAN3',
                         volts_per_div=1e-3,  # millivolts is a resoanable scale
                         offset_volts=-3e-3,
                         position_divs=0,
                         bandwidth='B20',
                         coupling='DC',  # set DC 50 Ohm coupling
                         level=-1.6e-3,
                         mode='SING',
                         trg_type='EDGE',
                         edge='NEG'):

    scope.set_vertical_scale(channel=channel, volts_per_div=volts_per_div)
    scope.set_vertical_offset(channel=channel, offset_volts=offset_volts)
    scope.set_vertical_position(channel=channel, position_divs=position_divs)
    scope.set_bandwidth(channel=channel, bandwidth=bandwidth)
    scope.set_coupling(channel=channel, coupling=coupling)
    scope.set_trigger(level=level, mode=mode, trg_type=trg_type, source=channel, edge=edge)


# %% Initialization Oscilloscope settings all-in-one

def initialization(scope, settings):
    # valid options: OFF | ON (off makes it faster)
    scope.set_remote_display(status=settings["display_status"])
    time.sleep(0.5)

    # Setup - horizontal axis
    scope.set_timescale(time_per_div=settings["TIME_DIV"])  # in milliseconds
    scope.set_reference_point(channel=settings["signal_channel"], percentage=10)

    # set Trigger
    set_trigger_settings(scope,
                         channel=settings["trigger_channel"],
                         volts_per_div=1e-3,
                         offset_volts=-3e-3,
                         position_divs=0,
                         bandwidth='B'+str(settings["BANDWIDTH_MHz"]),
                         coupling='DC',
                         level=settings["TRIGGER_LEVEL"],
                         mode='SING',
                         trg_type='EDGE',
                         edge='NEG'
                         )

    # Setup - vertical axis
    set_signal_channel_settings(scope,
                                channel=settings["signal_channel"],
                                coupling='DC',
                                position_divs=0,
                                bandwidth='B'+str(settings["BANDWIDTH_MHz"])
                                )

    # Dynamic offset setting - no need in initialization, only before measuring
    # set the desired small scale
    scope.set_vertical_scale(channel=settings["signal_channel"],
                             volts_per_div=settings["VOLTS_per_DIV"])

    # Acquisition setup
    # must be AVER for segmentation to take the average of segments too
    scope.set_acquisition_mode(settings["ACQ_MODE"])

    # set auto record with max at 10kpts
    scope.set_record_length(mode='AUTO', maximumRL=10e+3)

    # set manual record length - won't be used in my case
    # scope.set_record_length(samples_per_waveform=10e+3, mode='MAN')

    scope.set_sample_rate(mode='AUTO', minimum_sr=10e+6)
    scope.set_averaging_count(count=settings["NUM_AVERAGE"])

    if settings["isSEGM_RUN"]:
        # Segments is the number of average signals during segmentaiton or MAX for the maximum available
        # set fast segmentation if segments on 'MAX'
        # Note: if fast segmentation is ON, then you should run SINGLE otherwise it wont segment
        NUM_AVERAGE = settings["NUM_AVERAGE"]
        SEGMENTS = 'MAX' if NUM_AVERAGE >= 10000 else NUM_AVERAGE

        scope.enable_segmented_memory(segments=SEGMENTS, status='ON')

        # Show history panel, which is needed to average the segments (signals)
        _ = scope.show_history(state='ON')
        # not interested in the return, it's the time the display show each segment on screen
    else:
        scope.enable_segmented_memory(status='OFF')

    # High definition mode
    scope.set_HD_acquisition(bandwidth_Hz=10, status='OFF')

    # Dead time to ensure all parameters are set
    time.sleep(1)

# %% RUN ACQUISITION - handles both type of average acquisition, even segments >10k


def run_acquisition(scope,
                    VOLTS_per_DIV,
                    isSEGM_RUN,
                    LASER_REPETITION_RATE_Hz,
                    signal_channel,
                    NUM_AVERAGE,
                    pump_status='ON',
                    probe_status='ON'):

    # NUM_AVERAGE is the only variable for user input,
    # then SEGMENTS is set to 'MAX' if isSEGM_RUN is ON and NUM_AVERAGE is 10k or more

    SEGMENTS = 'MAX' if NUM_AVERAGE >= 10000 else NUM_AVERAGE

    if isSEGM_RUN:
        segments_per_cycle = 10000 if SEGMENTS == 'MAX' else SEGMENTS
        num_cycles = math.ceil(NUM_AVERAGE / segments_per_cycle)

        if num_cycles > 1:
            print(f"Segmentation ON → {segments_per_cycle} segments per cycle")
            print(f"User requested {NUM_AVERAGE} averages → running {num_cycles} cycles")

        running_avg = None
        acq_info = None

        # Creating the Autosave Folder, any PC bulletproof
        autosave_folder = Path.home() / ".RnS_scope_autosave"
        # on windows the folder will be created in C:\Users\<YOUR_USERNAME>\.RnS_scope_autosave
        autosave_folder.mkdir(exist_ok=True)  # checks if already exist, if so, nothing changed

        for cycle in range(num_cycles):

            # Switching ON both shutters at every cycle
            shutter('pump', pump_status)
            shutter('probe', probe_status)

            # Auto offset before each cycle #in theory no needed each cycle, but it is safer
            scope.auto_vertical_offset(channel=signal_channel, target_scale=VOLTS_per_DIV,
                                       settle_time=0.2, verbose=False)  # works with data in scope's RAM

            if num_cycles > 1:
                print(f"\n--- Cycle {cycle+1}/{num_cycles} ---")

            scope.control_acquisition(mode='SINGLE')

            scope.wait_acquisition_completion(
                expected_waveforms=segments_per_cycle,
                laser_repetition_rate_hz=LASER_REPETITION_RATE_Hz,
                buffer_ratio=5
            )

            scope.history_play()
            # wait_until_previous_operation_done(scope) #this replace the hardcoded wait

            # Switching OFF both shutters after acquisition, during history averaging
            shutter('pump', 'off')
            shutter('probe', 'off')

            # here was the hardcoded wait before
            wait_until_previous_operation_done(scope)  # this replace the hardcoded wait

            data, acq_info = scope.fetch_waveform(channel=signal_channel)
            wait_until_previous_operation_done(scope)  # to play extra safe

            data = np.array(data)

            # Update average with last acquisition
            if running_avg is None:
                running_avg = data.astype(float)
            else:
                running_avg += (data - running_avg) / (cycle + 1)

            # Safety feature: autosave before all cycles are acquried
            if should_autosave(cycle, num_cycles, num_cycles_treshold=5, min_cycle_gap=2):

                filename = get_daily_autosave_filename()

                XStart,  XStop, RecordLength, ValuesPerSample = acq_info
                time_array = np.linspace(XStart, XStop, int(RecordLength))

                autosave_backup(
                    time_array,
                    running_avg,
                    # just main parameters, not all of them
                    params={
                        "XStart": XStart,
                        "XStop": XStop,
                        "RecordLength": int(RecordLength),
                        "ValuesPerSample": ValuesPerSample,

                        "VOLTS_per_DIV": VOLTS_per_DIV,
                        "LASER_REPETITION_RATE_Hz": LASER_REPETITION_RATE_Hz,

                        "TOTAL AVERAGE COUNT": NUM_AVERAGE,
                        "cycle of 10'000 signals": cycle + 1,
                        "total cycles": num_cycles,
                        "timestamp": datetime.now().isoformat(),
                    },
                    directory=autosave_folder,
                    filename=filename,
                )

        print("\nDone with all segmentation cycles.")
        return running_avg, acq_info, (num_cycles, segments_per_cycle)

    # %% non-segmentation
    else:
        # Switching ON both shutters at the start of acquisition
        shutter('pump', pump_status)
        shutter('probe', probe_status)

        # Auto offset before each cycle #in theory no needed each cycle, but it is safer
        scope.auto_vertical_offset(channel=signal_channel, target_scale=VOLTS_per_DIV,
                                   settle_time=0.2, verbose=False)  # works with data in scope's RAM

        scope.control_acquisition(mode='RUN')

        try:
            if NUM_AVERAGE > 1:
                acquisition_done = scope.wait_acquisition_completion(
                    expected_waveforms=NUM_AVERAGE,
                    laser_repetition_rate_hz=LASER_REPETITION_RATE_Hz,
                    buffer_ratio=5)

                if acquisition_done:
                    data, acq_info = scope.fetch_waveform()
                    wait_until_previous_operation_done(scope)  # to play extra safe
                else:
                    print("Check: \n\tOscilloscope History \n\tPump-Laser shutter "
                          "\n\tTrigger settings \n\tTrigger-Photodiode status")
                    data, acq_info = None, None

            else:
                time.sleep(0.5)
                data, acq_info = scope.fetch_waveform(channel=signal_channel)
                wait_until_previous_operation_done(scope)  # to play extra safe

        finally:
            # Shutter OFF at the end, even if exceptions occur
            shutter('pump', 'off')
            shutter('probe', 'off')

            scope.control_acquisition(mode='STOP')

        return data, acq_info, None


# %% Main code flow
if __name__ == '__main__':

    def main():
        from RnS_Oscilloscope import RnS_Oscilloscope

        # Variables here
        display_status = 'ON'
        signal_channel = 'CHAN1'
        trigger_channel = 'CHAN3'
        LASER_REPETITION_RATE_Hz = 1e+3  # important to estimate the time of acquisition
        BANDWIDTH_MHz = 20  # Valid options: '20', '50', '100', '200', '350', 'FULL'
        ACQ_MODE = 'AVER'   # Valid options: SAMPle | PDETect | ENVelope | AVERage, thogh sample doesnt work
        NUM_AVERAGE = int(1e+3)  # how many signals to average, regardeless if segmentation is ON
        VOLTS_per_DIV = 1e-3
        TIME_DIV = 5e-6  # in seconds
        OFFSET_VOLTS = 197e-3  # if manual settings is used
        TRIGGER_LEVEL = -1.6e-3  # trigger level in volts
        isSEGM_RUN = True

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
            "(num_cycles, segments_per_cycle)": tuple
        }

        # Connect
        RSscope = RnS_Oscilloscope(
            'USB0::0x0AAD::0x0197::1335.5050k04-200414::INSTR')

        # Initialization parameters and channels settings
        initialization(RSscope, settings)

        # Acquisition
        print('\nMeasuring...')
        data, acq_info, segmentation_info = run_acquisition(RSscope, VOLTS_per_DIV,
                                                            isSEGM_RUN,
                                                            LASER_REPETITION_RATE_Hz,
                                                            signal_channel, NUM_AVERAGE)

        settings['(num_cycles, segments_per_cycle)'] = segmentation_info

        RSscope.plot_waveform(data, time_per_div=TIME_DIV,
                              title=f'Average of {int(NUM_AVERAGE)} Waveforms')
        print('Plotted data.')

        RSscope.disconnect()
        return data, acq_info, settings


# %% main execution
    try:
        data, \
            (XStart, XStop, RecordLength, ValuesPerSample), \
            settings = main()

        params = {
            "XStart": XStart,
            "XStop": XStop,
            "RecordLength": int(RecordLength),
            "ValuesPerSample": ValuesPerSample,
            "LASER_REPETITION_RATE_Hz": settings['LASER_REPETITION_RATE_Hz'],
            "BANDWIDTH_MHz": settings["BANDWIDTH_MHz"],
            "ACQ_MODE": settings['ACQ_MODE'],
            "AVERAGE COUNT": settings['NUM_AVERAGE'],
            "VOLTS_per_DIV": settings['VOLTS_per_DIV'],
            "TIME_DIV": settings['TIME_DIV'],
            "OFFSET_VOLTS": settings['OFFSET_VOLTS'],
            "TRIGGER_LEVEL": settings['TRIGGER_LEVEL'],
            "Segmentation ON": settings['isSEGM_RUN'],
            '(num_cycles, segments_per_cycle)': settings['(num_cycles, segments_per_cycle)']
        }

        wantToSave = ask_User('\nDo you want to save the data?')
        if wantToSave:
            directory = select_folder()
            save_data_csv(data, params, directory=directory)
            print('Data saved')

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user.\n")
    finally:
        print('\n---------------------------')
        # RSscope.disconnect()
        # print("🔌❌  Scope disconnected.")

        print("🛑 Both Shutters Closed.")
        # Reset to safe state
        shutter('pump', 'off')
        shutter('probe', 'off')

        print("\n\t✅ Finished.")