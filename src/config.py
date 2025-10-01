import json
from os import path

bundle_dir = path.abspath(path.dirname(__file__))

is_prod = "_internal" in str(bundle_dir)

filepath = f'{bundle_dir}/../config.json'
if is_prod:
    filepath = f'{bundle_dir}/../../config.json'

config = {}
with open(filepath) as f:
    config = json.load(f)


class Config:
    @classmethod
    def overview_card_downsample_factor(cls):
        return float(config["overviewCardDownsampleFactor"])

    @classmethod
    def route_colour(cls):
        return config["routeColour"]

    @classmethod
    def min_cruise_speed(cls):
        return float(config["minCruiseSpeed"])

    @classmethod
    def dash_speed(cls):
        return float(config["dashSpeed"])

    @classmethod
    def default_cruise_speed(cls):
        return float(config["defaultCruiseSpeed"])

    @classmethod
    def metric(cls):
        return bool(config['metric'])