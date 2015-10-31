# -*- coding: utf-8 -*-
#
# See LICENSE file
#

__author__ = 'pystart-gae'

import logging

from google.appengine.api import mail


def send_email(to_addr, subject, msg, reply_to=None):
    """ routine to send email messages, uses AppEngine email

    use only for reports, ordinary notifications should go to Slack

    """

    message = mail.EmailMessage()
    message.sender = 'pystart.gae@gmail.com'  # TODO - your email here.
    # message.cc = settings.CC  # TODO: dont need to CC for now
    message.to = to_addr
    message.body = msg
    message.subject = '[pystart] %s' % subject

    if not mail.is_email_valid(to_addr):
        logging.error('invalid email to address %s' % to_addr)
        return False

    logging.info('Sending email to %s' % to_addr)

    message.send()
