from django.urls import path
app_name = 'services'
from . import views

urlpatterns = [
    path("moderation/services/", views.ServiceModerationView.as_view(), name="moderation_services_list"),

]