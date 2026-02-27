from django.urls import path
app_name = 'cases'
from . import views

urlpatterns = [
    # Модерация
    path("moderation/cases/", views.CasesModerationView.as_view(), name="moderation_cases_list"),

]