from app.simulation.action.base import BaseAction


class MoveStraightAction(BaseAction):
    name = "move_straight"
    abbrev = "MST"

    def __init__(self):
        super().__init__()

    @staticmethod
    def is_applicable(dispatcher, train):
        """Overrides the parent action to define the criteria for MoveStraightAction application"""
        return (
            train.next_straight_section is not None and
            not dispatcher.is_section_occupied(train.next_straight_section, train.is_reversed)
        )

    def execute(self, dispatcher, train):
        """Overrides the base action execution to perform the train movement to the next straight section"""
        self.move_to(dispatcher, train, train.next_straight_section)

    def describe(self):
        return "Mov. str. to {}".format(self.moving_towards_section)
