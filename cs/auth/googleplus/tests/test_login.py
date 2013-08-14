from unittest2 import TestCase
from cs.auth.googleplus.testing import GOOGLEPLUS_AUTH_INTEGRATION_TESTING


class TestGoogleLogin(TestCase):

    layer = GOOGLEPLUS_AUTH_INTEGRATION_TESTING

    def test_bla(self):
        self.assertTrue(True)
