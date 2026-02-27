from django.urls import path
app_name = 'bookmarks'
from . import views

urlpatterns = [
    # Модерация
    path("moderation/bookmarks/", views.BookmarksModerationView.as_view(), name="moderation_bookmarks_list"),

]