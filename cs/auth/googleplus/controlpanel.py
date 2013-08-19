from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface

from cs.auth.googleplus import GOOGLEPLUSMessageFactory as _


class IGooglePlusLoginSettings(Interface):

    googleplus_client_id = schema.TextLine(
        title=_(u'GooglePlus Client ID'),
        description=_(u'The App ID/API Key you got when creating the app at '
                      u'https://developers.google.com/+/'))

    googleplus_client_secret = schema.TextLine(
        title=_(u'GooglePlus Client Secret'),
        description=_(u'The App Secret Key you got when creating the app at'
                      u'https://developers.google.com/+/'))


class GooglePlusloginControlPanelForm(RegistryEditForm):
    schema = IGooglePlusLoginSettings

GooglePlusloginControlPanelView = layout.wrap_form(
    GooglePlusloginControlPanelForm,
    ControlPanelFormWrapper)
GooglePlusloginControlPanelView.label = _(u"GooglePlus Login settings")
