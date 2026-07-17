# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 20:08:44 2025

@author: Dario
"""
# .\Utilities_package\filetools.py

import os
from datetime import datetime
import csv
import numpy as np
import tkinter as tk
from tkinter import filedialog


def select_folder():
    # Initialize the Tkinter root and hide the root window
    root = tk.Tk()
    root.withdraw()

    # Ask the user to select a folder
    folder_selected = filedialog.askdirectory(title="Select Folder to Save File")

    # Optional: show the selected folder (for debugging)
    print(f"Folder selected: {folder_selected}")

    return folder_selected


def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[
                                           ("CSV files", "*.csv"), ("All files", "*.*")])
    return file_path


def save_data_csv(data, params, x=None, save_time=False, directory=".", reference=False):
    date_str = datetime.now().strftime("%Y%m%d")
    base_name = f"TAISref_{date_str}_" if reference else f"TAISdata_{date_str}_"

    counter = 0
    while True:
        filename = f"{base_name}{counter:04d}.csv"
        full_path = os.path.join(directory, filename)
        if not os.path.exists(full_path):
            break
        counter += 1

    if save_time:
        if x is None:
            raise ValueError("x must be provided when save_time=True")
        if len(x) != len(data):
            raise ValueError("time and signal must have the same length")

    with open(full_path, "w") as f:
        for key, value in params.items():
            f.write(f"{key} = {value}\n")

        f.write("\n")

        if save_time:
            f.write("Time (s), Signal(V)\n")
            for xi, yi in zip(x, data):
                f.write(f"{xi}, {yi}\n")
        else:
            f.write("Signal (V)\n")
            for value in data:
                f.write(f"{value}\n")

    return full_path