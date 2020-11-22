import math


def seconds_to_interval(elapsed_seconds: int):
    elapsed_hours = math.floor(float(elapsed_seconds) / 3600.0)
    elapsed_minutes = math.floor(float(elapsed_seconds - elapsed_hours * 3600.0) / 60.0)
    elapsed_seconds = int(round(float(elapsed_seconds - elapsed_hours * 3600.0 - elapsed_minutes * 60.0)))
    return "{:02d}:{:02d}:{:02d}".format(elapsed_hours, elapsed_minutes, elapsed_seconds)
