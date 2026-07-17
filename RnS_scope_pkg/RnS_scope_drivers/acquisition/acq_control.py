# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 11:02:58 2025

@author: Dario
"""

# RnS_scope_drivers\acquisition\acq_control.py


def control_acquisition(scope, mode='SINGLE'):
    """
    Controls acquisition mode: 'SINGLE', 'RUN', or 'STOP'.
    """
    mode = mode.upper()
    if mode == 'SINGLE':
        scope.write('SING')
    elif mode == 'RUN':
        scope.write('RUN')
    elif mode == 'STOP':
        scope.write('STOP')
    else:
        raise ValueError("Invalid mode. Use 'SINGLE', 'RUN', or 'STOP'.")


def fetch_waveform(scope, channel='CHAN1'):
    import numpy as np
    import time

    scope.write('FORM ASC')  # ASCII format
    # scope.write('CHAN1:DATA:HEAD?')
    scope.write(f'{channel}:DATA:HEAD?')
    header = scope.read()
    XStart, XStop, RecordLength, ValuesPerSample = header.split(',')

    ''' CHANnel<ch>:DATA:HEADer?
        Returns the header of channel waveform data, the attributes of the waveform.
         
        Suffix: 
        <ch> 1 to 4, index of the analog channel
        
         Return values: 
        <XStart> 1. header value: start time XStart in s
        <XStop> 2. header value: end time XStop in s
        <RecordLength> 3. header value: record length of the waveform in samples

         <ValuesPerSample> 4. header value: number of values per sample interval.
         For most waveforms, the result is 1. For peak detect and envelope wave
        forms, it is 2. If the number is 2, the number of returned values is
         twice the number of samples (record length).
         '''

    scope.write(f'{channel}:DATA?')

    data = scope.read()

    return np.array([float(x) for x in data.split(',')]), [float(value) for value in [XStart, XStop, RecordLength, ValuesPerSample]]


def get_current_waveform_count(scope):
    '''
    #     ACQuire:CURRent?
    #  Returns the current number of acquisitions that have been acquired.
      Return values:
     <CurrAcqCnt>  Range:  0  to  18446744073709551615

      Increment: 1

    '''
    scope.write('ACQ:CURR?')
    curr_acq = int(scope.read())
    return curr_acq


def wait_acquisition_completion(scope,
                                expected_waveforms,
                                laser_repetition_rate_hz,
                                poll_interval=0.1,
                                buffer_ratio=2):
    import time
    """
    Waits until the expected number of waveforms have been acquired.

    Parameters:
    - expected_waveforms: total number of waveforms to acquire
    - laser_repetition_rate_hz: laser pulse frequency in Hz
    - poll_interval: time between checks (seconds)
    - buffer_ratio: extra time buffer (default 200%, it waits until 3 times what should be necesary)

    Returns:
    - True if acquisition completed
    - False if timeout occurred
    """
    expected_duration = expected_waveforms / laser_repetition_rate_hz
    timeout = expected_duration * (1 + buffer_ratio)  # add extra time with a % buffer

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            current_count = get_current_waveform_count(scope)
            if current_count >= expected_waveforms:
                return True
        except Exception:
            pass
        time.sleep(poll_interval)
    print('\nTimeout reached. Could not acquire waveforms')
    return False


def show_history(scope, state='OFF', TimePerAcq=4e-5):
    scope.write(f'ACQ:HIST {state}')
    """ACQuire:HISTory[:STATe] <State>
    Enables the history mode and allows you to save history waveforms to file.
    Parameters:     <State>
    Usage:         OFF | ON
    *RST: OFF
    Asynchronous command"""

    scope.write(f'ACQ:HIST:TPACq {TimePerAcq}')

    """ACQuire:HISTory:TPACq <TimePerAcq>
    Sets the display time for one acquisition. The shorter the time, the faster the replay is.
    Parameters:      <TimePerAcq>
    Usage:     Range:     4E-05  to  10
    Increment: 1
    *RST:    0.05
    Default unit: s
    Asynchronous command"""
    return TimePerAcq


def history_play(scope):
    scope.write('ACQuire:HIStory:PLAY')

# This show the waveform with index 'idnex' of the history, on the screen of the oscilloscope
# where 0 is the newest (last one) and older waveforms ahve negative indeces
# scope.write(f'ACQuire:HISTory:CURRent {index}')


def signals_available_in_history(scope):
    acq_count = scope.query('ACQuire:AVAilable?')
    print(f'Available acquisitions in history: {acq_count}')
    """    ACQuire:AVAilable?
     Number of acquisitions that is saved in the memory and available for history viewing. It
     is also the number of acquisitions in a fast segmentation acquisition series.
     Return values: 
    <AcquisitionCount> Range: 0  to  4294967295
     Increment: 1
     *RST: 0
     Usage: Query only
     Asynchronous command"""
    return acq_count


def average_signals_count(scope):
    avg_count = scope.query('ACQuire:AVERage?')
    print(f'Current average count: {avg_count}')
    """ACQuire:AVERage?
    Returns the current number of acquired waveforms that contribute to the average.
    Return values: 
    <CurrAverageCount> Range: 
    0  to  4294967295
    Increment: 1
    *RST: 
    Usage: 
    0
    Query only
    Asynchronous command"""
    return avg_count