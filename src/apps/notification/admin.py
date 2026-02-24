from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['get_status_display', 'user']
