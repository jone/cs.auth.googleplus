from cs.auth.googleplus import login as gplogin
from cs.auth.googleplus.controlpanel import IGooglePlusLoginSettings
from cs.auth.googleplus.interfaces import IGoogleUserLoggedInEvent
from cs.auth.googleplus.interfaces import IGoogleUserRegisteredEvent
from cs.auth.googleplus.testing import DUMMY_USER_PROFILE
from cs.auth.googleplus.testing import GOOGLEPLUS_AUTH_FUNCTIONAL_TESTING
from plone.app.testing import PLONE_SITE_ID
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from unittest2 import TestCase
from zope.component import getUtility
from zope.component import provideHandler
import os
import transaction


ORIG_AUTH = gplogin.GOOGLEPLUS_AUTH_URL
ORIG_TOKEN = gplogin.GOOGLEPLUS_ACCESS_TOKEN_URL
ORIG_PROFILE = gplogin.GOOGLEPLUS_PROFILE_URL


def prepare_google_plus_config_for_tests():
    host = os.environ.get('ZSERVER_HOST', 'localhost')
    port = int(os.environ.get('PLONE_TESTING_PORT',
                                  os.environ.get('ZSERVER_PORT', 55001)))

    portal_url = 'http://%s:%s/%s' % (host, port, PLONE_SITE_ID)
    gplogin.GOOGLEPLUS_AUTH_URL = '%s/auth' % portal_url
    gplogin.GOOGLEPLUS_ACCESS_TOKEN_URL = '%s/token' % portal_url
    gplogin.GOOGLEPLUS_PROFILE_URL = '%s/profile' % portal_url

    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IGooglePlusLoginSettings)
    proxy.googleplus_client_id = u'dummy_id'
    proxy.googleplus_client_secret = u'dummy_secret'


class TestGoogleLogin(TestCase):

    layer = GOOGLEPLUS_AUTH_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.portal_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager', ])
        login(self.portal, TEST_USER_NAME)

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

        prepare_google_plus_config_for_tests()
        transaction.commit()

    def login_user(self):
        self.browser.open('%s/googleplus-login' % self.portal_url)
        self.browser.getControl(name='accept').click()

    def test_redirect_to_google_on_first_request(self):
        self.browser.open('%s/googleplus-login' % self.portal_url)

        self.assertTrue(self.browser.url.startswith(
            gplogin.GOOGLEPLUS_AUTH_URL),
            'Expected to be redirected on first request')

    def test_successfully_logged_in(self):
        self.login_user()

        self.assertNotIn('userrole-anonymous',
                          self.browser.contents,
                          'User is not logged in')

        self.assertEquals('%s/logged_in' % self.portal_url, self.browser.url,
                          'Should be on logged_in page')

    def test_cancel_logging_in(self):
        self.browser.open('%s/googleplus-login' % self.portal_url)
        self.browser.getControl(name='cancel').click()

        self.assertIn('GOOGLEPLUS authentication denied',
                      self.browser.contents,
                      'The StatusMessage was not found')

    def test_enumerate_user_exact_match(self):
        self.login_user()
        mtool = self.portal.portal_membership
        id_ = DUMMY_USER_PROFILE['id']
        member = mtool.getMemberById(id_)

        self.assertIsNotNone(member,
            'Did not found the member with username: %s' % id_)
        self.assertEquals(member.getId(), DUMMY_USER_PROFILE['id'])

    def test_enumerate_list_all(self):
        self.login_user()
        mtool = self.portal.portal_membership

        self.assertEquals(1, len(mtool.listMembers()), 'Expect one entry')

    def test_enumerate_user_email_exact_match(self):
        self.login_user()

        pas_search = self.portal.restrictedTraverse('@@pas_search')
        users = pas_search.searchUsers(email=DUMMY_USER_PROFILE['email'],
                                       exact_match=True)

        self.assertEquals(1, len(users), 'There should be one user')

    def test_enumerate_user_email_NOT_match(self):
        self.login_user()

        pas_search = self.portal.restrictedTraverse('@@pas_search')
        users = pas_search.searchUsers(email='donotmatch',
                                       exact_match=True)

        self.assertEquals(0, len(users), 'Expect no user in the result.')

    def test_enumerate_user_email_NOT_exact_match(self):
        self.login_user()

        pas_search = self.portal.restrictedTraverse('@@pas_search')
        users = pas_search.searchUsers(email='donotmatch',
                                       exact_match=False)

        self.assertEquals(0, len(users), 'Expect no user in the result.')

    def test_enumerate_user_email_partialy_match(self):
        self.login_user()

        pas_search = self.portal.restrictedTraverse('@@pas_search')
        users = pas_search.searchUsers(email='@email',
                                       exact_match=False)

        self.assertEquals(1, len(users), 'Expect no user in the result.')

    def test_properties_for_user(self):
        self.login_user()
        mtool = self.portal.portal_membership
        member = mtool.getMemberById(DUMMY_USER_PROFILE['id'])

        self.assertEquals(member.getProperty('fullname'),
                          DUMMY_USER_PROFILE['name'])

        self.assertEquals(member.getProperty('username'),
                          DUMMY_USER_PROFILE['name'])

        self.assertEquals(member.getProperty('email'),
                          DUMMY_USER_PROFILE['email'])

    def test_events_are_fired_correctly(self):
        fired_events = []
        def google_user_event_handler(event):
            fired_events.append((type(event).__name__, event.principal.getId()))
        provideHandler(google_user_event_handler, [IGoogleUserRegisteredEvent])
        provideHandler(google_user_event_handler, [IGoogleUserLoggedInEvent])

        # login the first time -> expects IGoogleUserRegisteredEvent
        self.login_user()
        self.assertEquals([('GoogleUserRegisteredEvent', 'profileid')], fired_events)

        # destroy browser and login second time -> expects IGoogleUserLoggedInEvent
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.login_user()

        self.assertEquals([('GoogleUserRegisteredEvent', 'profileid'),
                           ('GoogleUserLoggedInEvent', 'profileid')], fired_events)
