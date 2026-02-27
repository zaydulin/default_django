from django.urls import path
app_name = 'moderation'
from . import views

urlpatterns = [
    # Модерация
    path("moderation/dashboard/", views.DashboardModerationView.as_view(), name="moderation_dashboard_list"),

]