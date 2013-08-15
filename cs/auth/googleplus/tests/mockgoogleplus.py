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
        # data = {'code': 'some-token',
        #         'state': 'profile'}
        # requests.post(self.request.get('redirect_uri'), data)

        return """
<html>
<body>
<form action="%s">
    <input type="hidden" name="code" value="some-token" />
    <input type="hidden" name="state" value="profile" />
    <input type="submit" name="accept" value="accept" />
</body>
</html>
""" % self.request.get('redirect_uri')


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
        return json.dumps({'id': 'profileid',
                           'name': 'Some Name',
                           'email': 'somename@email.com',
                           'picture': 'http://someurl....jpeg'})

