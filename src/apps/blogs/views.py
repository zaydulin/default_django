import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods

from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from moderation.models import Collaborations
from webmain.forms import SubscriptionForm
from blogs.models import TagsBlogs,  CategorysBlogs, Blogs
from django.utils.text import slugify
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from useraccount.models import Profile
from webmain.models import Seo
from django.template.loader import render_to_string
from django.core.paginator import Paginator

from apps.useraccount.views import CustomHtmxMixin

from .forms import BlogForm, CategoriesForm

"""Новости"""


class BlogView(CustomHtmxMixin, ListView):
    model = Blogs
    template_name = "blogs/blogs.html"
    context_object_name = "blogs"
    paginate_by = 6

    def get_template_names(self):
        is_htmx = bool(self.request.META.get('HTTP_HX_REQUEST'))

        # Для пагинационных запросов возвращаем другой шаблон
        if is_htmx and self.request.GET.get('page'):
            return ["blogs/partials/blog_page_content.html"]

        return super().get_template_names()

    def render_to_response(self, context, **response_kwargs):
        # Для HTMX пагинации возвращаем только контент
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            return render(self.request, "blogs/partials/blog_page_content.html", context)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Для пагинационных запросов добавляем флаг
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            context['is_pagination_request'] = True

        # Параметры из базы данных для страницы "Авторизация" (pagetype=5)
        try:
            seo_data_from_db = Seo.objects.get(pagetype=1)

            # Передаем данные из модели в контекст
            context['seo_previev'] = seo_data_from_db.previev
            context['seo_title'] = seo_data_from_db.title
            context['seo_description'] = seo_data_from_db.metadescription
            context['seo_propertytitle'] = seo_data_from_db.propertytitle
            context['seo_propertydescription'] = seo_data_from_db.propertydescription
            context['seo_head'] = seo_data_from_db.setting  # Если нужно добавлять дополнительные теги
        except Seo.DoesNotExist:
            # Если данных нет, используем значения по умолчанию
            context['seo_previev'] = None
            context['seo_title'] = 'Вход в систему - МойСайт'
            context['seo_description'] = 'Войдите в свою учетную запись для доступа к персональным данным'
            context['seo_propertytitle'] = 'og:title - Вход в систему'
            context['seo_propertydescription'] = 'og:description - Страница входа в личный кабинет'
            context['seo_head'] = '''
                <link rel="stylesheet" href="/static/css/login.css">
                <meta name="robots" content="noindex">
            '''

        return context

    def get_seo_context(self):
        """
        Просто возвращаем SEO данные для блоков
        """
        try:
            seo_data = Seo.objects.get(pagetype=5)
            return {
                'block_title': seo_data.title,
                'block_description': seo_data.metadescription,
                'block_propertytitle': seo_data.propertytitle,
                'block_propertydescription': seo_data.propertydescription,
                'block_propertyimage': seo_data.previev.url if seo_data.previev else '',
                'block_head': seo_data.setting or ''
            }
        except Seo.DoesNotExist:
            return {
                'block_title': 'Вход в систему',
                'block_description': 'Страница входа в аккаунт',
                'block_propertytitle': 'Вход в систему',
                'block_propertydescription': 'Страница входа',
                'block_propertyimage': '',
                'block_head': '<meta name="robots" content="noindex">'
            }

class BlogPaginationView(ListView):
    model = Blogs
    template_name = "blogs/partials/blog_items.html"  # Только элементы
    context_object_name = "blogs"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pagination_request'] = True
        return context

class BlogDetailView(CustomHtmxMixin, DetailView):
    model = Blogs
    template_name = "blogs/blog_detail.html"
    context_object_name = "blog"


"""Модерация"""



class ArticlesView(CustomHtmxMixin, ListView):
    model = Blogs
    template_name = 'moderation/blogs/articles.html'
    context_object_name = "blogs"
    paginate_by = 6

    def get_template_names(self):
        is_htmx = bool(self.request.META.get('HTTP_HX_REQUEST'))

        # Для пагинационных запросов возвращаем другой шаблон
        if is_htmx and self.request.GET.get('page'):
            return ["moderation/blogs/partials/blog_page_content.html"]

        return super().get_template_names()

    def render_to_response(self, context, **response_kwargs):
        # Для HTMX пагинации возвращаем только контент
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            return render(self.request, "moderation/blogs/partials/blog_page_content.html", context)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Для пагинационных запросов добавляем флаг
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            context['is_pagination_request'] = True

        # Параметры из базы данных для страницы "Авторизация" (pagetype=5)
        try:
            seo_data_from_db = Seo.objects.get(pagetype=1)

            # Передаем данные из модели в контекст
            context['seo_previev'] = seo_data_from_db.previev
            context['seo_title'] = seo_data_from_db.title
            context['seo_description'] = seo_data_from_db.metadescription
            context['seo_propertytitle'] = seo_data_from_db.propertytitle
            context['seo_propertydescription'] = seo_data_from_db.propertydescription
            context['seo_head'] = seo_data_from_db.setting  # Если нужно добавлять дополнительные теги
        except Seo.DoesNotExist:
            # Если данных нет, используем значения по умолчанию
            context['seo_previev'] = None
            context['seo_title'] = 'Вход в систему - МойСайт'
            context['seo_description'] = 'Войдите в свою учетную запись для доступа к персональным данным'
            context['seo_propertytitle'] = 'og:title - Вход в систему'
            context['seo_propertydescription'] = 'og:description - Страница входа в личный кабинет'
            context['seo_head'] = '''
                    <link rel="stylesheet" href="/static/css/login.css">
                    <meta name="robots" content="noindex">
                '''

        return context

    def get_seo_context(self):
        """
        Просто возвращаем SEO данные для блоков
        """
        try:
            seo_data = Seo.objects.get(pagetype=5)
            return {
                'block_title': seo_data.title,
                'block_description': seo_data.metadescription,
                'block_propertytitle': seo_data.propertytitle,
                'block_propertydescription': seo_data.propertydescription,
                'block_propertyimage': seo_data.previev.url if seo_data.previev else '',
                'block_head': seo_data.setting or ''
            }
        except Seo.DoesNotExist:
            return {
                'block_title': 'Вход в систему',
                'block_description': 'Страница входа в аккаунт',
                'block_propertytitle': 'Вход в систему',
                'block_propertydescription': 'Страница входа',
                'block_propertyimage': '',
                'block_head': '<meta name="robots" content="noindex">'
            }


class ArticlesPaginationView(ListView):
    model = Blogs
    template_name = "moderation/blogs/partials/blog_items.html"  # Только элементы
    context_object_name = "blogs"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pagination_request'] = True
        return context


class BlogFormView(LoginRequiredMixin, View):
    """Единый view для создания и редактирования блогов через попап"""

    def get(self, request, pk=None):
        """GET запрос - возвращает форму в offcanvas"""
        if pk:
            # Редактирование существующего блога
            blog = get_object_or_404(Blogs, pk=pk)
            form = BlogForm(instance=blog)
            title = f"Редактирование: {blog.name}"
        else:
            # Создание нового блога
            form = BlogForm()
            title = "Создание новой статьи"
            blog = None

        context = {
            'form': form,
            'title': title,
            'blog': blog,
        }

        # Для HTMX запросов возвращаем только форму
        if request.headers.get('HX-Request'):
            return render(request, 'moderation/blogs/partials/blog_form.html', context)

        # Для обычных запросов (если нужно)
        return render(request, 'moderation/blogs/blog_form_full.html', context)

    def post(self, request, pk=None):
        """POST запрос - сохраняет форму"""
        if pk:
            # Редактирование
            blog = get_object_or_404(Blogs, pk=pk)
            form = BlogForm(request.POST, request.FILES, instance=blog)
            action = 'updated'
        else:
            # Создание
            form = BlogForm(request.POST, request.FILES)
            action = 'created'

        if form.is_valid():
            blog = form.save(commit=False)

            # Если создаем новый блог, добавляем автора
            if not pk:
                blog.author = request.user

            blog.save()

            # Сохраняем ManyToMany поля
            form.save_m2m()

            # Для HTMX возвращаем обновленный элемент списка
            if request.headers.get('HX-Request'):
                # Получаем обновленный список блогов для замены
                blogs = Blogs.objects.all().order_by('-create')[:6]  # Последние 6

                response_html = f'''
                <div id="offcanvas-body-content" hx-swap-oob="true">
                    <div class="alert alert-success">Блог успешно {action}</div>
                </div>
                <div id="blog-items" hx-swap-oob="innerHTML">
                    {render_to_string('moderation/blogs/partials/blog_list.html', {'blogs': blogs, 'is_pagination_request': False}, request)}
                </div>
                <script>
                    var offcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('offcanvasRight'));
                    if (offcanvas) {{
                        setTimeout(() => {{
                            offcanvas.hide();
                        }}, 1500);
                    }}
                </script>
                '''

                return HttpResponse(response_html)

            return redirect('blogs:articles_list')

        # Если форма не валидна
        if request.headers.get('HX-Request'):
            context = {
                'form': form,
                'title': f"{'Редактирование' if pk else 'Создание'} статьи",
                'blog': blog if pk else None,
            }
            return render(request, 'moderation/blogs/partials/blog_form.html', context)

        return render(request, 'moderation/blogs/blog_form_full.html', {'form': form})


class CategoriesView(CustomHtmxMixin, ListView):
    model = CategorysBlogs
    template_name = 'moderation/blogs/categories.html'
    context_object_name = "categories"
    paginate_by = 6

    def get_template_names(self):
        is_htmx = bool(self.request.META.get('HTTP_HX_REQUEST'))

        # Для пагинационных запросов возвращаем другой шаблон
        if is_htmx and self.request.GET.get('page'):
            return ["moderation/blogs/partials/categories_page_content.html"]

        return super().get_template_names()

    def render_to_response(self, context, **response_kwargs):
        # Для HTMX пагинации возвращаем только контент
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            return render(self.request, "moderation/blogs/partials/categories_page_content.html", context)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Для пагинационных запросов добавляем флаг
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            context['is_pagination_request'] = True

        # Параметры из базы данных для страницы "Авторизация" (pagetype=5)
        try:
            seo_data_from_db = Seo.objects.get(pagetype=1)

            # Передаем данные из модели в контекст
            context['seo_previev'] = seo_data_from_db.previev
            context['seo_title'] = seo_data_from_db.title
            context['seo_description'] = seo_data_from_db.metadescription
            context['seo_propertytitle'] = seo_data_from_db.propertytitle
            context['seo_propertydescription'] = seo_data_from_db.propertydescription
            context['seo_head'] = seo_data_from_db.setting  # Если нужно добавлять дополнительные теги
        except Seo.DoesNotExist:
            # Если данных нет, используем значения по умолчанию
            context['seo_previev'] = None
            context['seo_title'] = 'Вход в систему - МойСайт'
            context['seo_description'] = 'Войдите в свою учетную запись для доступа к персональным данным'
            context['seo_propertytitle'] = 'og:title - Вход в систему'
            context['seo_propertydescription'] = 'og:description - Страница входа в личный кабинет'
            context['seo_head'] = '''
                        <link rel="stylesheet" href="/static/css/login.css">
                        <meta name="robots" content="noindex">
                    '''

        return context

    def get_seo_context(self):
        """
        Просто возвращаем SEO данные для блоков
        """
        try:
            seo_data = Seo.objects.get(pagetype=5)
            return {
                'block_title': seo_data.title,
                'block_description': seo_data.metadescription,
                'block_propertytitle': seo_data.propertytitle,
                'block_propertydescription': seo_data.propertydescription,
                'block_propertyimage': seo_data.previev.url if seo_data.previev else '',
                'block_head': seo_data.setting or ''
            }
        except Seo.DoesNotExist:
            return {
                'block_title': 'Вход в систему',
                'block_description': 'Страница входа в аккаунт',
                'block_propertytitle': 'Вход в систему',
                'block_propertydescription': 'Страница входа',
                'block_propertyimage': '',
                'block_head': '<meta name="robots" content="noindex">'
            }

class CategoriesPaginationView(ListView):
    model = CategorysBlogs
    template_name = "moderation/blogs/partials/categories_items.html"  # Только элементы
    context_object_name = "categories"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pagination_request'] = True
        return context

class CategoriesFormView(LoginRequiredMixin, View):
    """Единый view для создания и редактирования блогов через попап"""

    def get(self, request, pk=None):
        """GET запрос - возвращает форму в offcanvas"""
        if pk:
            # Редактирование существующего блога
            categories = get_object_or_404(CategorysBlogs, pk=pk)
            form = CategoriesForm(instance=categories)
            title = f"Редактирование: {categories.name}"
        else:
            # Создание нового блога
            form = CategoriesForm()
            title = "Создание новой категории"
            categories = None

        context = {
            'form': form,
            'title': title,
            'categories': categories,
        }

        # Для HTMX запросов возвращаем только форму
        if request.headers.get('HX-Request'):
            return render(request, 'moderation/blogs/partials/categories_form.html', context)

        # Для обычных запросов (если нужно)
        return render(request, 'moderation/blogs/categories_form_full.html', context)

    def post(self, request, pk=None):
        """POST запрос - сохраняет форму"""
        if pk:
            # Редактирование
            categories = get_object_or_404(CategorysBlogs, pk=pk)
            form = CategoriesForm(request.POST, request.FILES, instance=categories)
            action = 'updated'
        else:
            # Создание
            form = CategoriesForm(request.POST, request.FILES)
            action = 'created'

        if form.is_valid():
            categories = form.save(commit=False)

            # Для HTMX возвращаем обновленный элемент списка
            if request.headers.get('HX-Request'):
                # Получаем обновленный список блогов для замены
                categories = CategorysBlogs.objects.all().order_by('-create')[:6]  # Последние 6

                response_html = f'''
                <div id="offcanvas-body-content" hx-swap-oob="true">
                    <div class="alert alert-success">Блог успешно {action}</div>
                </div>
                <div id="blog-items" hx-swap-oob="innerHTML">
                    {render_to_string('moderation/blogs/partials/categories_list.html', {'categories': categories, 'is_pagination_request': False}, request)}
                </div>
                <script>
                    var offcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('offcanvasRight'));
                    if (offcanvas) {{
                        setTimeout(() => {{
                            offcanvas.hide();
                        }}, 1500);
                    }}
                </script>
                '''

                return HttpResponse(response_html)

            return redirect('blogs:categories_list')

        # Если форма не валидна
        if request.headers.get('HX-Request'):
            context = {
                'form': form,
                'title': f"{'Редактирование' if pk else 'Создание'} статьи",
                'categories': categories if pk else None,
            }
            return render(request, 'moderation/blogs/partials/categories_form.html', context)

        return render(request, 'moderation/blogs/categories_form_full.html', {'form': form})


class TagsView(CustomHtmxMixin, View):
    template_name = 'moderation/blogs/tags.html'

    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Теги',
        }
        return render(request, self.template_name, context)


class LikesView(CustomHtmxMixin, View):
    template_name = 'moderation/blogs/likes.html'

    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Лайки',
        }
        return render(request, self.template_name, context)


class CommentsView(CustomHtmxMixin, View):
    template_name = 'moderation/blogs/comments.html'

    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Комментарии',
        }
        return render(request, self.template_name, context)


class ComplaintsView(CustomHtmxMixin, View):
    template_name = 'moderation/blogs/complaints.html'

    def get(self, request, *args, **kwargs):
        context = {
            'title': 'Жалобы',
        }
        return render(request, self.template_name, context)

