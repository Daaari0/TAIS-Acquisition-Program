# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 11:09:01 2025

@author: Dario
"""
# RnS_scope_drivers\acquisition\acq_settings.py


def set_sample_rate(scope, mode='AUTO', minimum_sr=5e+6, sample_rate=500e+6):
    '''
     SR mode p122
     Defines how the sample rate is set.
     The sample rate considers the samples of the ADC (analog to digital converter),
     and the processing of the captured samples including interpolation.
     "Auto"
         Sample rate is determined automatically and changes due to instrument internal
         adjustments due to other setting changes. You can set
         a minimum sample rate with Min. sample rate.
     "Manual"
         The sample rate is manually defined with Sample rate.

         parameters:
             <SampleRateMode>       AUTO | MANual

        ACQuire:SRATe:MODE <SampleRateMode>

        AUTO
            Sample rate is determined automatically and changes due to
            instrument internal adjustments. You can set a minimum sample
            rate with
            ACQuire:SRATe:MINimum.
        MANual
            The sample rate is defined with
            ACQuire:SRATe[:VALue]
        '''

    scope.write(f'ACQ:SRAT:MODE {mode}')
    if mode == 'AUTO':
        scope.write(f'ACQ:SRAT:MIN {minimum_sr}')
    else:
        scope.write(f'ACQ:SRAT:VAL {sample_rate}')


def set_record_length(scope, samples_per_waveform=10e+3, mode='AUTO', maximumRL=10e+3):
    """
    RL mode
     Selects the mode of the waveform record length adjustment.
     The record length is the number of waveform samples that are stored in one waveform
     record after processing, including interpolation. It determines the length of the dis
    played waveform.

     "Auto"
         Record length is determined automatically and changes due to instru
         ment internal adjustments due to other setting changes. You can set
         a maximum record length with Record length limit.
         ACQuire:POINts:MAXimum <RecLengthLimit>
            Range:
            1000  to  800E+6, increment 2

     "Manual"
         The waveform record length is manually defined with Record length.
         The waveform record length is defined with
             ACQuire:POINts[:VALue]

        parameters:
            <RecLengthMode> AUTO | MANual

     ACQuire:POINts:MODE <RecLengthMode>
    """
    scope.write(f'ACQ:POIN:MODE {mode}')
    if mode == 'MAN':
        scope.write(f'ACQ:POIN {samples_per_waveform}')
    else:
        scope.write(f'ACQ:POIN:MAX {maximumRL}')

    scope.write('ACQ:RES?')
    time_resolution = float(scope.read())
    return print(f'Time resolution of {time_resolution} s')


def set_averaging_count(scope, count):
    """
    Sets the number of acquisitions to average.
    Only applies when acquisition mode is 'AVER'.

    parameter:
        <MaxAcqCnt>
        Range:
        1  to  16777215 (max is around 16.8 e+6)
    """
    scope.write(f'ACQ:COUN {count}')


def set_acquisition_mode(scope, mode='AVER'):
    """
    Sets acquisition mode.
    Options: <AcquMode> SAMPle | PDETect | ENVelope | AVERage
    """
    # ┌─────────────────────────────┐
    # │     MXO4 Acquisition Modes  │
    # └─────────────────────────────┘
    # Mode Name       SCPI Keyword   Description
    # ---------------------------------------------------------------
    # Peak Detect     'PDET'         Captures min/max values per sample interval
    # Average         'AVER'         Averages multiple acquisitions to reduce noise
    # Envelope        'ENV'          Captures min/max envelope over multiple sweeps
    # SAMPle doesnt work, not imprtant

    scope.write(f'ACQ:TYPE {mode}')


def set_HD_acquisition(scope, bandwidth_Hz=10, status='OFF'):
    # select HD mode
    '''
    Enables high definition mode, which increases the numeric resolution of the waveform
    signal.
    Parameters:
        <State>   OFF | ON
    ON: high definition mode
    OFF: normal oscilloscope mode

    HDEFinition:STATe <State>'''
    scope.write(f'HDEF:STAT {status}')

    # select bandwidth
    '''
     Sets the filter bandwidth for the high definition mode.
     Parameters:
     <Bandwidth>

        Range:
        1000  to  500E+6    Increment: 1000  Default unit: Hz

     HDEFinition:BWIDth <Bandwidth>'''
    scope.write(f'HDEF:BWID {bandwidth_Hz}')

    '''
     Displays the resulting vertical resolution in high definition mode. The higher the filter
     bandwidth, the lower the resolution.
     <Resolution> Range: 0  to  18 Increment: 0.1 Default unit: bit
     Query only
     HDEFinition:RESolution?'''
    if status == 'ON':
        scope.write('HDEF:RES?')
        resolution_bit = int(scope.read())

        return print(f'Bit resolution set to {resolution_bit}')
    else:
        return print('HD is off')


def enable_segmented_memory(scope, segments='MAX', status='OFF'):
    """
    Enables segmented memory acquisition.
    """

    '''
    If fast segmentation is enabled, the acquisitions are performed as fast as possible,
     without processing and displaying the waveforms. When acquisition has been stopped,
     the data is processed and the latest waveform is displayed. Older waveforms are
     stored in segments. You can display and analyze the segments using the history.
     
     NOTE: it limits to 10k average signals
     
    ACQuire:SEGMented:STATe <State>
    <State>  OFF | ON
    '''
    scope.write(f'ACQ:SEGM:STAT {status}')

    if status == 'ON':
        if segments == 'MAX':
            """ACQuire:SEGMented:MAX <MaxAcqs>
            parameter    <MaxAcqs>
             Usage:     OFF | ON
             *RST:     OFF
             Asynchronous command"""

            scope.write(f'ACQ:SEGM:MAX ON')
        else:
            scope.write(f'ACQ:COUN {segments}')

    else:
        scope.write(f'ACQ:SEGM:MAX OFF')