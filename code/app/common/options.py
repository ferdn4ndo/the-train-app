class BaseOptions:

    def __init__(self, **options):
        for option_name in options:
            self.__dict__[option_name] = options[option_name]
