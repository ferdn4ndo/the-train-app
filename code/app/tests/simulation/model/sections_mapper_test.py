import unittest

from app.routes.example import ExampleRoute


class TestSectionsMapper(unittest.TestCase):

    def test_get_routes_between_sections(self):
        """UT for the get_routes_between_sections method"""
        route = ExampleRoute()
        mapper = route.sections_mapper

        start_section = mapper.find_section_by_name('ZAS_P')
        end_section = mapper.find_section_by_name('ZPV_P')

        # We're expecting two possible routes between ZAS_P and ZPV_P (double in ZCM_P/ZCM_D)
        expected_routes = [
            ['ZAS_P', 'ZAS#1', 'ZAS_ZCM', 'ZCM#1', 'ZCM_P', 'ZCM#2', 'ZCM_ZPV', 'ZPV#1', 'ZPV_P'],
            ['ZAS_P', 'ZAS#1', 'ZAS_ZCM', 'ZCM#1', 'ZCM_D', 'ZCM#2', 'ZCM_ZPV', 'ZPV#1', 'ZPV_P']
        ]
        returned_routes = mapper.get_routes_between_sections(start_section, end_section)
        print(returned_routes)

        self.assertListEqual(expected_routes, returned_routes)

    def test_get_distance_between_sections(self):
        """UT for the get_distance_between_sections method"""
        route = ExampleRoute()
        mapper = route.sections_mapper

        start_section = mapper.find_section_by_name('ZAS_P')
        end_section = mapper.find_section_by_name('ZPV_P')

        expected_distance = sum([
            mapper.find_section_by_name('ZAS_P').length,
            mapper.find_section_by_name('ZAS#1').length,
            mapper.find_section_by_name('ZAS_ZCM').length,
            mapper.find_section_by_name('ZCM#1').length,
            mapper.find_section_by_name('ZCM_P').length,
            mapper.find_section_by_name('ZCM#2').length,
            mapper.find_section_by_name('ZCM_ZPV').length,
            mapper.find_section_by_name('ZPV#1').length,
            mapper.find_section_by_name('ZPV_P').length,
        ])
        returned_distance = mapper.get_distance_between_sections(start_section, end_section, is_reversed=False)
        returned_distance = mapper.get_distance_between_sections(start_section, end_section, is_reversed=False)
        returned_distance = mapper.get_distance_between_sections(start_section, end_section, is_reversed=False)

        self.assertEqual(expected_distance, returned_distance)

    def test_get_all_sections_before(self):
        """UT for the get_distance_between_sections method"""
        route = ExampleRoute()
        mapper = route.sections_mapper

        start_section = mapper.find_section_by_name('ZAS_ZCM')
        sections_before = mapper.get_all_sections_before(start_section, False)
        # Should return something like: ['ZAS_P', 'ZAS_D', 'ZAS#1']
        self.assertEqual(3, len(sections_before))

        sections_before = mapper.get_all_sections_before(start_section, True)
        # Should return something like: ['ZCM_D', 'ZCM_ZPV', 'ZCM_P', 'ZPV#1', 'ZCM#1', 'ZPV_D', 'ZCM#2', 'ZPV_P']
        self.assertEqual(8, len(sections_before))

    def test_get_all_sections_after(self):
        """UT for the get_distance_between_sections method"""
        route = ExampleRoute()
        mapper = route.sections_mapper

        start_section = mapper.find_section_by_name('ZAS_ZCM')
        sections_after = mapper.get_all_sections_after(start_section, False)
        # Should return something like: ['ZCM_D', 'ZCM_ZPV', 'ZCM_P', 'ZPV#1', 'ZCM#1', 'ZPV_D', 'ZCM#2', 'ZPV_P']
        self.assertEqual(8, len(sections_after))

        sections_after = mapper.get_all_sections_after(start_section, True)
        # Should return something like: ['ZAS_P', 'ZAS_D', 'ZAS#1']
        self.assertEqual(3, len(sections_after))
