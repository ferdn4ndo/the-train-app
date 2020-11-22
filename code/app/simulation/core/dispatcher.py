import math
from typing import List

from app.common.logger import generate_logger, LoggerFolders
from app.simulation.exception.error import ConflictConditionError
from app.simulation.math.dynamics import TimeDynamics
from app.simulation.action.all import ALL_POSSIBLE_ACTIONS, find_action
from app.simulation.model.section import Section
from app.simulation.model.sections_mapper import SectionsMapper
from app.simulation.model.train import Train


class Dispatcher:

    def __init__(
        self,
        simulation_uuid,
        time_dynamics: TimeDynamics,
        sections_mapper: SectionsMapper,
        trains_queue,
        trains_actions
    ):
        """Class constructor"""
        self.simulation_uuid = simulation_uuid
        self.time_dynamics = time_dynamics
        self.sections_mapper = sections_mapper
        self.trains_queue = trains_queue
        self.trains_actions = trains_actions

        self.logger = generate_logger(self.simulation_uuid, LoggerFolders.SIMULATIONS)

        self.trains = []
        self.steps_without_movement = 0
        self.last_positions = []
        self.occupancy_dict = {section.name: [] for section in sections_mapper.sections}

    def step(self):
        """Performs a full step calculation"""
        self.check_trains_to_add()
        self.update_occupancy_dict()
        self.trains[:] = [train for train in self.trains if not train.has_finished()]

        for train in self.trains:
            train.step()
            if train.executing_action is not None:
                train.executing_action.execute(self, train)
            self.update_train_sections(train)
            self.update_occupancy_dict()
            self.update_train_possible_actions(train)
            self.update_related_trains(train)
            self.update_train_cost(train)

        # Update the number of steps without train movement only if there are actually trains in the route
        if len(self.trains):
            self.update_steps_without_movement()
        else:
            self.steps_without_movement = 0

    def check_trains_to_add(self):
        """Check the list of trains to be added and - if ready - adds it"""
        if not len(self.trains_queue):
            return

        trains_to_add = [train for train in self.trains_queue if self.is_train_ready_to_be_added(train)]
        self.trains_queue = [train for train in self.trains_queue if not self.is_train_ready_to_be_added(train)]

        for train in trains_to_add:
            added_train = self.add_generic_train(**train)
            actions = next(iter([
                actions for prefix, actions in self.trains_actions.items()
                if prefix == train['prefix']
            ]), None)

            if actions is not None:
                added_train.actions_queue = [find_action(action) for action in actions]

    def is_train_ready_to_be_added(self, train):
        """Determines if a train is ready to be added in the simulation"""
        train_start_section = self.sections_mapper.find_section_by_name(train['start_section'])
        is_reversed = False if 'direction' not in train else False if train['direction'] == 'normal' else True

        if 'step_to_add' in train:
            return self.time_dynamics.current_step >= train['step_to_add'] and not self.is_section_occupied(
                train_start_section, is_reversed
            )
        return not self.is_section_occupied(train_start_section, is_reversed)

    def is_section_occupied(self, section: Section, is_reversed=False):
        """Determines if a given section is occupied"""
        if section.is_turnout() and not len(self.occupancy_dict[section.name]):
            return True if all(
                self.is_section_occupied(next_section, is_reversed)
                for next_section in self.sections_mapper.get_next_sections(section, is_reversed)
            ) else False
        return True if len(self.occupancy_dict[section.name]) else False

    def is_route_available(self, sections_names: List[str] = None, is_reversed=False):
        """Determines if a given route (a list of section names) has all the sections available (not occupied)"""
        if sections_names is None:
            sections_names = []

        sections = [self.sections_mapper.find_section_by_name(section_name) for section_name in sections_names]

        return True if all([not self.is_section_occupied(section, not is_reversed) for section in sections]) else False

    def add_generic_train(self, start_section: str, end_section: str, **train_options):
        """Adds a train to the route"""
        start_section_obj = self.sections_mapper.find_section_by_name(start_section)
        end_section_obj = self.sections_mapper.find_section_by_name(end_section)

        train = Train(
            dispatcher=self,
            time_dynamics=self.time_dynamics.clone(),
            start_section=start_section_obj,
            finish_section=end_section_obj,
            **train_options
        )

        if train.options.prefix in self.trains_actions:
            actions = self.trains_actions[train.options.prefix]
            train.actions_queue = [find_action(action) for action in actions]

        if self.is_section_occupied(train.options.start_section, train.is_reversed):
            raise ConflictConditionError("Error while adding train {}: section {} is already occupied".format(
                train.prefix, train.options.start_section
            ))

        self.trains.append(train)
        self.logger.debug("Added train {} from {} to {} (reversed: {}) to simulation {}".format(
            train.options.prefix, start_section, end_section, train.is_reversed, self.simulation_uuid
        ))

        return train

    def update_train_sections(self, train: Train):
        """Updates the sections attributes (prev, next, etc) for a train"""
        next_sections = self.sections_mapper.get_next_sections(train.current_head_section, train.is_reversed)
        previous_sections = self.sections_mapper.get_previous_sections(train.current_head_section, train.is_reversed)

        train.next_straight_section = next_sections[0] if len(next_sections) > 0 else None
        train.next_deviated_section = next_sections[1] if len(next_sections) > 1 else None
        train.next_turnout_section = self.sections_mapper.get_next_turnout(
            from_section=train.current_head_section,
            is_reversed=train.is_reversed
        )

        train.previous_straight_section = previous_sections[0] if len(previous_sections) > 0 else None
        train.previous_deviated_section = previous_sections[1] if len(previous_sections) > 1 else None
        train.previous_turnout_section = self.sections_mapper.get_previous_turnout(
            from_section=train.current_head_section,
            is_reversed=train.is_reversed
        )

        # number of route possible between the next train turnout and the previous one
        train.routes_between_closest_turnouts = self.sections_mapper.get_routes_between_sections(
            train.previous_turnout_section,
            train.next_turnout_section,
            train.is_reversed
        )

    def update_train_possible_actions(self, train: Train):
        """Updates the list of possible actions for a given train"""
        possible_actions = [action for action in ALL_POSSIBLE_ACTIONS if action.is_applicable(self, train)]
        train.possible_actions = possible_actions

        actions_abbrev = [action.abbrev for action in possible_actions]
        self.logger.debug("Train {} possible actions: {}".format(train.prefix, ", ".join(actions_abbrev)))

    def update_related_trains(self, train):
        """Updates the list of trains ahead/behind a given train"""
        train.trains_ahead = self.trains_moving_opposite_from_section(train.current_head_section, train.is_reversed)
        train.trains_behind = self.trains_moving_normal_before_section(train.current_head_section, train.is_reversed)

        # Filter out trains ahead that are on same section (and behind)
        train.trains_ahead[:] = [t for t in train.trains_ahead if not (
            t.current_head_section == train.current_head_section and t.relative_position < train.relative_position
        ) and t.prefix != train.prefix]

        # Filter out trains behind that are on same section (and ahead)
        train.trains_behind[:] = [t for t in train.trains_behind if not (
            t.current_head_section == train.current_head_section and t.relative_position > train.relative_position
        ) and t.prefix != train.prefix]

    def trains_moving_normal_before_section(self, section: Section, is_reversed=False) -> List:
        """Returns the list of trains moving in normal direction before a given section"""
        if section is None:
            return []

        trains_direction = 'normal' if not is_reversed else 'reversed'
        trains_behind = self.trains_in_section(section, trains_direction)

        sections_before = self.sections_mapper.get_all_sections_before(section, is_reversed)
        for previous_section in sections_before:
            section_object = self.sections_mapper.find_section_by_name(previous_section)
            trains_behind.extend(self.trains_in_section(section_object, trains_direction))

        return list(set(trains_behind))

    def trains_moving_opposite_from_section(self, section: Section, is_reversed=False) -> List:
        """Returns the list of trains moving opposite from a given section. Basically used to check trains moving in
        collision route (coming towards a given section)"""
        if section is None:
            return []

        trains_direction = 'normal' if is_reversed else 'reversed'
        trains_opposite = self.trains_in_section(section, trains_direction)

        sections_after = self.sections_mapper.get_all_sections_after(section, is_reversed)
        for next_section in sections_after:
            section_object = self.sections_mapper.find_section_by_name(next_section)
            trains_opposite.extend(self.trains_in_section(section_object, trains_direction))

        return list(set(trains_opposite))

    def trains_in_section(self, section, direction='both'):
        """Returns a list with the trains occupying a given section"""
        if direction == 'both':
            return [train for train in self.trains if train.current_head_section == section]

        return [
            train for train in self.trains if train.current_head_section == section and
            train.is_reversed == (direction == 'reversed')
        ]

    def update_train_cost(self, train):
        """Updates the accumulated cost of a given train"""
        train.last_accumulated_cost = train.accumulated_cost
        distance_to_goal = self.get_train_distance_to_goal(train)
        if distance_to_goal == math.inf:
            distance_to_goal = 2 * sum([section.length for section in self.sections_mapper.sections])
        train.instant_cost = train.options.priority * train.train_equation.calculate_cost(train, distance_to_goal)
        train.accumulated_cost += train.instant_cost

    def get_train_distance_to_goal(self, train: Train):
        """Calculates a train distance to the goal"""
        total_distance = (
            self.sections_mapper.get_distance_between_sections(
                train.current_head_section,
                train.options.finish_section,
                train.is_reversed
            ) - (
                train.relative_position * train.current_head_section.length
                if not train.is_reversed else
                (1 - train.relative_position) * train.current_head_section.length
            ) - train.options.finish_section.length + train.options.length
        )
        return total_distance

    def update_occupancy_dict(self):
        """Updates the occupancy dictionary with a list with each of the sections and its occupying trains """
        self.occupancy_dict = {
            section.name: self.trains_in_section(section)
            for section in self.sections_mapper.sections
        }

    def update_steps_without_movement(self):
        """Updates the number of steps without any train movement"""
        trains_positions = [train.relative_position for train in self.trains]
        if trains_positions != self.last_positions:
            self.last_positions = trains_positions
            self.steps_without_movement = 0
        else:
            self.steps_without_movement += 1

    def has_completed_every_train(self):
        """Determines if every train in the simulation has finished its trip (and the queue is empty)"""
        return len(self.trains_queue) == 0 and all([train.has_finished() for train in self.trains])

    def get_trains_positions(self):
        """Returns a list with each of the trains containing its section and position"""
        return [
            {'prefix': train.prefix, 'section': train.current_head_section.name, 'position': train.relative_position}
            for train in self.trains
        ]

    def move_train_to_section(self, train, new_section):
        if new_section is None:
            raise ConflictConditionError("Next section for train {} is none".format(train.prefix))

        if new_section.interdicted and not train.options.may_invade_interdicted_sections:
            raise ConflictConditionError(
                "Next section ({}) is interdicted and train {} is not allowed to invade!".format(
                    new_section.name,
                    train.prefix
                )
            )

        self.logger.debug("Train {} moved from section {} to {} at step {} ".format(
            train.prefix, train.current_head_section.name, new_section.name, self.time_dynamics.current_step
        ))

        train.section_start = next(
            connection.connection_origin for connection in train.current_head_section.connections
            if connection.destiny_section_name == new_section.name
        )

        train.current_head_section = new_section
        train.relative_position = 1.0 if train.is_reversed else 0.0

    def find_train_by_prefix(self, prefix: str) -> Train:
        """Helper function used to return the train object for a given prefix"""
        return next((train for train in self.trains if train.prefix == prefix), None)
