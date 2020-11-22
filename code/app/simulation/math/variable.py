import logging


class Variable:
    """Variable class, used to store and handle variable numeric values (always treated as floats)"""
    UNIT_METERS_PER_SECOND = 'm/s'
    UNIT_KILOMETERS_PER_HOUR = 'km/h'
    UNIT_MILES_PER_HOUR = 'mph'

    def __init__(self, value=0.0, unit=None):
        """Class constructor"""
        self.memory_size = 1024
        self.last_values = [None] * self.memory_size
        self.last_derivative_values = [None] * self.memory_size
        self.unit = unit

        self._value = value

    @property
    def value(self) -> float:
        """Getter for the variable value"""
        return float(self._value)

    @value.setter
    def value(self, value):
        """Setter for the variable value"""
        self.last_values.pop()
        self.last_values.append(self._value)
        self._value = value

    @value.deleter
    def value(self):
        """Deleter for the variable value"""
        del self._value

    def convert_to_unit(self, new_unit):
        """Convert the value to another unit"""
        if (
            self.unit is None or
            new_unit is None or
            new_unit.tag == self.unit.tag
        ):
            return self._value

        convert_functions = [
            {
                'from': self.UNIT_METERS_PER_SECOND,
                'to': self.UNIT_KILOMETERS_PER_HOUR,
                'product_constant': 1.6,
                'sum_constant': 0.0
            },
            {
                'from': self.UNIT_METERS_PER_SECOND,
                'to': self.UNIT_MILES_PER_HOUR,
                'product_constant': 2.2369363,
                'sum_constant': 0.0
            },
        ]

        convert_function = next((function_data for function_data in convert_functions if (
            function_data['from'] == self.unit and
            function_data['to'] == new_unit
        )), None)

        if convert_function is None:
            logging.warning(
                "Tried to convert variable from {} to {} unit, but no convert function is described for this case"
                .format(self.unit, new_unit)
            )
            return None

        return self._value * convert_function['product_constant'] + convert_function['sum_constant']
