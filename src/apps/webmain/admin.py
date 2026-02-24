from django.contrib import admin
from .models import *
import nested_admin
from django_ace import AceWidget
from django import forms

class GeneralSettingsForm(forms.ModelForm):
    message_header = forms.CharField(widget=AceWidget(mode='html',readonly=False,behaviours=True,showgutter=True,  wordwrap=False, usesofttabs=True))
    message_footer = forms.CharField(widget=AceWidget(mode='html',readonly=False,behaviours=True,showgutter=True,  wordwrap=False, usesofttabs=True))

@admin.register(Seo)
class SeoAdmin(admin.ModelAdmin):
    model = Seo


@admin.register(SettingsGlobale)
class SettingsGlobaleAdmin(admin.ModelAdmin):
    list_display = ["id",  "name"]
    list_display_links = ["id",  "name"]

