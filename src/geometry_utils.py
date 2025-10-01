import math
from typing import Tuple

type LatDMS = Tuple[int, int, int]
type LongDMS = Tuple[int, int, int]
type DMS = Tuple[LatDMS, LongDMS]

type LatDec = float
type LongDec = float

def bearing_from_dms(prev: DMS, to: DMS) -> int:

    to_lat = math.radians(to[0][0] + (to[0][1] / 60) + (to[0][2] / 3600))
    to_long = math.radians(to[1][0] + (to[1][1] / 60) + (to[1][2] / 3600))

    prev_lat = math.radians(prev[0][0] + (prev[0][1] / 60) + (prev[0][2] / 3600))
    prev_long = math.radians(prev[1][0] + (prev[1][1] / 60) + (prev[1][2] / 3600))

    x = math.cos(to_lat) * math.sin(to_long - prev_long)
    y = math.cos(prev_lat) * math.sin(to_lat) - math.sin(prev_lat) * math.cos(to_lat) * math.cos(to_long - prev_long)
    output_rad = math.atan2(x, y)
    return round((output_rad * 180 / math.pi + 360) % 360)