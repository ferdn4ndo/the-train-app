from app.simulation.model.route import Route


class ComparisonRouteOne(Route):
    """
    First route for results comparison between different controllers.

    Being the simplest one, it implements 2 trains going opposite with on almost-middle crossing point.
    It represents the real world route between Assis-SP (ZAS) and Palmital-SP (ZPV).
    """
    def __init__(self):
        super().__init__()
        self.name = "Comparison Route One"
        self.parse_sections_list([
            {
                'name': 'ZIM_P',
                'start_kilometer': 483.16988,
                'length': 672.04,
                'connections': [
                    {
                        'connects_to': 'ZIM#2',
                        'when_at': 'end_straight'
                    }
                ]
            },
            {
                'name': 'ZIM_D',
                'start_kilometer': 483.16988,
                'length': 672.04,
                'connections': [
                    {
                        'connects_to': 'ZIM#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'ZIM#2',
                'start_kilometer': 483.84192,
                'length': 72.97,
                'connections': [
                    {
                        'connects_to': 'ZIM_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZIM_D',
                        'when_at': 'start_deviated'
                    },
                    {
                        'connects_to': 'ZIM_ZPV',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'ZIM_ZPV',
                'start_kilometer': 483.91489,
                'length': 22000.71,
                'connections': [
                    {
                        'connects_to': 'ZIM#2',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZPV#1',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'ZPV#1',
                'start_kilometer': 505.9156,
                'length': 52.92,
                'connections': [
                    {
                        'connects_to': 'ZIM_ZPV',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZPV_P',
                        'when_at': 'end_straight'
                    },
                    {
                        'connects_to': 'ZPV_D',
                        'when_at': 'end_deviated'
                    },
                ]
            },
            {
                'name': 'ZPV_P',
                'start_kilometer': 505.96852,
                'length': 772.82,
                'connections': [
                    {
                        'connects_to': 'ZPV#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZPV#2',
                        'when_at': 'end_straight'
                    }
                ]
            },
            {
                'name': 'ZPV_D',
                'start_kilometer': 505.96852,
                'length': 777.82,
                'connections': [
                    {
                        'connects_to': 'ZPV#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZPV#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'ZPV#2',
                'start_kilometer': 506.74634,
                'length': 50.16,
                'connections': [
                    {
                        'connects_to': 'ZPV_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZPV_D',
                        'when_at': 'start_deviated'
                    },
                    {
                        'connects_to': 'ZPV_ZSY',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'ZPV_ZSY',
                'start_kilometer': 506.7965,
                'length': 13379.71,
                'connections': [
                    {
                        'connects_to': 'ZPV#2',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZSY_P',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'ZSY_P',
                'start_kilometer': 520.17621,
                'length': 346.12,
                'connections': [
                    {
                        'connects_to': 'ZPV_ZSY',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZSY_ZCM',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'ZSY_ZCM',
                'start_kilometer': 520.52233,
                'length': 11748.10,
                'connections': [
                    {
                        'connects_to': 'ZSY_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZCM#1',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'ZCM#1',
                'start_kilometer': 532.27043,
                'length': 53.69,
                'connections': [
                    {
                        'connects_to': 'ZSY_ZCM',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZCM_P',
                        'when_at': 'end_straight'
                    },
                    {
                        'connects_to': 'ZCM_D',
                        'when_at': 'end_deviated'
                    },
                ]
            },
            {
                'name': 'ZCM_P',
                'start_kilometer': 532.32412,
                'length': 814.90,
                'connections': [
                    {
                        'connects_to': 'ZCM#1',
                        'when_at': 'start_straight'
                    },
                ]
            },
            {
                'name': 'ZCM_D',
                'start_kilometer': 532.32412,
                'length': 814.90,
                'connections': [
                    {
                        'connects_to': 'ZCM#1',
                        'when_at': 'start_straight'
                    },
                ]
            },
        ])
