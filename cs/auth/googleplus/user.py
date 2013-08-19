from interfaces import IGooglePlusUser
from Products.PlonePAS.plugins.ufactory import PloneUser
from zope.interface import implements


class GooglePlusUser(PloneUser):
    implements(IGooglePlusUser)
