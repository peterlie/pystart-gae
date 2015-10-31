# -*- coding: utf-8 -*-
#
# See LICENSE file
#

__author__ = 'pystart-gae'

"""

This file implements a bot to send messages to Slack teamware

"""
import logging
logging.getLogger().setLevel(logging.DEBUG)

from google.appengine.api import urlfetch

import json
import settings
from utils import is_testenv


def botMsg(msg):
    """ simpler function to send a message via slack bot"""

    if not msg:
        return

    bot = SlackBot()
    bot.send(msg)
    logging.info('Slack msg: %s' % msg)


def testSlackBot():
    """ test slackbot """

    bot = SlackBot()
    bot.send('Testing 1 2 3....')


class SlackBot(object):
    """ bot

    """

    def __init__(self, webhook_url=settings.SLACK_WEBHOOK_URL, channel='#general', username='pystart-gae'):

        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username

    def send(self, message):
        """ send the message to slack """

        if not isinstance(message, basestring):
            logging.error('Ignoring SlackBot message, not a string, is %s' % type(message))
            return False

        if is_testenv():
            logging.debug('SlackBot ignored in testenv %s' % message)
            return True  # Don't bother slack with our local dev.

        logging.debug('SlackBot says %s' % message)

        payload = {
            "text": message,
            "username": self.username,
            "channel": self.channel}

        json_payload = json.dumps(payload)
        response = urlfetch.fetch(
            self.webhook_url,
            method=urlfetch.POST,
            payload=json_payload,
            headers={"Content-Type": "application/json"})

        if response.status_code == 200:
            return True
        else:
            logging.error('SlackBot error. Status code %s. Body %s', response.status_code, response.content)
            return False
