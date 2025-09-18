from django.urls import path
app_name = 'webmain'
from . import views


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contacts/', views.ContactView.as_view(), name='contacts'),
    path("faqs/", views.FaqsView.as_view(), name="faqs"),
    path('subscribe/',  views.subscribe, name='subscribe'),
    path('search/', views.MultiModelSearchView.as_view(), name='search'),

]