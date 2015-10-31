#!/usr/bin/env python

# See LICENSE file

"""

This file is part of pystart-gae contains and application data models.

"""

import logging
import datetime

from google.appengine.ext import ndb
from google.appengine.ext import deferred

from slack_bot import botMsg

FEW = 10
MANY = 100
TWO_MANY = 200
UPPER_LIMIT = 1000


class AppData(ndb.Model):
    """ application data
    """

    data = ndb.StringProperty(indexed=False)
    added = ndb.DateTimeProperty(indexed=True, auto_now_add=True)

    @classmethod
    def write(cls, data):
        """ write AppData entity with data """

        logging.debug('Writing app data: %s' % data)

        try:
            AppData(
                data=data
            ).put()
        except Exception as e:
            logging.error('%s writing app data' % e)
            return False

        return True

    @classmethod
    def get_some(cls, curs=None):
        """ get log entries with a cursor """

        if curs:
            clogs, next_curs, more_clogs = cls.query().order(-cls.timestamp).fetch_page(MANY, start_cursor=curs)
        else:
            clogs, next_curs, more_clogs = cls.query().order(-cls.timestamp).fetch_page(MANY)

        return clogs, next_curs, more_clogs

    @classmethod
    def purge_some(cls, count=MANY):
        """ routine to purge some old app data from datastore
        """

        if count > UPPER_LIMIT:
            count = UPPER_LIMIT
        if count <= 0:
            logging.warning('Invalid value %d in AppData.purge_some()' % count)
            return False

        ad_keys = None
        try:
            ad_keys = cls.query().order(cls.added).fetch(count, keys_only=True)
        except Exception, e:
            logging.error('%s getting old app data for purge_some' % e)
            return False

        try:
            logging.warning('Purging %d old app data entities' % count)
            ndb.delete_multi(ad_keys)
        except Exception as e:
            logging.error('%s in delete_multi in AppData.purge_some()' % e)
            return False

        return True

    @classmethod
    def purge(cls, before=None):
        """ purge old before a time
            if before is provided, purge logs older than that date, else keep around about a month's worth.
        """

        THIRTY_DAYS = 30

        if before:
            before_date = before
        else:
            before_date = datetime.datetime.utcnow() - datetime.timedelta(days=THIRTY_DAYS)

        logging.info('purging app data before %s' % before_date)

        deferred.defer(cls._purge, before=before_date, _queue="purger")
        return

    @classmethod
    def _purge(cls, before):
        """ purge old AppData from App Engine datastore.
            this runs deferred

        """

        ad_keys, next_curs, more = cls.query(cls.added <= before).fetch_page(TWO_MANY, keys_only=True)
        if ad_keys:
            logging.info('purger purging %d old app data before %s' % (len(ad_keys), before))
            try:
                ndb.delete_multi(ad_keys)
            except Exception as e:
                logging.error('purger error %s purging old app data' % e)
        else:
            logging.debug('purger - no app data to purge prior to %s' % before)

        if more:
            botMsg('app data purger has more to do after purging %d entries...' % len(ad_keys))
            # don't really need to use cursor if we're deleting before a data. unless saves query processing? don't know
            deferred.defer(cls._purge, before=before, _queue="purger")
        return
