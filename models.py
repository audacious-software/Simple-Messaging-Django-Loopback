# pylint: disable=line-too-long, no-member

from django.db.utils import ProgrammingError

from django.conf import settings
from django.core.checks import Warning, register # pylint: disable=redefined-builtin

@register()
def check_loopback(app_configs, **kwargs): # pylint: disable=unused-argument
    errors = []

    if 'simple_messaging_loopback' in settings.INSTALLED_APPS:
        from simple_messaging_switchboard.models import Channel, ChannelType # pylint: disable=import-outside-toplevel, import-error

        try:
            loopback_type = ChannelType.objects.filter(package_name='simple_messaging_loopback').first()

            if loopback_type is None:
                error = Warning('simple_messaging_loopback installed, but no corresponding Channel Type.', hint='Add Channel Type with the "simple_messaging_loopback" package type.', obj=None, id='simple_messaging_lopback.W001')
                errors.append(error)
            else:
                loopback_channel = Channel.objects.filter(channel_type=loopback_type).first()

                if loopback_channel is None:
                    error = Warning('simple_messaging_loopback installed, but no corresponding Channel.', hint='Add Channel the "simple_messaging_loopback" channel type. Disable if needed.', obj=None, id='simple_messaging_lopback.W001')
                    errors.append(error)
        except ProgrammingError:
            pass # Migrations not applied

    return errors
