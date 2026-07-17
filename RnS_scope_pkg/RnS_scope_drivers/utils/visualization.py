# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 11:39:43 2025

@author: Dario
"""
# RnS_scope_drivers\utils\visualization.py
import matplotlib.pyplot as plt


def plot_waveform_segmented(samples, time_per_div, num_divs=10, title='Oscilloscope Waveform'):
    """
    Plots waveform data using matplotlib.

    Parameters:
    - samples: list of voltage values
    - time_per_div: horizontal scale in seconds per division
    - num_divs: number of horizontal divisions (default 10)
    - title: plot title
    """
    total_time = time_per_div * num_divs
    time_axis = [i * (total_time / len(samples)) - time_per_div for i in range(len(samples))]

    plt.figure(figsize=(10, 4))
    plt.plot(time_axis, samples, color='blue', linewidth=1)
    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_waveform(samples, time_per_div, title='Oscilloscope Waveform'):
    """
    Plots waveform data using matplotlib.

    Parameters:
    - samples: list of voltage values
    - time_per_div: horizontal scale in seconds per division
    - num_divs: number of horizontal divisions (default 10)
    - title: plot title
    """
    total_time = time_per_div * 10
    time_axis = [i * (total_time / len(samples)) - time_per_div for i in range(len(samples))]

    plt.figure(figsize=(10, 4))
    plt.plot(time_axis, samples, color='blue', linewidth=1)
    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()