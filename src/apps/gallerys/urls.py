from django.urls import path
app_name = 'gallerys'
from . import views

urlpatterns = [
    path("moderation/gallerys/", views.GallerysModerationView.as_view(), name="moderation_gallerys_list"),

]