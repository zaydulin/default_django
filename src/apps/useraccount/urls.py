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

    path('moderation/edit_profile/', views.EditMyProfileView.as_view(), name='edit_profile'),
    # Модерация
    path("moderation/users/", views.UsersModerationView.as_view(), name="moderation_users_list"),
    path("moderation/clients/", views.ClientModerationView.as_view(), name="moderation_client_list"),
    path("moderation/user-information/", views.UserInformationModerationView.as_view(), name="moderation_user_information_list"),
    path("moderation/user-assets/", views.UserAssetsModerationView.as_view(), name="moderation_user_assets_list"),
    path("moderation/user-statistic/", views.UserStatisticModerationView.as_view(), name="moderation_user_statistic_list"),
    path("moderation/user-settings/", views.UserSettingsModerationView.as_view(), name="moderation_user_settings_list"),
    path("moderation/user-security/", views.UserSecurityModerationView.as_view(), name="moderation_user_security_list"),

]