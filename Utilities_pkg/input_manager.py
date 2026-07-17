# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 14:30:03 2025

@author: Dario
"""
# Code\Utilities_pkg\input_manager.py

def ask_User(question):

    while True:
        yesORnot = input(question+'\t(y/n):\t')
        answer = yesORnot_to_boolean(yesORnot)
        if answer is not None:
            break  # Break the loop if a valid choice is made
    return answer


def yesORnot_to_boolean(yesORnot):
    if yesORnot == 'Y' or yesORnot == 'y':
        boolean_choice = True
        print('\n\tYou declared you want to.')
    elif yesORnot == 'n' or yesORnot == 'N':
        boolean_choice = False
        print('\n\tYou declared you DON\'T want to.')
    else:
        boolean_choice = None
        print('\n\tInvalid input. Please enter Y/y or N/n.')
    return boolean_choice

def set_stage_coordinates():
    """
    Prompts user for stage bounds and step sizes.
    
    Returns:
    - x_bounds (list): [x1, x2]
    - z_bounds (list): [z1, z2]
    - step_sizes (list): [x_step, z_step]
    """
    x_bounds = [float(input('\nEnter x1 (mm):\t')), float(input('\nEnter x2 (mm):\t'))]
    z_bounds = [float(input('\nEnter z1 (mm):\t')), float(input('\nEnter z2 (mm):\t'))]
    step_sizes = [float(input('\nEnter step for X (mm):\t')), float(input('\nEnter step for Z (mm):\t'))]
    return x_bounds, z_bounds, step_sizes