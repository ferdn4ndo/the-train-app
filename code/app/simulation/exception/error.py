class Error(Exception):
    """
    Base class for exceptions in this module.
    """
    pass


class InvalidChoiceError(Error):
    """
    Exception raised when a given value doesn't match an expected list of choices
    """


class InvalidClassError(Error):
    """
    Exception raised when the expected object classs is not the expected one.

    Attributes:
        expected_type -- the expected type (class) of the object
        actual_type -- the actual type (class) of the object
    """

    def __init__(self, expected_type, actual_type):
        self.expected_type = expected_type
        self.actual_type = actual_type

        message = "Invalid type! Was expecting {} and got {}".format(
            expected_type, actual_type
        )

        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class UnprocessableEntityError(Error):
    """
    Exception raised when the expected object does not have the needed
    conditions to be processed.
    """
    pass


class ConflictConditionError(Error):
    """
    Exception raised when an unexpected conflict condition happens, halting
    the code flow
    """
    pass


class NotFoundError(Error):
    """
    Exception raised when a resource that should be present is not found, halting
    the code flow
    """
    pass

class EmptyCollectionError(Error):
    """
    Exception raised when a collection is empty and for that reason can't be
    processed
    """
    pass
