from app.simulation.action.base import BaseAction
from app.simulation.model.section import Section


class ReverseAction(BaseAction):
    name = "reverse"
    abbrev = "REV"

    @staticmethod
    def is_applicable(dispatcher, train):
        """Overrides the parent action to define the criteria for ReverseAction application"""

        # strategy: may reverse if reached route ends in current direction or all the following sections are blocked and
        # train is at a straight section

        in_straight_section = not train.current_head_section.is_turnout()
        all_next_sections_blocked = all(
            dispatcher.is_section_occupied(section, train.is_reversed)
            for section in dispatcher.sections_mapper.get_next_sections(train.current_head_section, train.is_reversed)
        )

        return (
            len(dispatcher.sections_mapper.get_next_sections(train.current_head_section, train.is_reversed)) == 0 or
            (in_straight_section and all_next_sections_blocked)
        )

        # strategy: may reverse if no possible route between train head section and its destiny
        """
        return dispatcher.sections_mapper.count_total_routes_between_sections(
            train.current_head_section, train.options.finish_section, train.is_reversed
        ) == 0
        """

        # strategy: may reverse if there's a an available section behind
        """
        previous_straight_section_available = not dispatcher.is_section_occupied(
            train.previous_straight_section,
            not train.is_reversed  # we use the inverse of current because we want to check after possibly reversing
        ) if train.previous_straight_section is not None else False

        previous_deviated_section_available = not dispatcher.is_section_occupied(
            train.previous_deviated_section,
            not train.is_reversed  # we use the inverse of current because we want to check after possibly reversing
        ) if train.previous_deviated_section is not None else False

        return previous_straight_section_available is not None or previous_deviated_section_available is not None
        """

    def execute(self, dispatcher, train):
        """Overrides the base action execution to perform the train action of wait for crossing"""
        if not train.is_at_section_end():
            train.go_at_maximum_speed()
            return

        train.is_reversed = not train.is_reversed
        train.section_start = (
            Section.SECTION_START_STRAIGHT
            if train.section_start in (Section.SECTION_END_STRAIGHT, Section.SECTION_END_DEVIATED)
            else Section.SECTION_END_STRAIGHT
        )
        self.executed = True
