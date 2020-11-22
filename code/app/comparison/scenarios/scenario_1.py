from app.comparison.scenario import Scenario
from app.routes.comparison_1 import ComparisonRouteOne


class ComparisonScenarioOne(Scenario):
    ROUTE = ComparisonRouteOne
    TRAINS = [
        {
            'prefix': 'O41',
            'start_section': 'ZIM_P',
            'end_section': 'ZCM_D',
            'priority': 50,
            'length': 450,
            'weight': 1.7e6,
        },
        {
            'prefix': 'O14',
            'start_section': 'ZCM_P',
            'end_section': 'ZIM_D',
            'direction': 'reversed',
            'priority': 50,
            'length': 450,
            'weight': 0.6e6,
        },
    ]
