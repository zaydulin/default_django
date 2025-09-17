from django.urls import path
app_name = 'blogs'
from . import views


urlpatterns = [
    path("blogs/", views.BlogView.as_view(), name="list"),
    path("<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),

]