import math
import random

from app.controller.core.base_controller import BaseController, free_up_memory
from app.simulation.action.all import ALL_POSSIBLE_ACTIONS
from app.simulation.model.train import Train


class ParticleSwarmOptimizationController(BaseController):
    NAME = "Particle Swarm Optimization Controller"
    ABBREV = "PSO"

    def __init__(self, route, trains=None, **options):
        """Controller constructor. Besides the parent, just creates the positions map and declare variables"""
        super().__init__(route, trains, **options)

        self.positions_map = self.calculate_positions_map()
        self.particles = []
        self.best_global_particle = None
        self.best_global_particle_cost = math.inf

    def get_default_options(self):
        """Overrides the original default options to add some pertinent PSO constants"""
        defaults = super().get_default_options()
        defaults.update({
            'inertial_parameter': 0.1,
            'personal_acceleration_coefficient': 0.5,
            'global_acceleration_coefficient': 0.3,
        })
        return defaults

    def calculate_positions_map(self):
        """Calculates the action to position map"""
        positions_map = {
            action.name: float(index)/float(len(ALL_POSSIBLE_ACTIONS))
            for index, action in enumerate(ALL_POSSIBLE_ACTIONS)
        }
        self.logger.debug("Positions map calculated: ".format('\n'.join([
            "{}: {}".format(action, value) for action, value in positions_map.items()
        ])))
        return positions_map

    def create_random_particles(self):
        """Creates the initial set of particles"""
        while len(self.solutions) < self.options['solutions_size']:
            self.create_solution()

    def get_train_position(self, train: Train):
        """Calculates a train position based on its action history"""
        return [
            self.positions_map[action['data']['name']]
            for action in train.actions_history
        ]

    def get_random_velocity(self, train: Train):
        """Calculates a train position based on its action history"""
        return [
            random.random() - self.positions_map[action['data']['name']]
            for action in train.actions_history
        ]

    def read_particles(self, solutions):
        """Parses the solutions (simulations) into the particles"""
        self.particles = [
            {
                'positions': {train.prefix: self.get_train_position(train) for train in solution.dispatcher.trains},
                'velocities': {train.prefix: self.get_random_velocity(train) for train in solution.dispatcher.trains},
                'best_positions': {},
                'best_cost': math.inf,
                'solution': solution,
            }
            for solution in solutions
        ]

    def update_particles_bests(self):
        """Iterates through each particle updating its personal best cost/position and updates the global"""
        for particle in self.particles:
            particle_current_cost = particle['solution'].accumulated_cost
            if particle_current_cost < particle['best_cost']:
                particle['best_cost'] = particle['solution'].accumulated_cost
                particle['best_positions'] = particle['positions']

            if particle_current_cost < self.best_global_particle_cost:
                self.best_global_particle_cost = particle_current_cost
                self.best_global_particle = particle

    def get_particle_new_velocity_personal(self, particle, train_prefix, velocity_index):
        """Calculates the personal term of the new velocity equation"""
        best_position = 0
        if (
            train_prefix in particle['best_positions'] and
            len(particle['best_positions'][train_prefix]) > velocity_index
        ):
            best_position = particle['best_positions'][train_prefix][velocity_index]

        current_position = 0
        if (
            train_prefix in particle['positions'] and
            len(particle['positions'][train_prefix]) > velocity_index
        ):
            current_position = particle['best_positions'][train_prefix][velocity_index]

        return self.options['personal_acceleration_coefficient'] * random.random() * (best_position - current_position)

    def get_particle_new_velocity_global(self, particle, train_prefix, velocity_index):
        """Calculates the global term of the new velocity equation"""
        best_position = 0
        if (
            self.best_global_particle is not None and
            train_prefix in self.best_global_particle['best_positions'] and
            len(particle['best_positions'][train_prefix]) > velocity_index
        ):
            best_position = particle['best_positions'][train_prefix][velocity_index]

        current_position = 0
        if train_prefix in particle['positions'] and len(particle['positions'][train_prefix]) > velocity_index:
            current_position = particle['best_positions'][train_prefix][velocity_index]

        return self.options['global_acceleration_coefficient'] * random.random() * (best_position - current_position)

    def update_particle_velocities_and_positions(self, particle):
        """Iterates through the velocity in each dimension of a particle updating it, then updates its positions"""
        new_velocities = {}
        for train_prefix in particle['velocities']:
            new_velocities[train_prefix] = [
                (
                    self.options['inertial_parameter'] * particle['velocities'][train_prefix][index] +
                    self.get_particle_new_velocity_personal(particle, train_prefix, index) +
                    self.get_particle_new_velocity_global(particle, train_prefix, index)
                )
                for index in range(len(particle['velocities'][train_prefix]))
            ]

            particle['positions'][train_prefix] = [
                particle['positions'][train_prefix][index] + new_velocities[train_prefix][index]
                for index in range(len(particle['positions'][train_prefix]))
            ]

    def get_action_from_position(self, position: float):
        """Converts a single position into an action"""
        max_position = max([action_value for action, action_value in self.positions_map.items()])
        while position > max_position:
            position -= max_position

        closest_distance = min([abs(action_value - position) for action, action_value in self.positions_map.items()])
        closest_action = next(
            action for action, action_value in self.positions_map.items()
            if abs(action_value - position) == closest_distance
        )

        return closest_action

    def parse_particle_positions(self, particle):
        """Converts the resulting particle positions in actions for the solution"""
        trains_actions = {
            train_prefix: [self.get_action_from_position(position) for position in particle['positions'][train_prefix]]
            for train_prefix in particle['positions']
        }
        self.create_solution(trains_actions)

    def take_step_actions(self):
        """Overrides the original controller step actions to add the PSO methods"""
        # at the very beginning we just run a random set of solutions to get the initial set of particles
        if not len(self.particles):
            self.create_random_particles()
            super().take_step_actions()
            self.read_particles(self.solutions)
            self.update_particles_bests()
            return

        del self.solutions[:]
        free_up_memory()

        for particle in self.particles:
            self.update_particle_velocities_and_positions(particle)
            self.parse_particle_positions(particle)

        super().take_step_actions()
