from django.urls import path
app_name = 'projects'
from . import views

urlpatterns = [
    path("projects/", views.ProjectView.as_view(), name="list"),
    path('projects/category/<slug:category_slug>/', views.ProjectView.as_view(), name='category_projects'),

    path('projects-page/<int:page>/', views.ProjectPaginationView.as_view(), name='project_pagination'),

    path("projects/<slug:slug>/", views.ProjectDetailView.as_view(), name="project_detail"),

    path("moderation/projects/", views.ProjectsModerationView.as_view(), name="moderation_projects_list"),

]