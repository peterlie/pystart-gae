#!/usr/bin/env python

# See LICENSE file

"""

This file contains routes and some handlers.

"""

import os
import logging
import sys

from google.appengine.ext import ndb
sys.modules['ndb'] = ndb   # so webapp2 sessions knows about ndb


import webapp2
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


import settings
from admin import AdminHandler
from admin import AdminLandingHandler
import handlers
from cron import CronHandler
from slack_bot import botMsg

from base_handler import BaseRequestHandler

# TODO - make a startup routine someplace which contains all these one time startup things.
logging.info('Startup - loading %s, app version = %s', __name__, os.getenv('CURRENT_VERSION_ID'))
logging.info('OS Environ - %s' % os.environ)


class AboutHandler(BaseRequestHandler):
    """   Simple about Page """

    def get(self):
        """ /about """

        self.log_access()
        return self.render_to_response('templates/about.html', {})


class SlackOpsHandler(BaseRequestHandler):
    """
        Respond to command originating from Slack.

        our token is 7mQHFumz9eeTXDDSoGMBJSju  --- settings.SLACK_OPS_TOKEN

        https://api.slack.com/slash-commands

        for  '/weather 94070'  some payload POSTed like:

            token=gIkuvaNzQIHg97ATvDxqgjtO
            team_id=T0001
            team_domain=example
            channel_id=C2147483705
            channel_name=test
            user_id=U2147483697
            user_name=Steve
            command=/weather
            text=94070

        TODO: this should be over HTTPS? otherwise someone else can access?  maybe obfuscate the URL?
        TODO: return success since we're telling Slack we got the message. And if problem, log and opsMsg it

    """

    def post(self):

        post_values = self.request.POST
        logging.debug('Slack Command POST: %s' % post_values)

        command = self.request.POST['command']
        text = self.request.POST['text'] or 'null'
        botMsg('Received Slack Slash Command %s %s' % (command, text))
        response_text = 'Received %s %s' % (command, text)

        if self.request.POST['token'] != settings.SLACK_OPS_TOKEN:
            logging.error('Invalid Slack Ops Token: %s' % self.request.POST['token'])
            return self.response.out.write('Invalid Ops Token')

        if text == 'test':
            # TODO - invoke tests
            logging.debug('Invoking (NOT FOR NOW) tests via slash ops command')
            # TODO: return some textual status of test results
            pass
        elif text == 'no text':
            # no subcommand, default: hello
            response_text = 'hello'
        else:
            logging.error('Unknown Ops subcommand %s' % text)
            response_text = 'Unknown Ops subcommand %s' % text

        return self.response.out.write(response_text)


routes = [
    webapp2.Route(r'/', handler=handlers.MainHandler, name='main'),
    webapp2.Route(r'/cron/<job>', handler=CronHandler),
    webapp2.Route(r'/admin', AdminLandingHandler, name='adminlanding'),
    webapp2.Route(r'/admin/<command>', AdminHandler),
    webapp2.Route(r'/about', AboutHandler, name='about'),
    webapp2.Route(r'/slackops', SlackOpsHandler, name='slackops')
]

# Sessions not needed yet, but will be I suppose... but use even w/o logins so as to save session state.
sess_config = {}
sess_config['webapp2_extras.sessions'] = {
    'secret_key': settings.SESSIONS_KEY,
    'session_max_age': settings.EIGHT_HOURS     # TODO: not sure this does much.
}


def handle_404(request, response, exception):
    err = 'handle_404 error %s' % request.path
    # TODO: don't unfurl and don't pass full url!, see: https://api.slack.com/docs/unfurling
    logging.error(err)
    response.write('Oops! could not find %s!' % request.url)
    response.set_status(404)

app = webapp2.WSGIApplication(routes, debug=True, config=sess_config)

app.error_handlers[404] = handle_404
