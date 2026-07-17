# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 10:21:15 2025

@author: Dario
"""
# Shutters_pkg/shutters_control.py

import pyhid_usb_relay

relay = pyhid_usb_relay.find()

# Map lasers directly to relay IDs
LASER_MAP = {'pump': 1, 'probe': 2}


def shutter(laser, status='OFF', verbose=False):
    """Turn a laser shutter ON or OFF."""
    shutter_id = LASER_MAP.get(laser)
    if shutter_id is None:
        raise ValueError(f"Unknown laser: {laser}")
    # checks if status is set to ON, in that case returns True and turns ON the relay
    relay.set_state(shutter_id, status.upper() == 'ON')
    if verbose:
        print(f'Set {laser.upper()} shutter (id={shutter_id}) to {status.upper()}')


'''
def shutter(laser, status = 'OFF'):
    if laser == 'probe':
        shutter_id=1
    elif laser == 'pump':
        shutter_id=2
        
    if status == 'ON':
        switch = True
    elif  status == 'OFF':
        switch = False
    
    relay.set_state(shutter_id, switch)  '''


if __name__ == '__main__':
    try:
        while True:
            '''laser=input('\nWhich Laser Shutter you wish to control? (probe/pump )\t')
            status=input('Change its status to: (ON/OFF)\t')
            shutter(laser, status)'''

            # Normalize input: strip spaces, lowercase/uppercase
            laser = input('\nWhich Laser Shutter you wish to control? (probe/pump)\t').strip().lower()
            # Fallback for typos
            if laser not in ('probe', 'pump'):
                print(f"⚠️ Unknown laser '{laser}'. Please type 'probe' or 'pump'.")
                continue

            status = input('Change its status to: (ON/OFF)\t').strip().upper()
            # Fallback for typos
            if status not in ('ON', 'OFF'):
                print(f"⚠️ Unknown status '{status}'. Please type 'ON' or 'OFF'.")
                continue

            # Safe call only if inputs are valid
            shutter(laser, status, True)

    except KeyboardInterrupt:
        print("Both relays are OFF.")
        # Reset to safe state
        shutter('pump', 'off')
        shutter('probe', 'off')