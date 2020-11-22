from typing import List

from PIL import Image
from PIL import ImageDraw

from app.common.logger import generate_logger, LoggerFolders
from app.simulation.model.simulation_frame import SimulationFrame


class BaseGraph:
    default_options = {}

    def __init__(self, sections: List, frame: SimulationFrame, **options):
        self.options = {}
        self.set_options(options)

        self.frame = frame
        self.logger = generate_logger(frame.simulation_uuid, LoggerFolders.SIMULATIONS)

        self.sections_names = [section['name'] for section in sections]
        self.image_size = self.get_content_size()

        self.image: Image = None
        self.draw: ImageDraw = None
        self.reset()

    def reset(self):
        self.image = Image.new("RGB", self.image_size, (255, 255, 255))
        self.draw = ImageDraw.Draw(self.image)

    def set_options(self, options):
        defaults = self.default_options
        defaults.update(options)
        self.options = defaults

    def get_content_size(self):
        return 0, 0

    def draw_background(self):
        pass

    def draw_content(self):
        pass

    def render(self) -> Image:
        self.reset()
        self.draw_background()
        self.draw_content()
        return self.image

    def show(self):
        self.render().show()
