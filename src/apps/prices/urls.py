from django.urls import path
app_name = 'prices'
from . import views

urlpatterns = [
    path("moderation/prices/", views.PricesModerationView.as_view(), name="moderation_prices_list"),

]