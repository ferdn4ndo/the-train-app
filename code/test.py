#!/usr/bin/env python3

from app.comparison.scenarios.scenario_2 import ComparisonScenarioTwo
from app.simulation.graph.synoptic_panel_video import SynopticPanelVideo
from controller.random_action.controller import RandomActionController


def main():
    scenario_two = ComparisonScenarioTwo(
        simulation_options={
            'max_steps': 1e5,
            'max_steps_without_train_movement': 100,
            'max_cost': 5e9,
        },
        solutions_size=5,
        max_iterations=20,
        controllers=[
            RandomActionController,
        ]
    )
    scenario_two.run(export_results=False)

    for controller in scenario_two.controllers:
        for solution in controller.solutions:
            synoptic = SynopticPanelVideo(solution.results)
            synoptic.export_video()


if __name__ == '__main__':
    main()
