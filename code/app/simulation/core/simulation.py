import copy
import json
import traceback
import uuid
from typing import List, Dict

from app.simulation.exception.error import Error
from app.simulation.math.dynamics import TimeDynamics
from app.simulation.model.simulation_results import SimulationResults
from app.common.logger import generate_logger, LoggerFolders
from app.simulation.core.dispatcher import Dispatcher


class Simulation:
    DEFAULT_OPTIONS = {
        'step_duration': 30,  # seconds
        'max_cost': 1e6,
        'max_steps': 1000,
        'max_steps_without_train_movement': 10,
        'abort_cost_multiplier': 100,
        'step_limit_multiplier': 10,
        'cost_limit_multiplier': 10,
        'without_movement_multiplier': 10,
        'controller_name': 'No Controller',
    }

    def __init__(self, route, trains_queue: List = None, trains_actions: Dict = None, **options):
        """Simulation class constructor"""
        if trains_actions is None:
            trains_actions = {}

        self.uuid = str(uuid.uuid4())

        self.logger = generate_logger(self.uuid, LoggerFolders.SIMULATIONS)

        self.options = {}
        self.set_options(options)

        self.error = None
        self.route = route()
        self.route.logger = self.logger

        self.time_dynamics = TimeDynamics(step_duration=self.options['step_duration'])
        self.current_step = 0
        self.accumulated_cost = 0

        self.dispatcher = Dispatcher(
            simulation_uuid=self.uuid,
            time_dynamics=self.time_dynamics,
            sections_mapper=self.route.sections_mapper,
            trains_queue=trains_queue,
            trains_actions=trains_actions
        )

        self.running = False
        self.has_finished = False
        self.has_completed_every_train = False
        self.trains_positions_history = []
        self.has_reached_no_movement_step_limit = False
        self.has_reached_step_limit = False
        self.has_reached_cost_limit = False
        self.has_aborted = False

        self.results = SimulationResults(simulation=self, controller_name=self.options['controller_name'])

    def get_status_text(self):
        """Retrieves current status of the simulation in a human-friendly way"""
        if self.running:
            return 'RUNNING'
        if not self.has_finished:
            return 'PAUSED'
        return 'SUCCESS' if self.has_completed_every_train else 'FAIL'

    def set_options(self, options):
        """Helper function used to update the class options with the given ones"""
        self.options = copy.deepcopy(self.DEFAULT_OPTIONS)
        self.options.update(options)
        self.logger.debug("Updated options: {}".format(json.dumps(self.options)))

    def start(self):
        """Starts the simulation"""
        if self.running:
            self.logger.warning(
                "STEP #{} - SIMULATION_START - Tried to start the simulation but it's already running"
                    .format(self.time_dynamics.current_step)
            )

        self.logger.debug("Simulation started!")

        self.running = True
        self.check_stop_conditions()

    def stop(self, reason="No reason"):
        """Stops the simulation and updates the reason why that happened with the given one"""
        if self.running:
            self.running = False
            self.logger.info("Simulation stopped at step {}: {} (final accum. cost: {:.2E})!".format(
                self.current_step, reason, self.accumulated_cost
            ))

    def step(self):
        """Performs the full set of actions of a single step"""
        #try:
        if self.running:
            self.time_dynamics.step()
            self.dispatcher.step()
            self.results.register_frame(self)
            self.trains_positions_history.append(self.dispatcher.get_trains_positions())
            self.accumulated_cost += sum([train.accumulated_cost for train in self.dispatcher.trains])

        if self.current_step > 0 and self.current_step % 1000 == 0:
            self.logger.info("Completed step {}...".format(self.current_step))

        self.logger.debug("Simulation finished step {} with cost {:.2E}!".format(
            self.current_step, self.accumulated_cost
        ))

        self.check_stop_conditions()
        self.current_step += 1

        #except Error as err:

        #    self.stop()
        #    self.error = str(err)

    def abort(self):
        """Function used to abort the simulation (unexpected stop)"""
        self.stop()
        self.has_aborted = True
        self.accumulated_cost = self.accumulated_cost * self.options['abort_cost_multiplier']
        self.logger.warning("Simulation has aborted: {}".format(self.error))

    def run(self):
        """Run the simulation until it finishes"""
        #try:
        self.start()
        while self.running:
            self.step()
        #except:
        #    self.logger.critical("Exception!", traceback.format_exc())

    def check_if_reached_step_limit(self):
        """Helper function used to check if the simulation has reached the step limit"""
        self.has_reached_step_limit = False
        limit_step = self.options['max_steps']
        if 0 < limit_step <= self.current_step:
            self.has_reached_step_limit = True
            self.accumulated_cost = self.accumulated_cost * self.options['step_limit_multiplier']
            self.stop("Reached step limit of {} (cost limit {})".format(self.options['max_steps'], self.options['max_cost']))

    def check_if_reached_cost_limit(self):
        """Helper function used to check if the simulation has reached the cost limit"""
        self.has_reached_cost_limit = False
        cost_limit = float(self.options['max_cost'])
        if self.accumulated_cost >= cost_limit:
            self.has_reached_cost_limit = True
            self.accumulated_cost = self.accumulated_cost * self.options['cost_limit_multiplier']
            self.stop("Reached cost limit of {:.2E}".format(cost_limit))

    def check_if_reached_no_movement_limit(self):
        """Helper function used to check if the simulation has reached the no-movement trains step limit"""
        self.has_reached_no_movement_step_limit = False
        max_steps_without_movement = self.options['max_steps_without_train_movement']
        if max_steps_without_movement and self.dispatcher.steps_without_movement > max_steps_without_movement:
            self.has_reached_no_movement_step_limit = True
            self.accumulated_cost = self.accumulated_cost * self.options['without_movement_multiplier']
            self.stop("Reached {} steps without any movement".format(max_steps_without_movement))

    def check_if_completed_every_train(self):
        """Helper function used to check if the simulation has completed every train"""
        self.has_completed_every_train = self.dispatcher.has_completed_every_train()
        if self.has_completed_every_train:
            self.stop("Completed every train")

    def check_stop_conditions(self):
        """Check the stop conditions"""
        if self.has_aborted:
            self.has_finished = True
            return

        self.check_if_reached_step_limit()
        self.check_if_reached_cost_limit()
        self.check_if_reached_no_movement_limit()
        self.check_if_completed_every_train()

        self.has_finished = any([
            self.has_completed_every_train,
            self.has_reached_step_limit,
            self.has_reached_cost_limit,
            self.has_reached_no_movement_step_limit,
            self.has_aborted,
        ])

    def get_trains_instant_cost(self):
        """Gets the total instant cost of the dispatcher trains"""
        total_cost = 0.0
        for train in self.dispatcher.trains:
            total_cost += train.instant_cost

        return total_cost
