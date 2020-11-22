from typing import List

from app.simulation.exception.error import UnprocessableEntityError
from app.simulation.graph.synoptic_panel_cell import SynopticPanelBaseCell, SynopticPanelSectionCell
from app.simulation.graph.synoptic_panel_section import SynopticPanelSection


class SynopticPanelGrid:

    def __init__(self, sections: List, cell_size=50):
        self.x = 0
        self.y = 0
        self.current_row = 0
        self.cells = []
        self.cell_size = cell_size
        self.open_connections = {}

        self.load_sections(sections)

    def load_sections(self, sections: List):
        del(self.cells[:])

        # Section buffer is used to store the sections that were not drawn during the first attempt
        section_buffer = []
        for section in sections:
            try:
                self.add_section(section)
            except UnprocessableEntityError:
                section_buffer.append(section)

        for section in section_buffer:
            self.add_section(section)

        self.normalize_positions()

    def add_section(self, section):
        panel_section = SynopticPanelSection(section)
        panel_section.move_to(self.get_section_coordinates(panel_section))
        self.cells.extend(panel_section.cells)

        for section_name, connection_data in panel_section.connections_map.items():
            if section_name not in self.open_connections:
                self.open_connections[section_name] = connection_data

        if section["name"] in self.open_connections:
            del (self.open_connections[section["name"]])

    def get_section_coordinates(self, panel_section):
        if self.open_connections == {}:
            return 0, 0

        if not panel_section.section["name"] in self.open_connections:
            raise UnprocessableEntityError(
                "Section '{}' doesn't have a starting point in the grid".format(panel_section.section["name"])
            )

        # HERE WE SHOULD CHECK THE CONNECTION DATA TO RETURN THE POSITIONS EITHER FROM THE BEGINNING OR THE END
        # OF THE SECTION
        connection = self.open_connections[panel_section.section["name"]]
        if connection["reversed"] is True:
            cells_x = [cell.x_index for cell in panel_section.cells if isinstance(cell, SynopticPanelSectionCell)]
            length = max(cells_x) - min(cells_x) + 1
            connection["coordinates"] = (
                connection["coordinates"][0] - length,
                connection["coordinates"][1]
            )

        return connection["coordinates"]

    def get_size(self):
        x_values = [cell.x_index for cell in self.cells]
        y_values = [cell.y_index for cell in self.cells]

        return (
            (max(x_values) - min(x_values) + 1) * SynopticPanelBaseCell.CELL_SIZE,
            (max(y_values) - min(y_values) + 1) * SynopticPanelBaseCell.CELL_SIZE
        )

    def normalize_positions(self):
        x_values = [cell.x_index for cell in self.cells]
        y_values = [cell.y_index for cell in self.cells]

        min_x, min_y = min(x_values), min(y_values)

        for cell in self.cells:
            cell.x_index -= min_x
            cell.y_index -= min_y
