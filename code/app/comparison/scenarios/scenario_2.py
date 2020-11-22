from app.comparison.scenario import Scenario
from app.routes.comparison_2 import ComparisonRouteTwo


class ComparisonScenarioTwo(Scenario):
    ROUTE = ComparisonRouteTwo
    TRAINS = [
        {
            'prefix': 'K10',
            'start_section': 'LDV_P',
            'end_section': 'LEB_P',
            'priority': 100,
        },
        {
            'prefix': 'K90',
            'start_section': 'LDV_D',
            'end_section': 'LEB_D',
            'priority': 70,
        },
        {
            'prefix': 'F30',
            'start_section': 'LDV_D',
            'end_section': 'LEB_D',
            'priority': 50,
            'step_to_add': 300,
        },
        {
            'prefix': 'U27',
            'start_section': 'LEB_D',
            'end_section': 'LDV_P',
            'direction': 'reversed',
            'priority': 50,
        },
        {
            'prefix': 'U23',
            'start_section': 'LEB_D',
            'end_section': 'LDV_P',
            'direction': 'reversed',
            'priority': 50,
            'step_to_add': 100,
        },
        {
            'prefix': 'W01',
            'start_section': 'LVW_D',
            'end_section': 'LLY_D',
            'direction': 'reversed',
        },
    ]
