from django.urls import path
app_name = 'connects'
from . import views

urlpatterns = [
    path("moderation/chats/", views.ChatsModerationView.as_view(), name="moderation_chats_list"),

]