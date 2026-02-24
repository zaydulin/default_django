from django import template
from django.db.models import Count
from django.middleware.csrf import get_token

from webmain.forms import SubscriptionForm
from webmain.models import SettingsGlobale

register = template.Library()


@register.simple_tag
def get_settings_first():
    return SettingsGlobale.objects.first()




@register.simple_tag(takes_context=True)
def render_subscription_form(context):
    request = context['request']
    form = SubscriptionForm()
    csrf_token = get_token(request)

    return {
        'form': form,
        'csrf_token': csrf_token
    }