from django.shortcuts import render
from apps.useraccount.views import CustomHtmxMixin
from django.views import View


class AccountsAndCashdesksView(CustomHtmxMixin, View):
    template_name = 'moderation/payment/accounts_and_cashdesks.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class OnlineCashdesksView(CustomHtmxMixin, View):
    template_name = 'moderation/payment/online_cashdesks.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class CounterpartiesView(CustomHtmxMixin, View):
    template_name = 'moderation/payment/counterparties.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class PaymentArticlesView(CustomHtmxMixin, View):
    template_name = 'moderation/payment/payment_articles.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class FinancialOperationsView(CustomHtmxMixin, View):
    template_name = 'moderation/payment/financial_operations.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class PaymentDocumentsView(CustomHtmxMixin, View):
    template_name = 'moderation/payment/payment_documents.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class CCMOperationsView(CustomHtmxMixin, View):
    template_name = 'moderation/payment/ccm_operations.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class PaymentReceptionView(CustomHtmxMixin, View):
    template_name = 'moderation/payment/payment_reception.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class PaymentReportsView(CustomHtmxMixin, View):
    template_name = 'moderation/payment/payment_reports.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class PaymentSettingsView(CustomHtmxMixin, View):
    template_name = 'moderation/payment/payment_settings.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)