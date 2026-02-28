from django.urls import path
app_name = 'payment'
from . import views

urlpatterns = [
    path("moderation/payments/accounts-cashdesks/", views.AccountsAndCashdesksView.as_view(), name="accounts_and_cashdesks_list"),
    path("moderation/payments/online-cashdesks/", views.OnlineCashdesksView.as_view(), name="online_cashdesks_list"),
    path("moderation/payments/counterparties/", views.CounterpartiesView.as_view(), name="counterparties_list"),
    path("moderation/payments/payment-articles/", views.PaymentArticlesView.as_view(), name="payment_articles_list"),
    path("moderation/payments/financial-operations/", views.FinancialOperationsView.as_view(), name="financial_operations_list"),
    path("moderation/payments/payment-documents/", views.PaymentDocumentsView.as_view(), name="payment_documents_list"),
    path("moderation/payments/ccm-operations/", views.CCMOperationsView.as_view(), name="ccm_operations_list"),
    path("moderation/payments/payment-reception/", views.PaymentReceptionView.as_view(), name="payment_reception_list"),
    path("moderation/payments/payment-reports/", views.PaymentReportsView.as_view(), name="payment_reports_list"),
    path("moderation/payments/payment-settings/", views.PaymentSettingsView.as_view(), name="payment_settings_list"),
]