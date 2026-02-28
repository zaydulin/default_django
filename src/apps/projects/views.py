from django.shortcuts import render
from apps.useraccount.views import CustomHtmxMixin
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from webmain.models import Seo
from projects.models import Projects, CategorysProjects


# Create your views here.

class ProjectView(ListView):
    model = Projects
    template_name = "active/projects/projects.html"
    context_object_name = "projects"
    paginate_by = 6

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Определяем категорию на раннем этапе
        self.category_slug = kwargs.get('category_slug')
        self.current_category = None

        if self.category_slug:
            try:
                self.current_category = CategorysProjects.objects.get(slug=self.category_slug)
            except CategorysProjects.DoesNotExist:
                self.current_category = None

    def get_queryset(self):
        """Фильтруем рекламы по категории если нужно"""
        queryset = super().get_queryset().order_by('-id')  # Добавляем сортировку

        if self.current_category:
            # Правильная фильтрация по ManyToManyField
            queryset = queryset.filter(category=self.current_category)

        return queryset

    def get_template_names(self):
        is_htmx = bool(self.request.META.get('HTTP_HX_REQUEST'))

        # Для пагинационных запросов возвращаем другой шаблон
        if is_htmx and self.request.GET.get('page'):
            return ["active/projects/partials/project_page_content.html"]

        return super().get_template_names()

    def render_to_response(self, context, **response_kwargs):
        # Для HTMX пагинации возвращаем только контент
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            return render(self.request, "active/projects/partials/project_page_content.html", context)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categorys'] = CategorysProjects.objects.all()
        context['current_category'] = self.current_category

        seo_data = None

        # 1️⃣ Пытаемся взять SEO для "Услуги" (pagetype=13)
        try:
            seo_data = Seo.objects.get(pagetype=12)
        except Seo.DoesNotExist:
            seo_data = None

        # 2️⃣ Если есть категория — приоритет у категории
        if self.current_category:
            category = self.current_category

            context['seo_title'] = (
                    category.title
                    or (f"{category.name} | {seo_data.title}" if seo_data else category.name)
            )

            context['seo_description'] = (
                    category.metadescription
                    or (seo_data.metadescription if seo_data else f"Услуги в категории {category.name}")
            )

            context['seo_propertytitle'] = (
                    category.propertytitle
                    or (seo_data.propertytitle if seo_data else category.name)
            )

            context['seo_propertydescription'] = (
                    category.propertydescription
                    or (seo_data.propertydescription if seo_data else '')
            )

            context['seo_previev'] = category.previev or (seo_data.previev if seo_data else None)
            context['seo_head'] = seo_data.setting if seo_data else ''

        # 3️⃣ Если категории нет — используем только SEO 13
        else:
            if seo_data:
                context['seo_title'] = seo_data.title
                context['seo_description'] = seo_data.metadescription
                context['seo_propertytitle'] = seo_data.propertytitle
                context['seo_propertydescription'] = seo_data.propertydescription
                context['seo_previev'] = seo_data.previev
                context['seo_head'] = seo_data.setting
            else:
                context['seo_title'] = "Услуги"
                context['seo_description'] = "Все услуги"
                context['seo_propertytitle'] = "Услуги"
                context['seo_propertydescription'] = ""
                context['seo_previev'] = None
                context['seo_head'] = ""

        # HTMX pagination
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            context['is_pagination_request'] = True

        return context


class ProjectPaginationView(ListView):
    model = Projects
    template_name = "active/projects/partials/project_items.html"  # Только элементы
    context_object_name = "projects"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pagination_request'] = True
        return context

class ProjectDetailView(DetailView):
    model = Projects
    template_name = "active/projects/project_detail.html"
    context_object_name = "project"

class ProjectsModerationView(CustomHtmxMixin, View):
    template_name = 'moderation/projects/projects.html'

    def get(self, request, *args, **kwargs):
        # Здесь ваша логика для GET-запроса
        # Например, получение данных из базы
        context = {
            # ваш контекст
        }
        return render(request, self.template_name, context)