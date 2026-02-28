from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.list import MultipleObjectMixin
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse

from moderation.models import Collaborations
from webmain.forms import SubscriptionForm
from webmain.models import SettingsGlobale, Seo
from django.http import Http404
import logging
from apps.useraccount.views import CustomHtmxMixin
from django.views import View


logger = logging.getLogger(__name__)


"""Подписка"""
def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Спасибо за подписку!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, f'Вы уже подписаны на рассылку!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class SettingsModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/site/settings.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)

class SettingsTemplatesModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/site/settings_templates.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)

class SettingsSmtpModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/site/settings_smtp.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)

class PagesModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/site/pages.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)