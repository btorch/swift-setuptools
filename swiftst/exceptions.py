""" See COPYING for license information """

class Error(StandardError):
    """
    Base class for all errors and exceptions
    """
    pass


class HostListError(Error):
    """
    Raised when host list generation fails.
    """
    def __init__(self, status, reason):
        self.status = status
        self.reason = reason
        Error.__init__(self)

    def __str__(self):
        return '%d - %s' % (self.status, self.reason)

    def __repr__(self):
        return '%d - %s' % (self.status, self.reason)
