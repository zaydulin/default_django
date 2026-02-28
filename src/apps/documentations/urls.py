from django.urls import path
app_name = 'documentations'
from . import views

urlpatterns = [
    path("moderation/documentations/", views.DocumentationsModerationView.as_view(), name="moderation_documentations_list"),

]