import uuid
import simplejson

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse
from webchat import settings

from eventlet.coros import event

# some global vars. 
# they won't hurt since this example is all single threaded 
CACHE_SIZE = 200
cache = []
new_message_event = event()


# req handlers
def main(request):
    if cache:
        request.session['cursor'] = cache[-1]['id']
    return render_to_response('index.html', 
        {'MEDIA_URL': settings.MEDIA_URL, 'messages': cache})

def message_new(request):
    name = request.META.get('REMOTE_ADDR') or 'Anonymous'
    msg = _create_message(name, request.POST['body'])
    global cache
    cache.append(msg)
    if len(cache) > CACHE_SIZE:
        cache = cache[-CACHE_SIZE:]
    new_message_event.send()
    new_message_event.reset()
    return _json_response(msg)

def message_updates(request):
    cursor = request.session.get('cursor')
    if not cache or cursor == cache[-1]['id']:
        new_message_event.wait()
    assert cursor != cache[-1]['id'], cursor
    try:
        for index, m in enumerate(cache):
            if m['id'] == cursor:
                return _json_response({'messages': cache[index+1:]})
        return _json_response({'messages': cache})
    finally:
        if cache:
            request.session['cursor'] = cache[-1]['id']
        else:
            request.session.pop('cursor', None)


# some helpers
def _create_message(from_, body):
    data = {'id': str(uuid.uuid4()), 'from': from_, 'body': body}
    data['html'] = render_to_string('message.html', 
        dictionary={'message': data})
    return data

def _json_response(value, **kwargs):
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    return HttpResponse(simplejson.dumps(value), **kwargs)

	
