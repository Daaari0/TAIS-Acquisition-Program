# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 11:03:47 2025

@author: Dario
"""

# RnS_scope_pkg.RnS_scope_drivers\controls\vertical_setup.py

from RnS_scope_pkg.RnS_scope_drivers.acquisition.acq_control import control_acquisition
import time


# %% VERTICAL SETUP


def set_vertical_scale(scope, channel='CHAN1', volts_per_div=0.05, verbose=True):
    """
    Manually sets the vertical scale for a given channel.

    Parameters:
    - channel: e.g., 'CHAN1'
    - volts_per_div: e.g., 0.5 for 0.5 V/div
    """

    '''CHANnel<ch>:SCALe <Scale>

    Suffix: 
        <ch>     1 to 4, index of the analog channel
    Parameters:
        <Scale> Range: 0.001  to  1
        Increment: 0.001
        *RST: 0.05
        Default unit: Depends on the connected probe'''

    scope.write(f'{channel}:SCALe {volts_per_div}')
    if verbose:
        print(f'Oscilloscope Vertical Scale: {volts_per_div}')

    '''current_scale = scope.query('CHAN1:SCALe?')
    print(f'Current scale: {current_scale}')
    #scope.write('CHAN1:SCALe 0.05')#this works
    scope.write(f'{channel}:SCALe {volts}') #this works
    '''


def set_vertical_offset(scope, channel='CHAN1', offset_volts=0.0):
    """
    Sets vertical offset for a given channel in volts.
    Positive values shift waveform down.
    """
    scope.write(f'{channel}:OFFS {offset_volts}')
    print(f'Oscilloscope Vertical Offset: {offset_volts}')


def set_vertical_position(scope, channel='CHAN1', position_divs=0.0):
    """
    Sets vertical position shift for a given channel in divisions.
    Negative values shift waveform down.

     Moves the selected signal up or down in the diagram. While the offset sets a voltage,
     position is a graphical setting given in divisions. The visual effect is the same as for off
     set.
     Remote command: 
    CHANnel<ch>:POSition 
    """
    scope.write(f'{channel}:POS {position_divs}')
    print(f'Oscilloscope Vertical Position: {position_divs}')


def set_bandwidth(scope, channel='CHAN1', bandwidth='FULL'):
    """
    Sets bandwidth limit for a given channel.
    Valid options: 'B20', 'B50', 'B100', 'B200', 'B350', 'FULL'
    """
    valid_bandwidths = {'B20', 'B50', 'B100', 'B200', 'B350', 'FULL'}
    bw = bandwidth.upper()
    if bw == 'BFULL':
        bw = 'FULL'
    if bw not in valid_bandwidths:
        raise ValueError(f"Invalid bandwidth setting: {bw}")
    scope.write(f'{channel}:BAND {bw}')
    print(f'Oscilloscope Bandwidth: {bw} MHz')


def set_coupling(scope, channel='CHAN1', coupling='DC'):
    '''
    The selected coupling is shown in the signal icon.
     "DC"  Passes both DC and AC components of the signal.
     "AC"  Connection through DC capacitor, removes DC and very low-fre
         quency components. AC coupling is useful if the DC component of a
          signal is of no interest. The waveform is centered on zero volts.

    CHANnel<ch>:COUPling 

    parameters:
        DC -->Connection with 50 Ω termination, passes both DC and AC com
       ponents of the signal.

         DCLimit -->  Connection with 1 MΩ termination, passes both DC and AC
          components of the signal.

         AC --> Connection with 1 MΩ termination through DC capacitor,
          removes DC and very low-frequency components. The wave
         form is centered on zero volts.

    '''
    scope.write(f'{channel}:COUP {coupling}')


# %%AUTO SETTINGS - to be cheked


def autoscale_vertical(scope, channel='CHAN1'):  # doesnt work
    scope.write(f'{channel}:SCAL:AUTO ON')


'''def auto_vertical_offset(scope, channel='CHAN1', scales=None, settle_time=0.2):
    """
    Iteratively centers the waveform by adjusting offset across multiple vertical scales.
    Prevents clipping at finer scales by refining offset progressively.
    """
    if scales is None:
        # Define descending vertical scales in volts/div
        scales = [0.25, 0.1, 0.05, 0.02, 0.005, 0.002, 1e-3, 0.5e-3]  # Adjust based on signal dynamics

    scope.write('FORM ASC')  # Ensure ASCII format for data

    for vdiv in scales:
        set_vertical_scale(scope, channel=channel, volts_per_div=vdiv)
        control_acquisition(scope, mode='RUN')
        time.sleep(settle_time)
        control_acquisition(scope, mode='STOP')

        scope.write(f'{channel}:DATA?')
        data = scope.read()
        samples = [float(x) for x in data.split(',') if x]

        if not samples:
            print(f"No data received at {vdiv:.3f} V/div.")
            continue

        signal_center = sum(samples) / len(samples)
        scope.write(f'{channel}:OFFS {signal_center}')
        print(f"Set offset to {signal_center:.3f} V at {vdiv:.3f} V/div")

    print("✅ Final offset set. Signal should be centered across all scales.")'''


def auto_vertical_offset(scope, channel='CHAN1', target_scale=2e-3, settle_time=0.2, verbose=False):
    """
    Iteratively centers the waveform by adjusting offset across multiple vertical scales.
    Prevents clipping at finer scales by refining offset progressively.
    """
    all_scales = [0.25, 0.1, 0.05, 0.02, 0.005, 0.002, 1e-3, 0.5e-3]

    '''if target_scale is None:
        # Define descending vertical scales in volts/div
        target_scale = 2e-3 # default value'''

    # Filter scales that are >= volts_per_div
    scales = [scale for scale in all_scales if scale >= target_scale]

    scope.write('FORM ASC')  # Ensure ASCII format for data

    for vdiv in scales:
        set_vertical_scale(scope, channel=channel, volts_per_div=vdiv, verbose=verbose)
        control_acquisition(scope, mode='RUN')
        time.sleep(settle_time)
        control_acquisition(scope, mode='STOP')

        scope.write(f'{channel}:DATA?')
        data = scope.read()
        samples = [float(x) for x in data.split(',') if x]

        if not samples:
            print(f"No data received at {vdiv:.3f} V/div.")
            continue

        signal_center = sum(samples) / len(samples)
        scope.write(f'{channel}:OFFS {signal_center}')
        if verbose:
            print(f"Set offset to {signal_center:.3f} V at {vdiv:.3f} V/div")

    print(f"✅ Final offset set at {signal_center:.2e}." +
          f"\n Signal should be centered across vertical axis at {target_scale} V/div.")