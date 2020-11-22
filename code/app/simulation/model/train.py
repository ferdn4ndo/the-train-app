import logging
import random
import string
from typing import List

from app.common.options import BaseOptions
from app.simulation.math.dynamics import TimeDynamics
from app.simulation.math.equation import TrainEquation
from app.simulation.model.section import Section


class TrainOptions(BaseOptions):
    """Base class for setting/getting train options"""
    action_cost: float = 100
    allow_reverse_action: bool = False
    cost_normalizer: float = 1e-9
    direction: str = 'normal'  # normal | reverse
    distance_to_goal_cost: float = 0.5
    finish_section: Section = None
    length: int = 100
    may_invade_interdicted_sections = False
    meter_travelled_cost: float = 0.2
    prefix: str = None
    prefix_format: str = 'A00'
    priority: int = 1  # min: 1
    start_relative_position = 0.5
    start_section: Section = None
    stopped_time_cost: float = 0.3
    time_dynamics: TimeDynamics = None
    traveling_time_cost: float = 0.4
    weight: float = 1e6


class Train:

    def __init__(
        self,
        **options
    ):
        """Train class constructor"""
        self.logger = logging.getLogger(__name__)
        self.options = TrainOptions(**options)

        self.executing_action = None

        self.time_dynamics = self.options.time_dynamics
        self.train_equation = TrainEquation(self.options)
        self.rolling_stock = []

        self.current_head_section = self.options.start_section
        self.current_tail_section = None
        self.section_start = Section.SECTION_END_STRAIGHT

        self.routes_between_closest_turnouts = []
        self.next_straight_section = None
        self.next_deviated_section = None
        self.next_turnout_section = None
        self.previous_straight_section = None
        self.previous_deviated_section = None
        self.previous_turnout_section = None
        self.possible_actions = []

        self.trains_ahead: List[Train] = []
        self.trains_behind: List[Train] = []

        self.actions_queue = []
        self.actions_history = []
        self.sections_history = []

        self.acceleration_leveler = 0.0  # -1.0 to +1.0
        self.odometer = 0.0  # [m]
        self.traveling_time = 0.0  # [s]
        self.stopped_time = 0.0  # [s]

        self.last_accumulated_cost = 0.0
        self.accumulated_cost = 0.0
        self.instant_cost = 0.0

        self.relative_position = self.options.start_relative_position
        self.operative = True

        self.prefix = self.options.prefix
        if self.prefix is None:
            self.prefix = self.generate_random_prefix()

        self.is_reversed = False if self.options.direction == 'normal' else True

    def __repr__(self):
        """As the prefix is the unique index, we use it to display a Train object"""
        return "<Train_{}>".format(self.prefix)

    def serialize(self):
        """Serializes the train"""
        return {
            "prefix":
                self.prefix,
            "possible_actions":
                [{"name": action.name, "abbrev": action.abbrev} for action in self.possible_actions],
            "executing_action":
                self.executing_action.describe()
                if self.executing_action is not None else "---",
            "last_action":
                self.actions_history[-2]["data"]["abbrev"] if len(self.actions_history) > 1 else "---",
            "is_reversed":
                self.is_reversed,
            "direction":
                self.options.direction,
            "priority":
                self.options.priority,
            "accumulated_cost":
                self.accumulated_cost,
            "instant_cost":
                self.instant_cost,
            "finished":
                self.has_finished(),
            "velocity":
                "{:.4f} km/h".format(self.train_equation.velocity.value * 3.6),
            "trains_opposite":
                ", ".join([train.prefix for train in self.trains_ahead]),
            "trains_behind":
                ", ".join([train.prefix for train in self.trains_behind]),
            "current_section":
                self.current_head_section.name,
            "relative_position":
                self.relative_position,
            "next_straight_section":
                self.next_straight_section.name if self.next_straight_section is not None else "",
            "next_deviated_section":
                self.next_deviated_section.name if self.next_deviated_section is not None else "",
            "next_turnout_section":
                self.next_turnout_section.name if self.next_turnout_section is not None else "",
            "previous_straight_section":
                self.previous_straight_section.name if self.previous_straight_section is not None else "",
            "previous_deviated_section":
                self.previous_deviated_section.name if self.previous_deviated_section is not None else "",
            "previous_turnout_section":
                self.previous_turnout_section.name if self.previous_turnout_section is not None else "",
            "routes_between_closest_turnouts":
                self.routes_between_closest_turnouts,
            "is_at_turnout_closing":
                self.is_at_turnout_closing(),
            "has_higher_priority_trains_behind":
                self.has_higher_priority_trains_behind(),
        }

    def stop(self):
        """Stops the train"""
        self.train_equation.desired_velocity = 0.0

    def generate_random_prefix(self):
        """Generates a random prefix for the train"""
        generated_prefix = []

        for char in self.options.prefix_format:
            if char == 'A':
                generated_prefix.append(random.choice(string.ascii_uppercase))
            elif char == '0':
                generated_prefix.append(random.choice(string.digits))

        return "".join(generated_prefix)

    def step(self):
        """Performs the calculations for a simulation step"""
        self.check_condition()
        self.train_equation.update_velocity()
        self.update_position()

        if self.operative:
            self.check_executing_action()

        self.update_times()
        self.log_status()

    def check_condition(self):
        """Check if the train is operative"""
        self.operative = True
        for unit in self.rolling_stock:
            if not unit.is_operative():
                self.operative = False
                break

    def update_position(self):
        """Update trains relative position to section (and also the odometer)"""
        new_position = self.train_equation.calculate_next_step_position(
            self.current_head_section.length,
            self.relative_position
        )

        if new_position < 0:
            new_position = 0.0
        elif new_position > 1:
            new_position = 1.0

        self.odometer += abs(self.current_head_section.length * (new_position - self.relative_position))
        self.relative_position = new_position

    def is_at_section_end(self):
        """Check if train is at current section end"""
        return (
            (self.relative_position <= 0.0000 and self.is_reversed) or
            (self.relative_position >= 1.0000 and not self.is_reversed)
        )

    def check_executing_action(self):
        """Checks the completion of current executing action"""
        if self.executing_action is not None and self.executing_action.was_executed(self):
            self.executing_action = None

        if self.executing_action is None:
            # ensure to put train in a stopped state if no action is taken
            self.stop()

            # set the next action to be executed
            self.set_next_action()

    def set_next_action(self):
        """Sets next action to be executed"""
        # if there's no possible action to take for next, skip
        if len(self.possible_actions) == 0:
            return

        # if there's an action queue and it's in the possible list, execute it. Else just discard.
        if len(self.actions_queue) > 0:
            selected_action = self.actions_queue.pop(0)
            if selected_action in self.possible_actions:
                self.set_action(selected_action)
                return

        # by default, take a random action
        self.set_action(random.choice(self.possible_actions))

    def go_at_maximum_speed(self):
        """Sets the desired velocity to the maximum possible one for current section/position"""
        max_km_h = self.current_head_section.maximum_velocity_at_relative_position(self.relative_position)
        self.train_equation.desired_velocity = (max_km_h / 3.6) * (1 if not self.is_reversed else -1)

    def set_action(self, action):
        """Sets the train executing action"""
        current_section = self.current_head_section
        self.executing_action = action()

        self.actions_history.append({
            'step': self.time_dynamics.current_step,
            'data': self.executing_action.serialize(),
            'at_section': current_section.name,
            'at_position': self.relative_position,
            'reversed': self.is_reversed,
            'accumulated_cost': self.accumulated_cost,
            'instant_cost': self.instant_cost,
        })

        self.logger.debug("Train {} took {} action at {:.2f} of section {} @ step {}".format(
            self.prefix, action.name, self.relative_position, current_section.name, self.time_dynamics.current_step
        ))

    def update_times(self):
        """Updates train time recorders"""
        if self.train_equation.velocity != 0:
            self.traveling_time += self.time_dynamics.step_duration
        else:
            self.stopped_time += self.time_dynamics.step_duration

    def log_status(self):
        """Logs train status"""
        self.logger.debug(
            'STEP #{} - {} - Train {} is at {:.2f}% of {} (velocity: {:.2f} m/s) [TOTAL COST: {}]'.format(
                self.time_dynamics.current_step,
                'TRAIN_STATUS',
                self.prefix,
                self.relative_position * 100.0,
                self.current_head_section.name,
                self.train_equation.velocity.value,
                self.accumulated_cost
            )
        )

    def has_finished(self):
        """Determine if train has finished its trip"""
        if self.options.finish_section is None or self.current_head_section != self.options.finish_section:
            return False

        return self.relative_position <= 0.5 if self.is_reversed else self.relative_position >= 0.5

        # end_section_length = self.options.finish_section.length
        # if self.is_reversed:
        #     return self.relative_position <= 1 - ((end_section_length - self.options.length) / end_section_length)
        #
        # return self.relative_position >= 1 - (self.options.length / end_section_length)

    def is_at_turnout_closing(self):
        """Determines if the train is about to enter a turnout closing section"""
        if self.next_straight_section is None or not self.next_straight_section == self.next_turnout_section:
            return False

        connections_after = 'end' if not self.is_reversed else 'start'
        connections_before = 'start' if not self.is_reversed else 'end'

        return (
            len(self.next_turnout_section.accessible_connections(connections_after)) == 1 and
            len(self.next_turnout_section.accessible_connections(connections_before)) > 1
        )

    def has_higher_priority_trains_behind(self):
        """Determines if there are any higher priority trains behind self one"""
        return any([train_behind.options.priority >= self.options.priority for train_behind in self.trains_behind])

    def keep_train_going_if_not_at_section_end(self):
        if not self.is_at_section_end():
            self.go_at_maximum_speed()
        else:
            self.stop()
