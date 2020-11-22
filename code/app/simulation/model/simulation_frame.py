import math


class SimulationFrame:

    def __init__(self, simulation, index=0):
        self.index = index
        self.simulation_uuid = simulation.uuid
        self.occupancy_dict = self.read_occupancy(simulation.dispatcher.occupancy_dict)
        self.trains = [train.serialize() for train in simulation.dispatcher.trains]
        self.total_cost = simulation.accumulated_cost
        self.timestamp = simulation.time_dynamics.get_current_timestamp()
        self.timestamp_formatted = self.get_formatted_timestamp()

    def serialize(self):
        return {
            "simulation_uuid": self.simulation_uuid,
            "trains": self.trains,
            "total_cost": self.total_cost,
            "occupancy_dict": self.occupancy_dict,
            "timestamp": self.timestamp,
            "timestamp_formatted": self.get_formatted_timestamp()
        }

    def get_formatted_timestamp(self):
        timestamp = float(self.timestamp)
        hours = int(math.floor(timestamp / (60.0 * 60.0)))
        minutes = int(math.floor((timestamp - (hours * 60.0 * 60.0)) / 60.0))
        seconds = int(math.floor(timestamp - (hours * 60.0 * 60.0) - (minutes * 60.0)))
        return "TS {:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

    def read_occupancy(self, occupancy_dict):
        return {
            section_name: [train.serialize() for train in trains]
            for section_name, trains in occupancy_dict.items()
        }
