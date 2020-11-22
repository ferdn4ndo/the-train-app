import math

from app.simulation.graph.synoptic_panel_cell import SynopticPanelSectionCell, SynopticPanelLabelCell
from app.simulation.model.section import Section


class SynopticPanelSection:

    def __init__(self, section, origin=Section.SECTION_START_STRAIGHT, **options):
        defaults = {
            "maximum_meters_per_cell": 10000
        }
        self.options = defaults
        self.options.update(options)

        self.origin_x = 0
        self.origin_y = 0

        self.cells = []
        self.connections_map = {}
        self.section = section
        self.origin = origin
        self.is_reversed = False

        if self.section["is_turnout"]:
            self.draw_turnout_section_cells()
        else:
            self.draw_straight_section_cells()
        self.draw_section_label()

    def draw_turnout_section_cells(self):
        start_connections = len(self.section["connections"]["start"])
        end_connections = len(self.section["connections"]["end"])

        self.connections_map[self.section["connections"]["start_straight"][0]] = {
            "coordinates": (0, 0),
            "reversed": True
        }
        self.connections_map[self.section["connections"]["end_straight"][0]] = {
            "coordinates": (1, 0),
            "reversed": False
        }

        #    ====
        #       \\
        # X> ========
        if self.origin == Section.SECTION_START_STRAIGHT and start_connections == 2 and end_connections == 1:
            self.cells = [
                SynopticPanelSectionCell(self.section, 0, -1, "left", "bottom-left"),
                SynopticPanelSectionCell(self.section, 0, 0, "both"),
            ]
            self.connections_map[self.section["connections"]["start_deviated"][0]] = {
                "coordinates": (0, -1),
                "reversed": True
            }

        # X> ====
        #       \\
        #    ========
        elif self.origin == Section.SECTION_START_DEVIATED and start_connections == 2 and end_connections == 1:
            self.cells = [
                SynopticPanelSectionCell(self.section, 0, 0, "left", "bottom-left"),
                SynopticPanelSectionCell(self.section, 0, 1, "both"),
            ]
            self.connections_map[self.section["connections"]["start_deviated"][0]] = {
                "coordinates": (0, -1),
                "reversed": True
            }

        #    ====
        #       \\
        #    ======== <X
        elif self.origin == Section.SECTION_END_STRAIGHT and start_connections == 2 and end_connections == 1:
            self.cells = [
                SynopticPanelSectionCell(self.section, 0, -1, "left", "bottom-left"),
                SynopticPanelSectionCell(self.section, 0, 0, "both"),
            ]
            self.connections_map[self.section["connections"]["start_deviated"][0]] = {
                "coordinates": (0, -1),
                "reversed": True
            }

        #        ====
        #       //
        #    ======== <X
        elif self.origin == Section.SECTION_END_STRAIGHT and start_connections == 1 and end_connections == 2:
            self.cells = [
                SynopticPanelSectionCell(self.section, 0, -1, "right", "bottom-right"),
                SynopticPanelSectionCell(self.section, 0, 0, "both"),
            ]
            self.connections_map[self.section["connections"]["end_deviated"][0]] = {
                "coordinates": (1, -1),
                "reversed": False
            }

        #        ====
        #       //
        # X> ========
        elif self.origin == Section.SECTION_START_STRAIGHT and start_connections == 1 and end_connections == 2:
            self.cells = [
                SynopticPanelSectionCell(self.section, 0, -1, "right", "bottom-right"),
                SynopticPanelSectionCell(self.section, 0, 0, "both"),
            ]
            self.connections_map[self.section["connections"]["end_deviated"][0]] = {
                "coordinates": (1, -1),
                "reversed": False
            }

        #        ==== <X
        #       //
        #    ========
        elif self.origin == Section.SECTION_START_STRAIGHT and start_connections == 1 and end_connections == 2:
            self.cells = [
                SynopticPanelSectionCell(self.section, 0, 0, "right", "bottom-right"),
                SynopticPanelSectionCell(self.section, 0, 1, "both"),
            ]
            self.connections_map[self.section["connections"]["end_deviated"][0]] = {
                "coordinates": (1, 1),
                "reversed": False
            }

    def draw_straight_section_cells(self):
        max_cell_length = self.options["maximum_meters_per_cell"]
        total_cells = math.ceil(float(self.section["length"]) / float(max_cell_length))

        if total_cells == 1:
            self.cells.append(SynopticPanelSectionCell(section=self.section, x_index=0, y_index=0, connects_on="both"))
            if len(self.section["connections"]["start_straight"]) > 0:
                self.connections_map[self.section["connections"]["start_straight"][0]] = {
                    "coordinates": (0, 0),
                    "reversed": True
                }
            if len(self.section["connections"]["end_straight"]) > 0:
                self.connections_map[self.section["connections"]["end_straight"][0]] = {
                    "coordinates": (1, 0),
                    "reversed": False
                }
            return

        start_position = 0
        increment_factor = (float(self.section["length"]) / float(total_cells)) / float(self.section["length"])
        self.cells.append(
            SynopticPanelSectionCell(
                section=self.section,
                x_index=0,
                y_index=0,
                connects_on="left",
                section_position_start=start_position,
                section_position_end=(start_position + increment_factor)
            )
        )

        if len(self.section["connections"]["start_straight"]) > 0:
            self.connections_map[self.section["connections"]["start_straight"][0]] = {
                "coordinates": (0, 0),
                "reversed": True
            }

        for x in range(1, total_cells - 1):
            start_position += increment_factor
            self.cells.append(
                SynopticPanelSectionCell(
                    section=self.section,
                    x_index=x,
                    y_index=0,
                    section_position_start=start_position,
                    section_position_end=(start_position + increment_factor)
                )
            )

        start_position += increment_factor
        self.cells.append(
            SynopticPanelSectionCell(
                section=self.section,
                x_index=(total_cells - 1),
                y_index=0,
                section_position_start=start_position,
                section_position_end=(start_position + increment_factor)
            )
        )
        if len(self.section["connections"]["end_straight"]) > 0:
            self.connections_map[self.section["connections"]["end_straight"][0]] = {
                "coordinates": (total_cells, 0),
                "reversed": False
            }

    def draw_section_label(self):
        self.cells.append(
            SynopticPanelLabelCell(
                section=self.section,
                x_index=float(self.get_x_length() - 1) / 2.0,
                y_index=min(self.get_y_positions()),
            )
        )

    def get_x_length(self):
        x_positions = self.get_x_positions()
        return max(x_positions) - min(x_positions) + 1

    def get_x_positions(self):
        return [cell.x_index for cell in self.cells]

    def get_y_positions(self):
        return [cell.x_index for cell in self.cells]

    def move_to(self, coordinates):
        for cell in self.cells:
            cell.x_index += coordinates[0]
            cell.y_index += coordinates[1]

        for connection in self.connections_map:
            self.connections_map[connection] = {
                "reversed": self.connections_map[connection]["reversed"],
                "coordinates": (
                    self.connections_map[connection]["coordinates"][0] + coordinates[0],
                    self.connections_map[connection]["coordinates"][1] + coordinates[1]
                )
            }

        self.origin_x += coordinates[0]
        self.origin_y += coordinates[1]
