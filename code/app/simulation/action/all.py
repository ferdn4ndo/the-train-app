from app.simulation.action.move_deviate import MoveDeviateAction
from app.simulation.action.move_straight import MoveStraightAction
from app.simulation.action.reverse import ReverseAction
from app.simulation.action.wait_crossing import WaitCrossingAction
from app.simulation.action.wait_overtake import WaitOvertakeAction

ALL_POSSIBLE_ACTIONS = [
    MoveStraightAction,
    MoveDeviateAction,
    WaitOvertakeAction,
    WaitCrossingAction,
    ReverseAction
]


def find_action(keyword):
    return next(
        action for action in ALL_POSSIBLE_ACTIONS
        if action.name == keyword or action.abbrev == keyword
    )
