import json
import os
from urllib.parse import quote

import osm2geojson
import requests
from tracking_decorator import TrackingDecorator

landuses = [
    {"name": "cemetery", "query": '"landuse"~"cemetery"'},
    {"name": "college", "query": '"landuse"~"college"'},
    {"name": "commercial", "query": '"landuse"~"commercial"'},
    {"name": "farmland", "query": '"landuse"~"farmland"'},
    {"name": "farmyard", "query": '"landuse"~"farmyard"'},
    {"name": "forest", "query": '"landuse"~"forest"'},
    {"name": "garden", "query": '"landuse"~"garden"'},
    {"name": "industrial", "query": '"landuse"~"industrial"'},
    {"name": "park", "query": '"leisure"~"park"'},
    {"name": "recreation_ground", "query": '"landuse"~"recreation_ground"'},
    {"name": "residential", "query": '"landuse"~"residential"'},
    {"name": "university", "query": '"landuse"~"university"'},
    {"name": "water", "query": '"natural"~"water"'},
    {"name": "wood", "query": '"landuse"~"wood"'},
]


def download_landuse_json(logger, query, xmin, ymin, xmax, ymax):
    try:
        return download_json(
            data=f"""
[out:json][timeout:25];
(
  node[{query}]({ymin}, {xmin}, {ymax}, {xmax});
  way[{query}]({ymin}, {xmin}, {ymax}, {xmax});
  relation[{query}]({ymin}, {xmin}, {ymax}, {xmax});
);
out geom;
"""
        )
    except Exception as e:
        logger.log_line(f"✗️ Exception: {str(e)}")
        return None


def download_json(data):
    formatted_data = quote(data.lstrip("\n"))

    url = f"https://overpass-api.de/api/interpreter?data={formatted_data}"
    response = requests.get(url)
    text = response.text.replace("'", "")
    return json.loads(text)


def convert_json_to_geojson(file_path, json_content):
    geojson = osm2geojson.json2geojson(json_content)

    with open(file_path, "w") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=4)

    return geojson


#
# Main
#

class OverpassLanduseLoader:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, city, xmin, ymin, xmax, ymax, clean=False, quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path, "landuse"), exist_ok=True)

        success, failure = 0, 0

        # Iterate over landuses
        for landuse in landuses:

            name = landuse["name"]
            query = landuse["query"]

            # Define file path
            file_path = os.path.join(results_path, "landuse", name + ".geojson")

            # Check if result needs to be generated
            if clean or not os.path.exists(file_path):

                # Download geojson
                json_content = download_landuse_json(
                    logger=logger,
                    query=query,
                    xmin=xmin,
                    ymin=ymin,
                    xmax=xmax,
                    ymax=ymax
                )

                if json_content is not None:

                    geojson = convert_json_to_geojson(
                        file_path=file_path,
                        json_content=json_content
                    )

                    if geojson is not None:
                        if not quiet:
                            success += 1
                            logger.log_line(f"✓ Download {city} landuse {name}")
                    else:
                        failure += 1
                else:
                    failure += 1
                    logger.log_line(f"✗️ Cannot download {city} landuse {name}")

        return success, failure
