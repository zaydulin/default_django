from django.urls import path
app_name = 'projects'
from . import views

urlpatterns = [
    path("moderation/projects/", views.ProjectsModerationView.as_view(), name="moderation_projects_list"),

]