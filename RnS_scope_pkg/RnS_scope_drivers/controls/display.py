# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 11:02:17 2025

@author: Dario
"""
# RnS_scope_drivers\controls\display.py
# %% DISPLAY


def set_remote_display(scope, status='OFF', verbose=True):
    '''
      Defines whether the display is updated while the instrument is in the remote state. If
      the display is switched off, the normal GUI is replaced by a static image while the
      instrument is in the remote state. Switching off the display can speed up the measurement. OFF is the recommended state.
      Parameters: <DisplayUpdate>
             ON| 1: The display is shown and updated during remote control.
            OFF| 0: The display shows a static image during remote control.
       SYSTem:DISPlay:UPDate <DisplayUpdate>
       '''
    scope.write(f'SYST:DISP:UPD {status}')
    if verbose:
        print(f'Oscilloscope Display status: {status}')