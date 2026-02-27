from django.urls import path
app_name = 'blogs'
from . import views


urlpatterns = [
    # Сайт
    path("blogs/", views.BlogView.as_view(), name="list"),
    path('page/<int:page>/', views.BlogPaginationView.as_view(), name='pagination'),
    path("blogs/<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),
    # Модерация
    path("moderation/blogs/", views.BlogsModerationView.as_view(), name="moderation_blogs_list"),
]