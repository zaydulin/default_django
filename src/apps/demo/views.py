from django.shortcuts import render
from apps.useraccount.views import CustomHtmxMixin
from django.views import View


# Create your views here.
class DemoView(CustomHtmxMixin, View):
    template_name = 'moderation/demo/demo.html'

    def get(self, request, *args, **kwargs):
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)

