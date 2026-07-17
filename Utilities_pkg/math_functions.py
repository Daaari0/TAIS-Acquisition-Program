# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 08:14:46 2025

@author: Dario
"""
# .\Utilities_package\math_functions
from decimal import Decimal, ROUND_HALF_UP


def decimal_range(start, stop, step, include_upper=True):
    """
    Generate a sequence of decimal numbers from start to stop,
    with a given step size. Endpoints are included with rounding
    consistent to the step size.
    """

    # Convert inputs to Decimal to avoid floating-point errors
    start = Decimal(str(start))
    stop = Decimal(str(stop))
    step = Decimal(str(step))

    # Compute how many steps fit between start and stop
    #    Use integer conversion with rounding to avoid precision issues
    n_steps = int(((stop - start) / step).to_integral_value(rounding=ROUND_HALF_UP))

    # If we want to include the upper bound, add one more step
    if include_upper:
        n_steps += 1

    # Generate each value in the sequence
    values = []
    for i in range(n_steps):
        value = start + step * i
        values.append(value)

    # Round the value to the same decimal precision as the step
    values = [float(value.quantize(step, rounding=ROUND_HALF_UP)) for value in values]

    return values


def stage_grid_size(x_bounds, z_bounds, step_sizes, include_upper=True):
    """
    Calculates the number of stage points based on bounds and step sizes,
    using decimal_range to ensure consistency.
    """
    # Generate sequences with decimal_range
    x_points = list(decimal_range(x_bounds[0], x_bounds[1], step_sizes[0], include_upper))
    z_points = list(decimal_range(z_bounds[0], z_bounds[1], step_sizes[1], include_upper))

    # Count them
    x_count = len(x_points)
    z_count = len(z_points)
    total_points = x_count * z_count

    return x_count, z_count, total_points


def expected_time(points_total, NUM_AVERAGE, LASER_REPETITION_RATE_Hz):
    acq_time_per_pixel = NUM_AVERAGE * 1/LASER_REPETITION_RATE_Hz * 1.1  # + buffer 10%
    avg_time_per_pixel = 12 * NUM_AVERAGE * 1e-4  # hardcoded 12s for average seg.history of 1e+4 signals
    total_time = points_total * (avg_time_per_pixel + acq_time_per_pixel)
    return total_time


def format_duration(seconds):
    seconds = int(round(seconds))

    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}min {secs}s" if secs else f"{minutes}min"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}min" if minutes else f"{hours}h"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h" if hours else f"{days}d"