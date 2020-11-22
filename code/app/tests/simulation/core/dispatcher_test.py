import unittest
import uuid

from app.routes.example import ExampleRoute
from app.simulation.core.dispatcher import Dispatcher
from app.simulation.math.dynamics import TimeDynamics
from app.simulation.model.train import Train


class TestDispatcher(unittest.TestCase):

    def test_get_train_distance_to_goal(self):
        """UT for the get_train_distance_to_goal method"""
        route = ExampleRoute()
        mapper = route.sections_mapper
        dispatcher = Dispatcher(str(uuid.uuid4()), TimeDynamics(), route.sections_mapper, [], {})

        train = Train(
            prefix='V99',
            start_section=mapper.find_section_by_name('ZCM_ZPV'),
            finish_section=mapper.find_section_by_name('ZPV_P'),
            start_relative_position=0.8,
            direction='normal',
            length=100
        )

        expected_distance_to_goal = (
            sum([
                mapper.find_section_by_name('ZCM_ZPV').length,
                mapper.find_section_by_name('ZPV#1').length,
                mapper.find_section_by_name('ZPV_P').length,
            ]) - (
                0.8 * mapper.find_section_by_name('ZCM_ZPV').length
            ) - mapper.find_section_by_name('ZPV_P').length + 100
        )
        returned_distance_to_goal = dispatcher.get_train_distance_to_goal(train)

        self.assertEqual(expected_distance_to_goal, returned_distance_to_goal)

    def test_is_route_available_valid_condition(self):
        """UT for the is_route_available method"""
        route = ExampleRoute()
        dispatcher = Dispatcher(str(uuid.uuid4()), TimeDynamics(), route.sections_mapper, [], {})

        dispatcher.add_generic_train(
            prefix='T01',
            start_section='ZCM_P',
            end_section='ZPV_P',
            start_relative_position=0.8,
            priority=75,
            direction='normal',
        )
        train1 = dispatcher.find_train_by_prefix('T01')

        dispatcher.update_occupancy_dict()
        dispatcher.update_train_sections(train1)

        routes = dispatcher.sections_mapper.get_routes_between_sections(
            dispatcher.sections_mapper.find_section_by_name('ZCM#1'),
            dispatcher.sections_mapper.find_section_by_name('ZCM#2'),
            False
        )

        routes_availability = [dispatcher.is_route_available(route) for route in routes]

        self.assertEqual(len([route for route in routes_availability if route is True]), 1)
        available_route = next((route for route in routes if dispatcher.is_route_available(route) is True), None)
        self.assertEqual(['ZCM#1', 'ZCM_D', 'ZCM#2'], available_route)

        self.assertEqual(len([route for route in routes_availability if route is False]), 1)
        unavailable_route = next((route for route in routes if dispatcher.is_route_available(route) is False), None)
        self.assertEqual(['ZCM#1', 'ZCM_P', 'ZCM#2'], unavailable_route)

    def test_trains_moving_normal_before_section(self):
        """UT for the trains_moving_normal_before_section method"""
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
        train1 = dispatcher.find_train_by_prefix('T01')

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

        dispatcher.update_related_trains(train2)
        self.assertEqual(1, len(train2.trains_behind))
        self.assertEqual([train1], train2.trains_behind)

    def test_trains_moving_opposite_from_section(self):
        """UT for the trains_moving_opposite_from_section"""
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
        train1 = dispatcher.find_train_by_prefix('T01')

        dispatcher.add_generic_train(
            prefix='T02',
            start_section='ZCM_D',
            end_section='ZPV_P',
            start_relative_position=0.8,
            priority=75,
            direction='reversed',
        )
        train2 = dispatcher.find_train_by_prefix('T02')

        dispatcher.update_occupancy_dict()

        dispatcher.update_related_trains(train2)
        self.assertEqual(1, len(train2.trains_ahead))
        self.assertEqual([train1], train2.trains_ahead)

        dispatcher.update_related_trains(train1)
        self.assertEqual(1, len(train1.trains_ahead))
        self.assertEqual([train2], train1.trains_ahead)
