import unittest

from app.simulation.graph.synoptic_panel_section import SynopticPanelSection
from app.routes.example import ExampleRoute


def get_serialized_section(name: str):
    route = ExampleRoute()
    return route.sections_mapper.find_section_by_name(name).serialize()


class TestSynopticPanelSection(unittest.TestCase):

    def test_straight_cells(self):
        """
        This test evaluates the section ZCM_ZPV from the example, which is 25km long. As the default
        parameter of the SynopticPanelSection is to split a cell on every 10km, the resultant
        representation of the ZCM_ZPV section should contain exactly 3 section cells and 1 label
        """
        section = get_serialized_section("ZCM_ZPV")
        panel_section = SynopticPanelSection(section)
        self.assertEqual(4, len(panel_section.cells))  # 3 section cells and 1 label cell

        x_positions = [cell.x_index for cell in panel_section.cells]
        x_positions.sort()
        self.assertEqual([0, 1, 1, 2], x_positions)

    def test_direct_turnout(self):
        """This test evaluates the section ZPV#1 from the example, which is a direct turnout."""
        section = get_serialized_section("ZPV#1")
        panel_section = SynopticPanelSection(section)
        self.assertEqual(3, len(panel_section.cells))  # 2 blocks and 1 label

        # superior part of the turnout (deviated beginning)
        self.assertEqual("right", panel_section.cells[0].connects_on)
        self.assertEqual("bottom-right", panel_section.cells[0].fill)
        self.assertEqual(0.0, panel_section.cells[0].section_position_start)
        self.assertEqual(1.0, panel_section.cells[0].section_position_end)
        self.assertEqual(0, panel_section.cells[0].x_index)
        self.assertEqual(-1, panel_section.cells[0].y_index)

        # inferior part of the turnout (straight section)
        self.assertEqual("both", panel_section.cells[1].connects_on)
        self.assertEqual("full", panel_section.cells[1].fill)
        self.assertEqual(0.0, panel_section.cells[1].section_position_start)
        self.assertEqual(1.0, panel_section.cells[1].section_position_end)
        self.assertEqual(0, panel_section.cells[1].x_index)
        self.assertEqual(0, panel_section.cells[1].y_index)


if __name__ == '__main__':
    unittest.main()
