from django.shortcuts import render
from apps.useraccount.views import CustomHtmxMixin
from django.views import View


class SettlementsView(CustomHtmxMixin, View):
    template_name = 'accounting/settlements.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class DailyCalculationView(CustomHtmxMixin, View):
    template_name = 'accounting/daily_calculation.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class PeriodCalculationView(CustomHtmxMixin, View):
    template_name = 'accounting/period_calculation.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class CalculationRulesView(CustomHtmxMixin, View):
    template_name = 'accounting/calculation_rules.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class CalculationCriteriaView(CustomHtmxMixin, View):
    template_name = 'accounting/calculation_criteria.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class CalculationSchemesView(CustomHtmxMixin, View):
    template_name = 'accounting/calculation_schemes.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class BonusesAndFinesView(CustomHtmxMixin, View):
    template_name = 'accounting/bonuses_and_fines.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)