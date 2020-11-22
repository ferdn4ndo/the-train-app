class ActionHistory:

    def __init__(self, dataset=None):
        if dataset is None:
            dataset = []

        self.dataset = dataset

    def take_snapshot(self, train):
        self.dataset.append({
            'step': train.time_dynamics.current_step,
            'data': train.executing_action.serialize(),
            'at_section': train.current_head_section.name,
            'at_position': train.relative_position,
            'reversed': train.is_reversed,
            'accumulated_cost': train.accumulated_cost,
        })
