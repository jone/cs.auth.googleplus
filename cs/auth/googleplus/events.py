from cs.auth.googleplus.interfaces import IGoogleUserEvent
from cs.auth.googleplus.interfaces import IGoogleUserLoggedInEvent
from cs.auth.googleplus.interfaces import IGoogleUserRegisteredEvent
from zope.interface import implements


class GoogleUserEvent(object):
    implements(IGoogleUserEvent)

    def __init__(self, principal, profile=None):
        self.principal = principal
        self.profile = profile or {}


class GoogleUserRegisteredEvent(GoogleUserEvent):
    implements(IGoogleUserRegisteredEvent)


class GoogleUserLoggedInEvent(GoogleUserEvent):
    implements(IGoogleUserLoggedInEvent)
