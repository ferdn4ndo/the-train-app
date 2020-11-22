import logging
import yaml
from pathlib import Path


class GisCoordinate:
    ELEVATION_FOLDER = "simulation/router/elevations/"

    def __init__(self, lat, lon, elevation=None):
        self.logger = logging.getLogger(__name__)

        self.lat = float(lat)
        self.lon = float(lon)

        self.elevation_filename = (
            self.ELEVATION_FOLDER +
            "{:.8f}_{:.8f}.point".format(
                self.lat, self.lon
            )
        )
        self.elevation_file = Path(self.elevation_filename)

        downloader = ElevationDownloader(self.ELEVATION_FOLDER)
        if elevation is None and self.elevation_file.is_file():
            self.elevation = self.read_elevation()
        elif elevation is None and not downloader.is_marked_for_download(self):
            self.elevation = 0.0
            downloader.mark_for_download(self)
        elif elevation is None:
            self.elevation = 0.0
        else:
            self.elevation = float(elevation)

    def __repr__(self):
        return (
            "<GisElevation_lat={:.8f}_lon={:.8f}_elevation={:.8f}>"
        ).format(
            self.lat,
            self.lon,
            self.elevation
        )

    def dump(self):
        return {
            "elevation": self.elevation,
            "location": {
                "lat": self.lat,
                "lng": self.lon
            },
            "resolution": 0
        }

    def read_elevation(self):
        coordinate_data = yaml.load(self.elevation_file.read_text())
        return float(coordinate_data['elevation'])


class ElevationDownloader:

    def __init__(self, elevation_folder, points_per_request=50):
        self.elevation_folder = elevation_folder
        self.to_download_filename = elevation_folder + "_to_download.txt"
        self.points_per_request = points_per_request

    def mark_for_download(self, coordinate):
        file_handler = open(self.to_download_filename, "a")
        file_handler.write(
            "{:.8f},{:.8f}\n".format(coordinate.lat, coordinate.lon)
        )
        file_handler.close()

    def is_marked_for_download(self, coordinate):
        with open(self.to_download_filename, "r") as file_handler:
            points = file_handler.read().split("\n")

        return True if "{:.8f},{:.8f}".format(
            coordinate.lat,
            coordinate.lon
        ) in points else False

    def download(self):
        with open(self.to_download_filename, "r") as file_handler:
            to_download_list = file_handler.read().split("\n")

        if len(to_download_list) > self.points_per_request:
            query_points = "|".join(to_download_list[:self.points_per_request])
        else:
            query_points = "|".join(to_download_list)

        api_key = os.environ['GOOGLE_MAPS_API_KEY']
        return
        output = yaml.dump(json_response, file, default_flow_style=False)
        elevation_file.write_text(output)
