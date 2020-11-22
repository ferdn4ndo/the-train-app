class Error(Exception):
    """ Base class for exceptions in this module. """
    pass


class InvalidConditionError(Error):
    """ Exception raised when an unexpected invalid condition happens, halting the code flow """
    pass
