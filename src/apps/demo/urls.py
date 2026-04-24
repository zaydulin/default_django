from django.urls import path
app_name = 'demo'
from . import views


urlpatterns = [
    path('demo/', views.DemoView.as_view(), name='demo'),

]