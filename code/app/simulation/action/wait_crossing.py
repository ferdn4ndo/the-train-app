from app.simulation.action.base import BaseAction


class WaitCrossingAction(BaseAction):
    name = "wait_for_crossing"
    abbrev = "WCR"

    def __init__(self):
        super().__init__()

        self.lookup_train = None

    @staticmethod
    def is_applicable(dispatcher, train):
        """Overrides the parent action to define the criteria for WaitCrossingAction application"""
        next_is_turnout = train.next_straight_section is not None and train.next_straight_section.is_turnout()
        if not next_is_turnout:
            return False

        # check if all other trains ahead are executing the WaitCrossingAction
        all_other_trains_ahead_waiting_crossing = all([
            type(other_train.executing_action) == WaitCrossingAction
            for other_train in train.trains_ahead
        ])

        has_available_siding = any([
            dispatcher.is_route_available(route, train.is_reversed)
            for route in train.routes_between_closest_turnouts
        ])

        return (
            has_available_siding and
            len(train.routes_between_closest_turnouts) > 1 and
            len(train.trains_ahead) > 0 and
            not all_other_trains_ahead_waiting_crossing
        )

    def execute(self, dispatcher, train):
        """Overrides the base action execution to perform the train action of wait for crossing"""
        train.keep_train_going_if_not_at_section_end()
        if self.lookup_train is None and len(train.trains_ahead) > 0:
            self.lookup_train = train.trains_ahead[0]
        self.executed = len(train.trains_ahead) == 0 or self.lookup_train not in train.trains_ahead

    def describe(self):
        return "Wait. CRS with {}".format(self.lookup_train.prefix if self.lookup_train is not None else '---')
