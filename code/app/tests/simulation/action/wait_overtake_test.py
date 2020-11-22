import unittest
import uuid

from app.routes.example import ExampleRoute
from app.simulation.action.wait_overtake import WaitOvertakeAction
from app.simulation.core.dispatcher import Dispatcher
from app.simulation.math.dynamics import TimeDynamics


class TestWaitOvertakeAction(unittest.TestCase):

    def test_simple_overtake(self):
        """
        Test the overtake action for the simple scenario:
                       //===[T02>]===\\
                      //              \\
        ===[T01>]====//================\\======

        Considering that priority(T01) > priority(T02), T02 should have wait_overtake_action applicable.
        """
        route = ExampleRoute()
        dispatcher = Dispatcher(str(uuid.uuid4()), TimeDynamics(), route.sections_mapper, [], {})

        dispatcher.add_generic_train(
            prefix='T01',
            start_section='ZAS_ZCM',
            end_section='ZPV_P',
            start_relative_position=0.8,
            priority=75,
            direction='normal',
        )

        dispatcher.add_generic_train(
            prefix='T02',
            start_section='ZCM_D',
            end_section='ZPV_P',
            start_relative_position=0.8,
            priority=75,
            direction='normal',
        )

        train2 = dispatcher.find_train_by_prefix('T02')
        dispatcher.update_occupancy_dict()
        dispatcher.update_train_sections(train2)
        dispatcher.update_related_trains(train2)

        self.assertTrue(train2.is_at_turnout_closing())
        self.assertGreaterEqual(len(train2.routes_between_closest_turnouts), 2)
        self.assertGreaterEqual(len(train2.trains_behind), 1)
        self.assertTrue(train2.has_higher_priority_trains_behind())

        self.assertTrue(WaitOvertakeAction.is_applicable(dispatcher, train2))

        dispatcher.update_train_possible_actions(train2)
        self.assertIn(WaitOvertakeAction, train2.possible_actions)
