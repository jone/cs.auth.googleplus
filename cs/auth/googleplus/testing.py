from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class GooglePlusAuthLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):

        import cs.auth.googleplus
        xmlconfig.file('configure.zcml', cs.auth.googleplus,
               context=configurationContext)


    def setUpPloneSite(self, portal):
        applyProfile(portal, 'cs.auth.googleplus:default')


GOOGLEPLUS_AUTH_FIXTURE = GooglePlusAuthLayer()

GOOGLEPLUS_AUTH_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GOOGLEPLUS_AUTH_FIXTURE, ), name="cs.auth.googleplus:Integration")
