# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 18:45:23 2026

@author: dario
"""

# Code\RnS_scope_pkg\autosave.py

import os
from datetime import datetime


def should_autosave(cycle, num_cycles, num_cycles_treshold=10, min_cycle_gap=10):
    if num_cycles <= num_cycles_treshold:  # autosaves only for acq longer than num_cycles_treshold cycles
        return False

    # min_cycle_gap = 10 # waits at least min_cycle_gap cycles to autosave
    percent_step = max(int(0.1 * num_cycles), min_cycle_gap)

    return (cycle + 1) % percent_step == 0  # return true for met requirments


def autosave_backup(x, data, params, filename="autosaved_backup", directory=".", reference=False):
    full_path = os.path.join(directory, filename)

    if len(x) != len(data):
        raise ValueError("time and signal must have the same length")

    with open(full_path, "w") as f:
        # parameters
        for key, value in params.items():
            f.write(f"{key} = {value}\n")
        f.write("\n")
        # wirte data
        f.write("Time (s), Signal(V)\n")
        for xi, yi in zip(x, data):
            f.write(f"{xi}, {yi}\n")

    print('\n Backup autosaved\n')
    return full_path


def get_daily_autosave_filename():
    date_str = datetime.now().strftime("%Y%m%d")
    return f"{date_str}_running_avg_autosave.csv"
