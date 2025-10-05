from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.list import MultipleObjectMixin
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse

from moderation.models import Collaborations
from webmain.forms import SubscriptionForm
from blogs.models import TagsBlogs,  CategorysBlogs, Blogs
from django.http import Http404
import logging

from webmain.models import Seo

logger = logging.getLogger(__name__)


class CustomHtmxMixin:
    def get_template_names(self):
        is_htmx = bool(self.request.META.get('HTTP_HX_REQUEST'))
        if is_htmx:
            return [self.template_name]
        else:
            return ['include_block.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template_htmx'] = self.template_name

        # Получаем SEO данные из View и передаем их для блоков
        seo_context = self.get_seo_context()
        context.update(seo_context)

        return context

    def get_seo_context(self):
        """
        Переопределите этот метод в дочерних классах
        чтобы вернуть SEO данные для этой страницы
        """
        return {
            'block_title': 'Заголовок по умолчанию',
            'block_description': 'Описание по умолчанию',
            'block_propertytitle': 'Property Title по умолчанию',
            'block_propertydescription': 'Property Description по умолчанию',
            'block_propertyimage': '',
            'block_head': ''
        }

"""Новости"""
class BlogView(CustomHtmxMixin, ListView):
    model = Blogs
    template_name = "blogs/blogs.html"
    context_object_name = "blogs"
    paginate_by = 6

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request") == "true":
            return render(self.request, "blogs/partials/blog_page.html", context)
        return super().render_to_response(context, **response_kwargs)


class BlogDetailView(DetailView):
    model = Blogs
    template_name = "blogs/blog_detail.html"
    context_object_name = "blog"
