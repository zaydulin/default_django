from django.urls import path
app_name = 'webmain'
from . import views


urlpatterns = [
    path("page/<slug:slug>/", views.PageDetailView.as_view(), name="page"),

]