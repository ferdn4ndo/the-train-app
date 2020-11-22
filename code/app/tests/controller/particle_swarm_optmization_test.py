import unittest

from controller.particle_swarm_optimization.controller import ParticleSwarmOptimizationController
from routes.example import ExampleRoute


class TestParticleSwarmOptimizationController(unittest.TestCase):

    def test_single_run(self):
        """Test a single complete run of the controller"""
        route = ExampleRoute
        trains = [
            {
                'prefix': 'M01',
                'start_section': 'ZAS_P',
                'end_section': 'ZPV_D'
            },
            {
                'prefix': 'M10',
                'start_section': 'ZPV_P',
                'end_section': 'ZAS_D',
                'is_reversed': True
            },
        ]

        controller = ParticleSwarmOptimizationController(route, trains, simulation_options={
            'max_steps': 500,
            'max_steps_without_train_movement': 0,
        }, controller_max_steps=3, controller_thread_workers=1, solutions_size=5, delete_temp_files=False)
        controller.run()
        controller.report()

        self.assertTrue(controller.iterations_counter > 0)
