import getopt
import os
import sys

file_path = os.path.realpath(__file__)
script_path = os.path.dirname(file_path)

# Make library available in path
library_paths = [
    os.path.join(script_path, "lib"),
    os.path.join(script_path, "lib", "loader"),
    os.path.join(script_path, "lib", "loader", "gtfs"),
    os.path.join(script_path, "lib", "loader", "overpass"),
    os.path.join(script_path, "lib", "log"),
]

for p in library_paths:
    if not (p in sys.path):
        sys.path.insert(0, p)

# Import library classes
from logger_facade import LoggerFacade
from tracking_decorator import TrackingDecorator
from gtfs_loader import GtfsLoader
from boundaries_loader import BoundariesLoader
from overpass_landuse_loader import OverpassLanduseLoader


#
# Main
#

@TrackingDecorator.track_time
def main(argv):
    # Set default values
    clean = False
    quiet = False

    transport_associations = [
        {"name": "avv",
         "url": "https://www.opendata-oepnv.de/dataset/dede57c7-9601-43cd-9fb6-8ab4c27412d2/resource/5373201d-021a-4cff-92be-bcb9e2365d8b/download/avv_gtfs_masten_mit_spnv_und_arr-lim-1.zip"},
        {"name": "hvv", "url": "https://opendata-oepnv.de/fileadmin/datasets/hvv/05-11-2021_Soll-Fahrplandaten.zip"},
        {"name": "mvv",
         "url": "https://www.opendata-oepnv.de/dataset/17065229-c3fd-46d7-84a9-aae55aadbf40/resource/208c55dd-15d6-4ea0-abd7-8433d64180ed/download/mvv_gtfs.zip"},
        {"name": "nwl",
         "url": "https://www.opendata-oepnv.de/dataset/89892705-b6e7-4ffc-977c-2ba9b86dde46/resource/38f05ab3-d9c7-4a44-bef5-5037fae430d7/download/gtfs-nwl-20211215.zip"},
        {"name": "vbb", "url": "https://www.vbb.de/fileadmin/user_upload/VBB/Dokumente/API-Datensaetze/GTFS.zip"},
        {"name": "vms", "url": "https://www.vms.de/fileadmin/user_upload/GTFS-Daten/GTFS_VMS_2021-12-19.zip"},
        {"name": "vrr", "url": "https://www.opendata-oepnv.de/dataset/496eea5d-d6ef-4dc2-aeb0-d15c4fbf3178/resource/8658008e-c006-46cf-8109-d08d3881d6ba/download/20211216_gtfs_vrr_od.zip"},
        {"name": "vrs",
         "url": "https://www.opendata-oepnv.de/dataset/19460e8a-bb64-4103-a429-4e5eec4578e9/resource/744a2ac6-eb8c-4734-b92c-7a43e84da45c/download/gtfs_vrs_mit_spnv-.zip"},
        {"name": "vvs", "url": "https://opendata-oepnv.de/fileadmin/datasets/vvs/09-11-2021_Soll-Fahrplandaten.zip"}
    ]

    cities = [
        "berlin", "bochum", "bonn", "bremen", "cottbus", "dortmund", "dresden", "duesseldorf", "duisburg", "frankfurt-main",
        "frankfurt-oder", "hamburg", "hamm", "koeln", "leipzig", "muenchen", "muenster", "potsdam", "stuttgart", "wuppertal"
    ]

    # Read command line arguments
    try:
        opts, args = getopt.getopt(argv, "hcqp:", ["help", "clean", "quiet"])
    except getopt.GetoptError:
        print("main.py --help --clean --quiet")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("main.py")
            print("--help                           show this help")
            print("--clean                          clean intermediate results before start")
            print("--quiet                          do not log outputs")
            sys.exit()
        elif opt in ("-c", "--clean"):
            clean = True
        elif opt in ("-q", "--quiet"):
            quiet = True

    # Set paths
    base_results_path = os.path.join(script_path, "data")

    # Initialize logger
    logger = LoggerFacade(base_results_path, console=True, file=False)

    # Iterate over transport associations
    for transport_association in transport_associations:
        results_path = os.path.join(base_results_path, "transport-associations", transport_association["name"])

        # Initialize logger
        logger = LoggerFacade(results_path, console=True, file=False)

        # Load GTFS data
        GtfsLoader().run(
            logger=logger,
            results_path=results_path,
            name=transport_association["name"],
            url=transport_association["url"],
            clean=clean,
            quiet=quiet
        )

    land_success_total, land_failure_total = 0, 0

    # Iterate over cities
    for city in cities:
        results_path = os.path.join(base_results_path, "cities", city)

        # Initialize logger
        logger = LoggerFacade(results_path, console=True, file=False)

        # Load bounding box
        xmin, ymin, xmax, ymax = BoundariesLoader().run(
            logger=logger,
            data_path=results_path,
            city=city,
            clean=clean,
            quiet=quiet
        )

        # Load land use
        success, failure = OverpassLanduseLoader().run(
            logger=logger,
            results_path=results_path,
            city=city,
            xmin=xmin,
            ymin=ymin,
            xmax=xmax,
            ymax=ymax,
            clean=clean,
            quiet=quiet
        )

        land_success_total += success
        land_failure_total += failure

    logger.log_line(f"✓ Landuse loader success {land_success_total} / failure {land_failure_total}")


if __name__ == "__main__":
    main(sys.argv[1:])
