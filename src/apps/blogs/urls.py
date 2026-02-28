from django.urls import path
app_name = 'blogs'
from . import views


urlpatterns = [
    # Сайт
    path("blogs/", views.BlogView.as_view(), name="list"),
    path('page/<int:page>/', views.BlogPaginationView.as_view(), name='pagination'),
    path("blogs/<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),
    # Модерация
    path("moderation/articles/", views.ArticlesView.as_view(), name="articles_list"),
    path('moderation/articles-page/<int:page>/', views.ArticlesPaginationView.as_view(), name='articles_pagination'),
    path('moderation/blog-form/', views.BlogFormView.as_view(), name='blog_form'),
    path('moderation/blog-form/<int:pk>/', views.BlogFormView.as_view(), name='blog_form'),

    path("moderation/categories/", views.CategoriesView.as_view(), name="categories_list"),
    path('moderation/categories-page/<int:page>/', views.CategoriesPaginationView.as_view(), name='categories_pagination'),
    path('moderation/categories-form/', views.CategoriesFormView.as_view(), name='categories_form'),
    path('moderation/categories-form/<int:pk>/', views.CategoriesFormView.as_view(), name='categories_form'),
    path("moderation/tags/", views.TagsView.as_view(), name="tags_list"),
    path('moderation/tags-page/<int:page>/', views.TagsPaginationView.as_view(), name='tags_pagination'),
    path('moderation/tags-form/', views.TagsFormView.as_view(), name='tags_form'),
    path('moderation/tags-form/<int:pk>/', views.TagsFormView.as_view(), name='tags_form'),
    path("moderation/likes/", views.LikesView.as_view(), name="likes_list"),
    path("moderation/comments/", views.CommentsView.as_view(), name="comments_list"),
    path("moderation/complaints/", views.ComplaintsView.as_view(), name="complaints_list"),

]