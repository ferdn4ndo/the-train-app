from PIL import Image, ImageDraw

from app.simulation.exception.error import InvalidChoiceError
from app.simulation.graph.font import RegularFont, H1Font


class SynopticPanelBaseCell:
    """Base cell class for a synoptic panel graph"""

    CELL_SIZE = 50  # px
    OUTLINE_SIZE = 2  # px

    def __init__(self, section, x_index=0, y_index=0):
        """Class constructor"""
        self.section = section
        self.x_index, self.y_index = x_index, y_index

    def get_start_pixels(self):
        """Retrieves a tuple with the start points (x,y) to draw the cell"""
        return self.x_index * self.CELL_SIZE, self.y_index * self.CELL_SIZE

    def generate_cell_image(self):
        """Generates the cell image"""
        image = Image.new('RGBA', (self.CELL_SIZE, self.CELL_SIZE), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        draw.line((0, 0) + image.size, fill=128)
        draw.rectangle((0, 0) + image.size, outline=128)
        return image


class SynopticPanelLabelCell(SynopticPanelBaseCell):
    """Class used to represent a label cell in a synoptic panel"""

    def generate_cell_image(self):
        """Overrides the original cell image generation method to draw a cell label"""
        image = Image.new('RGBA', (self.CELL_SIZE, self.CELL_SIZE), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        font = RegularFont().load()
        text = self.section['name']
        text_size = font.getsize(text)

        draw.rectangle(
            (
                (self.CELL_SIZE - text_size[0] - 10) / 2,
                3,
                (self.CELL_SIZE + text_size[0] + 10) / 2,
                20
            ),
            fill=(0, 0, 0),
            outline=128,
            width=2
        )
        draw.text(
            (
                (self.CELL_SIZE - text_size[0]) / 2,
                5,
            ),
            text,
            font=font
        )
        return image


class SynopticPanelSectionCell(SynopticPanelBaseCell):
    """Class used to represent a section cell in a synoptic panel"""

    FILL_OPTIONS = [
        "full",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
    ]

    CONNECTS_ON_OPTIONS = [
        "none",
        "left",
        "right",
        "both"
    ]

    OCCUPANCY_FILL_COLOR = (176, 63, 55)
    OCCUPANCY_BORDER_COLOR = (107, 35, 30)
    BACKGROUND_FILL_COLOR = (50, 50, 50, 255)  # 323232
    BACKGROUND_BORDER_COLOR = (77, 77, 77, 255)  # 040e17

    def __init__(
        self,
        section,
        x_index=0,
        y_index=0,
        connects_on="none",
        fill="full",
        section_position_start=0.0,
        section_position_end=1.0
    ):
        """Overrides parent class constructor to add pertinent options"""
        super().__init__(section, x_index, y_index)
        self.section_position_start = section_position_start
        self.section_position_end = section_position_end
        self.trains = []
        self.connects_on = connects_on
        self.fill = fill

        if connects_on not in self.CONNECTS_ON_OPTIONS:
            raise InvalidChoiceError("Unknown value '{}' for 'connects_on' property".format(connects_on))

        if fill not in self.FILL_OPTIONS:
            raise InvalidChoiceError("Unknown value '{}' for 'fill' property".format(fill))

    def is_occupied(self):
        """Check if the section cell is occupied by any train"""
        for train in self.trains:
            if self.section_position_start <= train["relative_position"] <= self.section_position_end:
                return True
        return False

    def generate_cell_image(self):
        """Overrides the original cell image generation method to draw a section label"""
        image = Image.new('RGBA', (self.CELL_SIZE, self.CELL_SIZE), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        if self.fill == "full":
            self.generate_full_cell(draw)
            return image

        rotate_angle = 0
        if self.fill == "top-right":
            rotate_angle = 270
        elif self.fill == "bottom-right":
            rotate_angle = 180
        elif self.fill == "bottom-left":
            rotate_angle = 90

        self.generate_quarter_cell(draw)
        image = image.rotate(rotate_angle)

        return image

    def generate_full_cell(self, draw):
        """Draw a section cells that occupies the whole rectangle"""
        coordinates = [
            # start
            (0, 0),
            # end
            (self.CELL_SIZE - 0, self.CELL_SIZE - 0)
        ]

        draw.rectangle(
            coordinates,
            fill=(self.BACKGROUND_FILL_COLOR if not self.is_occupied() else self.OCCUPANCY_FILL_COLOR),
            outline=(self.BACKGROUND_BORDER_COLOR if not self.is_occupied() else self.OCCUPANCY_BORDER_COLOR),
            width=self.OUTLINE_SIZE
        )

        if self.is_occupied():
            font = H1Font().load()
            prefix = self.trains[0]["prefix"] if len(self.trains) == 1 else "[...]"
            text_size = font.getsize(prefix)
            draw.text(
                (
                    (self.CELL_SIZE - text_size[0]) / 2,
                    22,
                ),
                prefix,
                font=font
            )
            self.draw_trains_direction(draw)

    def draw_trains_direction(self, draw):
        """Draw the trains direction in a given cell ('<', '>' or '<>')"""
        font = H1Font().load()
        sign = "<>"

        directions = [train["is_reversed"] for train in self.trains]
        if all(directions) or not any(directions):
            sign = "<" if self.trains[0]["is_reversed"] else ">"

        text_size = font.getsize(sign)
        draw.text(
            (
                (self.CELL_SIZE - text_size[0]) / 2,
                32,
            ),
            sign,
            font=font
        )

    def generate_quarter_cell(self, draw):
        """Draw a section cells that occupies just one triangle (quarter) of the whole cell rectangle"""
        points = [
            (0, 0),
            (0, self.CELL_SIZE),
            (self.CELL_SIZE, 0)
        ]
        draw.polygon(
            points,
            fill=(self.BACKGROUND_FILL_COLOR if not self.is_occupied() else self.OCCUPANCY_FILL_COLOR),
            outline=(self.BACKGROUND_BORDER_COLOR if not self.is_occupied() else self.OCCUPANCY_BORDER_COLOR),
        )
