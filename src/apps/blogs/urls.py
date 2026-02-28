from django.urls import path
app_name = 'blogs'
from . import views


urlpatterns = [
    # Сайт
    path("blogs/", views.BlogView.as_view(), name="list"),
    path('page/<int:page>/', views.BlogPaginationView.as_view(), name='pagination'),
    path("blogs/<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),
    # Модерация
    path("articles/", views.ArticlesView.as_view(), name="articles_list"),
    path("categories/", views.CategoriesView.as_view(), name="categories_list"),
    path("tags/", views.TagsView.as_view(), name="tags_list"),
    path("likes/", views.LikesView.as_view(), name="likes_list"),
    path("comments/", views.CommentsView.as_view(), name="comments_list"),
    path("complaints/", views.ComplaintsView.as_view(), name="complaints_list"),

]