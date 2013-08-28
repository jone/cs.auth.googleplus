from BTrees.OOBTree import OOBTree
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements
from zope.publisher.browser import BrowserView
from copy import copy

from collective.beaker.interfaces import ISession

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins import (
        IExtractionPlugin,
        IAuthenticationPlugin,
        ICredentialsResetPlugin,
        IPropertiesPlugin,
        IUserEnumerationPlugin,
        IUserFactoryPlugin
    )

from cs.auth.googleplus.user import GooglePlusUser
from cs.auth.googleplus.interfaces import IGooglePlusUser, ICSGooglePlusPlugin

import logging
logger = logging.getLogger('cs.auth.googleplus')


class SessionKeys:
    """Constants used to look up session keys
"""
    userId = "cs.auth.googleplus.id"
    userName = "cs.auth.googleplus.displayName"
    fullname = "cs.auth.googleplus.fullname"
    accessToken = "cs.auth.googleplus.accessToken"
    email = "cs.auth.googleplus.emails"
    location = "cs.auth.googleplus.currentLocation"
    profile_image = "cs.auth.googleplus.image"


class AddForm(BrowserView):
    """Add form the PAS plugin
"""

    template = ViewPageTemplateFile('addform.pt')

    def __call__(self):

        if 'form.button.Add' in self.request.form:
            name = self.request.form.get('id')
            title = self.request.form.get('title')

            plugin = CSGooglePlusUsers(name, title)
            self.context.context[name] = plugin

            self.request.response.redirect(self.context.absolute_url() +
                    '/manage_workspace?manage_tabs_message=Plugin+added.')

        return self.template()


class CSGooglePlusUsers(BasePlugin):
    """PAS plugin for authentication against Google+.
Here, we implement a number of PAS interfaces, using a session managed
by Beaker (via collective.beaker) to temporarily store the values we
have captured.
"""

    # List PAS interfaces we implement here
    implements(
            ICSGooglePlusPlugin,
            IExtractionPlugin,
            ICredentialsResetPlugin,
            IAuthenticationPlugin,
            IPropertiesPlugin,
            IUserEnumerationPlugin,
            IUserFactoryPlugin
        )

    def __init__(self, id, title=None):
        self.__name__ = self.id = id
        self.title = title
        self._storage = OOBTree()

    #
    # IExtractionPlugin
    #
    def extractCredentials(self, request):
        """This method is called on every request to extract credentials.
In our case, that means looking for the values we store in the
session.
o Return a mapping of any derived credentials.
o Return an empty mapping to indicate that the plugin found no
appropriate credentials.
"""

        # Get the session from Beaker.

        session = ISession(request, None)

        if session is None:
            return None

        # We have been authenticated and we have a session that has not yet
        # expired:

        if SessionKeys.userId in session:

            return {
                    'src': self.getId(),
                    'userid': session[SessionKeys.userId],
                    'username': session[SessionKeys.userId],

                }

        return None

    #
    # IAuthenticationPlugin
    #

    def authenticateCredentials(self, credentials):
        """This method is called with the credentials that have been
extracted by extractCredentials(), to determine whether the user is
authenticated or not.
We basically trust our session data, so if the session contains a
user, we treat them as authenticated. Other systems may have more
stringent needs, but we should avoid an expensive check here, as this
method may be called very often - at least once per request.
credentials -> (userid, login)
o 'credentials' will be a mapping, as returned by extractCredentials().
o Return a tuple consisting of user ID (which may be different
from the login name) and login
o If the credentials cannot be authenticated, return None.
"""

        # If we didn't extract, ignore
        if credentials.get('src', None) != self.getId():
            return

        # We have a session, which was identified by extractCredentials above.
        # Trust that it extracted the correct user id and login name

        if (
            'userid' in credentials and
            'username' in credentials
        ):
            return (credentials['userid'], credentials['username'],)

        return None

    #
    # ICredentialsResetPlugin
    #

    def resetCredentials(self, request, response):
        """This method is called if the user logs out.
Here, we simply destroy their session.
"""
        session = ISession(request, None)
        if session is None:
            return

        session.delete()

    #
    # IPropertiesPlugin
    #

    def getPropertiesForUser(self, user, request=None):
        """This method is called whenever Plone needs to get properties for
a user. We return a dictionary with properties that map to those
Plone expect.
user -> {}
o User will implement IPropertiedUser.
o Plugin should return a dictionary or an object providing
IPropertySheet.
o Plugin may scribble on the user, if needed (but must still
return a mapping, even if empty).
o May assign properties based on values in the REQUEST object, if
present
"""
        # If this is a GooglePlus User, it implements IGooglePlusUser
        if not IGooglePlusUser.providedBy(user):
            return {}

        else:
            user_data = self._storage.get(user.getId(), None)
            if user_data is None:
                return {}

            return user_data

    #
    # IUserEnumerationPlugin
    #

    def enumerateUsers(self,
                       id=None,
                       login=None,
                       exact_match=False,
                       sort_by=None,
                       max_results=None,
                       **kw):
        """This function is used to search for users.
It supports exact_match and partial search
"""

        def match(data, criterias, exact_match=False):
            """Search for users with the given criterias"""
            for propertyname, searchstring in criterias.items():
                stored_value = data.get(propertyname, None)
                if stored_value is None:
                    return False

                if isinstance(stored_value, unicode):
                    stored_value = stored_value.decode('utf-8')
                if isinstance(searchstring, unicode):
                    searchstring = searchstring.decode('utf-8')

                if exact_match and searchstring != stored_value:
                    return False
                else:
                    if searchstring not in stored_value:
                        return False
            return True

        if id is not None or login is not None:
            # No diffrents between id and login
            name = id or login
            data = self._storage.get(name, None)
            if data is not None:
                return ({'id': name,
                       'login': name,
                       'title': data.get('fullname'),
                       'email': data.get('email'),
                       'pluginid': self.getId()}, )
            else:
                return ()

        criterias = copy(kw)
        result = [(userid, data) for (userid, data) in self._storage.items()
                     if match(data, criterias, exact_match)]

        return tuple(
            [{'id': user_id,
              'login': user_id,
              'title': data.get('fullname'),
              'email': data.get('email'),
              'pluginid': self.getId()
            } for (user_id, data) in result])


    # IUserFactoryPlugin interface
    def createUser(self, user_id, name):
        # Create a GooglePlusUser just if this is a GooglePlus User id
        user_data = self._storage.get(user_id, None)
        if user_data is not None:
            return GooglePlusUser(user_id, name)

        return None
