from django.urls import path
app_name = 'connects'
from . import views

urlpatterns = [
    path("moderation/chats/", views.ChatsModerationView.as_view(), name="moderation_chats_list"),
    path("moderation/calls/", views.CallsModerationView.as_view(), name="moderation_calls_list"),

]