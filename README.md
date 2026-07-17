# TAIS-Acquisition-Program
Python project for automated 2D data acquisition using a Rohde &amp; Schwarz oscilloscope and a GMT linear motorized stage. Includes Python-to-SCPI drivers, mid- and high-level modules to fully automate the scanning routine with continuous data acquisition, saving, shutters management, and an automated vertical offset setting to center the signal.

## Core Features
*   **Automated 2D Mapping:** Coordinates stage movement and oscilloscope capture for bidirectional grid scanning.
*   **Hardware Drivers:** Wraps raw oscilloscope SCPI commands and motor controller pulses into object-oriented Python methods.
*   **Data Acquisition and Storage:** Oscilloscope auto-offset, acquisition and storage as CSV files.

## Project Structure
*   `TAIS_main_v03.4.py`: The primary orchestration script for fully automated grid scanning (2D acquisition).
*   `Acquire_RnS_scope.py`: Utility script for isolated waveform capturing and averaging (e.g., in-cuvette measurements).
*   `Move_stage.py`: Interactive loop utility for manual stage positioning.
*   `RnS_scope_pkg/`: Mid- and high-level functions and driver-wrapper class for the oscilloscope.
*   `GMT_Stage_pkg/`: Core motor controller communication package.
*   `Shutters_pkg/`: Shutters' logic-dedicated package (USB relay).
*   `Utilities_pkg/`: Data saving routines, coordinate mapping, and mathematical helper functions.

## Getting Started

### 1. 2D Acquisition (TAIS_main_v03.4.py)
Before execution, update the configuration dictionaries in the script with the scope parameters, sample metadata, scanning boundaries (`x_bounds`, `z_bounds`), and `step_sizes`. 

Once run, the user interacts with the program through the terminal as follows:
1. Press **ENTER** to initiate the automatic stage axis calibration.
2. Review the calculated grid size and runtime estimate, then confirm or override the ranges.
3. Choose whether to save the data, which launches a graphical window to select the destination folder.
4. Choose whether to capture a preliminary pump-only reference signal at coordinates x,z = 1, 1.
The script then runs the raster scan, logs progress percentages per pixel, and continuously saves CSV files.

### 2. Single Acquisition (Acquire_RnS_scope.py)
Before execution, define the channel mapping, target trigger thresholds, bandwidth limits, and total waveform averaging counts directly inside the script variables. 

When run, the workflow proceeds as follows:
1. The script initializes the instrument settings and executes the single-point data capture.
2. A graphical window automatically renders a plot of the final averaged voltage vs time trace.
3. The terminal prompts the user to confirm whether to save the data.
4. Upon validation, a directory window pops up to save the time-voltage curve and metadata into a CSV file.

### 3. Manual Stage Positioning (Move_stage.py)
Before execution, verify that the `com_port` variable matches the physical serial port allocation of the motor controller hardware.

When run, the interactive terminal sequence follows this loop:
1. The stage runs an automated homing cycle and prints out the maximum axis boundaries.
2. The terminal prompts the user to type a numerical millimeter value for the X axis, then moves the stage.
3. The terminal prompts the user to type a numerical millimeter value for the Z axis, then moves the stage.
This positioning loop repeats indefinitely until the user manually terminates the script in the console.
