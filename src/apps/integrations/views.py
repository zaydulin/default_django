from django.shortcuts import render
from apps.useraccount.views import CustomHtmxMixin
from django.views import View


# Create your views here.

class SocialModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/integrations/social.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)

class TelephonyModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/integrations/telephony.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)

class PaymentModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/integrations/payments.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)

class DopServiseModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/integrations/dopservice.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)

class NeiroModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/integrations/neiro.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)