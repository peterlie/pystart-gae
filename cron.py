#!/usr/bin/env python
#
# See LICENSE file
#

__author__ = 'pystart-gae'

"""

This module contains the cron handler.


"""

import logging
logging.getLogger().setLevel(logging.DEBUG)

from base_handler import BaseRequestHandler
# import datetime

# from google.appengine.ext import deferred


class CronHandler(BaseRequestHandler):
    """ implements cron-based jobs"""

    def get(self, job):
        """ /cron/<job> """

        legal_jobs = [
            'report',
            'test',
            'worker',
            'purger',
            'robot'
        ]

        # verify request really came from app engine cron
        if not self.request.headers.get('X-Appengine-Cron'):
            logging.warning('Cron but not from appengine, ignoring')
            return self.abort('403')

        if job not in legal_jobs:
            logging.error('CronHandler just cannot %s' % job)
            return self.abort('400')
        else:
            logging.debug('CronHandler: %s' % job)

        if job == 'report':
            # maybe email a report?

            logging.warning('CronHandler report not implemented.')
            return

        elif job == 'test':
            # just say hi

            logging.info('CronHandler test says Hi..')
            return

        elif job == 'worker':
            """  do some works """

            # deferred.defer(the_worker, curs=None, sample_count=100, _queue="worker")

            return

        elif job == 'purger':
            """ purge old data from datastore """

            logging.warning('CronHandler purger not implemented.')
            return

        elif job == 'robot':
            """ collect 100 (on average) samples

            """

            logging.warning('CronHandler robot not implemented.')
            return

        else:
            # can't imagine why we're here.
            logging.error('CronHandler unknown job: %s' % job)
            return self.abort('400')
