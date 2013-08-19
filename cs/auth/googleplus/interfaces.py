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
