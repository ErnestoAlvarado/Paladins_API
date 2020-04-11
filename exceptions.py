class Error(Exception):
    pass


class ServerAndClientTimeMismatch(Error):
    """"Client and Server do not have matching timestamps"""
    pass


class RateLimitReached(Error):
    """Occurs when user reaches daily request limit or max sessions per day"""
    pass


class InvalidSession(Error):
    """ Session has died unexpectedly or no session exists"""
    pass


class InvalidDevId(Error):
    pass


class BadInput(Error):
    pass


class NotFound(Error):
    pass
