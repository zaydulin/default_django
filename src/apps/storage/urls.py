from django.urls import path
app_name = 'ticket'
from . import views

urlpatterns = [
    path("moderation/tickets/", views.TicketsModerationView.as_view(), name="moderation_tickets_list"),

]