from django.urls import path
app_name = 'course'
from . import views

urlpatterns = [
    path("moderation/dashboard/", views.DashboardModerationView.as_view(), name="moderation_dashboard_list"),
    path("my-courses/", views.MyCoursesView.as_view(), name="my_courses_list"),
    path("completed-courses/", views.CompletedCoursesView.as_view(), name="completed_courses_list"),
    path("certificates/", views.CertificatesView.as_view(), name="certificates_list"),
    path("created-courses/", views.CreatedCoursesView.as_view(), name="created_courses_list"),
]