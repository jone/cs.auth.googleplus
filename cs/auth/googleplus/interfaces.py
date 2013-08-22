from zope.interface import Attribute
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IGooglePlusLoginLayer(IDefaultBrowserLayer):
    """
Zope 3 browser layer for collective.facebooklogin.
"""


class IGooglePlusUser(Interface):
    """
Marker interface for Users logged in through Google+

"""


class ICSGooglePlusPlugin(Interface):
    """
Marker interface
"""


class IGoogleUserEvent(Interface):
    """An event related to a google user.
    """

    principal = Attribute("The PAS user object")
    profile = Attribute("A dict with profile data from google")


class IGoogleUserRegisteredEvent(IGoogleUserEvent):
    """A new user has been registered and logged in to this site the
    first time.
    """


class IGoogleUserLoggedInEvent(IGoogleUserEvent):
    """A already existing user has logged in.
    """
