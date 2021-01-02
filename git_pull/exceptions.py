class DeniedRequest(Exception):
    """
    Thrown when Github denies a web request.
    """

    pass


class InvalidUsernameError(Exception):
    """
    Thrown when Github username doesn't exist.
    """

    pass
