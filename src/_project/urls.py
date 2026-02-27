from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('ckeditor/', include('ckeditor_uploader.urls')),
    #path("__debug__/", include("debug_toolbar.urls")),
    path("_nested_admin/", include("nested_admin.urls")),
    path('developer_management/', admin.site.urls),
    path('', include('balance.urls', namespace='balance')),
    path('', include('blogs.urls', namespace='blogs')),
    path('', include('bookmark.urls', namespace='bookmark')),
    path('', include('cases.urls', namespace='cases')),
    path('', include('company.urls', namespace='company')),
    path('', include('connects.urls', namespace='connects')),
    path('', include('connects.urls', namespace='connects')),
    path('', include('course.urls', namespace='course')),
    path('', include('crm.urls', namespace='crm')),
    path('', include('gallerys.urls', namespace='gallerys')),
    path('', include('hr.urls', namespace='hr')),
    path('', include('mail.urls', namespace='mail')),
    path('', include('moderation.urls', namespace='moderation')),
    path('', include('notification.urls', namespace='notification')),
    path('', include('prices.urls', namespace='prices')),
    path('', include('projects.urls', namespace='projects')),
    path('', include('services.urls', namespace='services')),
    path('', include('shops.urls', namespace='shops')),
    path('', include('ticket.urls', namespace='ticket')),
    path('', include('useraccount.urls', namespace='useraccount')),
    path('', include('webmain.urls', namespace='webmain')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)