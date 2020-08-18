class SwiplError(BaseException):
    pass


class SWIExecutableNotFound(SwiplError):
    """Exception raised if SWI-Prolog executable is not found on the specified path."""

    pass


class SWICompileError(SwiplError):
    """Exception raised if loaded module has compile errors."""

    pass


class SWIQueryError(SwiplError):
    """Exception raised if query raises an error."""

    pass


class SWIQueryTimeout(SwiplError):
    pass
