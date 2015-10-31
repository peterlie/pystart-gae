#!/usr/bin/env python
#
# See LICENSE file
#

__author__ = 'pystart-gae'

"""

This file contains admin routines

"""

import logging
logging.getLogger().setLevel(logging.DEBUG)

# import humanize

# from slack_bot import botMsg

from base_handler import BaseRequestHandler
from google.appengine.api import users
from webapp2_extras.appengine.users import admin_required
# from google.appengine.datastore.datastore_query import Cursor

from utils import decode
from models import AppData

# from dateutil import parser

import datetime


def run_tests():
    # TODO - put some test code here.

    return True  # but for now assume success


class AdminLandingHandler(BaseRequestHandler):
    """ Admin Landing Page """

    @admin_required
    def get(self):
        """ /admin """

        self.log_access()

        return self.render_to_response(
            'templates/admin_results.html', {'what_result': 'Landing Page', 'results': 'Seats and Tray Tables Up'})


class AdminHandler(BaseRequestHandler):
    """ manage the app

        these all require admin privs (google appengine admin)

        TODO: put commands in a list to make for easier validation

    """

    @admin_required
    def get(self, command):

        self.log_access()

        # now that the decorator provided the belt, pull on the suspenders:
        if not users.is_current_user_admin():
            logging.error('aborting in admin because someone got here without admin privs')
            return self.abort(403)

        if command == 'a':
            """ do a

            """

            self.session.add_flash('testing msg - error', level='error')
            self.session.add_flash('this is A really - info', level='info')
            return self.render_to_response(
                'templates/admin_results.html', {'what_result': 'Page A', 'results': 'A results'})

        elif command == 'b':
            """ do b

            """

            data = {}

            data.update({})

            self.session.add_flash('this is B really', level='info')

            return self.render_to_response(
                'templates/admin_results.html', {'what_result': 'Page B', 'results': 'B results'})

        elif command == 'test':
            # generic admin page for testing etc...
            # TODO - change name of page to admin_test for God's sake

            self.session.add_flash('Not Implemented', level='alert-warning')
            return self.render_to_response(
                'templates/admin_results.html', {'what_result': 'Testing', 'results': 'Testing Not Implemented'})

        else:
            # Unknown admin command?

            self.session.add_flash('Unknown command %s' % command, level='error')
            logging.error('Unknown admin command %s' % command)
            self.redirect('/admin')

    # ========================================================================================================================

    def post(self, command):

        logging.debug('admin POST command %s' % command)

        self.log_access()

        if not users.is_current_user_admin():
            logging.error('aborting in admin because someone got to post without admin privs')
            return self.abort(403)

        elif command == 'showappdata':

            FETCH_NUM = 100

            app_data = None
            app_data = AppData.query().fetch(FETCH_NUM)

            return self.render_to_response(
                'templates/appdata.html',
                {
                    'app_data': app_data
                })

        elif command == 'purgeappdata':
            """ purge app logs

            TODO document/make setting of 30 day default purge period

            """

            before_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)

            logging.info('Admin Purging App Data before %s' % before_date)

            try:
                AppData.purge(before=before_date)
            except Exception as e:
                self.session.add_flash('%s' % e, level='error')

            return self.redirect('/admin')

        elif command == 'purge_some_app_data':
            """ purge some app data

            """

            HOW_MANY = 100

            count = decode(self.request.get('count'))
            if count:
                count = int(count)
            else:
                count = HOW_MANY

            logging.info('Admin Purging Some App Data - count: %d' % count)

            try:
                AppData.purge_some(count=count)
            except Exception as e:
                self.session.add_flash('%s' % e, level='error')

            return self.redirect('/admin')

        elif command == 'runtests':
            logging.info('Admin Run Tests')

            self.session.add_flash('Running Tests', level='info')

            try:
                result = run_tests()
            except Exception as e:
                return self.render_to_response(
                    'templates/admin_results.html', {'what_result': 'Testing', 'results': '%s' % e})

            return self.render_to_response(
                'templates/admin_results.html', {'what_result': 'Testing', 'results': result})

        else:
            self.session.add_flash('Unknown Admin command %s' % command, level='error')
            return self.redirect('/admin')

        # We should not get here.
        logging.error('We should not get here, falling thru bottom of admin post handler')
        self.session.add_flash('Wut? Fell thru Admin...?', level='error')
        return self.redirect('/admin')
