# -*- coding: utf-8 -*-
"""
Created on Thu Nov 27 15:29:45 2025

@author: dario
"""
# Acquire_RnS_scope.py

# Scope class and higher-level function
from RnS_scope_pkg.RnS_Oscilloscope import RnS_Oscilloscope
from RnS_scope_pkg.RnS_manager import initialization, run_acquisition

# Utils
from Utilities_pkg.filetools import save_data_csv, select_folder
from Utilities_pkg.input_manager import ask_User


if __name__ == '__main__':
    import numpy as np

    def main():
        # Variables here
        display_status = 'ON'
        signal_channel = 'CHAN1'
        trigger_channel = 'CHAN3'
        LASER_REPETITION_RATE_Hz = 10e+3  # important to estimate the time of acquisition
        BANDWIDTH_MHz = 20  # Valid options: '20', '50', '100', '200', '350', 'FULL'
        ACQ_MODE = 'AVER'   # Valid options: SAMPle | PDETect | ENVelope | AVERage, thogh sample doesnt work
        NUM_AVERAGE = int(1e+5)  # how many signals to average, regardeless if segmentation is ON
        VOLTS_per_DIV = 1e-3
        TIME_DIV = 3e-6  # in seconds
        OFFSET_VOLTS = 197e-3  # if manual settings is used
        TRIGGER_LEVEL = -1.3e-3  # trigger level in volts

        isSEGM_RUN = True if NUM_AVERAGE >= 10000 else False  # better FALSE for num_average less than 10k

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
                                                            signal_channel, NUM_AVERAGE,
                                                            pump_status='ON',
                                                            probe_status='ON')

        settings['(num_cycles, segments_per_cycle)'] = segmentation_info

        RSscope.plot_waveform(data, time_per_div=TIME_DIV,
                              title=f'Average of {int(NUM_AVERAGE)} Waveforms')
        print('Plotted data.')

        RSscope.disconnect()
        return data, acq_info, settings


# %% After running "main", namely the acquisition, saving data

    data, \
        (XStart, XStop, RecordLength, ValuesPerSample), \
        settings = main()

    time_array = np.linspace(XStart, XStop, int(RecordLength))

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
        '(num_cycles, segments_per_cycle)': settings['(num_cycles, segments_per_cycle)'],
        # TODO: add metadata infos
        'sample': 'FMN',
        'solvent': 'H2O',
        'asorbance at 355': '0.1',
        'pump laser': '355',
        'probe laser': '640',
        'comment': 'OD=1 on 640CW, none on 355Hz'
    }

    wantToSave = ask_User('\nDo you want to save the data?')
    if wantToSave:
        print('Please, select the folder through the pop-up window...')
        folder_path = select_folder()
        save_data_csv(data, params, x=time_array, save_time=True, directory=folder_path)

        print('Data saved')