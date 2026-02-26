from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import HttpResponseServerError, HttpResponseForbidden, JsonResponse
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
import json
from django.shortcuts import render, get_object_or_404
from django.db import transaction
import base64
from django.core.files.base import ContentFile
from django.db.models import Count
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
import time


# Models
from webmain.models import Seo
from ticket.models import Ticket, TicketComment, TicketCommentMedia
from useraccount.models import Profile

# Forms
from useraccount.forms import SignUpForm, UserProfileForm, PasswordResetEmailForm, SetPasswordFormCustom
from ticket.forms import TicketCommentForm,   TicketWithCommentForm

User = get_user_model()


class CustomHtmxMixin:
    def get_template_names(self):
        is_htmx = bool(self.request.META.get('HTTP_HX_REQUEST'))
        if is_htmx:
            return [self.template_name]
        else:
            return ['moderation/include_block.html']

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

def custom_logout(request):
    logout(request)
    return redirect('useraccount:login')

"""Регистрация/Авторизация"""


class CustomLoginView(CustomHtmxMixin, TemplateView):
    template_name = "moderation/useraccount/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Параметры из базы данных для страницы "Авторизация" (pagetype=5)
        try:
            seo_data_from_db = Seo.objects.get(pagetype=5)

            # Передаем данные из модели в контекст
            context['seo_previev'] = seo_data_from_db.previev
            context['seo_title'] = seo_data_from_db.title
            context['seo_description'] = seo_data_from_db.metadescription
            context['seo_propertytitle'] = seo_data_from_db.propertytitle
            context['seo_propertydescription'] = seo_data_from_db.propertydescription
            context['seo_head'] = seo_data_from_db.setting  # Если нужно добавлять дополнительные теги
        except Seo.DoesNotExist:
            # Если данных нет, используем значения по умолчанию
            context['seo_previev'] = None
            context['seo_title'] = 'Вход в систему - МойСайт'
            context['seo_description'] = 'Войдите в свою учетную запись для доступа к персональным данным'
            context['seo_propertytitle'] = 'og:title - Вход в систему'
            context['seo_propertydescription'] = 'og:description - Страница входа в личный кабинет'
            context['seo_head'] = '''
                <link rel="stylesheet" href="/static/css/login.css">
                <meta name="robots" content="noindex">
            '''

        return context

    def get_seo_context(self):
        """
        Просто возвращаем SEO данные для блоков
        """
        try:
            seo_data = Seo.objects.get(pagetype=5)
            return {
                'block_title': seo_data.title,
                'block_description': seo_data.metadescription,
                'block_propertytitle': seo_data.propertytitle,
                'block_propertydescription': seo_data.propertydescription,
                'block_propertyimage': seo_data.previev.url if seo_data.previev else '',
                'block_head': seo_data.setting or ''
            }
        except Seo.DoesNotExist:
            return {
                'block_title': 'Вход в систему',
                'block_description': 'Страница входа в аккаунт',
                'block_propertytitle': 'Вход в систему',
                'block_propertydescription': 'Страница входа',
                'block_propertyimage': '',
                'block_head': '<meta name="robots" content="noindex">'
            }

    def get(self, request, *args, **kwargs):
        # Убедитесь, что вызываем родительский get, который использует миксин
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):  # Добавьте *args, **kwargs
        identifier = request.POST.get("username")
        password = request.POST.get("password")

        user = None

        # 1) Пробуем найти по username
        try:
            user_obj = User.objects.get(username=identifier)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

        # 2) Пробуем найти по email
        if user is None:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        # 3) Пробуем найти по телефону (если есть поле phone)
        if user is None:
            try:
                user_obj = User.objects.get(phone=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            if request.headers.get("Hx-Request") == "true":
                return render(request, "moderation/useraccount/partials/login_success.html")
            return redirect("home")
        else:
            # Для HTMX запросов возвращаем частичный шаблон
            if request.headers.get("Hx-Request") == "true":
                return render(request, "moderation/useraccount/partials/login_error.html", {
                    "error": "Неверные данные для входа"
                })
            else:
                # Для обычных запросов показываем форму с ошибкой
                context = self.get_context_data()
                context['error'] = "Неверные данные для входа"
                return self.render_to_response(context)



class CheckUsernameView(View):
    def post(self, request):
        username = request.POST.get("username")
        exists = User.objects.filter(username=username).exists()
        return render(request, "moderation/useraccount/partials/register_username_check.html", {"exists": exists})


class CheckEmailView(View):
    def post(self, request):
        email = request.POST.get("email")
        exists = User.objects.filter(email=email).exists()
        return render(request, "moderation/useraccount/partials/register_email_check.html", {"exists": exists})


class CheckPhoneView(View):
    def post(self, request):
        phone = request.POST.get("phone")
        exists = User.objects.filter(phone=phone).exists()
        return render(request, "moderation/useraccount/partials/register_phone_check.html", {"exists": exists})

class RegisterView(CustomHtmxMixin, TemplateView):  # Используем TemplateView
    template_name = "moderation/useraccount/register.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_seo_context(self):
        """SEO данные для страницы регистрации"""
        try:
            seo_data = Seo.objects.get(pagetype=6)  # pagetype для регистрации
            return {
                'block_title': seo_data.title,
                'block_description': seo_data.metadescription,
                'block_propertytitle': seo_data.propertytitle,
                'block_propertydescription': seo_data.propertydescription,
                'block_propertyimage': seo_data.previev.url if seo_data.previev else '',
                'block_head': seo_data.setting or ''
            }
        except Seo.DoesNotExist:
            return {
                'block_title': 'Регистрация - МойСайт',
                'block_description': 'Создайте новый аккаунт на нашем сайте',
                'block_propertytitle': 'Регистрация',
                'block_propertydescription': 'Страница регистрации',
                'block_propertyimage': '',
                'block_head': '<meta name="robots" content="noindex">'
            }

    def post(self, request):
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Валидация
        if not all([username, email, phone, password1, password2]):
            return render(request, "partials/register_error.html", {"code": "empty_fields"})

        if password1 != password2:
            return render(request, "partials/register_error.html", {"code": "password_mismatch"})

        if User.objects.filter(username=username).exists():
            return render(request, "partials/register_error.html", {"code": "username_exists"})

        if User.objects.filter(email=email).exists():
            return render(request, "partials/register_error.html", {"code": "email_exists"})

        if User.objects.filter(phone=phone).exists():
            return render(request, "partials/register_error.html", {"code": "phone_exists"})

        # Создание пользователя
        user = User.objects.create_user(
            username=username,
            email=email,
            phone=phone,
            password=password1,
        )
        login(request, user)

        if request.headers.get("Hx-Request") == "true":
            return render(request, "partials/register_success.html")

        return redirect("home")

class CustomPasswordResetView(PasswordResetView):
    template_name = 'site/useraccount/restore_access.html'
    email_template_name = 'site/email/password_reset_email.html'
    subject_template_name = 'site/email/password_reset_subject.txt'
    form_class = PasswordResetEmailForm
    success_url = reverse_lazy('useraccount:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'site/useraccount/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'site/useraccount/restore_access_user.html'
    form_class = SetPasswordFormCustom
    success_url = reverse_lazy('useraccount:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'site/useraccount/password_reset_complete.html'


@method_decorator(login_required(login_url='useraccount:login'), name='dispatch')
class EditMyProfileView(TemplateView, LoginRequiredMixin):
    template_name = 'moderation/useraccount/profile_edit.html'

    def get(self, request, *args, **kwargs):
        initial_data = {'birthday': request.user.birthday.strftime('%Y-%m-%d') if request.user.birthday else None}
        form = UserProfileForm(instance=request.user, initial=initial_data)
        password_form = PasswordChangeForm(user=request.user)  # Форма для смены пароля

        context = self.get_context_data(form=form, password_form=password_form, title='Личные данные')
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        password_form = PasswordChangeForm(data=request.POST, user=request.user)  # Форма для смены пароля

        # Обработка данных профиля
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлен успешно.")
        else:
            messages.error(request, "Ошибка при обновлении профиля.")
            print("Form errors:", form.errors)

        # Обработка смены пароля
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Чтобы пользователь не вышел после смены пароля
            messages.success(request, "Пароль изменен успешно.")
        else:
            messages.error(request, "Ошибка при смене пароля.")
            print("Password form errors:", password_form.errors)

        context = self.get_context_data(form=form, password_form=password_form, title='Личные данные')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Вызов `super()` сохраняет функциональность
        try:
            seo_data = Seo.objects.get(pagetype=8)
            context['seo_previev'] = seo_data.previev
            context['seo_title'] = seo_data.title
            context['seo_description'] = seo_data.metadescription
            context['seo_propertytitle'] = seo_data.propertytitle
            context['seo_propertydescription'] = seo_data.propertydescription
        except Seo.DoesNotExist:
            context['seo_previev'] = None
            context['seo_title'] = None
            context['seo_description'] = None
            context['seo_propertytitle'] = None
            context['seo_propertydescription'] = None
        return context
