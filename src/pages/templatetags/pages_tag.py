from django import template
from django.db.models import Count
from django.middleware.csrf import get_token

from pages.models import Pages

register = template.Library()


@register.simple_tag
def get_pages():
    return Pages.objects.all().filter(publishet=True)

