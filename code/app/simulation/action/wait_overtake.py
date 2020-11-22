from app.simulation.action.base import BaseAction


class WaitOvertakeAction(BaseAction):
    name = "wait_for_overtake"
    abbrev = "WOT"

    def __init__(self):
        super().__init__()

        self.lookup_train = None

    @staticmethod
    def is_applicable(dispatcher, train):
        """Overrides the parent action to define the criteria for WaitOvertakeAction application"""
        # it may not be executed until the train is about to enter in the next turnout and the turnout is closing
        if not train.is_at_turnout_closing():
            return False

        return (
            len(train.routes_between_closest_turnouts) > 1 and
            any(
                dispatcher.is_route_available(route, train.is_reversed)
                for route in train.routes_between_closest_turnouts
            ) and
            len(train.trains_behind) > 0 and
            train.has_higher_priority_trains_behind()
        )

    def execute(self, dispatcher, train):
        """Overrides the base action execution to perform the train action of wait for overtake"""
        train.keep_train_going_if_not_at_section_end()
        if self.lookup_train is None and len(train.trains_behind) > 0:
            self.lookup_train = train.trains_behind[0]
        self.executed = len(train.trains_behind) == 0 or self.lookup_train not in train.trains_behind

    def describe(self):
        return "Wait. OVT by {}".format(self.lookup_train.prefix if self.lookup_train is not None else '---')
