from django.urls import path
app_name = 'webmain'
from . import views


urlpatterns = [
    path('subscribe/',  views.subscribe, name='subscribe'),

]