#
# django template tag to display a unix timestamp as a human readable time.
# on appengine:
# ...add the following line to base request handler init, assuming name of this file is unixtime.py in templatetags directory:
# template.register_template_library('templatetags.unixtime')
#

from google.appengine.ext import webapp
import datetime

register = webapp.template.create_template_register()

@register.filter('unixtime')
def convert_timestamp_to_time(timestamp):
    try:
        result = datetime.datetime.fromtimestamp(float(timestamp))
    except Exception:
        return timestamp
    return result
