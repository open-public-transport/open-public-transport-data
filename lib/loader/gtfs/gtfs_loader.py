import os

import requests
from tracking_decorator import TrackingDecorator


def download_file(logger, file_path, url):
    try:
        data = requests.get(url)
        with open(file_path, 'wb') as file:
            file.write(data.content)
    except Exception as e:
        logger.log_line(f"✗️ Exception: {str(e)}")
        return None


#
# Main
#

class GtfsLoader:

    @TrackingDecorator.track_time
    def run(self, logger, results_path, name, url, clean=False, quiet=False):
        # Make results path
        os.makedirs(os.path.join(results_path), exist_ok=True)

        # Define file path
        file_path = os.path.join(results_path, "GTFS.zip")

        # Check if result needs to be generated
        if clean or not os.path.exists(file_path):

            download_file(
                logger=logger,
                file_path=file_path,
                url=url
            )

            if not quiet:
                logger.log_line(f"✓ Download {file_path}")
        else:
            logger.log_line(f"✓ Already exists {file_path}")
