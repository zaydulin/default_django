from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
from django.http import HttpResponse

from .models import Message, MessageDir, MessageMask,StopList, MessageFile, MessageRm, UserSettingsSMTP, MassMailCampaign, MassMailLog, MessageTemplates
from django.contrib.auth.models import User
from django.contrib import messages
import smtplib
import ssl
from useraccount.views import CustomHtmxMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from django.contrib.auth import get_user_model

User = get_user_model()  # Получаем кастомную модель пользователя

# moderation/mail/stoplist.html


class StopListView(View):
    """
    Стоп-лист для блокировки нежелательных писем
    """

    def get(self, request):
        # Получаем или создаём единственную запись
        stoplist, created = StopList.objects.get_or_create(
            id=1,
            defaults={'list': 'mail@na.ru, mail2@na.ru'}
        )

        # Получаем список email-адресов
        emails = stoplist.get_emails_list()

        # Разбиваем на три колонки
        total = len(emails)
        chunk_size = (total + 2) // 3  # Округление вверх

        columns = [
            emails[i:i + chunk_size]
            for i in range(0, total, chunk_size)
        ]

        # Дополняем до трёх колонок пустыми списками
        while len(columns) < 3:
            columns.append([])

        context = {
            'stoplist': stoplist,
            'created': created,
            'columns': columns,
            'total_count': total,
        }

        return render(request, 'moderation/mail/stoplist.html', context)

    def post(self, request):
        stoplist, created = StopList.objects.get_or_create(id=1)
        action = request.POST.get('action', '')

        if action == 'add_single':
            # Добавление одного email
            email = request.POST.get('email', '').strip()
            if email:
                if stoplist.add_email(email):
                    messages.success(request, f'✅ Email "{email}" добавлен в стоп-лист!')
                else:
                    messages.warning(request, f'⚠️ Email "{email}" уже есть в стоп-листе!')
            else:
                messages.error(request, '❌ Введите email адрес!')

        elif action == 'add_bulk':
            # Массовое добавление
            bulk_emails = request.POST.get('bulk_emails', '').strip()
            if bulk_emails:
                # Поддерживаем разделение по запятым, пробелам и переводам строк
                import re
                # Разделяем по запятым, пробелам, переводам строк
                emails_list = re.split(r'[,\n\s]+', bulk_emails)
                # Фильтруем пустые и валидные email
                valid_emails = [e for e in emails_list if e and '@' in e]

                if valid_emails:
                    new_emails = stoplist.add_emails_bulk(valid_emails)
                    if new_emails:
                        messages.success(
                            request,
                            f'✅ Добавлено {len(new_emails)} новых email-адресов!'
                        )
                    else:
                        messages.warning(request, '⚠️ Все email-адреса уже есть в стоп-листе!')
                else:
                    messages.error(request, '❌ Не найдено валидных email-адресов!')
            else:
                messages.error(request, '❌ Введите email-адреса для добавления!')

        elif action == 'remove':
            # Удаление email
            email = request.POST.get('email', '').strip()
            if email and stoplist.remove_email(email):
                messages.success(request, f'✅ Email "{email}" удалён из стоп-листа!')
            else:
                messages.error(request, f'❌ Email "{email}" не найден в стоп-листе!')

        return redirect('mail:stoplist')


class StopListAPIView(View):
    """API для работы со стоп-листом"""

    def get(self, request):
        """Получить все email"""
        stoplist, _ = StopList.objects.get_or_create(id=1)
        emails = stoplist.get_emails_list()
        return JsonResponse({'emails': emails, 'count': len(emails)})

    def post(self, request):
        """Добавить email через API"""
        import json
        data = json.loads(request.body)
        stoplist, _ = StopList.objects.get_or_create(id=1)

        if 'email' in data:
            success = stoplist.add_email(data['email'])
            return JsonResponse({'success': success, 'email': data['email']})

        if 'emails' in data:
            new_emails = stoplist.add_emails_bulk(data['emails'])
            return JsonResponse({'success': True, 'added': new_emails, 'count': len(new_emails)})

        return JsonResponse({'error': 'No email provided'}, status=400)

    def delete(self, request):
        """Удалить email через API"""
        import json
        data = json.loads(request.body)
        stoplist, _ = StopList.objects.get_or_create(id=1)

        if 'email' in data:
            success = stoplist.remove_email(data['email'])
            return JsonResponse({'success': success, 'email': data['email']})

        return JsonResponse({'error': 'No email provided'}, status=400)


class MessageTemplateListView(ListView):
    """Список всех шаблонов"""
    model = MessageTemplates
    template_name = 'moderation/mail/template_list.html'
    context_object_name = 'templates'
    ordering = ['-created_at']
    paginate_by = 10


class MessageTemplateDetailView(DetailView):
    """Детальный просмотр шаблона"""
    model = MessageTemplates
    template_name = 'moderation/mail/template_detail.html'
    context_object_name = 'template'


class MessageTemplateCreateView(SuccessMessageMixin, CreateView):
    """Создание нового шаблона"""
    model = MessageTemplates
    template_name = 'moderation/mail/template_create.html'
    fields = ['mask', 'name']  # Указываем поля, которые будут в форме
    success_url = reverse_lazy('mail:message_templates_list')
    success_message = "Шаблон успешно создан!"


class MessageTemplateUpdateView(SuccessMessageMixin, UpdateView):
    """Редактирование шаблона"""
    model = MessageTemplates
    template_name = 'moderation/mail/template_update.html'
    fields = ['mask', 'name']  # Указываем поля, которые будут в форме
    success_url = reverse_lazy('mail:message_templates_list')
    success_message = "Шаблон успешно обновлен!"


class MessageTemplateDeleteView(SuccessMessageMixin, DeleteView):
    """Удаление шаблона"""
    model = MessageTemplates
    template_name = 'moderation/mail/template_delete.html'
    success_url = reverse_lazy('mail:message_templates_list')
    success_message = "Шаблон успешно удален!"


class MassMailCampaignListView(LoginRequiredMixin, View):
    """Список кампаний массовой рассылки"""
    template_name = 'moderation/mail/mass_mail_list.html'

    def get(self, request):
        campaigns = MassMailCampaign.objects.filter(user=request.user).order_by('-created_at')

        # Статистика
        total_campaigns = campaigns.count()
        draft_campaigns = campaigns.filter(status='draft').count()
        sent_campaigns = campaigns.filter(status='sent').count()
        scheduled_campaigns = campaigns.filter(status='scheduled').count()

        # Пагинация
        from django.core.paginator import Paginator
        paginator = Paginator(campaigns, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'campaigns': page_obj,
            'total_campaigns': total_campaigns,
            'draft_campaigns': draft_campaigns,
            'sent_campaigns': sent_campaigns,
            'scheduled_campaigns': scheduled_campaigns,
        }
        return render(request, self.template_name, context)


class MassMailCampaignCreateView(LoginRequiredMixin, View):
    """Создание новой кампании массовой рассылки"""
    template_name = 'moderation/mail/mass_mail_form.html'

    def get(self, request):
        smtp_settings = UserSettingsSMTP.objects.filter(user=request.user)
        messagetemplates = MessageTemplates.objects.all().order_by('-created_at')

        # Получаем глобальный стоп-лист
        global_stoplist = StopList.get_instance()
        stoplist_emails = global_stoplist.get_emails_list()

        context = {
            'smtp_settings': smtp_settings,
            'messagetemplates': messagetemplates,
            'is_edit': False,
            'global_stoplist': global_stoplist,
            'stoplist_emails': stoplist_emails,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        try:
            # Получаем данные из формы
            name = request.POST.get('name')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            recipient_emails = request.POST.get('recipient_emails', '')
            from_email = request.POST.get('from_email')
            from_name = request.POST.get('from_name')
            scheduled_time = request.POST.get('scheduled_time')
            use_smtp_id = request.POST.get('use_smtp')
            stop_list = request.POST.get('stop_list', '')

            # Получаем настройки отправки
            message_count = request.POST.get('message_count', 50)
            message_interval = request.POST.get('message_interval', 2)

            # Валидация
            try:
                message_count = int(message_count)
                message_interval = int(float(message_interval))
            except (ValueError, TypeError):
                message_count = 50
                message_interval = 2

            message_count = max(1, min(1000, message_count))
            message_interval = max(0, min(60, message_interval))

            # Получаем SMTP настройки
            use_smtp = None
            if use_smtp_id:
                try:
                    use_smtp = UserSettingsSMTP.objects.get(id=use_smtp_id, user=request.user)
                except UserSettingsSMTP.DoesNotExist:
                    pass

            # Создаем кампанию
            campaign = MassMailCampaign.objects.create(
                name=name,
                subject=subject,
                message=message,
                recipient_emails=recipient_emails,
                from_email=from_email,
                from_name=from_name,
                use_smtp_settings=use_smtp,
                user=request.user,
                status='draft',
                message_count=message_count,
                message_interval=message_interval,
                stop_list=stop_list
            )

            # Обработка файла
            if 'recipient_file' in request.FILES:
                campaign.recipient_file = request.FILES['recipient_file']
                campaign.save()

                file_content = campaign.recipient_file.read().decode('utf-8')
                file_emails = []
                for line in file_content.split('\n'):
                    for email in line.split(','):
                        email = email.strip()
                        if email and '@' in email:
                            file_emails.append(email)

                if campaign.recipient_emails:
                    campaign.recipient_emails += '\n' + '\n'.join(file_emails)
                else:
                    campaign.recipient_emails = '\n'.join(file_emails)
                campaign.save()

            campaign.total_recipients = len(campaign.get_recipients_list())
            campaign.save()

            if scheduled_time:
                from datetime import datetime
                campaign.scheduled_time = datetime.fromisoformat(scheduled_time)
                campaign.status = 'scheduled'
                campaign.save()

            messages.success(request, f'Кампания "{name}" успешно создана')
            return redirect('mail:mass_mail_list')

        except Exception as e:
            messages.error(request, f'Ошибка при создании: {str(e)}')
            return redirect('mail:mass_mail_create')


class MassMailCampaignEditView(LoginRequiredMixin, View):
    """Редактирование кампании массовой рассылки"""
    template_name = 'moderation/mail/mass_mail_form.html'

    def get(self, request, campaign_id):
        campaign = get_object_or_404(MassMailCampaign, id=campaign_id, user=request.user)
        smtp_settings = UserSettingsSMTP.objects.filter(user=request.user)
        messagetemplates = MessageTemplates.objects.all().order_by('-created_at')

        # Получаем глобальный стоп-лист
        global_stoplist = StopList.get_instance()
        stoplist_emails = global_stoplist.get_emails_list()

        context = {
            'campaign': campaign,
            'smtp_settings': smtp_settings,
            'messagetemplates': messagetemplates,
            'is_edit': True,
            'global_stoplist': global_stoplist,
            'stoplist_emails': stoplist_emails,
        }
        return render(request, self.template_name, context)

    def post(self, request, campaign_id):
        campaign = get_object_or_404(MassMailCampaign, id=campaign_id, user=request.user)

        try:
            # Обновляем данные
            campaign.name = request.POST.get('name')
            campaign.subject = request.POST.get('subject')
            campaign.message = request.POST.get('message')
            campaign.recipient_emails = request.POST.get('recipient_emails', '')
            campaign.from_email = request.POST.get('from_email')
            campaign.from_name = request.POST.get('from_name')
            campaign.stop_list = request.POST.get('stop_list', '')

            # Настройки отправки
            message_count = request.POST.get('message_count', 50)
            message_interval = request.POST.get('message_interval', 2)

            try:
                campaign.message_count = int(message_count)
                campaign.message_interval = int(float(message_interval))
            except (ValueError, TypeError):
                campaign.message_count = 50
                campaign.message_interval = 2

            campaign.message_count = max(1, min(1000, campaign.message_count))
            campaign.message_interval = max(0, min(60, campaign.message_interval))

            # SMTP настройки
            use_smtp_id = request.POST.get('use_smtp')
            if use_smtp_id:
                try:
                    campaign.use_smtp_settings = UserSettingsSMTP.objects.get(
                        id=use_smtp_id, user=request.user
                    )
                except UserSettingsSMTP.DoesNotExist:
                    campaign.use_smtp_settings = None
            else:
                campaign.use_smtp_settings = None

            # Планирование
            scheduled_time = request.POST.get('scheduled_time')
            if scheduled_time:
                from datetime import datetime
                campaign.scheduled_time = datetime.fromisoformat(scheduled_time)
            else:
                campaign.scheduled_time = None

            # Обработка нового файла
            if 'recipient_file' in request.FILES:
                campaign.recipient_file = request.FILES['recipient_file']
                campaign.save()

                file_content = campaign.recipient_file.read().decode('utf-8')
                file_emails = []
                for line in file_content.split('\n'):
                    for email in line.split(','):
                        email = email.strip()
                        if email and '@' in email:
                            file_emails.append(email)

                if campaign.recipient_emails:
                    campaign.recipient_emails += '\n' + '\n'.join(file_emails)
                else:
                    campaign.recipient_emails = '\n'.join(file_emails)

            # Обновляем количество получателей
            campaign.total_recipients = len(campaign.get_recipients_list())
            campaign.save()

            messages.success(request, f'Кампания "{campaign.name}" успешно обновлена')
            return redirect('mail:mass_mail_list')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении: {str(e)}')
            return redirect('mail:mass_mail_edit', campaign_id=campaign.id)


class MassMailMoveToStopListView(LoginRequiredMixin, View):
    """
    Перемещает все загруженные email-адреса из текущей кампании в глобальный стоп-лист
    """

    def post(self, request, campaign_id):
        campaign = get_object_or_404(MassMailCampaign, id=campaign_id, user=request.user)

        # Получаем все email из получателей
        recipients = campaign.get_recipients_list()

        if not recipients:
            messages.warning(request, '⚠️ Нет email-адресов для перемещения в стоп-лист!')
            return redirect('mail:mass_mail_edit', campaign_id=campaign.id)

        # Перемещаем в стоп-лист
        result = campaign.move_emails_to_stoplist(recipients)

        if result['added_count'] > 0:
            messages.success(
                request,
                f'✅ Перемещено {result["added_count"]} email-адресов в глобальный стоп-лист!\n'
                f'Осталось получателей: {result["remaining_count"]}'
            )

            # Показываем первые 5 добавленных
            for email in result['added_emails'][:5]:
                messages.info(request, f'📧 Добавлен в стоп-лист: {email}')

            if result['added_count'] > 5:
                messages.info(request, f'... и ещё {result["added_count"] - 5} адресов')
        else:
            messages.info(request, 'ℹ️ Не удалось переместить адреса')

        return redirect('mail:mass_mail_edit', campaign_id=campaign.id)


class GetTemplateView(LoginRequiredMixin, View):
    """Получение шаблона по ID"""
    def get(self, request, template_id):
        try:
            template = MessageTemplates.objects.get(id=template_id)
            return JsonResponse({
                'success': True,
                'id': template.id,
                'name': template.name,
                'mask': template.mask,
                'created_at': template.created_at.strftime('%d.%m.%Y %H:%M:%S'),
                'updated_at': template.updated_at.strftime('%d.%m.%Y %H:%M:%S'),
            })
        except MessageTemplates.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Шаблон не найден'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class MassMailCampaignCancelView(LoginRequiredMixin, View):
    """Отмена массовой рассылки"""

    def post(self, request, campaign_id):
        campaign = get_object_or_404(MassMailCampaign, id=campaign_id, user=request.user)
        campaign.status = 'cancelled'
        campaign.save()
        messages.success(request, f'Рассылка "{campaign.name}" отменена')
        return redirect('mail:mass_mail_detail', campaign_id=campaign.id)

class MassMailCampaignDetailView(LoginRequiredMixin, View):
    """Детальный просмотр кампании массовой рассылки"""
    template_name = 'moderation/mail/mass_mail_detail.html'

    def get(self, request, campaign_id):
        campaign = get_object_or_404(MassMailCampaign, id=campaign_id, user=request.user)
        logs = campaign.logs.all().order_by('-created_at')[:50]

        context = {
            'campaign': campaign,
            'logs': logs,
        }
        return render(request, self.template_name, context)


class MassMailCampaignSendView(LoginRequiredMixin, View):
    """Запуск массовой рассылки"""

    def post(self, request, campaign_id):
        campaign = get_object_or_404(MassMailCampaign, id=campaign_id, user=request.user)

        try:
            # Здесь будет логика отправки
            # В реальном проекте это должно быть в Celery задаче

            campaign.status = 'sending'
            campaign.save()

            # Имитация отправки
            recipients = campaign.get_recipients_list()
            for email in recipients:
                # Создаем лог
                MassMailLog.objects.create(
                    campaign=campaign,
                    email=email,
                    status='pending'
                )

            messages.success(request, f'Рассылка "{campaign.name}" запущена')

        except Exception as e:
            messages.error(request, f'Ошибка при запуске: {str(e)}')

        return redirect('mail:mass_mail_detail', campaign_id=campaign.id)


class MassMailCampaignDeleteView(LoginRequiredMixin, View):
    """Удаление кампании массовой рассылки"""

    def post(self, request, campaign_id):
        campaign = get_object_or_404(MassMailCampaign, id=campaign_id, user=request.user)
        name = campaign.name
        campaign.delete()

        messages.success(request, f'Кампания "{name}" удалена')
        return redirect('mail:mass_mail_list')

class AllMessagesListView(LoginRequiredMixin, View):
    """Страница со списком всех сообщений всех пользователей (для администраторов)"""
    template_name = 'moderation/mail/all_messages_list.html'

    def get(self, request):
        # Проверяем права доступа (только для staff или суперпользователей)
        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, 'У вас нет доступа к этой странице')
            return redirect('mail:message_list')

        # Получаем параметр выбранного пользователя
        selected_user_id = request.GET.get('user_id')
        selected_user = None

        # Базовый запрос - все сообщения
        all_messages = Message.objects.all().select_related('user').prefetch_related(
            'dirs', 'masks', 'files', 'read_by'
        ).order_by('-created_at')

        # Фильтруем по пользователю, если выбран
        if selected_user_id:
            try:
                selected_user = User.objects.get(id=selected_user_id)
                all_messages = all_messages.filter(
                    Q(user=selected_user) | Q(clients__icontains=selected_user.email)
                ).distinct()
            except User.DoesNotExist:
                pass

        # Получаем всех пользователей для выпадающего списка (используем get_user_model)
        users = User.objects.filter(is_active=True).order_by('username')

        # Поиск
        search_query = request.GET.get('search', '')
        if search_query:
            all_messages = all_messages.filter(
                Q(message__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(clients__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )

        # Пагинация
        from django.core.paginator import Paginator
        paginator = Paginator(all_messages, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Статистика
        total_messages = Message.objects.count()
        total_users = User.objects.filter(is_active=True).count()

        context = {
            'messages': page_obj,
            'users': users,
            'selected_user_id': selected_user_id,
            'selected_user': selected_user,
            'search_query': search_query,
            'total_messages': total_messages,
            'total_users': total_users,
        }
        return render(request, self.template_name, context)


class AllMessageDetailView(LoginRequiredMixin, View):
    """Просмотр конкретного сообщения"""
    template_name = 'moderation/mail/all_message_detail.html'

    def get(self, request, message_id):
        user_email = request.user.email.lower()

        message = get_object_or_404(
            Message.objects.select_related('user', 'message_rm')
            .prefetch_related('files', 'dirs', 'masks', 'read_by'),
            Q(id=message_id) & (Q(user=request.user) | Q(clients__icontains=user_email))
        )

        # Определяем тип сообщения для отображения
        if message.user == request.user:
            if message.self_field:
                message.display_type = 'draft'
            else:
                message.display_type = 'outgoing'
        elif user_email in [email.lower() for email in message.get_clients_list()]:
            message.display_type = 'incoming'
        else:
            message.display_type = 'other'

        # Отмечаем сообщение как прочитанное (только для входящих)
        if message.display_type == 'incoming' and request.user not in message.read_by.all():
            message.read_by.add(request.user)

        # Получаем все email адреса, связанные с этим сообщением
        all_emails = set(message.get_related_emails())
        all_emails.add(user_email)

        # Создаем Q объект для поиска всех сообщений, связанных с этими email
        email_queries = Q()
        for email in all_emails:
            email_queries |= Q(clients__icontains=email) | Q(user__email__icontains=email)

        # Получаем все сообщения, связанные с этой перепиской
        thread_messages = Message.objects.filter(
            email_queries,
            message_rm__isnull=True
        ).exclude(
            id=message.id
        ).select_related('user').prefetch_related('files', 'read_by').distinct().order_by('-created_at')

        # Определяем тип для каждого сообщения в переписке
        for msg in thread_messages:
            if msg.user == request.user:
                if msg.self_field:
                    msg.display_type = 'draft'
                else:
                    msg.display_type = 'outgoing'
            elif user_email in [email.lower() for email in msg.get_clients_list()]:
                msg.display_type = 'incoming'
            else:
                msg.display_type = 'other'

        # Группируем сообщения по дате
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        messages_today = []
        messages_yesterday = []
        messages_earlier = []

        for msg in thread_messages:
            msg_date = msg.created_at.date()
            if msg_date == today:
                messages_today.append(msg)
            elif msg_date == yesterday:
                messages_yesterday.append(msg)
            else:
                messages_earlier.append(msg)

        # ============ ДОБАВЛЯЕМ СЧЕТЧИКИ ДЛЯ БОКОВОЙ ПАНЕЛИ ============
        # Получаем все сообщения пользователя для подсчета
        all_user_messages = Message.objects.filter(
            Q(user=request.user) | Q(clients__icontains=user_email)
        ).distinct()

        # Получаем директории и маски пользователя
        user_dirs = MessageDir.objects.filter(user=request.user)
        user_masks = MessageMask.objects.filter(user=request.user)

        # Счетчики для папок
        all_for_count = list(all_user_messages)
        counters = {
            'inbox': len([m for m in all_for_count if
                          m.message_type == 'incoming' and not m.message_rm]),
            'sent': len([m for m in all_for_count if
                         m.message_type == 'outgoing' and not m.message_rm and m.user == request.user]),
            'draft': len([m for m in all_for_count if
                          m.message_type == 'draft' and not m.message_rm]),
            'spam': 0,
            'trash': len([m for m in all_for_count if m.message_rm]),
        }
        # ============ КОНЕЦ ДОБАВЛЕННОГО КОДА ============

        context = {
            'message': message,
            'thread_messages': thread_messages,
            'messages_today': messages_today,
            'messages_yesterday': messages_yesterday,
            'messages_earlier': messages_earlier,
            'total_thread_count': thread_messages.count(),
            'all_emails': list(all_emails),
            'user_email': request.user.email,
            # ДОБАВЛЯЕМ В КОНТЕКСТ
            'user_dirs': user_dirs,
            'user_masks': user_masks,
            'counters': counters,
            'current_folder': request.GET.get('folder', 'inbox'),
        }
        return render(request, self.template_name, context)


class MessageListView(LoginRequiredMixin, View):
    """Главная страница со списком сообщений"""
    template_name = 'moderation/mail/message_list.html'

    def get(self, request):
        user_email = request.user.email.lower()

        # Получаем все сообщения, где пользователь является отправителем или получателем
        all_messages = Message.objects.filter(
            Q(user=request.user) | Q(clients__icontains=user_email)
        ).distinct().select_related('user').prefetch_related('dirs', 'masks', 'files', 'read_by')

        # Определяем тип для отображения и фильтруем по папкам
        folder = request.GET.get('folder', 'inbox')
        user_messages = []

        for msg in all_messages:
            # Используем message_type из БД для определения display_type
            if msg.message_type == 'draft':
                msg.display_type = 'draft'
            elif msg.message_type == 'incoming':
                msg.display_type = 'incoming'
            elif msg.message_type == 'outgoing':
                msg.display_type = 'outgoing'
            else:
                # Если тип не определен, определяем по логике
                recipients = [email.lower() for email in msg.get_clients_list()]
                if msg.user == request.user:
                    if msg.self_field:
                        msg.display_type = 'draft'
                        # Обновляем в БД
                        msg.message_type = 'draft'
                        msg.save(update_fields=['message_type'])
                    else:
                        msg.display_type = 'outgoing'
                        if msg.message_type != 'outgoing':
                            msg.message_type = 'outgoing'
                            msg.save(update_fields=['message_type'])
                elif user_email in recipients:
                    msg.display_type = 'incoming'
                    if msg.message_type != 'incoming':
                        msg.message_type = 'incoming'
                        msg.save(update_fields=['message_type'])
                else:
                    msg.display_type = 'other'

            # Фильтруем по папкам
            if folder == 'inbox' and msg.display_type == 'incoming' and not msg.message_rm:
                user_messages.append(msg)
            elif folder == 'sent' and msg.display_type == 'outgoing' and not msg.message_rm:
                user_messages.append(msg)
            elif folder == 'draft' and msg.display_type == 'draft' and not msg.message_rm:
                user_messages.append(msg)
            elif folder == 'trash' and msg.message_rm:
                user_messages.append(msg)
            elif folder == 'all' and not msg.message_rm:
                user_messages.append(msg)

        # Поиск
        search_query = request.GET.get('search', '')
        if search_query:
            user_messages = [msg for msg in user_messages if
                             search_query.lower() in msg.message.lower() or
                             search_query.lower() in (msg.subject or '').lower() or
                             search_query.lower() in msg.clients.lower() or
                             search_query.lower() in msg.user.email.lower()]

        # Пагинация
        from django.core.paginator import Paginator
        paginator = Paginator(user_messages, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Получаем директории и маски пользователя
        user_dirs = MessageDir.objects.filter(user=request.user)
        user_masks = MessageMask.objects.filter(user=request.user)

        # Счетчики для папок
        all_for_count = list(all_messages)
        counters = {
            'inbox': len([m for m in all_for_count if
                          m.message_type == 'incoming' and not m.message_rm]),
            'sent': len([m for m in all_for_count if
                         m.message_type == 'outgoing' and not m.message_rm and m.user == request.user]),
            'draft': len([m for m in all_for_count if
                          m.message_type == 'draft' and not m.message_rm]),
            'spam': 0,
            'trash': len([m for m in all_for_count if m.message_rm]),
        }

        # Для отладки - выведем в консоль
        print(f"Всего сообщений: {all_messages.count()}")
        print(f"Входящие: {counters['inbox']}")
        print(f"Исходящие: {counters['sent']}")
        print(f"Черновики: {counters['draft']}")

        context = {
            'messages': page_obj,
            'user_dirs': user_dirs,
            'user_masks': user_masks,
            'counters': counters,
            'current_folder': folder,
            'search_query': search_query,
            'user_email': request.user.email,
        }
        return render(request, self.template_name, context)


class MessageDetailView(LoginRequiredMixin, View):
    """Просмотр конкретного сообщения"""
    template_name = 'moderation/mail/message_detail.html'

    def get(self, request, message_id):
        user_email = request.user.email.lower()

        message = get_object_or_404(
            Message.objects.select_related('user', 'message_rm')
            .prefetch_related('files', 'dirs', 'masks', 'read_by'),
            Q(id=message_id) & (Q(user=request.user) | Q(clients__icontains=user_email))
        )

        # Определяем тип сообщения для отображения
        if message.user == request.user:
            if message.self_field:
                message.display_type = 'draft'
            else:
                message.display_type = 'outgoing'
        elif user_email in [email.lower() for email in message.get_clients_list()]:
            message.display_type = 'incoming'
        else:
            message.display_type = 'other'

        # Отмечаем сообщение как прочитанное (только для входящих)
        if message.display_type == 'incoming' and request.user not in message.read_by.all():
            message.read_by.add(request.user)

        # Получаем все email адреса, связанные с этим сообщением
        all_emails = set(message.get_related_emails())
        all_emails.add(user_email)

        # Создаем Q объект для поиска всех сообщений, связанных с этими email
        email_queries = Q()
        for email in all_emails:
            email_queries |= Q(clients__icontains=email) | Q(user__email__icontains=email)

        # Получаем все сообщения, связанные с этой перепиской
        thread_messages = Message.objects.filter(
            email_queries,
            message_rm__isnull=True
        ).exclude(
            id=message.id
        ).select_related('user').prefetch_related('files', 'read_by').distinct().order_by('-created_at')

        # Определяем тип для каждого сообщения в переписке
        for msg in thread_messages:
            if msg.user == request.user:
                if msg.self_field:
                    msg.display_type = 'draft'
                else:
                    msg.display_type = 'outgoing'
            elif user_email in [email.lower() for email in msg.get_clients_list()]:
                msg.display_type = 'incoming'
            else:
                msg.display_type = 'other'

        # Группируем сообщения по дате
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        messages_today = []
        messages_yesterday = []
        messages_earlier = []

        for msg in thread_messages:
            msg_date = msg.created_at.date()
            if msg_date == today:
                messages_today.append(msg)
            elif msg_date == yesterday:
                messages_yesterday.append(msg)
            else:
                messages_earlier.append(msg)

        # ============ ДОБАВЛЯЕМ СЧЕТЧИКИ ДЛЯ БОКОВОЙ ПАНЕЛИ ============
        # Получаем все сообщения пользователя для подсчета
        all_user_messages = Message.objects.filter(
            Q(user=request.user) | Q(clients__icontains=user_email)
        ).distinct()

        # Получаем директории и маски пользователя
        user_dirs = MessageDir.objects.filter(user=request.user)
        user_masks = MessageMask.objects.filter(user=request.user)

        # Счетчики для папок
        all_for_count = list(all_user_messages)
        counters = {
            'inbox': len([m for m in all_for_count if
                          m.message_type == 'incoming' and not m.message_rm]),
            'sent': len([m for m in all_for_count if
                         m.message_type == 'outgoing' and not m.message_rm and m.user == request.user]),
            'draft': len([m for m in all_for_count if
                          m.message_type == 'draft' and not m.message_rm]),
            'spam': 0,
            'trash': len([m for m in all_for_count if m.message_rm]),
        }
        # ============ КОНЕЦ ДОБАВЛЕННОГО КОДА ============

        context = {
            'message': message,
            'thread_messages': thread_messages,
            'messages_today': messages_today,
            'messages_yesterday': messages_yesterday,
            'messages_earlier': messages_earlier,
            'total_thread_count': thread_messages.count(),
            'all_emails': list(all_emails),
            'user_email': request.user.email,
            # ДОБАВЛЯЕМ В КОНТЕКСТ
            'user_dirs': user_dirs,
            'user_masks': user_masks,
            'counters': counters,
            'current_folder': request.GET.get('folder', 'inbox'),
        }
        return render(request, self.template_name, context)



class MessageCreateView(LoginRequiredMixin, View):

    def post(self, request):
        try:
            message_text = request.POST.get('message', '')
            subject = request.POST.get('subject', '')
            self_field = request.POST.get('self_field') == 'on'

            # строка получателей
            recipients = request.POST.get('recipients', '')

            new_message = Message.objects.create(
                user=request.user,
                message=message_text,
                subject=subject,
                clients=recipients,
                self_field=self_field
            )

            if not self_field:
                new_message.read_by.add(request.user)

            files = request.FILES.getlist('files')

            for file in files:
                MessageFile.objects.create(
                    file=file,
                    message=new_message
                )

            return JsonResponse({
                'status': 'success',
                'message': 'Сообщение отправлено',
                'id': str(new_message.id)
            })

        except Exception as e:
            import traceback
            traceback.print_exc()

            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class MessageDeleteView(LoginRequiredMixin, View):
    """Удаление сообщения (перемещение в корзину или полное удаление)"""

    def post(self, request, message_id):
        message = get_object_or_404(
            Message,
            Q(id=message_id) & (Q(user=request.user) | Q(clients__icontains=request.user.email))
        )

        # Если сообщение уже в корзине, удаляем полностью
        if message.message_rm:
            message.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'Сообщение полностью удалено'
            })

        # Иначе создаем запись об удалении
        message_rm = MessageRm.objects.create(
            name=f"Deleted message {message.id}",
            key=f"delete_key_{message.id}"
        )
        message.message_rm = message_rm
        message.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Сообщение перемещено в корзину'
        })


@method_decorator(csrf_exempt, name='dispatch')
class MessageRestoreView(LoginRequiredMixin, View):
    """Восстановление сообщения из корзины"""

    def post(self, request, message_id):
        message = get_object_or_404(
            Message,
            Q(id=message_id) & (Q(user=request.user) | Q(clients__icontains=request.user.email)) & Q(
                message_rm__isnull=False)
        )

        message_rm = message.message_rm
        message.message_rm = None
        message.save()
        message_rm.delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Сообщение восстановлено'
        })


@method_decorator(csrf_exempt, name='dispatch')
class MessageMarkReadView(LoginRequiredMixin, View):
    """Пометить сообщение как прочитанное"""

    def post(self, request, message_id):
        message = get_object_or_404(
            Message,
            Q(id=message_id) & (Q(user=request.user) | Q(clients__icontains=request.user.email))
        )

        # Добавляем пользователя в список прочитавших
        message.read_by.add(request.user)

        return JsonResponse({
            'status': 'success',
            'message': 'Сообщение помечено как прочитанное'
        })


@method_decorator(csrf_exempt, name='dispatch')
class MessageToggleStarView(LoginRequiredMixin, View):
    """Добавить/убрать звездочку у сообщения"""

    def post(self, request, message_id):
        message = get_object_or_404(
            Message,
            Q(id=message_id) & (Q(user=request.user) | Q(clients__icontains=request.user.email))
        )

        # Здесь логика для звездочек
        # Например, создать/удалить маску с типом "starred"

        return JsonResponse({
            'status': 'success',
            'message': 'Звездочка обновлена'
        })


class GetUsersListView(LoginRequiredMixin, View):
    """API для получения списка пользователей (для поля Кому)"""

    def get(self, request):
        search = request.GET.get('search', '')
        users = User.objects.filter(is_active=True)

        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        users = users.exclude(id=request.user.id)[:10]

        data = [{
            'id': user.id,
            'text': f"{user.get_full_name() or user.username} ({user.email})",
            'email': user.email,
        } for user in users]

        return JsonResponse({'results': data})


@method_decorator(csrf_exempt, name='dispatch')
class CreateDirectoryView(LoginRequiredMixin, View):
    """Создание новой директории"""

    def post(self, request):
        name = request.POST.get('name')
        if not name:
            return JsonResponse({'status': 'error', 'message': 'Название обязательно'}, status=400)

        directory, created = MessageDir.objects.get_or_create(
            name=name,
            user=request.user
        )

        if created:
            return JsonResponse({
                'status': 'success',
                'message': 'Директория создана',
                'id': directory.id,
                'name': directory.name
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Директория с таким названием уже существует'
            }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class AddToDirectoryView(LoginRequiredMixin, View):
    """Добавление сообщения в директорию"""

    def post(self, request, message_id):
        message = get_object_or_404(
            Message,
            Q(id=message_id) & (Q(user=request.user) | Q(clients__icontains=request.user.email))
        )

        dir_id = request.POST.get('dir_id')
        directory = get_object_or_404(MessageDir, id=dir_id, user=request.user)

        message.dirs.add(directory)

        return JsonResponse({
            'status': 'success',
            'message': f'Сообщение добавлено в папку {directory.name}'
        })


class MailSettingsModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/mail/mail_settings.html'

    def get(self, request, *args, **kwargs):
        # Получаем или создаем настройки SMTP для текущего пользователя
        smtp_settings, created = UserSettingsSMTP.objects.get_or_create(user=request.user)

        context = {
            'smtp_settings': smtp_settings,
            'created': created,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            # Получаем или создаем настройки
            smtp_settings, created = UserSettingsSMTP.objects.get_or_create(user=request.user)

            # Обновляем поля из POST запроса
            smtp_settings.message_header = request.POST.get('message_header', '')
            smtp_settings.message_footer = request.POST.get('message_footer', '')
            smtp_settings.email_host = request.POST.get('email_host', '')
            smtp_settings.default_from_email = request.POST.get('default_from_email', '')
            smtp_settings.email_port = request.POST.get('email_port', '')
            smtp_settings.email_host_user = request.POST.get('email_host_user', '')
            smtp_settings.email_host_password = request.POST.get('email_host_password', '')
            smtp_settings.email_use_tls = request.POST.get('email_use_tls') == 'on'
            smtp_settings.email_use_ssl = request.POST.get('email_use_ssl') == 'on'

            smtp_settings.save()

            if request.htmx:
                # Если HTMX запрос, возвращаем только сообщение об успехе
                return render(request, 'moderation/mail/partials/settings_success.html', {
                    'message': 'Настройки успешно сохранены'
                })
            else:
                # Обычный POST запрос
                messages.success(request, 'Настройки успешно сохранены')
                return redirect('mail:mail_settings')

        except Exception as e:
            if request.htmx:
                return render(request, 'moderation/mail/partials/settings_error.html', {
                    'error': str(e)
                })
            else:
                messages.error(request, f'Ошибка при сохранении: {str(e)}')
                return redirect('mail:mail_settings')


@csrf_exempt
def test_smtp_connection(request):
    """Тестирование подключения к SMTP серверу"""
    if request.method == 'POST':
        try:
            # Получаем данные из запроса
            host = request.POST.get('email_host')
            port = request.POST.get('email_port')
            user = request.POST.get('email_host_user')
            password = request.POST.get('email_host_password')
            use_tls = request.POST.get('email_use_tls') == 'on'
            use_ssl = request.POST.get('email_use_ssl') == 'on'

            if not host or not port:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Не указан сервер или порт'
                })

            port = int(port)

            # Пробуем подключиться
            if use_ssl:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(host, port, context=context)
            else:
                server = smtplib.SMTP(host, port)
                if use_tls:
                    server.starttls()

            # Пробуем авторизоваться
            if user and password:
                server.login(user, password)

            server.quit()

            return JsonResponse({
                'status': 'success',
                'message': 'Подключение успешно'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Метод не поддерживается'
    })
