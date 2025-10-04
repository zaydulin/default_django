from django.views.generic import DetailView

from pages.models import Pages

"""Страницы"""
class PageDetailView(DetailView):
    """Страница"""
    model = Pages
    template_name = 'page_detail.html'
    context_object_name = 'page'
    slug_field = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context['page']
        if page:
            context['pageinformation'] = page.description
            context['seo_previev'] = page.previev
            context['seo_title'] = page.title
            context['seo_description'] = page.metadescription
            context['seo_propertytitle'] = page.propertytitle
            context['seo_propertydescription'] = page.propertydescription
        else:
            context['pageinformation'] = None
        return context


