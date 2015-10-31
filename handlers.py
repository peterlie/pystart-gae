#!/usr/bin/env python
#
# See LICENSE file
#

__author__ = 'pystart-gae'

"""

This file contains non-admin webapp2 rquest handlers.

"""

from base_handler import BaseRequestHandler

import logging
logging.getLogger().setLevel(logging.DEBUG)

from slack_bot import botMsg

from models import AppData

from utils import AppError

# from google.appengine.datastore.datastore_query import Cursor


class MainHandler(BaseRequestHandler):
    """ non-logged in home page

    """
    def get(self):

        msg = self.log_access()
        botMsg('%s' % msg)

        return self.render_to_response('templates/index.html', {'data': None})


class DataHandler(BaseRequestHandler):
    """ display some data """

    def get(self):
        """ /data """

        self.log_access()

        data = None

        try:
            data = AppData.get_some()
        except AppError, e:
            # exception already logged
            self.session.add_flash('%s' % e, level='error')
        except Exception, e:
            self.session.add_flash('System Error: %s' % e, level='error')

        self.render_to_response('templates/index.html', {'data': data})
