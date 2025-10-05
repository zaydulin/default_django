from django.urls import path
app_name = 'blogs'
from . import views


urlpatterns = [
    path("blogs/", views.BlogView.as_view(), name="list"),
    path('page/<int:page>/', views.BlogPaginationView.as_view(), name='pagination'),

    path("<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),
    path('blog/create/', views.BlogCreateUpdateView.as_view(), name='blog_create'),
    path('blog/edit/<int:pk>/', views.BlogCreateUpdateView.as_view(), name='blog_edit'),

]