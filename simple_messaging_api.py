# pylint: disable=line-too-long, no-member

import importlib
import json

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from simple_messaging.models import IncomingMessage, IncomingMessageMedia

def process_outgoing_message(outgoing_message, metadata=None): # pylint: disable=unused-argument
    return {
        'loopback': 'Sent at %s via loopback.' % timezone.now().isoformat()
    }

def simple_messaging_media_enabled(outgoing_message): # pylint: disable=unused-argument
    try:
        return settings.SIMPLE_MESSAGING_MEDIA_ENABLED
    except AttributeError:
        pass

    return True

def process_incoming_request(request): # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    if request.POST.get('LoopbackMessage', None) is None:
        return None

    response = {}

    responses = []

    for app in settings.INSTALLED_APPS:
        try:
            response_module = importlib.import_module('.simple_messaging_api', package=app)

            responses.extend(response_module.simple_messaging_response(request.POST))
        except ImportError:
            pass
        except AttributeError:
            pass

    response['responses'] =  responses

    if request.method == 'POST': # pylint: disable=too-many-nested-blocks
        record_responses = True

        for app in settings.INSTALLED_APPS:
            try:
                response_module = importlib.import_module('.simple_messaging_api', package=app)

                record_responses = response_module.simple_messaging_record_response(request.POST)
            except ImportError:
                pass
            except AttributeError:
                pass

        if record_responses:
            now = timezone.now()

            destination = request.POST.get('To', '')
            sender = request.POST.get('From', '')

            incoming = IncomingMessage(recipient=destination, sender=sender)
            incoming.receive_date = now
            incoming.message = request.POST.get('LoopbackMessage', '').strip()
            incoming.transmission_metadata = json.dumps(dict(request.POST), indent=2)

            incoming.save()

            incoming.encrypt_sender()

            index_counter = 0

            for key in request.FILES.keys():
                incoming_media = request.FILES[key]

                media = IncomingMessageMedia(message=incoming)

                media.content_url = 'loopback://%s' % incoming_media.name
                media.content_type = incoming_media.content_type
                media.index = index_counter

                media.content_file.save(incoming_media.name, incoming_media)

                media.save()

                index_counter += 1

            for app in settings.INSTALLED_APPS:
                try:
                    response_module = importlib.import_module('.simple_messaging_api', package=app)

                    response_module.process_incoming_message(incoming)
                except ImportError:
                    pass
                except AttributeError:
                    pass

    return HttpResponse(json.dumps(response, indent=2), content_type='application/json')

def simple_messaging_custom_console_ui(context): # pylint: disable=invalid-name
    return render_to_string("simple_messaging/console_loopback.html", context)
