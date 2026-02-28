from django.shortcuts import render
from apps.useraccount.views import CustomHtmxMixin
from django.views import View


# Create your views here.

class DashboardModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/dashboard.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)

class GroupsModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/groups.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)

class AppealsModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/appeals.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)
