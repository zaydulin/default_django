from django.urls import path
app_name = 'mail'
from . import views

urlpatterns = [
    path("moderation/mails/", views.MailModerationView.as_view(), name="moderation_mails_list"),
    path("moderation/list/", views.MailSettingsModerationView.as_view(), name="moderation_settings_list"),

]