from django.shortcuts import render
from apps.useraccount.views import CustomHtmxMixin
from django.views import View


# Create your views here.

class GallerysModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/gallerys/gallerys.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)