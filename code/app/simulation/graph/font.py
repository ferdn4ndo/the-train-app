import os

from PIL import ImageFont


class BaseFont:
    FONTS_DIR = "fonts"  # relative to this file

    def __init__(self, filename="roboto/Roboto-Condensed.ttf", size=12):
        self.path = os.path.join(os.path.dirname(__file__), self.FONTS_DIR, filename)
        self.size = size

    def load(self):
        return ImageFont.truetype(font=self.path, size=self.size)


class RegularFont(BaseFont):
    def __init__(self):
        super().__init__(size=12)


class H1Font(BaseFont):

    def __init__(self):
        super().__init__("roboto/Roboto-Black.ttf", 14)


class H2Font(BaseFont):

    def __init__(self):
        super().__init__("roboto/Roboto-BoldCondensed.ttf", 14)


class H3Font(BaseFont):

    def __init__(self):
        super().__init__("roboto/Roboto-BoldCondensed.ttf", 12)
