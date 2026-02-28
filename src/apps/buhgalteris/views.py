from django.shortcuts import render
from apps.useraccount.views import CustomHtmxMixin
from django.views import View


class SettlementsView(CustomHtmxMixin, View):
    template_name = 'moderation/buhgalteris/settlements.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class DailyCalculationView(CustomHtmxMixin, View):
    template_name = 'moderation/buhgalteris/daily_calculation.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class PeriodCalculationView(CustomHtmxMixin, View):
    template_name = 'moderation/buhgalteris/period_calculation.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class CalculationRulesView(CustomHtmxMixin, View):
    template_name = 'moderation/buhgalteris/calculation_rules.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class CalculationCriteriaView(CustomHtmxMixin, View):
    template_name = 'moderation/buhgalteris/calculation_criteria.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class CalculationSchemesView(CustomHtmxMixin, View):
    template_name = 'moderation/buhgalteris/calculation_schemes.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class BonusesAndFinesView(CustomHtmxMixin, View):
    template_name = 'moderation/buhgalteris/bonuses_and_fines.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)