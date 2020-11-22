from app.common.date import seconds_to_interval


class TimeDynamics:

    def __init__(self, step_duration=0.001, start_timestamp=0, current_step=0):
        self.start_timestamp = start_timestamp
        self.step_duration = step_duration
        self.current_step = current_step

        self.current_timestamp = self.start_timestamp

    def clone(self):
        return TimeDynamics(
            step_duration=self.step_duration,
            start_timestamp=self.start_timestamp,
            current_step=self.current_step
        )

    def serialize(self):
        return {
            'id': hex(id(self)),
            'start timestamp': self.start_timestamp,
            'step duration': self.step_duration,
            'current step': self.current_step,
            'current timestamp': self.current_timestamp,
        }

    def reset(self):
        self.current_step = 0
        self.current_timestamp = self.start_timestamp

    def get_step_duration(self):
        return self.step_duration

    def step(self):
        self.current_timestamp = self.current_timestamp + self.step_duration
        self.current_step += 1

    def get_current_timestamp(self):
        return self.current_timestamp

    def get_elapsed_time(self):
        elapsed_seconds = self.current_timestamp - self.start_timestamp
        return seconds_to_interval(elapsed_seconds)
