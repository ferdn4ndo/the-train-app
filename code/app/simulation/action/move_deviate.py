from app.simulation.action.base import BaseAction


class MoveDeviateAction(BaseAction):
    name = "move_to_deviated"
    abbrev = "MDV"

    @staticmethod
    def is_applicable(dispatcher, train):
        """Overrides the parent action to define the criteria for MoveDeviateAction application"""
        return (
            train.next_deviated_section is not None and
            not dispatcher.is_section_occupied(train.next_deviated_section, train.is_reversed)
        )

    def execute(self, dispatcher, train):
        """Overrides the base action execution to perform the train movement to the next deviated section"""
        self.move_to(dispatcher, train, train.next_deviated_section)

    def describe(self):
        return "Mov. dev. to {}".format(self.moving_towards_section)
