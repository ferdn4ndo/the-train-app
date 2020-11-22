import logging
from typing import List

from app.simulation.model.section import Section
from app.simulation.model.sections_mapper import SectionsMapper


class Route:
    def __init__(self, logger: logging.Logger = None, start_sections: List = None, name: str = "Unnamed Route"):
        """Class constructor. Sets logger, name and sections."""
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.name = name

        self.sections_mapper = SectionsMapper(logger=self.logger, sections=start_sections)

    def parse_sections_list(self, sections):
        """Parses a list of dicts, each one representing one section with it's arguments and values"""
        self.sections_mapper.read_sections([Section(**section_data) for section_data in sections])

    def serialize(self):
        return {
            'name': self.name,
            'sections_mapper': self.sections_mapper.serialize(),
        }
