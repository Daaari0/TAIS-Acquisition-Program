# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 15:01:04 2025

@author: Dario
"""
# \Utilities_pkg\utils.py

def preprocess_parameters(scope,
                          settings,
                          acq_info,
                          data,
                          folder_path,
                          stage_XZ):
    target_x, target_z = stage_XZ

    LASER_REPETITION_RATE_Hz = settings["LASER_REPETITION_RATE_Hz"]
    BANDWIDTH_MHz = settings["BANDWIDTH_MHz"]
    ACQ_MODE = settings["ACQ_MODE"]
    VOLTS_per_DIV = settings["VOLTS_per_DIV"]
    TIME_DIV = settings["TIME_DIV"]
    OFFSET_VOLTS = settings["OFFSET_VOLTS"]
    TRIGGER_LEVEL = settings["TRIGGER_LEVEL"]
    isSEGM_RUN = settings["isSEGM_RUN"]
    average_count = settings['NUM_AVERAGE']
    segmentation_info = settings['(num_cycles, segments_per_cycle)']

    # Settings used in acquisition to be saved on file
    XStart, XStop, RecordLength, ValuesPerSample = acq_info
    params = {
        "timeStart": XStart,
        "timeStop": XStop,
        "RecordLength": int(RecordLength),
        "ValuesPerSample": ValuesPerSample,
        "LASER_REPETITION_RATE_Hz": LASER_REPETITION_RATE_Hz,
        "BANDWIDTH_MHz": BANDWIDTH_MHz,
        "ACQ_MODE": ACQ_MODE,
        "AVERAGE COUNT": average_count,
        "VOLTS_per_DIV": VOLTS_per_DIV,
        "TIME_DIV": TIME_DIV,
        "OFFSET_VOLTS": OFFSET_VOLTS,
        "TRIGGER_LEVEL": TRIGGER_LEVEL,
        "Segmentation ON": isSEGM_RUN,
        '(num_cycles, segments_per_cycle)': segmentation_info,
        "Stage position (x,z)": (target_x, target_z)
    }
    return params