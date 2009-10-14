#!/usr/bin/env python

import sys
import os
import traceback

from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command
from django.core.signals import got_request_exception

sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'webchat.settings'



call_command('syncdb')
application = WSGIHandler()

if __name__ == '__main__':
    from eventlet import api, wsgi
    
    def exception_printer(sender, **kwargs):
        traceback.print_exc()

    got_request_exception.connect(exception_printer)
    
    print 'Serving on 8080...'
    wsgi.server(api.tcp_listener(('', 8080)), application)
