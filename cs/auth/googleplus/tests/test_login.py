from cs.auth.googleplus import login as gplogin
from cs.auth.googleplus.testing import GOOGLEPLUS_AUTH_FUNCTIONAL_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from unittest2 import TestCase
from zope.component import getUtility
from cs.auth.googleplus.controlpanel import IGooglePlusLoginSettings
import transaction

ORIG_AUTH = gplogin.GOOGLEPLUS_AUTH_URL
ORIG_TOKEN = gplogin.GOOGLEPLUS_ACCESS_TOKEN_URL
ORIG_PROFILE = gplogin.GOOGLEPLUS_PROFILE_URL


class TestGoogleLogin(TestCase):

    layer = GOOGLEPLUS_AUTH_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal_url = portal.portal_url()
        setRoles(portal, TEST_USER_ID, ['Manager', ])
        login(portal, TEST_USER_NAME)

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

        gplogin.GOOGLEPLUS_AUTH_URL = 'http://localhost:55001/plone/auth'
        gplogin.GOOGLEPLUS_ACCESS_TOKEN_URL = 'http://localhost:55001/plone/token'
        gplogin.GOOGLEPLUS_PROFILE_URL = 'http://localhost:55001/plone/profile'

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IGooglePlusLoginSettings)
        proxy.googleplus_client_id = u'dummy_id'
        proxy.googleplus_client_secret = u'dummy_secret'

        transaction.commit()

    def test_redirect_to_google_on_first_request(self):

        self.browser.open('%s/googleplus-login' % self.portal_url)

        self.assertTrue(self.browser.url.startswith(
                            gplogin.GOOGLEPLUS_AUTH_URL),
                        'Expected to be redirected on first request')

    def test_successfully_logged_in(self):
        self.browser.open('%s/googleplus-login' % self.portal_url)
        self.browser.getControl(name='accept').click()

        self.assertEquals('%s/logged_in' % self.portal_url, self.browser.url,
            'Should be on logged_in page')

    def tearDown(self):
        gplogin.GOOGLEPLUS_AUTH_URL = ORIG_AUTH
        gplogin.GOOGLEPLUS_ACCESS_TOKEN_URL = ORIG_TOKEN
        gplogin.GOOGLEPLUS_PROFILE_URL = ORIG_PROFILE
