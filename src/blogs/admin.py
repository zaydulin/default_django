from django.contrib import admin
from .models import *
import nested_admin
from django_ace import AceWidget
from django import forms

@admin.register(CategorysBlogs)
class CategorysBlogsAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description"]
    prepopulated_fields = {"slug": ('name',), }
    list_display_links = ["id", "name", "description"]
    save_as = True
    save_on_top = True

@admin.register(TagsBlogs)
class TagsBlogsAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description"]
    prepopulated_fields = {"slug": ('name',), }
    list_display_links = ["id", "name", "description"]
    save_as = True
    save_on_top = True


@admin.register(Blogs)
class BlogsAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug"]
    prepopulated_fields = {"slug": ('name',), }
    list_display_links = ["id", "name", "slug"]
    save_as = True
    save_on_top = True


