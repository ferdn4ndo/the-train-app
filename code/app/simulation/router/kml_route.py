import os
import re
import logging

from lxml import etree, objectify
from app.simulation.model.route import Route
from app.simulation.model.section import Section, SectionConnection
from app.simulation.router.coordinate import GisCoordinate


class KmlRouteParser:

    def __init__(self, schema_filename=None):
        self.logger = logging.getLogger(__name__)

        if schema_filename is not None:
            module_dir = os.path.split(__file__)[0]
            schema_file = os.path.join(module_dir, schema_filename)
            with open(schema_file) as f:
                self.schema = etree.XMLSchema(file=f)
                self.schema_parser = objectify.makeparser(
                    schema=self.schema.schema,
                    strip_cdata=False
                )
        else:
            self.schema = None
            self.schema_parser = objectify.makeparser(
                strip_cdata=False
            )

    def from_string(self, source):
        return objectify.fromstring(source, parser=self.schema_parser)

    def from_filename(self, filename):
        with open(filename) as file_handler:
            return objectify.parse(file_handler, parser=self.schema_parser)


class KmlRouteReader(Route):
    STRAIGHT_LINE_NAME = "main"
    DEVIATED_LINE_NAME = "deviated"

    def __init__(self, filename, raw_content=False):
        super().__init__()
        parser = KmlRouteParser()

        if raw_content:
            self.logger.debug(
                "KML_ROUTE_READER - Created with raw content of {} bytes"
                .format(len(filename))
            )
            xml_element_tree = parser.from_string(filename)
        else:
            self.logger.debug(
                "KML_ROUTE_READER - Created with file '{}' (not raw content)"
                .format(filename)
            )
            xml_element_tree = parser.from_filename(filename)

        self.xml_root = xml_element_tree.getroot()
        self.name = str(self.xml_root.Document.Folder.name)
        self.read_sections()

    def read_sections(self):
        folder = self.xml_root.Document.Folder

        sections = [
            self.parse_section(placemark)
            for placemark in folder.Placemark
        ]

        sections = self.merge_turnouts(sections)

        for section_data in sections:
            section = Section(**section_data)
            self.sections.append(section)

    def parse_section(self, placemark):
        data = {
            'name': str(placemark.name),
            'length': 1000,
            'connections': [],
            'lines': [],
        }

        data['connections'] = self.get_kml_section_connections(placemark)
        data['lines'] = self.parse_section_lines(placemark)

        return data

    def parse_section_lines(self, placemark):
        line_points = str(placemark.LineString.coordinates).strip().split(" ")

        return [
            {
                'type': self.STRAIGHT_LINE_NAME,
                'points': list(
                    self.parse_line_coordinate(coordinate)
                    for coordinate in line_points
                )
            }
        ]

    def parse_line_coordinate(self, coordinate):
        lon, lat, elevation = coordinate.split(",")
        elevation = None if float(elevation) == 0.0 else elevation
        return GisCoordinate(lat, lon, elevation)

    def get_kml_section_connections(self, placemark):
        connections = []
        description = str(placemark.description)

        x = re.search(r"(?<=CONNECTIONS_START=)[\w\d#]*", description)
        if x.group(0):
            connections += list(
                SectionConnection(connection, "start")
                for connection in x.group(0).split(',')
            )

        x = re.search(r"(?<=CONNECTIONS_END=)[\w\d#]*", description)
        if x.group(0):
            connections += list(
                SectionConnection(connection, "end")
                for connection in x.group(0).split(',')
            )

        return connections

    def merge_turnouts(self, sections):
        merged_sections = []

        for section in sections:
            name = section['name']

            # not a turnout, simply append to the new sections list and skip
            if '#' not in name:
                merged_sections.append(section)
                continue

            name_parts = name.split('#')
            id_parts = name_parts[1].split('_')

            turnout_name = name_parts[0] + '#' + id_parts[0]
            turnout_path_index = id_parts[1]
            section['lines'][0]['type'] = (
                self.STRAIGHT_LINE_NAME
                if int(turnout_path_index) == 1 else
                self.DEVIATED_LINE_NAME
            )

            merged_section = next(
                (
                    section for section in merged_sections
                    if section["name"] == turnout_name
                ),
                False
            )

            if merged_section is not False:
                merged_section['connections'] = self.merge_connections(
                    merged_section['connections'],
                    section['connections']
                )
                merged_section['lines'].append(section['lines'][0])
            else:
                section['name'] = turnout_name
                merged_sections.append(section)

        return merged_sections

    def merge_connections(self, original_connections, new_connections):
        original_connections.extend(
            [
                connection for connection in new_connections
                if connection not in original_connections
            ]
        )

        return original_connections
