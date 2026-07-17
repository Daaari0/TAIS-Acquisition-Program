# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 13:50:28 2025

@author: Dario

class that gathers all oscillsocope related functions
"""

# RnS_scope_pkg\RnS_Oscilloscope.py

# Import connection
from RnS_scope_pkg.RnS_scope_drivers.config.connection import connect_oscilloscope, disconnect_oscilloscope

# Acquisition modules
from RnS_scope_pkg.RnS_scope_drivers.acquisition import acq_control, acq_settings

# Controls modules
from RnS_scope_pkg.RnS_scope_drivers.controls import display, trigger, horizontal_setup, vertical_setup

# Utility modules
from RnS_scope_pkg.RnS_scope_drivers.utils import visualization


class RnS_Oscilloscope:
    def __init__(self, resource_str: str, timeout_ms: int = 5000):
        """Initialize connection to the oscilloscope when object is created."""
        self.scope = self.connect(resource_str, timeout_ms)

    def connect(self, resource_str, timeout_ms):
        """Establish connection to the oscilloscope."""
        try:
            return connect_oscilloscope(resource_str, timeout_ms)
        except Exception as e:
            print(f"Connection failed: {e}")
            return None

    def disconnect(self):
        """Disconnect from the oscilloscope."""
        # Setting the display to ON
        self.set_remote_display(status='ON', verbose=False)
        # Going back to Local from Remote
        # self.return_to_local() #cannot go to local, at least via USB connection
        # TODO: # works?
        disconnect_oscilloscope(self.scope)

    # == SCPI commands and query, Useful for troubleshuting ==
    def write(self, cmd: str):
        """Send a SCPI command to the oscilloscope."""
        if self.scope:
            return self.scope.write(cmd)
        else:
            raise RuntimeError("Scope not connected")

    def query(self, cmd: str):
        """Send a SCPI query and return the response."""
        if self.scope:
            return self.scope.query(cmd)
        else:
            raise RuntimeError("Scope not connected")

    def read(self):
        """Send a SCPI read and return the response."""
        if self.scope:
            return self.scope.read()
        else:
            raise RuntimeError("Scope not connected")

    # ---------------- Acquisition Control ----------------

    def control_acquisition(self, mode='SINGLE'):
        return acq_control.control_acquisition(self.scope, mode)

    def fetch_waveform(self, channel='CHAN1'):
        return acq_control.fetch_waveform(self.scope, channel)

    def get_current_waveform_count(self):
        return acq_control.get_current_waveform_count(self.scope)

    def wait_acquisition_completion(self, expected_waveforms, laser_repetition_rate_hz,
                                    poll_interval=0.1, buffer_ratio=0.2):

        return acq_control.wait_acquisition_completion(
            self.scope, expected_waveforms,
            laser_repetition_rate_hz,
            poll_interval,
            buffer_ratio)

    def show_history(self, state='OFF', TimePerAcq=4e-5):
        return acq_control.show_history(self.scope, state, TimePerAcq)

    def history_play(self):
        return acq_control.history_play(self.scope)

    def signals_available_in_history(self):
        return acq_control.signals_available_in_history(self.scope)

    def average_signals_count(self):
        return acq_control.average_signals_count(self.scope)

    # ---------------- Acquisition Settings ----------------
    def set_sample_rate(self, mode='AUTO', minimum_sr=5e+6, sample_rate=500e+6):
        return acq_settings.set_sample_rate(self.scope, mode, minimum_sr, sample_rate)

    def set_record_length(self, samples_per_waveform=10e+3, mode='AUTO', maximumRL=10e+3):
        return acq_settings.set_record_length(self.scope, samples_per_waveform, mode, maximumRL)

    def set_averaging_count(self, count):
        self.enable_segmented_memory(status='OFF')
        return acq_settings.set_averaging_count(self.scope, count)

    def set_acquisition_mode(self, mode='AVER'):
        return acq_settings.set_acquisition_mode(self.scope, mode)

    def set_HD_acquisition(self, bandwidth_Hz=10, status='OFF'):
        return acq_settings.set_HD_acquisition(self.scope, bandwidth_Hz, status)

    def enable_segmented_memory(self, segments='MAX', status='OFF'):
        return acq_settings.enable_segmented_memory(self.scope, segments, status)

    # ---------------- Display Controls ----------------
    def set_remote_display(self, status='OFF', verbose=True):
        return display.set_remote_display(self.scope, status, verbose)

    # ---------------- Trigger Controls ----------------
    def set_trigger(self, level=-1.6e-3, mode='SING', trg_type='EDGE', source='C3', edge='NEG'):
        return trigger.set_trigger(self.scope, level, mode, trg_type, source, edge)

    # ---------------- Horizontal Setup ----------------
    def set_timescale(self, time_per_div):
        return horizontal_setup.set_timescale(self.scope, time_per_div)

    def set_timerange(self, timewindow):
        return horizontal_setup.set_timerange(self.scope, timewindow)

    def set_horizontal_position(self, channel='CHAN1', position_seconds=0.0):
        return horizontal_setup.set_horizaontal_position(self.scope, channel, position_seconds)

    def set_reference_point(self, channel='CHAN1', percentage=10):
        return horizontal_setup.set_reference_point(self.scope, channel, percentage)

    # ---------------- Vertical Setup ----------------
    def set_vertical_scale(self, channel='CHAN1', volts_per_div=0.05, verbose=False):
        return vertical_setup.set_vertical_scale(self.scope, channel, volts_per_div, verbose)

    def set_vertical_offset(self, channel='CHAN1', offset_volts=0.0):
        return vertical_setup.set_vertical_offset(self.scope, channel, offset_volts)

    def set_vertical_position(self, channel='CHAN1', position_divs=0.0):
        return vertical_setup.set_vertical_position(self.scope, channel, position_divs)

    def set_bandwidth(self, channel='CHAN1', bandwidth='FULL'):
        return vertical_setup.set_bandwidth(self.scope, channel, bandwidth)

    def set_coupling(self, channel='CHAN1', coupling='DC'):
        return vertical_setup.set_coupling(self.scope, channel, coupling)

    def autoscale_vertical(self, channel='CHAN1'):
        return vertical_setup.autoscale_vertical(self.scope, channel)

    def auto_vertical_offset(self, channel='CHAN1', target_scale=10e-3, settle_time=0.2, verbose=False):
        return vertical_setup.auto_vertical_offset(self.scope, channel, target_scale, settle_time, verbose)

    # ---------------- Visualization Utilities ----------------
    def plot_waveform_segmented(self, samples, time_per_div, num_divs=10, title='Oscilloscope Waveform'):
        return visualization.plot_waveform_segmented(samples, time_per_div, num_divs, title)

    def plot_waveform(self, samples, time_per_div, title='Oscilloscope Waveform'):
        return visualization.plot_waveform(samples, time_per_div, title)


if __name__ == "__main__":

    def main():
        resource_str = 'USB0::0x0AAD::0x0197::1335.5050k04-200414::INSTR'

        print("🔌 Connecting to oscilloscope...")
        scope = RnS_Oscilloscope(resource_str)

        try:
            # ---------------- Display Controls ----------------
            print("\n=== Display Controls ===")
            scope.set_remote_display("ON")

            # ---------------- Trigger Controls ----------------
            print("\n=== Trigger Controls ===")
            scope.set_trigger(level=-1.6e-3, mode="SING", source="C3", edge="NEG")

            # ---------------- Horizontal Setup ----------------
            print("\n=== Horizontal Setup ===")
            scope.set_timescale(5e-6)
            scope.set_timerange(5e-3)  # i dont use it
            scope.set_horizontal_position(channel="CHAN1", position_seconds=0.0)
            scope.set_reference_point(channel="CHAN1", percentage=10)

            # ---------------- Vertical Setup ----------------
            print("\n=== Vertical Setup ===")
            scope.set_vertical_scale(channel="CHAN1", volts_per_div=0.1)
            scope.set_vertical_offset(channel="CHAN1", offset_volts=0.01)
            scope.set_vertical_position(channel="CHAN1", position_divs=0)
            scope.set_bandwidth(channel="CHAN1", bandwidth="B20")
            scope.set_coupling(channel="CHAN1", coupling="DC")

            # scope.autoscale_vertical("CHAN1") # i dont use it - may not even work
            scope.auto_vertical_offset("CHAN1", target_scale=10e-3, settle_time=0.2)

            # ---------------- Acquisition Control ----------------
            print("\n=== Acquisition Control ===")
            scope.control_acquisition("RUN")
            samples, header = scope.fetch_waveform("CHAN1")
            # print(f"Fetched {len(samples)} samples with header: {header}") #useless
            scope.control_acquisition("STOP")
            print("Current waveform count:", scope.get_current_waveform_count())
            scope.show_history("ON")
            scope.history_play()
            scope.signals_available_in_history()
            scope.average_signals_count()  # ok, but checks how it works

            # ---------------- Acquisition Settings ----------------
            print("\n=== Acquisition Settings ===")
            scope.set_sample_rate(mode="AUTO", minimum_sr=10e6)
            scope.set_record_length(samples_per_waveform=20000, mode="MAN")
            scope.enable_segmented_memory(segments=100, status="OFF")
            scope.set_averaging_count(4)
            scope.set_acquisition_mode("AVER")
            scope.set_HD_acquisition(bandwidth_Hz=20, status="ON")

            # ---------------- Visualization ----------------
            print("\n=== Visualization ===")
            scope.plot_waveform(samples, time_per_div=1e-6, title="Test Waveform")
            scope.plot_waveform_segmented(samples, time_per_div=1e-6, num_divs=10)

        finally:
            print("\n🔌 Closing connection...")
            scope.disconnect()  # works?

    main()