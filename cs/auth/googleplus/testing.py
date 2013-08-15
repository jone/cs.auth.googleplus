from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig
from App.config import getConfiguration


DUMMY_USER_PROFILE = {'id': 'profileid',
                      'name': 'SomeName',
                      'email': 'somename@email.com',
                      'picture': 'http://someurl....jpeg'}


class GooglePlusAuthLayer(PloneSandboxLayer):

    defaultBases = (PLONE_ZSERVER, )

    # Simulated ZConfig data
    zconfigData = {
        'cache.type': 'memory',
        'cache.regions': 'short, long',
        'cache.short.expire': '3',
        'cache.long.expire': '10',
        'session.type': 'memory',
        'session.key': 'beaker.session',
        'session.auto': 'off',
    }

    def setUpZope(self, app, configurationContext):

        cfg = getConfiguration()
        cfg.product_config = {'beaker': self.zconfigData}

        import cs.auth.googleplus
        xmlconfig.file('configure.zcml', cs.auth.googleplus,
                       context=configurationContext)

        import cs.auth.googleplus.tests
        xmlconfig.file('tests.zcml', cs.auth.googleplus.tests,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'cs.auth.googleplus:default')


GOOGLEPLUS_AUTH_FIXTURE = GooglePlusAuthLayer()

GOOGLEPLUS_AUTH_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GOOGLEPLUS_AUTH_FIXTURE, ), name="cs.auth.googleplus:Integration")
