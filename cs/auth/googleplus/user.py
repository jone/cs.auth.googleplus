from zope.interface import implements
from interfaces import IGooglePlusUser
from Products.PlonePAS.plugins.ufactory import PloneUser

class GooglePlusUser(PloneUser):
    implements(IGooglePlusUser)


