from django.urls import path
app_name = 'ticket'
from . import views

urlpatterns = [
    path("moderation/settlements/", views.SettlementsView.as_view(), name="settlements_list"),
    path("moderation/daily-calculation/", views.DailyCalculationView.as_view(), name="daily_calculation_list"),
    path("moderation/period-calculation/", views.PeriodCalculationView.as_view(), name="period_calculation_list"),
    path("moderation/calculation-rules/", views.CalculationRulesView.as_view(), name="calculation_rules_list"),
    path("moderation/calculation-criteria/", views.CalculationCriteriaView.as_view(), name="calculation_criteria_list"),
    path("moderation/calculation-schemes/", views.CalculationSchemesView.as_view(), name="calculation_schemes_list"),
    path("moderation/bonuses-and-fines/", views.BonusesAndFinesView.as_view(), name="bonuses_and_fines_list"),

]