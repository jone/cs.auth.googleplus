import hashlib
import json
import requests
import urllib

from collective.beaker.interfaces import ISession
from plone.registry.interfaces import IRegistry
from Products.CMFPlone import PloneMessageFactory as pmf
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility
from zope.event import notify
from zope.publisher.browser import BrowserView


from cs.auth.googleplus import GOOGLEPLUSMessageFactory as _
from cs.auth.googleplus.events import GoogleUserLoggedInEvent
from cs.auth.googleplus.events import GoogleUserRegisteredEvent
from cs.auth.googleplus.interfaces import ICSGooglePlusPlugin
from cs.auth.googleplus.plugin import SessionKeys


GOOGLEPLUS_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLEPLUS_ACCESS_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
GOOGLEPLUS_AUTHENTICATION_SALT_KEY = 'cs.auth.googleplus.AUTHENTICATION_SALT_KEY'
GOOGLEPLUS_PROFILE_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
PERMISSIONS = (r"https://www.googleapis.com/auth/userinfo.profile" +
               r" https://www.googleapis.com/auth/userinfo.email")
RESPONSE = 'code'
STATE = 'profile'
GRANT = 'authorization_code'

from logging import getLogger
log = getLogger('cs.auth.googleplus')


class GooglePlusLogin(BrowserView):
    """This view implements the Google+ OAuth 2.0 login protocol.

The user may access the view via a link in an action or elsewhere. He
will then be immediately redirected to Google+, which will ask him to
authorize this as an application.
Assuming that works, Google+ will redirect the user back to this same
view, with a code in the request.
"""

    def __call__(self):
        registry = getUtility(IRegistry)
        GOOGLEPLUS_CLIENT_ID = registry.get('cs.auth.googleplus.controlpanel.IGooglePlusLoginSettings.googleplus_client_id').encode()
        GOOGLEPLUS_CLIENT_SECRET = registry.get('cs.auth.googleplus.controlpanel.IGooglePlusLoginSettings.googleplus_client_secret').encode()

        verificationCode = self.request.form.get("code", None)
        error = self.request.form.get("error", None)
        errorReason = self.request.form.get("error_reason", None)

        salt = hashlib.sha256().hexdigest()
        session = ISession(self.request)
        session[GOOGLEPLUS_AUTHENTICATION_SALT_KEY] = salt
        args = {
                'state': STATE,
                'scope': PERMISSIONS,
                'client_id': GOOGLEPLUS_CLIENT_ID,
                'redirect_uri': "%s/%s" % (self.context.absolute_url(),
                                           self.__name__),
                'response_type': RESPONSE,
            }

        # Did we get an error back after a Google+ redirect?
        if error is not None or errorReason is not None:
            log.info(error)
            log.info(errorReason)
            IStatusMessage(self.request).add(_(
                u"GOOGLEPLUS authentication denied"), type="error")
            self.request.response.redirect(self.context.absolute_url())
            return u""

        # Check if this the status is the same...
        return_salt = self.request.form.get('status', '')
        session_salt = session.get(GOOGLEPLUS_AUTHENTICATION_SALT_KEY)
        if return_salt and return_salt != session_salt:
            IStatusMessage(self.request).add(_(
                u"GooglePlus authentication denied"), type="error")
            self.request.response.redirect(self.context.absolute_url())
            log.info('%s != %s' % (
                return_salt,
                session.get(GOOGLEPLUS_AUTHENTICATION_SALT_KEY)))
            return u""

        # If there is no code, this is probably the first request, so redirect
        # to Google+
        if verificationCode is None:
            self.request.response.redirect(
                    "%s?%s" % (GOOGLEPLUS_AUTH_URL, urllib.urlencode(args),)
                )
            return u""

        # If we are on the return path form Google+,
        # exchange the return code for a token
        args = {
            'code': verificationCode,
            'client_id': GOOGLEPLUS_CLIENT_ID,
            'client_secret': GOOGLEPLUS_CLIENT_SECRET,
            'redirect_uri': "%s/%s" % (
                self.context.absolute_url(),
                self.__name__),
            'grant_type': GRANT,
            }

        response = requests.post(GOOGLEPLUS_ACCESS_TOKEN_URL, data=args)

        #Load the profile using the access token we just received
        accessToken = response.json()["access_token"]

        def unicode_to_utf8(data):
            if isinstance(data, unicode):
                return data.encode('utf-8')
            else:
                return data

        def dict_unicode_to_utf8(data):
            new_data = {}
            for key, value in data.items():
                new_data[unicode_to_utf8(key)] = unicode_to_utf8(value)
            return new_data

        profile = json.load(urllib.urlopen(
                "%s?%s" % (
                    GOOGLEPLUS_PROFILE_URL,
                    urllib.urlencode({'access_token': accessToken}),)
            ), object_hook=dict_unicode_to_utf8)

        userId = profile.get('id')
        name = profile.get('name')
        email = profile.get('email', '')
        username = profile.get('name')
        profile_image = profile.get('picture')

        if not userId:
            IStatusMessage(self.request).add(
                _(u"Insufficient information in GooglePlus profile"),
                type="error")
            self.request.response.redirect(self.context.absolute_url())
            return

        # Save the data in the session so that the extraction plugin can
        # authenticate the user to Plone
        session[SessionKeys.accessToken] = accessToken
        session[SessionKeys.userId] = userId
        session[SessionKeys.userName] = username
        session[SessionKeys.fullname] = name
        session[SessionKeys.email] = email
        session[SessionKeys.profile_image] = profile_image
        session.save()

        # Add user data into our plugin storage:
        acl = self.context.acl_users
        initial_login = acl.getUserById(userId) is None

        acl_plugins = acl.plugins
        ids = acl_plugins.listPluginIds(IExtractionPlugin)
        for id in ids:
            plugin = getattr(acl_plugins, id)
            if ICSGooglePlusPlugin.providedBy(plugin):
                user_data = plugin._storage.get(
                    session[SessionKeys.userId], {})
                user_data['username'] = session[SessionKeys.userName]
                user_data['fullname'] = session[SessionKeys.fullname]
                user_data['email'] = session[SessionKeys.email]
                plugin._storage[session[SessionKeys.userId]] = user_data

        IStatusMessage(self.request).add(
            pmf(u"Welcome! You are now logged in."),
            type="info")

        return_args = ''
        if self.request.get('came_from', None) is not None:
            return_args = {'came_from': self.request.get('came_from')}
            return_args = '?' + urllib.urlencode(return_args)

        user = acl.getUserById(userId)
        if initial_login:
            notify(GoogleUserRegisteredEvent(user, profile))
        else:
            notify(GoogleUserLoggedInEvent(user, profile))

        self.request.response.redirect(
            self.context.absolute_url() + '/logged_in' + return_args)
