# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 11:04:40 2025

@author: Dario
"""
# RnS_scope_drivers\controls\horizontal_setup.py

# %% HORIZONTAL SETUP


def set_timescale(scope, time_per_div):
    '''Sets the horizontal scale, the time per division, for all waveforms in the time domain,
     for example, channel and math waveforms.

     Parameters:     <TimebaseScale>

        Range: 200E-12  to  10E+3
        Increment: 1E-12
        Default unit: s/div

     Asynchronous command'''

    scope.write(f'TIM:SCAL {time_per_div}')
    print(f'Oscilloscope Time Scale: {time_per_div} s/div')


def set_timerange(scope, timewindow):
    ''' Sets the time of one acquisition, which is the time across the 10 divisions of the 
        diagram: Acquisition time = Time scale * 10 divisions

     Parameters:     <TimebaseRange>

        Range: 2E-9  to  100E+3
        Increment: 1E-12
        Default unit: s

     Asynchronous command'''
    scope.write(f'TIM:RANG {timewindow}')
    print(f'Oscilloscope Time Window: {timewindow} s')


def set_horizaontal_position(scope, channel='CHAN1', position_seconds=0.0):
    """
    Defines the time distance between the reference point and the trigger point, which is
     the zero point of the diagram. The horizontal position is also known as trigger offset.

     If you want to see a section of the waveform some time before or after the trigger, enter
     this time as horizontal position. The requested waveform section is shown around the
     reference point. Use positive values to see waveform sections after the trigger - the
     waveform and the diagram origin move to the left.

     parameters
     <Position>     Range: -159.99E-3  to  1E+26
                     Increment: 1E-12
                     Default unit: s
     Remote command: 
    TIMebase:HORizontal:POSition <Position>
    """
    scope.write(f'TIM:HOR:POS {position_seconds}')
    print(f'Oscilloscope Horizotal Position: {position_seconds} s')


def set_reference_point(scope, channel='CHAN1', percentage=10):
    '''Sets the position of the reference point in % of the screen. It defines which part of the
         waveform is shown.
    The reference point marks the rescaling center of the time scale on the screen. If you
         modify the time scale, the reference point remains fixed on the screen, and the scale is
         stretched or compressed to both sides of the reference point. If the "Position" is 0, the
         trigger point is on the reference point.
    The reference point is not marked in the diagram.

     <RescaleCtrPos>    Range: 0  to  100, increment 1, unit %

    TIMebase:REFerence <RescaleCtrPos> '''

    scope.write(f'TIM:REF {percentage}')
    print(f'Oscilloscope Horizotal Reference Point (trigger): {percentage} %')