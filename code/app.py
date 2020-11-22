#import app

from app.comparison.scenarios.scenario_1 import ComparisonScenarioOne
from app.comparison.scenarios.scenario_2 import ComparisonScenarioTwo

# scenario_one = ComparisonScenarioOne(simulation_options={
#     'step_duration': 10,
#     'max_steps': 10000,
#     'max_steps_without_train_movement': 0,
#     'max_cost': 1e7,
# }, solutions_size=5, max_consecutive_steps_with_same_best=0, max_iterations=50)
# scenario_one.run(export_results=True)

scenario_one = ComparisonScenarioOne(simulation_options={
    'step_duration': 10,
    'max_steps': 1000,
    'max_steps_without_train_movement': 0,
    'max_cost': 1e3,
}, solutions_size=3, max_consecutive_steps_with_same_best=0, max_iterations=30)
scenario_one.run(export_results=True)
