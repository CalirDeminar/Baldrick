import math
import haversine
from haversine import Unit
import unittest

from typing import List, Tuple, Union


class WayPoint:
    name: str = ''
    index: int = -1
    lat: Tuple[int, int, int] = [0, 0, 0]
    long: Tuple[int, int, int] = [0, 0, 0]
    x_pixel: int = 0
    y_pixel: int = 0
    bearing_from_last: Union[int, None] = None
    bearing_to_next: Union[int, None] = None
    distance_from_last: float = 0
    time = None
    tags = []
    speed = None
    min_alt = None
    notes = ""

    def __init__(self, string_list_to_parse: List[str], index: int):
        if len(string_list_to_parse) < 8:
            raise Exception("Invalid Way Point List Line")
        lat = (
            int(string_list_to_parse[1].strip()),
            int(string_list_to_parse[2].strip()),
            int(string_list_to_parse[3].strip())
        )
        long = (
            int(string_list_to_parse[4].strip()),
            int(string_list_to_parse[5].strip()),
            int(string_list_to_parse[6].strip())
        )
        self.name = string_list_to_parse[0]
        self.lat = lat
        self.long = long
        self.index = index
        self.notes = string_list_to_parse[7].strip()
        taggables = list(map(lambda i: i.strip(), string_list_to_parse[8:]))
        digit_tags = list(
            filter(
                lambda i: i.isdigit(),
                taggables
            )
        )
        if len(digit_tags) > 0:
            self.min_alt = int(digit_tags[0])
        self.tags = list(
            filter(
                lambda i: not i.isdigit(),
                taggables
            )
        )

    def bearing_from(self, previous: 'WayPoint'):
        own_lat = math.radians(self.lat[0] + (self.lat[1]/60) + (self.lat[2]/3600))
        own_long = math.radians(self.long[0] + (self.long[1]/60) + (self.long[2]/3600))

        prev_lat = math.radians(previous.lat[0] + (previous.lat[1]/60) + (previous.lat[2]/3600))
        prev_long = math.radians(previous.long[0] + (previous.long[1]/60) + (previous.long[2]/3600))

        x = math.cos(own_lat) * math.sin(own_long-prev_long)
        y = math.cos(prev_lat) * math.sin(own_lat) - math.sin(prev_lat) * math.cos(own_lat) * math.cos(own_long-prev_long)
        output_rad = math.atan2(x, y)
        return round((output_rad*180/math.pi + 360) % 360)

    def to_degrees(self):
        return to_degrees(self.lat, self.long)

    def distance_from(self, wp: 'WayPoint'):
        return haversine.haversine(self.to_degrees(), wp.to_degrees(), unit=Unit.NAUTICAL_MILES)


def to_degrees(lat: Tuple[int, int, int], long: Tuple[int, int, int]):
    return (
        lat[0] + (lat[1]/60) + (lat[2]/3600),
        long[0] + (long[1]/60) + (long[2]/3600)
    )


def to_lat_long(lat: float, long: float):
    lat_d = round(lat)
    lat_m = round((lat - lat_d)*60)
    lat_s = round((lat - lat_d - (lat_m/60))*60*60)

    long_d = round(long)
    long_m = round((long - long_d)*60)
    long_s = round((long - long_d - (long_m/60))*60*60)

    return (
        (lat_d, lat_m, lat_s),
        (long_d, long_m, long_s)
    )


def lat_long_to_string(lat: Tuple[int, int, int], long: Tuple[int, int, int]):
    lat_second_round = 0
    if lat[2] >= 30:
        lat_second_round = 1
    long_second_round = 0
    if long[2] >= 30:
        long_second_round = 1

    return "N%02d %02d E%02d %02d" % (
                lat[0],
                lat[1] + lat_second_round,
                long[0],
                long[1] + long_second_round
            )


class TestWaypoint(unittest.TestCase):
    def test_bearing_correct_on_long(self):
        self.assertEqual(
            WayPoint(["wp1", "0", "0", "0", "0", "0", "0"], 0).bearing_from(
                WayPoint(["wp2", "1", "0", "0", "0", "0", "0"], 1)
            ),
            180
        )
        self.assertEqual(
            WayPoint(["wp1", "1", "0", "0", "0", "0", "0"], 0).bearing_from(
                WayPoint(["wp2", "0", "0", "0", "0", "0", "0"], 1)
            ),
            0
        )

    def test_bearing_correct_on_lat(self):
        self.assertEqual(
            WayPoint(["wp1", "0", "0", "0", "0", "0", "0"], 0).bearing_from(
                WayPoint(["wp2", "0", "0", "0", "1", "0", "0"], 1)
            ),
            270
        )
        self.assertEqual(
            WayPoint(["wp1", "0", "0", "0", "1", "0", "0"], 0).bearing_from(
                WayPoint(["wp2", "0", "0", "0", "0", "0", "0"], 1)
            ),
            90
        )

    def test_bearing_correct_on_lat_long(self):
        self.assertEqual(
            WayPoint(["wp1", "0", "0", "0", "0", "0", "0"], 0).bearing_from(
                WayPoint(["wp2", "1", "0", "0", "1", "0", "0"], 1)
            ),
            225
        )
        self.assertEqual(
            WayPoint(["wp1", "1", "0", "0", "1", "0", "0"], 0).bearing_from(
                WayPoint(["wp2", "0", "0", "0", "0", "0", "0"], 1)
            ),
            45
        )
        self.assertEqual(
            WayPoint(["wp1", "46", "0", "0", "46", "0", "0"], 0).bearing_from(
                WayPoint(["wp2", "45", "0", "0", "45", "0", "0"], 1)
            ),
            35
        )

    def test_to_degrees(self):
        self.assertEqual(to_degrees((20, 30, 0), (20, 30, 0)), (20.5, 20.5))

    def test_to_lat_long(self):
        self.assertEqual(to_lat_long(20.5, 20.5), ((20, 30, 0), (20, 30, 0)))


if __name__ == "__main__":
    unittest.main()
