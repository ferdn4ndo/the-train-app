#!/usr/bin/env python3

from app.comparison.scenarios.scenario_1 import ComparisonScenarioOne
from app.comparison.scenarios.scenario_2 import ComparisonScenarioTwo


def main():
    """Simply run both scenarios"""
    scenario_one = app.comparison.ComparisonScenarioOne(simulation_options={
        'max_steps': 500,
        'max_steps_without_train_movement': 0,
        'max_cost': 1e6,
    }, solutions_size=10, max_consecutive_steps_with_same_best=0, max_iterations=200)
    scenario_one.run(export_results=True)

    scenario_two = app.comparison.ComparisonScenarioTwo(simulation_options={
        'max_steps': 10000,
        'max_steps_without_train_movement': 0,
        'max_cost': 5e9,
    }, solutions_size=5, max_consecutive_steps_with_same_best=0, max_iterations=100)
    scenario_two.run(export_results=True)


if __name__ == '__main__':
    main()
