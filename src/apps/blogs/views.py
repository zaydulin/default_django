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
from apps.webmain.views import CustomHtmxSiteMixin

from .forms import BlogForm, CategoriesForm, TagsForm

"""Новости"""


class BlogView(CustomHtmxSiteMixin, ListView):
    model = Blogs
    template_name = "active/blogs/blogs.html"
    context_object_name = "blogs"
    paginate_by = 6

    def get_template_names(self):
        is_htmx = bool(self.request.META.get('HTTP_HX_REQUEST'))

        # Для пагинационных запросов возвращаем другой шаблон
        if is_htmx and self.request.GET.get('page'):
            return ["active/blogs/partials/blog_page_content.html"]

        return super().get_template_names()

    def render_to_response(self, context, **response_kwargs):
        # Для HTMX пагинации возвращаем только контент
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            return render(self.request, "active/blogs/partials/blog_page_content.html", context)
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
    template_name = "active/blogs/partials/blog_items.html"  # Только элементы
    context_object_name = "blogs"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pagination_request'] = True
        return context

class BlogDetailView(CustomHtmxSiteMixin, DetailView):
    model = Blogs
    template_name = "active/blogs/blog_detail.html"
    context_object_name = "blog"


"""Модерация"""



class ArticlesView(CustomHtmxMixin, ListView):
    model = Blogs
    template_name = 'moderation/blogs/articles.html'
    context_object_name = "blogs"
    paginate_by = 6

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["moderation/blogs/partials/articles_rows.html"]
        return ["moderation/blogs/articles.html"]

    def render_to_response(self, context, **response_kwargs):
        # Для HTMX пагинации возвращаем только контент
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            return render(self.request, "moderation/blogs/partials/articles_rows.html", context)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pagination_request'] = bool(self.request.headers.get('HX-Request') and self.request.GET.get('page'))

        # SEO данные
        try:
            seo_data_from_db = Seo.objects.get(pagetype=1)
            context['seo_previev'] = seo_data_from_db.previev
            context['seo_title'] = seo_data_from_db.title
            context['seo_description'] = seo_data_from_db.metadescription
            context['seo_propertytitle'] = seo_data_from_db.propertytitle
            context['seo_propertydescription'] = seo_data_from_db.propertydescription
            context['seo_head'] = seo_data_from_db.setting
        except Seo.DoesNotExist:
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

class ArticlesPaginationView(ListView):
    model = Blogs
    template_name = "moderation/blogs/partials/pagination_articles_response.html"
    context_object_name = "blogs"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pagination_request'] = True
        return context


class BlogFormView(LoginRequiredMixin, View):
    """Единый view для создания и редактирования блогов"""

    def get(self, request, pk=None):
        """GET запрос - возвращает форму"""
        if pk:
            blog = get_object_or_404(Blogs, pk=pk)
            form = BlogForm(instance=blog)
            title = f"Редактирование: {blog.name}"
            print(f"Editing blog: {blog.id}, slug: {blog.slug}")
            print(f"Blog data: name={blog.name}, description={blog.description[:50]}...")
        else:
            form = BlogForm()
            title = "Создание новой статьи"

        context = {
            'form': form,
            'title': title,
        }

        return render(request, 'moderation/blogs/partials/articles_form.html', context)

    def post(self, request, pk=None):
        """POST запрос - сохраняет форму"""
        print(f"POST request data: {request.POST}")
        print(f"FILES: {request.FILES}")

        if pk:
            blog = get_object_or_404(Blogs, pk=pk)
            form = BlogForm(request.POST, request.FILES, instance=blog)
            print(f"Editing blog ID: {pk}, current data: {blog.name}")
        else:
            form = BlogForm(request.POST, request.FILES)
            print("Creating new blog")

        if form.is_valid():
            print("Form is valid, saving...")
            blog = form.save(commit=False)

            if not pk:
                blog.author = request.user
                print(f"Setting author: {request.user}")

            blog.save()
            form.save_m2m()  # Сохраняем ManyToMany поля (category, tags)

            print(f"Blog saved successfully! ID: {blog.id}, Name: {blog.name}")

            if request.headers.get('HX-Request'):
                # Получаем обновленный список (первая страница)
                blogs = Blogs.objects.all().order_by('-create')
                paginator = Paginator(blogs, 6)
                page_obj = paginator.get_page(1)

                # Рендерим строки через шаблон
                rows_html = render_to_string(
                    'moderation/blogs/partials/articles_rows.html',
                    {'blogs': page_obj},
                    request
                )

                # Рендерим пагинацию
                pagination_html = render_to_string(
                    'moderation/blogs/partials/articles_pagination.html',
                    {'page_obj': page_obj},
                    request
                )

                # Формируем ответ
                response = HttpResponse()

                # Обновляем tbody
                response.write(f'''
                <tbody id="articles-items" hx-swap-oob="outerHTML">
                    {rows_html}
                </tbody>
                ''')

                # Обновляем пагинацию
                response.write(f'''
                <div id="pagination-container" hx-swap-oob="outerHTML">
                    {pagination_html}
                </div>
                ''')

                # Сообщение об успехе
                response.write(f'''
                <div id="offcanvas-body-content" hx-swap-oob="innerHTML">
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        <strong>Успешно!</strong> Статья "{blog.name}" успешно сохранена
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                    <script>
                        (function() {{
                            setTimeout(function() {{
                                var offcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('offcanvasRight'));
                                if (offcanvas) {{
                                    offcanvas.hide();
                                }}
                                setTimeout(function() {{
                                    document.getElementById('offcanvas-body-content').innerHTML = '';
                                }}, 300);
                            }}, 1500);
                        }})();
                    </script>
                </div>
                ''')

                return response

            return redirect('blogs:articles_list')

        else:
            print(f"Form is invalid. Errors: {form.errors}")
            print(f"Form data: {form.data}")

        # Если форма не валидна
        if request.headers.get('HX-Request'):
            context = {
                'form': form,
                'title': f"{'Редактирование' if pk else 'Создание'} статьи",
                'errors': form.errors,
            }
            return render(request, 'moderation/blogs/partials/articles_form.html', context)

        return render(request, 'moderation/blogs/partials/articles_form.html', {'form': form})

class CategoriesView(CustomHtmxMixin, ListView):
    model = CategorysBlogs
    template_name = 'moderation/blogs/categories.html'
    context_object_name = "categories"
    paginate_by = 6

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ["moderation/blogs/partials/categories_rows.html"]
        return ["moderation/blogs/categories.html"]



    def render_to_response(self, context, **response_kwargs):
        # Для HTMX пагинации возвращаем только контент
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            return render(self.request, "moderation/blogs/partials/categories_page_content.html", context)
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['is_pagination_request'] = bool(self.request.headers.get('HX-Request') and self.request.GET.get('page'))

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
    template_name = "moderation/blogs/partials/pagination_response.html"  # Новый шаблон
    context_object_name = "categories"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pagination_request'] = True
        return context

class CategoriesFormView(LoginRequiredMixin, View):
    """Единый view для создания и редактирования категорий"""

    def get(self, request, pk=None):
        """GET запрос - возвращает форму"""
        if pk:
            category = get_object_or_404(CategorysBlogs, pk=pk)
            form = CategoriesForm(instance=category)
            title = f"Редактирование: {category.name}"
        else:
            form = CategoriesForm()
            title = "Создание новой категории"

        context = {
            'form': form,
            'title': title,
        }

        return render(request, 'moderation/blogs/partials/categories_form.html', context)

    def post(self, request, pk=None):
        """POST запрос - сохраняет форму"""
        if pk:
            category = get_object_or_404(CategorysBlogs, pk=pk)
            form = CategoriesForm(request.POST, request.FILES, instance=category)
        else:
            form = CategoriesForm(request.POST, request.FILES)

        if form.is_valid():
            category = form.save()

            if request.headers.get('HX-Request'):
                # Получаем обновленный список категорий (первая страница)
                categories = CategorysBlogs.objects.all().order_by('-create')
                paginator = Paginator(categories, 6)
                page_obj = paginator.get_page(1)

                # Рендерим строки через шаблон
                rows_html = render_to_string(
                    'moderation/blogs/partials/categories_rows.html',
                    {'categories': page_obj},
                    request
                )

                # Рендерим пагинацию
                pagination_html = render_to_string(
                    'moderation/blogs/partials/categories_pagination.html',
                    {'page_obj': page_obj},
                    request
                )

                # Формируем ответ
                response = HttpResponse()

                # Обновляем tbody
                response.write(f'''
                <tbody id="categories-items" hx-swap-oob="outerHTML">
                    {rows_html}
                </tbody>
                ''')

                # Обновляем пагинацию
                response.write(f'''
                <div id="pagination-container" hx-swap-oob="outerHTML">
                    {pagination_html}
                </div>
                ''')

                # Сообщение об успехе
                response.write(f'''
                <div id="offcanvas-body-content" hx-swap-oob="innerHTML">
                    <div class="alert alert-success">
                        Категория "{category.name}" успешно сохранена
                    </div>
                    <script>
                        setTimeout(function() {{
                            var offcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('offcanvasRight'));
                            if (offcanvas) {{
                                offcanvas.hide();
                            }}
                        }}, 1500);
                    </script>
                </div>
                ''')

                return response

            return redirect('blogs:categories_list')

        # Если форма не валидна
        if request.headers.get('HX-Request'):
            context = {
                'form': form,
                'title': f"{'Редактирование' if pk else 'Создание'} категории",
            }
            return render(request, 'moderation/blogs/partials/categories_form.html', context)

        return render(request, 'moderation/blogs/partials/categories_form.html', {'form': form})

class TagsView(CustomHtmxMixin, ListView):
    model = TagsBlogs
    template_name = 'moderation/blogs/tags.html'
    context_object_name = "tags"
    paginate_by = 6

    def get_template_names(self):
        is_htmx = bool(self.request.META.get('HTTP_HX_REQUEST'))

        # Для пагинационных запросов возвращаем другой шаблон
        if is_htmx and self.request.GET.get('page'):
            return ["moderation/blogs/partials/tags_page_content.html"]

        return super().get_template_names()

    def render_to_response(self, context, **response_kwargs):
        # Для HTMX пагинации возвращаем только контент
        if self.request.headers.get("HX-Request") and self.request.GET.get('page'):
            return render(self.request, "moderation/blogs/partials/tags_page_content.html", context)
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

class TagsPaginationView(ListView):
    model = TagsBlogs
    template_name = "moderation/blogs/partials/tags_items.html"  # Только элементы
    context_object_name = "tags"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pagination_request'] = True
        return context

class TagsFormView(LoginRequiredMixin, View):
    """Единый view для создания и редактирования блогов через попап"""

    def get(self, request, pk=None):
        """GET запрос - возвращает форму в offcanvas"""
        if pk:
            # Редактирование существующего блога
            tags = get_object_or_404(TagsBlogs, pk=pk)
            form = TagsForm(instance=tags)
            title = f"Редактирование: {tags.name}"
        else:
            # Создание нового блога
            form = TagsForm()
            title = "Создание новой категории"
            tags = None

        context = {
            'form': form,
            'title': title,
            'tags': tags,
        }

        # Для HTMX запросов возвращаем только форму
        if request.headers.get('HX-Request'):
            return render(request, 'moderation/blogs/partials/tags_form.html', context)

        # Для обычных запросов (если нужно)
        return render(request, 'moderation/blogs/tags_form_full.html', context)

    def post(self, request, pk=None):
        """POST запрос - сохраняет форму"""
        if pk:
            # Редактирование
            tags = get_object_or_404(TagsBlogs, pk=pk)
            form = TagsForm(request.POST, request.FILES, instance=tags)
            action = 'updated'
        else:
            # Создание
            form = TagsForm(request.POST, request.FILES)
            action = 'created'

        if form.is_valid():
            tags = form.save(commit=False)
            tags.save()

            # Для HTMX возвращаем обновленный элемент списка
            if request.headers.get('HX-Request'):
                # Получаем обновленный список блогов для замены
                tags = TagsBlogs.objects.all().order_by('-create')[:6]  # Последние 6

                response_html = f'''
                <div id="offcanvas-body-content" hx-swap-oob="true">
                    <div class="alert alert-success">Тег успешно {action}</div>
                </div>
                <div id="blog-items" hx-swap-oob="innerHTML">
                    {render_to_string('moderation/blogs/partials/tags_list.html', {'tags': tags, 'is_pagination_request': False}, request)}
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

            return redirect('blogs:tags_list')

        # Если форма не валидна
        if request.headers.get('HX-Request'):
            context = {
                'form': form,
                'title': f"{'Редактирование' if pk else 'Создание'} тега",
                'tags': tags if pk else None,
            }
            return render(request, 'moderation/blogs/partials/tags_form.html', context)

        return render(request, 'moderation/blogs/tags_form_full.html', {'form': form})




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

