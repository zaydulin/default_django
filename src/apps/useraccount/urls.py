from django.urls import path
app_name = 'useraccount'
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("register/check-username/", views.CheckUsernameView.as_view(), name="check_username"),
    path("register/check-email/", views.CheckEmailView.as_view(), name="check_email"),
    path("register/check-phone/", views.CheckPhoneView.as_view(), name="check_phone"),

    path('login/', views.CustomLoginView.as_view(), name='login'),

    path('logout/', views.custom_logout, name='logout'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('edit_profile/', views.EditMyProfileView.as_view(), name='edit_profile'),

]