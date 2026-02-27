from django.urls import path
app_name = 'notification'
from . import views

urlpatterns = [
    path("moderation/notifications/", views.NotificationModerationView.as_view(), name="moderation_notification_list"),

]