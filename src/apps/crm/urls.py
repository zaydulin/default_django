from django.urls import path
app_name = 'crm'
from . import views

urlpatterns = [
    path("moderation/crm/", views.CrmModerationView.as_view(), name="moderation_crm_list"),

]