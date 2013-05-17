
Introduction
============

A PAS plugin to login into a Plone Site using Google+.


Installation and getting started
-----------------------------------

Add 'cs.auth.googleplus' and 'requests' to your buildout.cfg's eggs list.

You have to add a configuration similar to this to your buildout.cfg::

 zope-conf-additional =
    <product-config beaker>
        session type file
        session.data_dir ${buildout:directory}/var/sessions/data
        session.lock_dir ${buildout:directory}/var/sessions/lock
        session.key beaker.session
        session.secret this-is-my-secret-${buildout:directory}
    </product-config>

This is needed because we are using collective.beaker to handle Google+ login
session information.

Install the product in the Plone Control Panel

Create a new Google+ app at https://developers.google.com/+/ and fill in the
required data in the plugin's control panel form.


Credit
--------


