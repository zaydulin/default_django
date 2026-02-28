from django.urls import path
app_name = 'course'
from . import views

urlpatterns = [
    path("moderation/courses/dashboard/", views.DashboardModerationView.as_view(), name="moderation_course_dashboard_list"),
    path("moderation/courses/my-courses/", views.MyCoursesView.as_view(), name="my_courses_list"),
    path("moderation/courses/completed-courses/", views.CompletedCoursesView.as_view(), name="completed_courses_list"),
    path("moderation/courses/certificates/", views.CertificatesView.as_view(), name="certificates_list"),
    path("moderation/courses/created-courses/", views.CreatedCoursesView.as_view(), name="created_courses_list"),
]