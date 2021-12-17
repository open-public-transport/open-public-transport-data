import json
import os

from tracking_decorator import TrackingDecorator


def read_geojson(file_path):
    file = open(file_path)
    return json.load(file)


def get_bounding_box(polygon):
    env = polygon.GetEnvelope()
    return env[0], env[2], env[1], env[3]


#
# Main
#

class BoundariesLoader:

    @TrackingDecorator.track_time
    def run(self, logger, data_path, city, clean=False, quiet=False):
        geojson = read_geojson(os.path.join(data_path, "boundaries", "boundaries.geojson"))
        features = geojson["features"]

        xmin = None
        ymin = None
        xmax = None
        ymax = None

        for feature in features:
            geometry = feature["geometry"]
            coordinates = geometry["coordinates"]

            while not (type(coordinates[0][0]) == float and type(coordinates[0][1]) == float):
                coordinates = coordinates[0]

            for coordinate in coordinates:

                x = coordinate[0]
                y = coordinate[1]

                if xmin == None or x < xmin:
                    xmin = x
                if ymin == None or y < ymin:
                    ymin = y
                if xmax == None or x > xmax:
                    xmax = x
                if ymax == None or y > ymax:
                    ymax = y

        if not quiet:
            logger.log_line(f"✓ Bounding box of {city} is [{xmin}, {ymin}, {xmax}, {ymax}]")

        return [xmin, ymin, xmax, ymax]