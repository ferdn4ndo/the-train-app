import unittest
import uuid

from app.routes.example import ExampleRoute
from simulation.core.dispatcher import Dispatcher
from simulation.math.dynamics import TimeDynamics


class TestTrain(unittest.TestCase):

    def test_is_at_turnout_closing(self):
        """UT for the is_at_turnout_closing method"""
        route = ExampleRoute()
        dispatcher = Dispatcher(str(uuid.uuid4()), TimeDynamics(), route.sections_mapper, [], {})

        dispatcher.add_generic_train(
            prefix='T01',
            start_section='ZCM#1',
            end_section='ZPV_P',
            start_relative_position=1.0,
            priority=75,
            direction='normal',
        )
        train1 = dispatcher.find_train_by_prefix('T01')
        dispatcher.update_train_sections(train1)
        self.assertFalse(train1.is_at_turnout_closing())

        dispatcher.move_train_to_section(train1, route.sections_mapper.find_section_by_name('ZCM_P'))
        dispatcher.update_train_sections(train1)
        self.assertTrue(train1.is_at_turnout_closing())
