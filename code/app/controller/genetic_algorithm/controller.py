import random

from app.controller.core.base_controller import BaseController, free_up_memory
from app.simulation.model.train import Train
from app.simulation.action.all import ALL_POSSIBLE_ACTIONS
from app.simulation.core.simulation import Simulation


class GeneticAlgorithmController(BaseController):
    NAME = "Genetic Algorithm Controller"
    ABBREV = "GA"

    def __init__(self, route, trains=None, **options):
        """Overrides BaseController constructor to fill the population randomly at the moment it's created"""
        super().__init__(route, trains, **options)

        while len(self.solutions) < self.options['solutions_size']:
            self.create_solution()

    def get_default_options(self):
        """Overrides the original default options to add some pertinent Genetic Algorithm constants"""
        defaults = super().get_default_options()
        defaults.update({
            'train_crossing_probability': 0.8,
            'selection_preserve_ratio': 0.6,
            'solution_mutation_probability': 0.3,
            'train_mutation_probability': 0.5,
            'gene_mutation_occurrence': 0.5,
        })
        return defaults

    def take_step_actions(self):
        """Overrides the parent method to execute the actions pertinent to the Genetic Algorithm"""
        solved_solutions = [solution for solution in self.solutions if solution.has_finished]

        if len(solved_solutions):
            self.apply_selection_operator()
            self.apply_crossover_operator()
            self.apply_mutation_operator()

        super().take_step_actions()

    def apply_selection_operator(self):
        """Applies the selection operator in the solutions"""
        solutions_list = {solution.uuid: solution.accumulated_cost for solution in self.solutions}
        ordered_uuids = sorted(solutions_list, key=solutions_list.get)
        total_preserved = round(self.options['selection_preserve_ratio'] * len(ordered_uuids))

        preserved_uuids = ordered_uuids[0:total_preserved]
        self.logger.debug("Selector Operator - Preserved UUIDs: {}".format('; '.join(preserved_uuids)))

        total_to_remove = len([solution for solution in self.solutions if solution.uuid not in preserved_uuids])
        self.solutions = [solution for solution in self.solutions if solution.uuid in preserved_uuids]
        free_up_memory()

        self.logger.info("Selection operator removed {} individuals from the population (from {} to {})".format(
            total_to_remove, len(ordered_uuids), len(self.solutions)
        ))

    def apply_crossover_operator(self):
        """Applies the crossover operator in the solutions"""
        while len(self.solutions) < self.options['solutions_size']:
            individual1 = random.choice(self.solutions)
            individual2 = random.choice(self.solutions)

            if len(individual1.dispatcher.trains) != len(individual2.dispatcher.trains):
                self.logger.debug(
                    "Trying to crossover solutions with different number of trains: [{}] and [{}]!".format(
                        ",".join([train.prefix for train in individual1.dispatcher.trains]),
                        ",".join([train.prefix for train in individual2.dispatcher.trains])
                    )
                )
                continue

            genes = self.get_crossed_genes(individual1, individual2)
            self.create_solution(genes)

    def get_crossed_genes(self, individual1: Simulation, individual2: Simulation):
        """Helper function to cross the genes of two given simulations"""
        genes = {}
        for train1 in individual1.dispatcher.trains:
            if random.random() >= self.options['train_crossing_probability']:
                genes[train1.options.prefix] = [action['data']['name'] for action in train1.actions_history]
                continue

            train2 = next((
                train for train in individual2.dispatcher.trains if train.options.prefix == train1.options.prefix
            ), None)

            if train2 is None:
                self.logger.debug("Unable to find partner solution for crossing train {}!".format(train1.prefix))
                genes[train1.options.prefix] = [action['data']['name'] for action in train1.actions_history]
                continue

            total_genes1 = int(round(len(train1.actions_history) / 2.0))
            train_genes = [action['data']['name'] for action in train1.actions_history[0:total_genes1]]

            total_genes2 = int(round(len(train2.actions_history) / 2.0))
            train_genes.extend([action['data']['name'] for action in train2.actions_history[total_genes2:]])

            genes[train1.options.prefix] = train_genes
        return genes

    def apply_mutation_operator(self):
        """Apply the mutation operator on the whole solution, given some occurrences rate (probabilities)"""
        solutions_uuids_to_remove = []
        for solution in self.solutions:
            if random.random() >= (1 - self.options['solution_mutation_probability']):
                genes = {
                    train.prefix: [action['data']['name'] for action in train.actions_history]
                    for train in solution.dispatcher.trains
                }
                for train in solution.dispatcher.trains:
                    if random.random() >= (1 - self.options['train_mutation_probability']):
                        genes[train.prefix] = self.mutate_train(train)

                self.create_solution(genes)
                solutions_uuids_to_remove.append(solution.uuid)
                self.logger.debug("Mutation Operator - Mutated solution {}".format(solution.uuid))

        self.solutions = [solution for solution in self.solutions if solution.uuid not in solutions_uuids_to_remove]

    def mutate_train(self, train: Train):
        """Function used to mutate a single train, given a certain occurrence rate (probability)"""
        genes = [action['data']['name'] for action in train.actions_history]
        for gene_index in range(len(genes)):
            if random.random() >= self.options['gene_mutation_occurrence']:
                genes[gene_index] = random.choice(ALL_POSSIBLE_ACTIONS).name
        return genes
