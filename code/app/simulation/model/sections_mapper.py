import copy
import math
from logging import Logger
from typing import List

from app.simulation.exception.error import ConflictConditionError, NotFoundError
from app.simulation.model.section import Section
from app.common.cache import Cache


class SectionsMapper:
    CACHE_MODULE = 'sections_mapper'

    def __init__(self, logger: Logger = None, sections: List[Section] = None):
        """Class constructor"""
        self.logger = logger
        self.sections = []
        self.cache_module_name = 'SectionsMapper'
        self.read_sections(sections)

    def serialize(self):
        """Serializer function"""
        return {
            'sections': [section.serialize() for section in self.sections],
            'cache_keys': [key for key in Cache.list_keys(self.cache_module_name)],
        }

    def read_sections(self, sections: List):
        """Stores a list of sections and checks the route integrity"""
        if sections is None:
            sections = []
        self.sections = sections
        self.cache_module_name = 'SectionsMapper_{}'.format(','.join([section.name for section in sections]))

    def check_integrity(self):
        """
        Check the integrity of the route sections (if every endpoint is interconnected through the same amount of
        routes from each direction)
        """
        start_endpoints = [
            section for section in self.sections
            if not section.accessible_connections("start")
        ]
        for start_endpoint in start_endpoints:
            self.check_endpoint_integrity(start_endpoint)

        end_endpoints = [
            section for section in self.sections
            if not section.accessible_connections("end")
        ]
        for end_endpoint in end_endpoints:
            self.check_endpoint_integrity(end_endpoint, look_reversed=True)
        self.logger.info("Finished integrity check for the route.")

    def get_next_sections(self, from_section: Section, is_reversed=False):
        """Gets the list of next connected sections from a given section and a direction"""
        connection_origin = "start" if is_reversed else "end"
        next_sections_name = from_section.accessible_connections(connection_origin)
        return [next_section for next_section in self.sections if next_section.name in next_sections_name]

    def get_previous_sections(self, from_section: Section, is_reversed=False):
        """Gets the list of previous connected sections from a given section and a direction"""
        connection_origin = "end" if is_reversed else "start"
        previous_sections_name = from_section.accessible_connections(connection_origin)
        return [next_section for next_section in self.sections if next_section.name in previous_sections_name]

    def get_all_sections_before(self, from_section: Section, is_reversed=False):
        """Gets all the sections before a given one and a direction"""
        sections_before = [section.name for section in self.get_previous_sections(from_section, is_reversed)]

        for section in self.get_previous_sections(from_section, is_reversed):
            sections_before.extend(self.get_all_sections_before(section, is_reversed))

        return list(set(sections_before))

    def get_all_sections_after(self, from_section: Section, is_reversed=False):
        """Gets all the sections after a given one and a direction"""
        sections_after = [section.name for section in self.get_next_sections(from_section, is_reversed)]

        for section in self.get_next_sections(from_section, is_reversed):
            sections_after.extend(self.get_all_sections_after(section, is_reversed))

        return list(set(sections_after))

    def get_routes_between_sections(
        self,
        start_section: Section,
        end_section: Section,
        is_reversed=False,
        chain: List = None,
    ):
        """
        Returns a list of lists, each one representing a set of sections that describes a possible route between
        the start section and the end section.
        """
        if start_section is None or end_section is None:
            return []

        cache_key = "get_routes_between_sections_{}_{}_{}_{}".format(
            start_section.name, end_section.name, is_reversed,
            ';'.join(chain) if chain is not None else '[]'
        )
        if Cache.get_from_key(self.cache_module_name, cache_key) is not None:
             return Cache.get_from_key(self.cache_module_name, cache_key)

        routes = []

        # appends current section to the chain
        if chain is None:
            chain = []
        chain.append(start_section.name)

        # reached the goal, appends current chain to the routes list and early return
        if start_section == end_section:
            routes.append(copy.deepcopy(chain))
            return routes

        # if not reached the goal, iterate recursively through the next possible sections ...
        for next_section in self.get_next_sections(start_section, is_reversed):
            next_routes = self.get_routes_between_sections(next_section, end_section, is_reversed, copy.deepcopy(chain))
            # ... extending the list of routes with any of the connections that reaches the goal
            if next_routes:
                routes.extend(next_routes)

        # finally return the list of routes
        Cache.save_to_key(self.cache_module_name, cache_key, routes)
        return routes

    def get_distance_between_sections(self, start_section, end_section, is_reversed=False):
        """Returns the minimum possible route distance between two sections and a direction"""
        cache_key = "get_distance_between_sections_{}_{}_{}".format(start_section.name, end_section.name, is_reversed)
        if Cache.get_from_key(self.cache_module_name, cache_key) is not None:
            return Cache.get_from_key(self.cache_module_name, cache_key)

        routes = self.get_routes_between_sections(start_section, end_section, is_reversed)
        routes_lengths = [
            sum([self.find_section_by_name(section).length for section in route])
            for route in routes
        ]
        if not routes_lengths:
            return math.inf
        min_distance = min(routes_lengths)

        Cache.save_to_key(self.cache_module_name, cache_key, min_distance)
        return min_distance

    def count_total_routes_between_sections(self, start_section, end_section, is_reversed=False):
        """Returns the number of routes between two given sections"""
        return len(self.get_routes_between_sections(start_section, end_section, is_reversed))

    def check_endpoint_integrity(self, endpoint: Section, look_reversed=False):
        """
        Checks the integrity of an endpoint (if it's reachable by the same amount of other endpoints on both directions)
        """
        opposite_origin = "start" if look_reversed else "end"
        opposite_endpoints = [
            section for section in self.sections
            if not section.accessible_connections(opposite_origin) and not section == endpoint
        ]

        for destiny_section in opposite_endpoints:
            routes_normal = self.count_total_routes_between_sections(endpoint, destiny_section, look_reversed)
            routes_opposite = self.count_total_routes_between_sections(destiny_section, endpoint, not look_reversed)

            if routes_normal != routes_opposite:

                for section in self.sections:
                    print(section.name)
                    print("section: {} endpoint: {} destiny_section: {} look_reverded: {}".format(
                        section.name, endpoint.name, destiny_section.name, look_reversed
                    ))
                    print(self.get_routes_between_sections(endpoint, destiny_section, look_reversed))
                    print(self.get_routes_between_sections(destiny_section, endpoint, not look_reversed))



                raise ConflictConditionError(
                    "Conectivity integrity error: starting at section {} and ending at section {}, there are {} routes in normal direction, and {} in the opposite one."
                    .format(endpoint.name, destiny_section.name, routes_normal, routes_opposite)
                )

    def find_section_by_name(self, section_name):
        """Finds one section by its name"""
        for section in self.sections:
            if section.name == section_name:
                return section
        raise NotFoundError("Section {} wasn't found!".format(section_name))

    def get_next_turnout(self, from_section: Section, is_reversed=False):
        """Gets the first next turnout section ahead from a given section and a direction"""
        cursor_at = from_section
        while True:
            if cursor_at.is_turnout():
                return cursor_at

            if not len(self.get_next_sections(cursor_at, is_reversed)):
                return None

            cursor_at = self.get_next_sections(cursor_at, is_reversed)[0]

    def get_previous_turnout(self, from_section: Section, is_reversed=False):
        """Gets the first previous turnout section behind a given section and a direction"""
        cursor_at = from_section
        while True:
            if cursor_at.is_turnout():
                return cursor_at

            if not len(self.get_previous_sections(cursor_at, is_reversed)):
                return None

            cursor_at = self.get_previous_sections(cursor_at, is_reversed)[0]
