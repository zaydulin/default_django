from django.urls import path
app_name = 'integrations'
from . import views

urlpatterns = [
    path("moderation/integrations/social/", views.SocialModerationView.as_view(), name="moderation_social_list"),
    path("moderation/integrations/telephony/", views.TelephonyModerationView.as_view(), name="moderation_telephony_list"),
    path("moderation/integrations/payments/", views.PaymentModerationView.as_view(), name="moderation_payments_list"),
    path("moderation/integrations/dopservice/", views.DopServiseModerationView.as_view(), name="moderation_dopservice_list"),
    path("moderation/integrations/neiro/", views.NeiroModerationView.as_view(), name="moderation_neiro_list"),

]