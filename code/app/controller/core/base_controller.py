import copy
import gc
import multiprocessing
import time

from typing import List

from app.common.threading import ThreadingExecutor
from app.controller.core.worker import run_solution
from app.simulation.core.simulation import Simulation
from app.common.date import seconds_to_interval
from app.common.logger import generate_logger, LoggerFolders


def free_up_memory():
    """Force the Garbage Collector to release unreferenced memory"""
    gc.collect()


class BaseController:
    NAME = "Base Controller"
    ABBREV = "--"

    def __init__(self, route, trains: List = None, **options):
        self.logger = generate_logger(self.NAME, LoggerFolders.CONTROLLERS)

        self.options = self.get_default_options()
        self.options.update(copy.deepcopy(options))

        self.solutions: List[Simulation] = []
        self.best_solution_results = None
        self.best_solution_cost = float('inf')
        self.best_solution_last_updated_step = 0
        self.best_solution_status = '---'
        self.iterations_counter = 0   # number of times a solution (simulation) was run
        self.successful_iterations_counter = 0  # number of times a solution was run and was successful
        self.stop_reason = ""

        self.best_cost_per_step = []

        self.route = route
        self.current_step = 0
        self.runtime = 0
        self.trains = trains

        self.logger.debug("{} was created with route {}".format(self.NAME, route))
        self.running = False

    def get_default_options(self):
        return {
            'solutions_size': 20,
            'simulation_options': {},
            'max_thread_workers': multiprocessing.cpu_count() * 2,
            'max_iterations': 50,
            'max_consecutive_steps_with_same_best': 3,
        }

    def get_simulation_options(self):
        defaults = copy.deepcopy(Simulation.DEFAULT_OPTIONS)
        defaults.update(self.options['simulation_options'])
        return defaults

    def create_solution(self, trains_actions=None):
        """Creates a solution with the computed trains actions"""
        solution = Simulation(
            route=self.route,
            trains_queue=copy.deepcopy(self.trains),
            trains_actions=trains_actions,
            **self.get_simulation_options()
        )
        solution.options['controller_name'] = self.NAME
        self.solutions.append(solution)

    def run(self):
        self.running = True

        start_time = time.time()
        while self.running:
            self.take_step_actions()
        self.runtime = time.time() - start_time

    def update_best_solution(self):

        completed_solutions = [solution for solution in self.solutions if solution.has_completed_every_train]
        best_solutions = self.solutions if len(completed_solutions) == 0 else completed_solutions

        for solution in best_solutions:
            solution_cost = solution.accumulated_cost
            if solution_cost < self.best_solution_cost:
                self.best_solution_results = solution.results
                self.best_solution_cost = solution_cost
                self.best_solution_last_updated_step = self.current_step
                self.best_solution_status = solution.get_status_text()

                self.best_solution_results.controller_name = self.NAME

                self.logger.info(
                    "Updated global best: {:.2E} @ step {} with status {}".format(
                        self.best_solution_cost,
                        self.best_solution_last_updated_step,
                        self.best_solution_status
                    )
                )

        self.best_cost_per_step.append(self.best_solution_cost)

    def check_stop_conditions(self):
        if self.iterations_counter >= self.options['max_iterations']:
            self.stop("Reached maximum iterations count")

        if self.options['max_consecutive_steps_with_same_best'] > 0:
            delta = (
                self.best_solution_last_updated_step +
                self.options['max_consecutive_steps_with_same_best'] - 1
            )

            if self.current_step >= delta:
                self.stop("Same best cost for {} steps".format(
                    self.options['max_consecutive_steps_with_same_best']
                ))

    def stop(self, reason="Aborted"):
        self.running = False
        self.logger.info("Stopped at step {}: {}".format(self.current_step, reason))
        self.stop_reason = reason

    def run_unsolved_solutions(self):
        ts = time.time()
        solutions_to_solve = [solution for solution in self.solutions if not solution.has_finished]

        max_iterations = self.options['max_iterations']
        if max_iterations > 0 and self.iterations_counter + len(solutions_to_solve) > max_iterations:
            solutions_to_solve[:] = solutions_to_solve[0:(max_iterations - self.iterations_counter)]
        
        total_solutions_to_solve = len(solutions_to_solve)
        total_executors = min(self.options['max_thread_workers'], total_solutions_to_solve)

        self.logger.info("Starting {} unsolved solutions @ step {} (max_executors: {}, iterations_counter: {})".format(
            len(solutions_to_solve), self.current_step, total_executors, self.iterations_counter
        ))

        executor = ThreadingExecutor(run_solution, total_executors)
        executor.run(solutions_to_solve)

        self.iterations_counter += total_solutions_to_solve
        self.successful_iterations_counter += len(
            [solution for solution in solutions_to_solve if solution.has_completed_every_train]
        )

        self.logger.info(
            "Finished {} solutions @ step {} on {:.2f} seconds".format(
                total_solutions_to_solve,
                self.current_step,
                time.time() - ts,
            )
        )

    def take_step_actions(self):
        self.run_unsolved_solutions()
        self.update_best_solution()
        self.check_stop_conditions()

        self.current_step += 1

    def report(self):
        return "\n".join([
            "\n== {} Report ==".format(self.NAME),

            "Options used:",
            "\tCONTROLLER - max_thread_workers: {}".format(self.options['max_thread_workers']),
            "\tCONTROLLER - max_iterations: {}".format(self.options['max_iterations']),
            "\tCONTROLLER - max_consecutive_steps_with_same_best: {}".format(
                self.options['max_consecutive_steps_with_same_best']
            ),
            "\n".join(["\tSIMULATION - {}: {}".format(k, v) for k, v in self.options['simulation_options'].items()]),
            "\nTotal steps: {}".format(self.current_step),
            "Total iterations: {}".format(self.iterations_counter),
            "Total successful iterations: {}".format(self.successful_iterations_counter),
            "Stop reason: {}".format(self.stop_reason),
            "Best solution UUID: {}".format(
                self.best_solution_results.simulation_uuid if self.best_solution_results is not None else '---'
            ),
            "Best solution cost: {}".format(
                self.best_solution_cost if self.best_solution_results is not None else '---'
            ),
            "Best solution status: {}".format(self.best_solution_status),
            "Best solution total steps: {}".format(
                len(self.best_solution_results.frames) if self.best_solution_results is not None else '---'
            ),
            "Best solution calculated real time elapsed: {}".format(
                self.best_solution_results.calculated_time_elapsed if self.best_solution_results is not None else '---'
            ),
            "Controller total runtime: {}".format(seconds_to_interval(self.runtime)),
        ])

    def report_to_file(self, filename):
        report_content = self.report()
        with open(filename, 'w') as file:
            file.write(report_content)
        self.logger.info("Exported report to file '{}'".format(filename))
