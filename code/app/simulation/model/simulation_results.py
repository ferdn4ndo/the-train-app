import logging

from app.simulation.model.simulation_frame import SimulationFrame


class SimulationResults:

    def __init__(self, simulation, frames=None, controller_name='Undefined Controller'):
        self.logger = logging.getLogger(__name__)
        self.route_name = simulation.route.name
        self.simulation_uuid = simulation.uuid
        self.controller_name = controller_name
        self.calculated_time_elapsed = simulation.time_dynamics.get_elapsed_time()
        self.has_finished = simulation.has_finished
        self.frames = [frame.serialize() for frame in frames] if frames is not None else []
        self.sections = [section.serialize() for section in simulation.route.sections_mapper.sections]
        self.trains_log = []

    def reset(self):
        del self.frames[:]
        del self.trains_log[:]

    def register_frame(self, simulation):
        frame = SimulationFrame(simulation, len(self.frames))
        self.frames.append(frame)

        for train in frame.trains:
            if train["prefix"] not in self.trains_log:
                self.trains_log.append(train["prefix"])

        self.calculated_time_elapsed = simulation.time_dynamics.get_elapsed_time()
        self.has_finished = simulation.has_finished

    def serialize(self):
        return {
            "route_name": self.route_name,
            "sections": self.sections,
            "simulation_uuid": self.simulation_uuid,
            "final_total_cost": self.get_last_total_cost(),
            "final_status": self.get_final_status(),
            "frames": [frame.serialize() for frame in self.frames],
        }

    def get_last_total_cost(self):
        if len(self.frames) == 0:
            return 0
        return self.frames[-1].total_cost

    def get_final_status(self):
        all_trains_finished = True
        for train in self.frames[-1].trains:
            if not train["finished"]:
                all_trains_finished = False

        return "SUCCESS" if all_trains_finished else "FAIL"
