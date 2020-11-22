from app.simulation.model.route import Route


class ExampleRoute(Route):
    def __init__(self):
        super().__init__()
        self.name = "Example Route"
        self.parse_sections_list([
            {
                'name': 'ZAS_P',
                'length': 2000,
                'connections': [
                    {
                        'connects_to': 'ZAS#1',
                        'when_at': 'end_straight'
                    }
                ],
                'lines': [
                    {
                        'type': 'main',
                        'points': [
                            {
                                "elevation": 0,
                                "location": {
                                    "lat": -22.6624,
                                    "lng": 50.4258
                                }
                            },
                            {
                                "elevation": 0,
                                "location": {
                                    "lat": -22.6625,
                                    "lng": 50.4256
                                }
                            },
                        ]
                    }
                ]
            },
            {
                'name': 'ZAS_D',
                'length': 2000,
                'connections': [
                    {
                        'connects_to': 'ZAS#1',
                        'when_at': 'end_straight'
                    }
                ]
            },
            {
                'name': 'ZAS#1',
                'length': 50,
                'connections': [
                    {
                        'connects_to': 'ZAS_ZCM',
                        'when_at': 'end_straight'
                    },
                    {
                        'connects_to': 'ZAS_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZAS_D',
                        'when_at': 'start_deviated'
                    },

                ]
            },
            {
                'name': 'ZAS_ZCM',
                'length': 15000,
                'connections': [
                    {
                        'connects_to': 'ZAS#1',
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
                'length': 50,
                'connections': [
                    {
                        'connects_to': 'ZAS_ZCM',
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
                'length': 2000,
                'connections': [
                    {
                        'connects_to': 'ZCM#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZCM#2',
                        'when_at': 'end_straight'
                    }
                ]
            },
            {
                'name': 'ZCM_D',
                'length': 2002,
                'connections': [
                    {
                        'connects_to': 'ZCM#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZCM#2',
                        'when_at': 'end_straight'
                    }
                ]
            },
            {
                'name': 'ZCM#2',
                'length': 50,
                'connections': [
                    {
                        'connects_to': 'ZCM_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'ZCM_D',
                        'when_at': 'start_deviated'
                    },
                    {
                        'connects_to': 'ZCM_ZPV',
                        'when_at': 'end_straight'
                    },

                ]
            },
            {
                'name': 'ZCM_ZPV',
                'length': 25000,
                'connections': [
                    {
                        'connects_to': 'ZCM#2',
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
                'start_kilometer': 506.6875,
                'length': 68.75,
                'connections': [
                    {
                        'connects_to': 'ZCM_ZPV',
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
                'start_kilometer': 506.725625,
                'length': 810,
                'connections': [
                    {
                        'connects_to': 'ZPV#1',
                        'when_at': 'start_straight'
                    }
                ]
            },
            {
                'name': 'ZPV_D',
                'start_kilometer': 506.725625,
                'length': 810,
                'connections': [
                    {
                        'connects_to': 'ZPV#1',
                        'when_at': 'start_straight'
                    }
                ]
            },
        ])
