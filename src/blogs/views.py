from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import render, get_object_or_404
from moderation.models import Collaborations
from webmain.forms import SubscriptionForm
from blogs.models import TagsBlogs,  CategorysBlogs, Blogs
from django.utils.text import slugify
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from useraccount.models import Profile
from webmain.models import Seo


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


class BlogCreateUpdateView(CustomHtmxMixin, TemplateView):
    template_name = 'blogs/blog_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        users = Profile.objects.all()

        if pk:
            blog = get_object_or_404(Blogs, pk=pk)
            context.update({
                'blog': blog,
                'categories': CategorysBlogs.objects.all(),
                'tags': TagsBlogs.objects.all(),
                'users': users
            })
        else:
            context.update({
                'categories': CategorysBlogs.objects.all(),
                'tags': TagsBlogs.objects.all(),
                'users': users
            })

        return context

    def get(self, request, *args, **kwargs):
        # TemplateView автоматически использует get_template_names() из миксина
        return super().get(request, *args, **kwargs)

    def post(self, request, pk=None):
        # Получаем данные из формы
        name = request.POST.get('name')
        resource = request.POST.get('resource', '')
        category_ids = request.POST.getlist('category')
        tag_ids = request.POST.getlist('tags')
        description = request.POST.get('description', '')
        title = request.POST.get('title', '')
        metadescription = request.POST.get('metadescription', '')
        propertytitle = request.POST.get('propertytitle', '')
        propertydescription = request.POST.get('propertydescription', '')
        publishet = request.POST.get('publishet', 'off') == 'on'

        previev = request.FILES.get('previev', None)
        cover = request.FILES.get('cover', None)
        image = request.FILES.get('image', None)

        # Получаем выбранного автора
        author_id = request.POST.get('author')
        author = get_object_or_404(Profile, pk=author_id)

        # Генерация slug
        slug = slugify(name)  # Применяем slugify для преобразования в sluggable строку

        # Если редактируем блог, то slug не меняем
        if pk:
            blog = get_object_or_404(Blogs, pk=pk)
            # Если slug не изменяется, оставляем старый
            slug = blog.slug
        else:
            # Генерация уникального slug для нового блога
            count = 1
            original_slug = slug
            while Blogs.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{count}"
                count += 1

        # Если редактируем существующий блог
        if pk:
            blog = get_object_or_404(Blogs, pk=pk)
            blog.name = name
            blog.resource = resource
            blog.description = description
            blog.title = title
            blog.metadescription = metadescription
            blog.propertytitle = propertytitle
            blog.propertydescription = propertydescription
            blog.slug = slug  # Оставляем существующий slug при редактировании
            blog.publishet = publishet
            blog.author = author

            # Обработка файлов
            if previev:
                blog.previev = previev
            if cover:
                blog.cover = cover
            if image:
                blog.image = image

            # Обновляем категории и теги
            blog.category.set(CategorysBlogs.objects.filter(id__in=category_ids))
            blog.tags.set(TagsBlogs.objects.filter(id__in=tag_ids))

            blog.save()

            if 'HX-Request' in request.META:
                return JsonResponse({'success': True, 'message': 'Blog updated successfully!'})
            else:
                return render(request, self.template_name, {'blog': blog, 'categories': CategorysBlogs.objects.all(), 'tags': TagsBlogs.objects.all(), 'users': Profile.objects.all()})

        # Если создаем новый блог (pk не передан)
        else:
            try:
                blog = Blogs.objects.create(
                    author=author,
                    name=name,
                    resource=resource,
                    description=description,
                    title=title,
                    metadescription=metadescription,
                    propertytitle=propertytitle,
                    propertydescription=propertydescription,
                    slug=slug,  # Используем уникальный slug
                    publishet=publishet,
                )

                # Обработка файлов
                if previev:
                    blog.previev = previev
                if cover:
                    blog.cover = cover
                if image:
                    blog.image = image

                # Сохранение категорий и тегов
                blog.category.set(CategorysBlogs.objects.filter(id__in=category_ids))
                blog.tags.set(TagsBlogs.objects.filter(id__in=tag_ids))

                blog.save()

                if 'HX-Request' in request.META:
                    return JsonResponse({'success': True, 'message': 'Blog created successfully!'})

                return render(request, self.template_name, {'blog': blog, 'categories': CategorysBlogs.objects.all(), 'tags': TagsBlogs.objects.all(), 'users': Profile.objects.all()})

            except ValidationError as e:
                if 'HX-Request' in request.META:
                    return JsonResponse({'success': False, 'error': str(e)})

                return render(request, self.template_name, {'error': str(e)})
