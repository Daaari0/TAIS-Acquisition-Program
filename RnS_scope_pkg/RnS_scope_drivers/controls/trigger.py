# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 11:05:30 2025

@author: Dario
"""

# RnS_scope_drivers\controls\trigger.py


# %% TRIGGER


def set_trigger(scope,  level=-1.6e-3, mode='SING', trg_type='EDGE', source='C3', edge='NEG'):

    # selecting the trigger mode, at single (SING) event or sequence (SEQ)
    scope.write(f'TRIG:MEV:MODE {mode}')

    # select type of trigger, for sequent is selected for each considtion
    # scope.write('TRIG:EVEN:TYPE EDGE')
    scope.write(f'TRIG:EVEN:TYPE {trg_type}')
    '''
        TRIGger:EVENt<ev>:TYPE <Type>
     Selects the trigger type. In a trigger sequence, the trigger type is set for each condition.
     Suffix: 
    <ev> 1 = A-trigger, 2 = B-trigger, 3 = reset event
     Parameters:
     <Type> 
     EDGE | GLITch | WIDTh | RUNT | WINDow | TIMeout | INTerval |
     SLEWrate | ANEDge | SETHold | STATe | PATTern
     
     ANEDge = analog edge trigger is the only trigger type if the
     extern trigger source is used.
     
     For SETHold, also DATatoclock can be used.

     Asynchronous command'''

    # select channel or other source
    scope.write(f'TRIG:EVEN:SOUR {source}')  # also C1 works as well as CHAN1
    ''' TRIGger:EVENt<ev>:SOURce <SourceDetailed>
    
        Selects the source of the trigger signal for the selected trigger event. The trigger
     source works even if it is not displayed in a diagram.
     Available sources depend on the trigger sequence setting. If you trigger on a single
     event, all inputs can be used as trigger source. If you trigger on a sequence, only ana
    log channels can be set as trigger source.
    
     Suffix: 
    <ev> 1 = A-trigger, 2 = B-trigger, 3 = reset event
    
     Parameters:
     <SourceDetailed>      C1 | C2 | C3 | C4 | EXTernanalog | LINE | D0 | D1 | D2 | D3 | D4
          | D5 | D6 | D7 | D8 | D9 | D10 | D11 | D12 | D13 | D14 | D15 | 
         SBUS1 | SBUS2 | SBUS3 | SBUS4
    
     C1 | C2 | C3 | C4
     Available for single event and all events in a trigger sequence
     EXTernanalog | LINE | D0 | D1 | D2 | D3 | D4 | D5 | D6 | D7 |
     D8 | D9 | D10 | D11 | D12 | D13 | D14 | D15 | SBUS1 | SBUS2 |
     SBUS3 | SBUS4
     Available for single event (EVENt1)

     Asynchronous command
    '''
    # select the slope in case of edge trigger -  POSitive | NEGative | EITHer
    scope.write(f'TRIG:EVEN:EDGE:SLOP {edge}')
    '''
    TRIGger:EVENt<ev>:EDGE:SLOPe <Slope>
     Sets the edge direction for the trigger.
     
     Suffix: 
    <ev> 1 = A-trigger, 2 = B-trigger, 3 = reset event
     
     Parameters: <Slope> POSitive | NEGative | EITHer
     
     Usage: Asynchronous command
     '''

    # set trigger level
    scope.write(f'TRIG:EVEN1:LEV3 {level}')
    '''
    TRIGger:EVENt<ev>:LEVel<n>[:VALue] <Level>
         Sets the trigger level for the specified event and source (channel).
         If the trigger source is serial bus, the trigger level is set by the thresholds in the proto
        col configuration.
         Suffix: 
        <ev> 1 = A-trigger, 2 = B-trigger, 3 = reset event
         <n>  1 to 4, index of the analog channel
         Parameters:
         <Level> Range: -10  to  10, Increment: 0.001 in volts
         Usage: 

         Asynchronous command'''

    # select trigger mode/hold-off
    scope.write(f'TRIG:MODE NORM')
    ''' Trigger mode
         Sets the trigger mode which determines the behavior of the instrument if no trigger
         occurs. The current setting is shown on the trigger label.
         In a trigger sequence, the trigger mode affects only the A-trigger.
         To toggle quickly between "Auto" and "Normal" mode, use the [Auto Norm] key on the
         front panel (in "Trigger" section).
     "Auto" 
         The instrument triggers repeatedly after a time interval if the trigger
         conditions are not fulfilled. If a real trigger occurs, it takes prece
        dence. This mode helps to see the waveform even before the trigger
         conditions are set correctly. The waveform on the screen is not
         synchronized, and successive waveforms are not triggered at the
         same point of the waveform. The time interval depends on the time
        base settings.
     "Normal"
         The instrument acquires a waveform only if a trigger occurs, that is, if
         all trigger conditions are fulfilled. If no trigger occurs, no waveform is
         acquired and the last acquired waveform is displayed. If no waveform
         was captured before, none is displayed.
         When no trigger has been found for longer than one second, a mes
        sage box appears that shows the time elapsed since the last trigger.
     "Free run"
         The instrument starts acquisition immediately and triggers after a
         short time interval independent of the timebase settings and faster
         than in "Auto" mode. Real triggers are ignored. Use this mode if the
         "Auto" mode is too slow.

             parameters:
             <TriggerMode>   AUTO | NORMal | FREerun
             
        TRIGger:MODE <TriggerMode>'''
    print('Oscilloscope Trigger settings:')
    print(f'\t Mode: NORMAL')
    print(f'\t on a: {mode} event')
    print(f'\t Edge: {edge}')
    print(f'\t Source: {source}')


# %%AUTO SETTINGS - to be cheked


def auto_trigger(scope, channel='CHAN1'):
    """
    Automatically sets a trigger level based on signal amplitude.

    TRIGger:FINDlevel
     Sets the trigger level automatically to 0.5 * (MaxPeak – MinPeak).
     In a trigger sequence, "Find level" affects all active events of the sequence (A, B, and
     R event).
     Usage: 
    Event
     Asynchronous command
     Manual operation: See "Find level" on page 159
    """
    # Set temporary acquisition mode
    scope.write('ACQ:MODE NORM')
    scope.write('SING')  # Single-shot

    # Wait briefly for acquisition
    import time
    time.sleep(0.5)

    # Get waveform data
    scope.write('FORM ASC')
    scope.write(f'{channel}:DATA?')
    data = scope.read()
    samples = [float(x) for x in data.split(',') if x]

    if not samples:
        print("No data received for auto trigger.")
        return

    # Estimate trigger level
    min_val = min(samples)
    max_val = max(samples)
    trigger_level = (min_val + max_val) / 2

    # Set trigger
    scope.write('TRIG:MODE EDGE')
    scope.write(f'TRIG:EDGE:SOUR {channel}')
    scope.write(f'TRIG:LEV {trigger_level}')
    print(f"Auto trigger level set to {trigger_level:.3f} V")