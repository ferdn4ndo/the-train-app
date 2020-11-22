from app.simulation.math.variable import Variable


class TrainEquation:
    def __init__(self, options):
        """Class constructor"""
        self.train_options = options
        self.time_dynamics = options.time_dynamics

        self.velocity = Variable()  # [m/s]
        self.desired_velocity = 0

        self.total_power = 1000  # [W]

    def update_velocity(self):
        """Updates the train velocity"""
        if self.velocity.value != self.desired_velocity:
            # we should perform some calculations here
            self.velocity.value = self.desired_velocity

    def calculate_next_step_position(self, section_length, last_relative_position):
        """Calculates the next relative position of the train, based on the section length and on last position"""
        time_diff = self.time_dynamics.get_step_duration()
        last_real_position = section_length * last_relative_position
        new_real_position = self.velocity.value * time_diff + last_real_position
        return new_real_position / section_length

    def calculate_cost(self, train, distance_to_goal=0.0):
        """Calculates the instant cost of a given train and its current distance to the goal"""
        return float(self.train_options.cost_normalizer * (
            train.odometer * self.train_options.meter_travelled_cost +
            train.traveling_time * self.train_options.traveling_time_cost +
            train.stopped_time * self.train_options.stopped_time_cost +
            distance_to_goal * self.train_options.distance_to_goal_cost +
            len(train.actions_history) * self.train_options.action_cost
        ))
