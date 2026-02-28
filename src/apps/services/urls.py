from django.urls import path
app_name = 'services'
from . import views

urlpatterns = [
    path("service/", views.ServiceView.as_view(), name="list"),
    path('service/category/<slug:category_slug>/', views.ServiceView.as_view(), name='category_services'),
    path('service-page/<int:page>/', views.ServicePaginationView.as_view(), name='service_pagination'),
    path("service/<slug:slug>/", views.ServiceDetailView.as_view(), name="service_detail"),
    # Модерация
    path("moderation/services/", views.ServiceModerationView.as_view(), name="moderation_services_list"),

]