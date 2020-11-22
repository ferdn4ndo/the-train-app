import math
from typing import Type, List

from PIL import Image, ImageDraw

from app.simulation.graph.base_graph import BaseGraph
from app.simulation.graph.font import RegularFont, H1Font, H2Font, H3Font
from app.simulation.graph.synoptic_panel_cell import SynopticPanelSectionCell, SynopticPanelLabelCell, \
    SynopticPanelBaseCell
from app.simulation.graph.synoptic_panel_grid import SynopticPanelGrid
from app.simulation.model.simulation_frame import SimulationFrame


class SynopticPanel(BaseGraph):
    default_options = {
        "margin_top": 25,
        "margin_bottom": 10,
        "margin_left": 10,
        "margin_right": 10,
        "spacer_height": 10,
        "spacer_line_height": 2,
        "cell_size": 50,  # cell size (height and width) in pixels
        "content_width": 600,
        "cell_real_max_length": 50000,  # max "real life" section length
        # that a cell may represent in meters
        "frame_to_render": 0,  # index of the frame to render
        "train_log_lines": 1,
    }

    SPACER_COLOR = (25, 27, 27, 255)
    PANEL_BACKGROUND_COLOR = (35, 37, 37, 255)
    TRAIN_INFO_BLOCK_BACKGROUND_COLOR = (30, 32, 32, 255)
    TRAIN_INFO_BLOCK_SIZE = (250, 300)

    def __init__(self, sections: List, frame: SimulationFrame, **options):
        self.grid = SynopticPanelGrid(sections)
        super().__init__(sections, frame, **options)

    def get_content_size(self):
        cells_size = self.grid.get_size()
        log_size = self.get_train_log_size()

        widths = [
            self.options["margin_left"],
            cells_size[0],
            self.options["margin_right"],
        ]

        heights = [
            self.options["margin_top"],
            cells_size[1],
            self.options["spacer_height"],
            log_size[1],
            self.options["margin_top"],
        ]

        total_width, total_height = int(sum(widths)), int(sum(heights))

        macro_block_size = 16
        adjusted_height = math.ceil(total_height/macro_block_size)*macro_block_size
        adjusted_width = math.ceil(total_width/macro_block_size)*macro_block_size

        return adjusted_width, adjusted_height

    def draw_background(self):
        self.draw.rectangle(
            xy=[
                (0, 0),
                (self.image_size[0], self.image_size[1])
            ],
            fill=self.PANEL_BACKGROUND_COLOR
        )

    def draw_content(self):
        self.draw_cells(SynopticPanelSectionCell)
        self.draw_cells(SynopticPanelLabelCell)
        self.draw_spacer()
        self.draw_trains_log()

    def draw_cells(self, cell_type: Type[SynopticPanelBaseCell]) -> None:
        cell_base_x = self.options["margin_left"]
        cell_base_y = self.options["margin_top"]

        for cell in self.grid.cells:
            if isinstance(cell, SynopticPanelSectionCell):
                occupancy = self.frame.occupancy_dict
                cell.trains = occupancy[cell.section["name"]]

            if isinstance(cell, cell_type):
                start_pixels = cell.get_start_pixels()
                x = int(start_pixels[0] + cell_base_x)
                y = int(start_pixels[1] + cell_base_y)

                self.image.paste(cell.generate_cell_image(), (x, y), cell.generate_cell_image())

    def draw_spacer(self):
        """ Draw the spacer between the panel and the train log in the image """
        spacer_size = (self.image_size[0], int(self.options["spacer_height"]))
        spacer_image = Image.new('RGBA', spacer_size, (255, 255, 255, 0))
        spacer_draw = ImageDraw.Draw(spacer_image)
        spacer_draw.rectangle(
            (
                0,  # x1
                int(float(self.options["spacer_height"] - self.options["spacer_line_height"]) / 2),  # y1
                self.image_size[0],  # x2
                int(float(self.options["spacer_height"] + self.options["spacer_line_height"]) / 2)  # y2
            ),
            fill=self.SPACER_COLOR
        )

        grid_size = self.grid.get_size()
        spacer_position = (0, self.options["margin_top"] + grid_size[1])
        self.image.paste(spacer_image, spacer_position, spacer_image)

    def draw_trains_log(self):
        grid_size = self.grid.get_size()
        log_position = (
            int(self.options["margin_left"]),
            int(self.options["margin_top"] + grid_size[1] + self.options["spacer_height"])
        )
        trains_log_image = self.generate_trains_log_image()
        self.image.paste(trains_log_image, log_position, trains_log_image)

    def generate_trains_log_image(self):
        log_size = self.get_train_log_size()

        image = Image.new('RGBA', log_size, (255, 255, 255, 0))

        x, y = 0, 0
        for train in self.frame.trains:
            if x + self.TRAIN_INFO_BLOCK_SIZE[0] >= log_size[0]:
                x = 0
                y += self.TRAIN_INFO_BLOCK_SIZE[1]

            train_log_image = self.draw_single_train_log(train)
            image.paste(train_log_image, (x, y), train_log_image)
            x += self.TRAIN_INFO_BLOCK_SIZE[0]

        return image

    def get_train_log_size(self):
        grid_size = self.grid.get_size()
        trains_per_line = math.floor(float(grid_size[0] / float(self.TRAIN_INFO_BLOCK_SIZE[0])))
        lines = math.ceil(float(self.options['train_log_lines']) / trains_per_line)

        return int(grid_size[0]), int(lines * self.TRAIN_INFO_BLOCK_SIZE[1])

    def draw_single_train_log(self, train):
        image = Image.new('RGBA', self.TRAIN_INFO_BLOCK_SIZE, (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        border_width = 5
        border_position = (border_width, border_width, image.size[0] - border_width, image.size[1] - border_width)
        draw.rectangle(border_position, fill=self.TRAIN_INFO_BLOCK_BACKGROUND_COLOR)
        h1_font, h2_font, h3_font, text_font = H1Font().load(), H2Font().load(), H3Font().load(), RegularFont().load()

        col1_x = border_width + 5
        col2_x = int(self.TRAIN_INFO_BLOCK_SIZE[0] / 2)
        base_y = border_width + 10

        row_height = 35
        spacer_height = 20
        second_line_offset = 15

        heights = {
            "train_title": base_y,
            "train_priority": base_y + 2,
            "row_1_title": base_y + spacer_height,
            "row_1_text": base_y + spacer_height + second_line_offset,
            "row_2_title": base_y + spacer_height + row_height,
            "row_2_text": base_y + spacer_height + second_line_offset + row_height,
            "row_3_title": base_y + spacer_height + row_height * 2,
            "row_3_text": base_y + spacer_height + second_line_offset + row_height * 2,
            "row_4_title": base_y + spacer_height + row_height * 3,
            "row_4_text": base_y + spacer_height + second_line_offset + row_height * 3,
            "row_5_title": base_y + spacer_height + row_height * 4,
            "row_5_text": base_y + spacer_height + second_line_offset + row_height * 4,
            "sections_title": base_y + spacer_height + row_height * 5,
            "sections_line_1": base_y + spacer_height + row_height * 5 + spacer_height,
            "sections_line_2": base_y + spacer_height + row_height * 5 + spacer_height + second_line_offset,
            "sections_line_3": base_y + spacer_height + row_height * 5 + spacer_height + second_line_offset * 2,
        }

        draw.text((col1_x, heights["train_title"]), "TRAIN {}".format(train["prefix"]), font=h1_font)
        draw.text((col2_x, heights["train_priority"]), "PRIORITY: {}".format(train["priority"]), font=text_font)

        # ROW 1

        draw.text((col1_x, heights["row_1_title"]), "head_section", font=h3_font)
        draw.text((col1_x, heights["row_1_text"]), "{}".format(train["current_section"]), font=text_font)

        draw.text((col2_x, heights["row_1_title"]), "relative_position", font=h3_font)
        draw.text((col2_x, heights["row_1_text"]), "{:.5f}".format(train["relative_position"]), font=text_font)

        # ROW 2

        draw.text((col1_x, heights["row_2_title"]), "velocity", font=h3_font)
        draw.text((col1_x, heights["row_2_text"]), "{}".format(train["velocity"]), font=text_font)

        draw.text((col2_x, heights["row_2_title"]), "accumulated_cost", font=h3_font)
        draw.text((col2_x, heights["row_2_text"]), "{:.4f}".format(train["accumulated_cost"]), font=text_font)

        # ROW 3

        draw.text((col1_x, heights["row_3_title"]), "trains_opposite", font=h3_font)
        draw.text((col1_x, heights["row_3_text"]), "{}".format(train["trains_opposite"]), font=text_font)

        draw.text((col2_x, heights["row_3_title"]), "trains_behind", font=h3_font)
        draw.text((col2_x, heights["row_3_text"]), "{}".format(train["trains_behind"]), font=text_font)

        # ROW 4

        draw.text((col1_x, heights["row_4_title"]), "last_action", font=h3_font)
        draw.text((col1_x, heights["row_4_text"]), train["last_action"], font=text_font)

        draw.text((col2_x, heights["row_4_title"]), "executing_action", font=h3_font)
        draw.text((col2_x, heights["row_4_text"]), train["executing_action"], font=text_font)

        # ROW 5

        possible_actions = [action["abbrev"] for action in train["possible_actions"]]
        draw.text((col1_x, heights["row_5_title"]), "possible_actions", font=h3_font)
        draw.text((col1_x, heights["row_5_text"]), "{}".format(",".join(possible_actions)), font=text_font)

        draw.text((col2_x, heights["row_5_title"]), "direction", font=h3_font)
        draw.text(
            (col2_x, heights["row_5_text"]),
            "{}".format("reversed" if train["is_reversed"] else "normal"),
            font=text_font
        )

        # SECTIONS

        draw.text((col1_x, heights["sections_title"]), "Sections", font=h2_font)

        draw.text(
            (col1_x, heights["sections_line_1"]),
            "NEXT_STR={}".format(train["next_straight_section"]),
            font=text_font
        )
        draw.text(
            (col1_x, heights["sections_line_2"]),
            "NEXT_DEV={}".format(train["next_deviated_section"]),
            font=text_font
        )
        draw.text(
            (col1_x, heights["sections_line_3"]),
            "NEXT_TRN={}".format(train["next_turnout_section"]),
            font=text_font
        )
        draw.text(
            (col2_x, heights["sections_line_1"]),
            "PREV_STR={}".format(train["previous_straight_section"]),
            font=text_font
        )
        draw.text(
            (col2_x, heights["sections_line_2"]),
            "PREV_DEV={}".format(train["previous_deviated_section"]),
            font=text_font
        )
        draw.text(
            (col2_x, heights["sections_line_3"]),
            "PREV_TRN={}".format(train["previous_turnout_section"]),
            font=text_font
        )

        return image
