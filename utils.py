#!/usr/bin/env python

"""

This file contains utility routines. cribbed from lots of places, including Django, Mozilla etc...

If you're looking for more utility goodness, also check: https://github.com/dgilland/pydash

"""

from os import urandom
from os import environ
from os import getenv
from binascii import hexlify
from base64 import b64decode, b64encode

import six

import json

import ast
import time
import re
import unicodedata
# import logging


def is_testenv():
    """
    True if devserver, False if appengine server

    Appengine uses 'Google App Engine/<version>',
    Devserver uses 'Development/<version>'
    """
    return environ.get('SERVER_SOFTWARE', '').startswith('Development')


def decode(var):
    """Safely decode form input"""

    if not var:
        return var
    return unicode(var, 'utf-8') if isinstance(var, str) else unicode(var)


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-ascii characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """
    _slugify_strip_re = re.compile(r'[^\w\s-]')
    _slugify_hyphenate_re = re.compile(r'[-\s]+')

    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)


def msec_time():
    """Return current epoch time in milliseconds. """
    return int(time.time() * 1000.0)  # floor


def merge_dicts(a, b):
    """Merge b into a recursively, without overwriting values. """

    for k, v in b.items():
        if isinstance(v, dict):
            merge_dicts(a.setdefault(k, {}), v)
        else:
            a.setdefault(k, v)


def random_bytes_hex(bytes_length):
    """Return a hexstring of bytes_length cryptographic-friendly random bytes."""

    return hexlify(urandom(bytes_length)).decode('utf-8')


def native_value(value):
    """Convert string value to native python values. """

    if isinstance(value, six.string_types):
        if value.lower() in ['on', 'true', 'yes']:
            value = True
        elif value.lower() in ['off', 'false', 'no']:
            value = False
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            pass
    return value


def read_env(key, value):
    """Read the setting key from environment variables."""

    envkey = key.replace('.', '_').replace('-', '_').upper()
    return native_value(getenv(envkey, value))


def encode64(content, encoding='utf-8'):
    """Encode some content in base64."""

    return b64encode(content.encode(encoding)).decode(encoding)


def decode64(encoded_content, encoding='utf-8'):
    """Decode some base64 encoded content."""

    return b64decode(encoded_content.encode(encoding)).decode(encoding)


def extract_json_data(request):
    if request.body:
        try:
            body = json.loads(request.body)
            if isinstance(body, dict):
                return body
            request.errors.add(
                'body', None,
                "Invalid JSON: Should be a JSON object, got %s" % body
            )
            return {}
        except ValueError as e:
            request.errors.add(
                'body', None,
                "Invalid JSON request body: %s" % e)
            return {}
    else:
        return {}


class AppError(Exception):
    """ custom exception

    TODO: move this to exceptions.py or something like that.

    """
    pass


class RateLimitedError(Exception):
    """ rate limited by some external service"""
    pass
