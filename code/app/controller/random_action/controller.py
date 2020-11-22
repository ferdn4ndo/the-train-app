from math import inf

from app.controller.core.base_controller import BaseController, free_up_memory


class RandomActionController(BaseController):
    NAME = "Random Action Controller"
    ABBREV = "RND"

    def __init__(self, route, trains=None, **options):
        super().__init__(route, trains, **options)

        while len(self.solutions) < self.options['solutions_size']:
            self.create_solution()

    def take_step_actions(self):
        del self.solutions[:]
        free_up_memory()

        while len(self.solutions) < self.options['solutions_size']:
            self.create_solution()

        super().take_step_actions()
        self.update_max_simulation_cost()

    def update_max_simulation_cost(self, max_cost=inf):
        if max_cost == inf and 'max_cost' in self.options['simulation_options']:
            max_cost = self.options['simulation_options']['max_cost']

        if self.best_solution_results is None:
            self.options['simulation_options']['max_cost'] = max_cost
            return

        if self.best_solution_cost < max_cost:
            self.options['simulation_options']['max_cost'] = self.best_solution_cost
