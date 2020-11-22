from app.simulation.model.route import Route


class ComparisonRouteTwo(Route):
    """
    Second route for results comparison between different controllers.

    It represents the real world route between Desvio Ribas (LDV) and Engenheiro Bley (LEB).

    Stations:

    LDV - DESVIO RIBAS - km 230,900
    LLY - LINEU DO AMARAL - km 222,700
    LLP - ÂNGELO LOPES - km 209,300
    LMO - MACHADO DA COSTA - km 196,300
    LWV - ENG WALTER S. VELOSO - km 186,000
    LOZ - OZÓRIO ALMEIDA - km 180,200
    LEB - ENG BLEY - km 170,400
    """
    def __init__(self):
        super().__init__()
        self.name = "Comparison Route Two"
        self.parse_sections_list([
            {
                'name': 'LDV_P',
                'description': 'Desvio Ribas - Via Principal',
                'length': 2074,
                'connections': [
                    {
                        'connects_to': 'LDV#1',
                        'when_at': 'end_straight'
                    }
                ],
            },
            {
                'name': 'LDV_D',
                'description': 'Desvio Ribas - Via Desviada',
                'length': 2074,
                'connections': [
                    {
                        'connects_to': 'LDV#1',
                        'when_at': 'end_straight'
                    }
                ]
            },
            {
                'name': 'LDV#1',
                'length': 103,
                'description': 'Desvio Ribas - AMV Extremidade Sul',
                'connections': [
                    {
                        'connects_to': 'LDV_LLY',
                        'when_at': 'end_straight'
                    },
                    {
                        'connects_to': 'LDV_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LDV_D',
                        'when_at': 'start_deviated'
                    },

                ]
            },
            {
                'name': 'LDV_LLY',
                'description': 'Trecho Desvio Ribas - Lineu do Amaral',
                'length': 7032,
                'connections': [
                    {
                        'connects_to': 'LDV#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LLY#1',
                        'when_at': 'end_straight'
                    },

                ]
            },
            {
                'name': 'LLY#1',
                'length': 103,
                'description': 'Lineu do Amaral - AMV Extremidade Norte',
                'connections': [
                    {
                        'connects_to': 'LDV_LLY',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LLY_P',
                        'when_at': 'end_straight'
                    },
                    {
                        'connects_to': 'LLY_D',
                        'when_at': 'end_deviated'
                    },

                ]
            },
            {
                'name': 'LLY_P',
                'length': 1640,
                'description': 'Lineu do Amaral - Via Principal',
                'connections': [
                    {
                        'connects_to': 'LLY#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LLY#2',
                        'when_at': 'end_straight'
                    }
                ]
            },
            {
                'name': 'LLY_D',
                'length': 1643,
                'description': 'Lineu do Amaral - Via Desviada',
                'connections': [
                    {
                        'connects_to': 'LLY#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LLY#2',
                        'when_at': 'end_straight'
                    }
                ]
            },
            {
                'name': 'LLY#2',
                'length': 132,
                'description': 'Lineu do Amaral - AMV Extremidade Sul',
                'connections': [
                    {
                        'connects_to': 'LLY_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LLY_D',
                        'when_at': 'start_deviated'
                    },
                    {
                        'connects_to': 'LLY_LLP',
                        'when_at': 'end_straight'
                    },

                ]
            },
            {
                'name': 'LLY_LLP',
                'description': 'Trecho Lineu do Amaral - Ângelo Lopes',
                'length': 11462,
                'connections': [
                    {
                        'connects_to': 'LLY#2',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LLP#1',
                        'when_at': 'end_straight'
                    },

                ]
            },
            {
                'name': 'LLP#1',
                'description': 'Ângelo Lopes - AMV Extremidade Norte',
                'length': 124,
                'connections': [
                    {
                        'connects_to': 'LLY_LLP',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LLP_P',
                        'when_at': 'end_straight'
                    },
                    {
                        'connects_to': 'LLP_D',
                        'when_at': 'end_deviated'
                    },

                ]
            },
            {
                'name': 'LLP_P',
                'description': 'Ângelo Lopes - Via Principal',
                'length': 1400,
                'connections': [
                    {
                        'connects_to': 'LLP#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LLP#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LLP_D',
                'description': 'Ângelo Lopes - Via Desviada',
                'length': 1394,
                'connections': [
                    {
                        'connects_to': 'LLP#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LLP#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LLP#2',
                'description': 'Ângelo Lopes - AMV Extremidade Sul',
                'length': 82,
                'connections': [
                    {
                        'connects_to': 'LLP_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LLP_D',
                        'when_at': 'start_deviated'
                    },
                    {
                        'connects_to': 'LLP_LMO',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LLP_LMO',
                'description': 'Trecho Ângelo Lopes - Machado da Costa',
                'length': 11788,
                'connections': [
                    {
                        'connects_to': 'LLP#2',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LMO#1',
                        'when_at': 'end_straight'
                    },

                ]
            },
            {
                'name': 'LMO#1',
                'description': 'Machado da Costa - AMV Extremidade Norte',
                'length': 97,
                'connections': [
                    {
                        'connects_to': 'LLP_LMO',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LMO_P',
                        'when_at': 'end_straight'
                    },
                    {
                        'connects_to': 'LMO_D',
                        'when_at': 'end_deviated'
                    },

                ]
            },
            {
                'name': 'LMO_P',
                'description': 'Machado da Costa - Via Principal',
                'length': 1344,
                'connections': [
                    {
                        'connects_to': 'LMO#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LMO#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LMO_D',
                'description': 'Machado da Costa - Via Desviada',
                'length': 1346,
                'connections': [
                    {
                        'connects_to': 'LMO#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LMO#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LMO#2',
                'description': 'Machado da Costa - AMV Extremidade Sul',
                'length': 104,
                'connections': [
                    {
                        'connects_to': 'LMO_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LMO_D',
                        'when_at': 'start_deviated'
                    },
                    {
                        'connects_to': 'LMO_LVW',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LMO_LVW',
                'description': 'Trecho Machado da Costa - Eng. Walter S. Veloso',
                'length': 8585,
                'connections': [
                    {
                        'connects_to': 'LMO#2',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LVW#1',
                        'when_at': 'end_straight'
                    },

                ]
            },
            {
                'name': 'LVW#1',
                'description': 'Eng. Walter S. Veloso - AMV Extremidade Norte',
                'length': 92,
                'connections': [
                    {
                        'connects_to': 'LMO_LVW',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LVW_P',
                        'when_at': 'end_straight'
                    },
                    {
                        'connects_to': 'LVW_D',
                        'when_at': 'end_deviated'
                    },

                ]
            },
            {
                'name': 'LVW_P',
                'description': 'Eng. Walter S. Veloso - Via Principal',
                'length': 1473,
                'connections': [
                    {
                        'connects_to': 'LVW#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LVW#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LVW_D',
                'description': 'Eng. Walter S. Veloso - Via Desviada',
                'length': 1471,
                'connections': [
                    {
                        'connects_to': 'LVW#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LVW#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LVW#2',
                'description': 'Eng. Walter S. Veloso - AMV Extremidade Sul',
                'length': 101,
                'connections': [
                    {
                        'connects_to': 'LVW_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LVW_D',
                        'when_at': 'start_deviated'
                    },
                    {
                        'connects_to': 'LVW_LOZ',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LVW_LOZ',
                'description': 'Trecho Eng. Walter S. Veloso - Ozório Almeida',
                'length': 4497,
                'connections': [
                    {
                        'connects_to': 'LVW#2',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LOZ#1',
                        'when_at': 'end_straight'
                    },

                ]
            },
            {
                'name': 'LOZ#1',
                'description': 'Ozório Almeida - AMV Extremidade Norte',
                'length': 106,
                'connections': [
                    {
                        'connects_to': 'LVW_LOZ',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LOZ_P',
                        'when_at': 'end_straight'
                    },
                    {
                        'connects_to': 'LOZ_D',
                        'when_at': 'end_deviated'
                    },

                ]
            },
            {
                'name': 'LOZ_P',
                'description': 'Ozório Almeida - Via Principal',
                'length': 1303,
                'connections': [
                    {
                        'connects_to': 'LOZ#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LOZ#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LOZ_D',
                'description': 'Ozório Almeida - Via Desviada',
                'length': 1304,
                'connections': [
                    {
                        'connects_to': 'LOZ#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LOZ#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LOZ#2',
                'description': 'Ozório Almeida - AMV Extremidade Sul',
                'length': 111,
                'connections': [
                    {
                        'connects_to': 'LOZ_P',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LOZ_D',
                        'when_at': 'start_deviated'
                    },
                    {
                        'connects_to': 'LOZ_LEB',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LOZ_LEB',
                'description': 'Trecho Ozório Almeida - Eng. Bley',
                'length': 8549,
                'connections': [
                    {
                        'connects_to': 'LOZ#2',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LEB#1',
                        'when_at': 'end_straight'
                    },

                ]
            },
            {
                'name': 'LEB#1',
                'description': 'Eng. Bley - AMV Extremidade Norte',
                'length': 42,
                'connections': [
                    {
                        'connects_to': 'LOZ_LEB',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LEB#2',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LEB#2',
                'description': 'Eng. Bley - AMV Pátio Central Norte',
                'length': 60,
                'connections': [
                    {
                        'connects_to': 'LEB#1',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LEB_P',
                        'when_at': 'end_straight'
                    },
                    {
                        'connects_to': 'LEB_2',
                        'when_at': 'end_deviated'
                    },

                ]
            },
            {
                'name': 'LEB_P',
                'description': 'Eng. Bley - Via Principal',
                'length': 1379,
                'connections': [
                    {
                        'connects_to': 'LEB#2',
                        'when_at': 'start_straight'
                    },
                ]
            },
            {
                'name': 'LEB_2',
                'description': 'Eng. Bley - Pátio Central Alça',
                'length': 492,
                'connections': [
                    {
                        'connects_to': 'LEB#2',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LEB#3',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LEB#3',
                'description': 'Eng. Bley - AMV TPS Leste',
                'length': 42,
                'connections': [
                    {
                        'connects_to': 'LEB_2',
                        'when_at': 'start_straight'
                    },
                    {
                        'connects_to': 'LEB_D',
                        'when_at': 'end_straight'
                    },
                ]
            },
            {
                'name': 'LEB_D',
                'description': 'Eng. Bley - Via Desviada',
                'length': 791,
                'connections': [
                    {
                        'connects_to': 'LEB#3',
                        'when_at': 'start_straight'
                    },
                ]
            },
        ])
