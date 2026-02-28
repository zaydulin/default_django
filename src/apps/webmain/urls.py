from django.urls import path
app_name = 'webmain'
from . import views


urlpatterns = [
    path('subscribe/',  views.subscribe, name='subscribe'),
    path("moderation/site/settings/", views.SettingsModerationView.as_view(), name="moderation_settings"),
    path("moderation/site/settings-templates/", views.SettingsTemplatesModerationView.as_view(), name="moderation_settings_templates"),
    path("moderation/site/settings-smtp/", views.SettingsSmtpModerationView.as_view(), name="moderation_settings_smtp"),
    path("moderation/site/pages/", views.PagesModerationView.as_view(), name="moderation_pages_list"),

]