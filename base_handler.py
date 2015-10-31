#!/usr/bin/env python
#
# See LICENSE file
#

__author__ = 'pystart-gae'

"""

This module contains the base request handler that any module with handlers must import.


"""
import sys
import os
import traceback

from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
sys.modules['ndb'] = ndb   # so webapp2 sessions knows about ndb

import logging
logging.getLogger().setLevel(logging.DEBUG)

import settings

import webapp2
from webapp2_extras import sessions
from webapp2_extras import sessions_ndb
from webapp2_extras import auth
# from webapp2_extras.auth import AuthError
# TODO need to follow this.  Webapp2 auth, sessions and login lots of work yet.   https://gist.github.com/2942374

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from slack_bot import botMsg
from utils import is_testenv


class BaseRequestHandler(webapp2.RequestHandler):
    """ Catch any exceptions and log them, including traceback
        todo: need to execute super if debug, and also todo: need to display error page to user
        All other request handlers here inherit from this base class.

        todo: take advantage of webapp2 exception goodies.
        """

    def __init__(self, request, response):
        """ webapp2 needs these reset each handler invocation"""

        self.initialize(request, response)
        logging.getLogger().setLevel(logging.DEBUG)
        template.register_template_library('templatetags.unixtime')
        os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

    # webapp2 sessions
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()

    @webapp2.cached_property
    def session(self):
        # Returns a database session (using default cookie?)
        return self.session_store.get_session(
            name='db_session',
            factory=sessions_ndb.DatastoreSessionFactory)

    def head(self, *args):
        """Head is used by Twitter. If not used the tweet button shows 0"""
        pass

    def template_path(self, filename):
        """Returns the full path for a template from its path relative to here."""
        return os.path.join(os.path.dirname(__file__), filename)

    def render_to_response(self, filename, template_args):
        """Renders a Django template and sends it to the client.

        Args:
          filename: template path (relative to this file)
          template_args: argument dict for the template

        """

        if users.is_current_user_admin():
            admin_user = True
            logout_url = users.create_logout_url('/')
        else:
            admin_user = False
            logout_url = None

        if is_testenv():
            test_ver = 'Testing...'
        else:
            test_ver = " "

        # Preset values for the template (thanks to metachris for the inspiration)
        #
        values = {
            'test_ver': test_ver,
            'version': settings.VERSION,
            'logout_url': logout_url,
            'is_admin': admin_user,
            'request': self.request,
            'current_uri': self.request.uri,
            'flashes': self.session.get_flashes()
        }

        # Add manually supplied template values
        template_args.update(values)
        self.response.out.write(
            template.render(self.template_path(filename), template_args)
        )

    def log_access(self):
        """ log some request data, return a nice string """

        user = users.get_current_user()
        if user:
            usrmsg = '%s' % user.nickname()
        else:
            usrmsg = 'Anon'

        city = self.request.headers.get('X-AppEngine-City')
        region = self.request.headers.get('X-AppEngine-Region')
        country = self.request.headers.get('X-AppEngine-Country')
        if country == 'ZZ':
            # ZZ means what? location not available? private browsing?  sdk?
            msg = 'Unspecified location'
        else:
            msg = '%s, %s, %s' % (city, region, country)

        ref = self.request.referer or 'no referer'
        ip = self.request.remote_addr or 'no remote addr'
        host = self.request.host or 'no host'
        path = self.request.path or 'no path'

        msg = '%s: %s, %s, %s, %s %s' % (path, host, msg, ref, ip, usrmsg)

        logging.info(msg)

        return msg

    def log_error(self, msg=None):
        """ log an error

        msg: error message to be logged

        """

        if not msg:
            msg = 'pystart-gae Error'
        logging.error(msg)
        return

    def log_exception(self, msg=None, e=None):
        """ log an exception

        msg: our error send_message
        e: exception passed in, or not

        TODO: use this more places

        TODO: i don't think this works right yet, msg is sometimes incomplete.

        """

        if not msg:
            if e:
                msg = e
            else:
                msg = sys.exc_info()[0].__name__
        msg = '%s, %s' % (msg, self.request.remote_addr)
        logging.exception(msg)
        botMsg('%s ' % msg)

    def render_error(self, errormsg, usermsg='Application Error'):
        """Logs the error, notifies the client with the error message.

           TODO - use usermsg or get rid of it

        """

        self.log_error(errormsg)
        self.session.add_flash('%s' % errormsg, level='alert-error')
        self.redirect(self.request.uri)  # TODO - it would be bad if this caused looping errors

    def handle_exception(self, exception, debug_mode):
        # TODO: this can probably be seriously cleaned up.
        exception_name = sys.exc_info()[0].__name__
        exception_details = str(sys.exc_info()[1])
        exception_traceback = ''.join(traceback.format_exception(*sys.exc_info()))
        self.log_exception(msg=exception_name)
        ctx = {
            'usermsg': exception_name,
            'errormsg': exception_details,
            'flashes': self.session.get_flashes()}

        if users.is_current_user_admin() or is_testenv():
            ctx.update({'traceback': exception_traceback})
        if users.is_current_user_admin():
            admin_user = True
            logout_url = users.create_logout_url('/')
            ctx.update({
                'logout_url': logout_url,
                'is_admin': admin_user,
                'request': self.request,
                'current_uri': self.request.uri})

            self.response.out.write(template.render('templates/errors.html', ctx))
        else:
            self.session.add_flash('%s' % exception_name, level='alert-error')
            self.redirect(self.request.uri)
