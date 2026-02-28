from django.urls import path
app_name = 'hr'
from . import views

urlpatterns = [
    path("moderation/calendar/", views.CalendarModerationView.as_view(), name="moderation_calendar"),

]