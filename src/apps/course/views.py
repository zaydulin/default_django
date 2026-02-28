from django.shortcuts import render
from apps.useraccount.views import CustomHtmxMixin
from django.views import View

# Create your views here.

class DashboardModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/courses/dashboard.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)


class MyCoursesView(CustomHtmxMixin, View):
    template_name = 'moderation/courses/my_courses.html'

    def get(self, request, *args, **kwargs):
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)


class CompletedCoursesView(CustomHtmxMixin, View):
    template_name = 'moderation/courses/completed_courses.html'

    def get(self, request, *args, **kwargs):
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)


class CertificatesView(CustomHtmxMixin, View):
    template_name = 'moderation/courses/certificates.html'

    def get(self, request, *args, **kwargs):
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)


class CreatedCoursesView(CustomHtmxMixin, View):
    template_name = 'moderation/courses/created_courses.html'

    def get(self, request, *args, **kwargs):
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)