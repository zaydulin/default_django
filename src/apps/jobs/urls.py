from django.urls import path
app_name = 'jobs'
from . import views

urlpatterns = [
    path("moderation/jobs/", views.JobsModerationView.as_view(), name="moderation_jobs_list"),
    path("moderation/jobs-aplication/", views.JobsAplicationModerationView.as_view(), name="moderation_jobs_aplication"),

]