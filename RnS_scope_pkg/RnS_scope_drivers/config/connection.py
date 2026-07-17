# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 11:02:12 2025

@author: Dario
"""
# RnS_scope_drivers\config\connection.py
import pyvisa


def connect_oscilloscope(resource_str, timeout_ms=5000):
    rm = pyvisa.ResourceManager()
    scope = rm.open_resource(resource_str)
    scope.timeout = timeout_ms
    return scope


def disconnect_oscilloscope(scope):
    try:
        scope.close()
        print("Oscilloscope disconnected.")
    except Exception as e:
        print(f"Error disconnecting: {e}")