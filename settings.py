#!/usr/bin/env python

ADMIN = 'pystart-gae@gmail.com'

VERSION = '0.0.0'

APP_SESSION_NAME = 'pystart-gae-session'
SESSIONS_KEY = 'pick-a-random-string'

# slack bot
SLACK_API_TOKEN = 'api-token-here'
SLACK_WEBHOOK_URL = 'webhook-url-here'
SLACK_OPS_TOKEN = 'ops-token-here'

# constants to make memcache calls easier to read
TEN_SECONDS = 10
ONE_MINUTE = TEN_SECONDS * 6
FIVE_MINUTES = ONE_MINUTE * 5
TEN_MINUTES = ONE_MINUTE * 10
FIFTEEN_MINUTES = ONE_MINUTE * 15
THIRTY_MINUTES = ONE_MINUTE * 30
ONE_HOUR = ONE_MINUTE * 60
FOUR_HOURS = ONE_HOUR * 4
SIX_HOURS = ONE_HOUR * 6
EIGHT_HOURS = ONE_HOUR * 8
