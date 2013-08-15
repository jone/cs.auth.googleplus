from cs.auth.googleplus.testing import DUMMY_USER_PROFILE
from zope.publisher.browser import BrowserView
import json


class Auth(BrowserView):
    """Mock googleplus auth"""

    def __call__(self):
        """Receives data like
        {'scope': 'https://www.googleapis.com/auth/userinfo.profile...',
        'state': 'profile',
        'redirect_uri': 'http://domain...',
        'response_type': 'code',
        'client_id': 'some-cliend-id'}
        """

        return """
<html>
<body>
<form action="%(url)s">
    <input type="hidden" name="code" value="some-token" />
    <input type="hidden" name="state" value="profile" />
    <input type="submit" name="accept" value="accept" />
</form>
<form action="%(url)s">
    <input type="hidden" name="error" value="some-error" />
    <input type="hidden" name="error_reason" value="some error reason" />
    <input type="submit" name="cancel" value="cancel" />
</form>

</body>
</html>
""" % {'url': self.request.get('redirect_uri')}


class Token(BrowserView):
    """Mock for googleplus token"""

    def __call__(self):
        """Receives data like
        {'client_secret': 'fHicaEcQZAZMjFpuqWOSqyrw',
        'code': 'some-code',
        'grant_type': 'authorization_code',
        'client_id': '*.apps.googleusercontent.com',
        'redirect_uri': 'http://domain...'}
        """
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'access_token': 'some_access_token'})



class Profile(BrowserView):
    """Mock for googleplus token"""

    def __call__(self):
        """Receives data like
        {'access_token': 'some-access-token'}
        """
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(DUMMY_USER_PROFILE)

