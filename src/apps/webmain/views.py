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

class CustomHtmxSiteMixin:
    def get_template_names(self):
        is_htmx = bool(self.request.META.get('HTTP_HX_REQUEST'))
        if is_htmx:
            return [self.template_name]
        else:
            return ['active/include_block.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template_htmx'] = self.template_name

        # Получаем SEO данные из View и передаем их для блоков
        seo_context = self.get_seo_context()
        context.update(seo_context)

        return context

    def get_seo_context(self):
        """
        Переопределите этот метод в дочерних классах
        чтобы вернуть SEO данные для этой страницы
        """
        return {
            'block_title': 'Заголовок по умолчанию',
            'block_description': 'Описание по умолчанию',
            'block_propertytitle': 'Property Title по умолчанию',
            'block_propertydescription': 'Property Description по умолчанию',
            'block_propertyimage': '',
            'block_head': ''
        }

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