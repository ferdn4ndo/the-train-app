from app.common.logger import generate_logger, LoggerFolders
from app.simulation.exception.error import ConflictConditionError


class BaseAction:
    name = "none"
    abbrev = "---"

    def __init__(self):
        """Class constructor"""
        self.moving_towards_section = ""
        self.lookup_train_prefix = ""
        self.executed = False

    @staticmethod
    def is_applicable(dispatcher, train):
        """Define the criteria for the action application (should be overridden by children)"""
        return True

    def was_executed(self, train):
        """Define the criteria for the action to be considered executed (could be overridden by children)"""
        return self.executed

    def serialize(self):
        return {
            "name": self.name,
            "abbrev": self.abbrev,
            "executed": self.executed,
            "description": self.describe()
        }

    def describe(self):
        """Define the message to describe the action (should be overridden by children)"""
        return "No action (idle)"

    def execute(self, dispatcher, train):
        """Define the action execution method (should be overridden by children)"""
        self.executed = True

    def move_to(self, dispatcher, train, next_section=None):
        """Helper function to be used by functions that moves a train from a section to another"""
        self.moving_towards_section = next_section.name if next_section is not None else ''

        if not train.is_at_section_end():
            train.go_at_maximum_speed()
            return
        train.stop()

        # if reached section end and there's no next straight section to move, raise error
        if next_section is None:
            raise ConflictConditionError("Tried to move into a non-existing section")

        # if section is not occupied, move the train to it
        if not dispatcher.is_section_occupied(next_section, train.is_reversed):
            dispatcher.move_train_to_section(train, next_section)

        # in any case (being moved to the new section or not due to its occupancy), mark the action as executed
        self.executed = True
