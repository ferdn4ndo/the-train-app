import os
import time
import uuid
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List

from app.common.cache import Cache
from app.common.date import seconds_to_interval
from app.common.logger import generate_logger, LoggerFolders
from app.controller.genetic_algorithm.controller import GeneticAlgorithmController
from app.controller.particle_swarm_optimization.controller import ParticleSwarmOptimizationController
from app.controller.random_action.controller import RandomActionController
from app.simulation.graph.synoptic_panel_video import SynopticPanelVideo


class Scenario:
    ALL_CONTROLLERS = [
        RandomActionController,
        ParticleSwarmOptimizationController,
        GeneticAlgorithmController,
    ]

    # Override the following constants when creating a custom scenario:
    ROUTE = None
    TRAINS = {}

    def __init__(self, route=None, trains=None, controllers=None, **options):
        """Scenario class constructor"""
        self.uuid = str(uuid.uuid4())
        self.logger = generate_logger(self.uuid, LoggerFolders.COMPARISONS)

        self.options = {}
        self.set_options(options)

        Cache.clear_all()

        if route is None:
            route = self.ROUTE
        self.route = route
        self.check_route_integrity()

        if trains is None:
            trains = self.TRAINS
        self.trains = trains

        if controllers is not None:
            self.ALL_CONTROLLERS = controllers

        self.controllers: List = []
        self.stop_reason = ""

        self.runtime = 0
        self.reset_controllers()

    def set_options(self, options):
        """Helper function used to update the class options with the given ones"""
        defaults = {}
        defaults.update(options)
        self.options = defaults

    def check_route_integrity(self):
        """Function used to check the route integrity"""
        self.logger.info("Checking route integrity...")
        route = self.route()
        route.sections_mapper.check_integrity()

    def reset_controllers(self):
        del(self.controllers[:])
        for controller in self.ALL_CONTROLLERS:
            self.controllers.append(controller(self.route, self.trains, **self.options))

    def run(self, export_results=False):
        if Cache.is_disabled():
            self.logger.warning("Caching is disabled!")
        self.logger.info("Starting scenario with route {} and trains: {}".format(
            self.route.__name__,
            ', '.join(train['prefix'] for train in self.trains))
        )
        start_time = time.time()
        for controller in self.controllers:
            controller.run()

        if export_results:
            self.export_results()

        self.runtime = int(time.time() - start_time)
        self.logger.info("Finished running scenario! Duration: {}\n\n".format(seconds_to_interval(self.runtime)))

    def get_results_dir(self):
        path = os.path.join(os.environ['DATA_DIR'], 'results', 'comparisons', self.uuid)
        Path(path).mkdir(parents=True, exist_ok=True)
        return path

    def export_base_graph(self, filename: str):
        filepath = os.path.join(self.get_results_dir(), filename)
        plt.savefig('{}.eps'.format(filepath), format='eps')
        plt.savefig('{}.png'.format(filepath))
        self.logger.info("Exported graph {}".format(filename))

    def export_cost_vs_step_graph(self):
        graph1 = plt.figure(1)
        plt.title("Best solution total cost x step")

        for controller in self.controllers:
            plt.plot(controller.best_cost_per_step, label=controller.NAME)

        plt.legend()
        plt.ylabel('Cost')
        plt.xlabel('Step')

        filename = 'graph_best_cost_per_step'
        self.export_base_graph(filename)
        plt.clf()
        plt.close(graph1)

    def export_successful_and_failed_simulations_graph(self):
        plt.rcdefaults()
        fig, ax = plt.subplots()

        controllers = ([controller.ABBREV for controller in self.controllers])
        y_pos = np.arange(len(controllers))
        failed_simulations = [
            controller.iterations_counter - controller.successful_iterations_counter
            for controller in self.controllers
        ]
        successful_simulations = [controller.successful_iterations_counter for controller in self.controllers]

        ax.barh(y_pos, failed_simulations, align='center', height=.66, color='r')
        ax.barh(y_pos, successful_simulations, align='center', height=.66, left=failed_simulations, color='g',label='run time')

        ax.legend(['Failed Simulations', 'Successful Simulations'])

        ax.set_yticks(y_pos)
        ax.set_yticklabels(controllers)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Total of unique simulations')
        ax.set_title('Total unique successful and failed simulations')

        filename = 'graph_total_unique_simulations'
        self.export_base_graph(filename)

        fig.clf()
        plt.close(fig)

    def export_total_execution_time_graph(self):
        plt.rcdefaults()
        fig, ax = plt.subplots()

        controllers = ([controller.ABBREV for controller in self.controllers])
        y_pos = np.arange(len(controllers))
        execution_time = [controller.runtime for controller in self.controllers]

        ax.barh(y_pos, execution_time, align='center', height=0.66, color='blue')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(controllers)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Total execution time (seconds)')
        ax.set_title('Total execution time to complete')

        filename = 'graph_total_execution_time'
        self.export_base_graph(filename)

        fig.clf()
        plt.close(fig)

    def export_total_steps_graph(self):
        plt.rcdefaults()
        fig, ax = plt.subplots()

        controllers = ([controller.ABBREV for controller in self.controllers])
        total_steps = [controller.current_step for controller in self.controllers]

        ax.bar(controllers, total_steps, align='center', width=0.66, color='orange')
        ax.set_ylabel('Total Epochs')
        ax.set_title('Total epochs to complete')

        filename = 'graph_total_epochs'
        self.export_base_graph(filename)

        fig.clf()
        plt.close(fig)

    def export_graphs(self):
        self.export_cost_vs_step_graph()
        self.export_successful_and_failed_simulations_graph()
        self.export_total_execution_time_graph()
        self.export_total_steps_graph()

    def export_results(self):
        if any([controller.best_solution_results is None for controller in self.controllers]):
            self.logger.warning("ONE OR MORE CONTROLLERS DOESN'T HAVE A BEST SOLUTION!")

        path = self.get_results_dir()

        self.logger.info("Exporting graphs...")
        self.export_graphs()

        self.logger.info("Exporting report...")

        report_text = '\n'.join([
            "===== SCENARIO REPORT =====",
            "Route: {}".format(self.route.__name__),
            "Trains: \n {}".format(
                "\n\n".join(
                    "\n".join([
                        "\tPrefix: {}".format(train['prefix']),
                        "\tStart Section: {}".format(train['start_section']),
                        "\tEnd Section: {}".format(train['end_section']),
                        "\tIs Reversed: {}".format(
                            ('YES' if train['is_reversed'] else 'NO') if 'is_reversed' in train else 'NO'
                        ),
                        "\tPriority: {}".format(train['priority'] if 'priority' in train else 1),
                    ]) for train in self.trains
                )
            )
        ])

        for controller in self.controllers:
            report_text += "\n\n" + controller.report()

        report_filename = os.path.join(path, 'report.txt')
        with open(report_filename, 'w') as file:
            file.write(report_text)
        self.logger.info("Exported report to {}".format(report_filename))

        self.logger.info("Exporting videos...")
        finished_controllers = [
            controller for controller in self.controllers if controller.best_solution_results is not None
        ]
        for controller in self.controllers:
            synoptic = SynopticPanelVideo(controller.best_solution_results)
            video_filename = os.path.join(path, 'best_solution_synoptic_{}'.format(controller.NAME))
            synoptic.export_video(video_filename)
