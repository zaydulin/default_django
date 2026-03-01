from django import forms
from .models import Blogs, CategorysBlogs, TagsBlogs
from ckeditor.widgets import CKEditorWidget


# forms.py
class BlogForm(forms.ModelForm):
    class Meta:
        model = Blogs
        fields = ['name', 'slug', 'description', 'publishet', 'category', 'tags',
                 'image', 'cover', 'previev', 'resource', 'title', 'metadescription',
                 'propertytitle', 'propertydescription']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),  # RichTextField в админке, но для формы Textarea
            'resource': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'metadescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'propertytitle': forms.TextInput(attrs={'class': 'form-control'}),
            'propertydescription': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'previev': forms.FileInput(attrs={'class': 'form-control'}),
            'publishet': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].help_text = 'Уникальный идентификатор для URL. Должен быть уникальным.'
        # Делаем некоторые поля необязательными
        self.fields['resource'].required = False
        self.fields['title'].required = False
        self.fields['metadescription'].required = False
        self.fields['propertytitle'].required = False
        self.fields['propertydescription'].required = False
        self.fields['cover'].required = False
        self.fields['previev'].required = False

    def clean_slug(self):
        """Валидация slug с исключением текущего объекта при редактировании"""
        slug = self.cleaned_data.get('slug')

        if not slug:
            raise forms.ValidationError("Slug не может быть пустым")

        instance = getattr(self, 'instance', None)
        queryset = Blogs.objects.filter(slug=slug)

        if instance and instance.pk:
            queryset = queryset.exclude(pk=instance.pk)

        if queryset.exists():
            raise forms.ValidationError("Статья с таким Slug уже существует")

        return slug
class CategoriesForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = CategorysBlogs
        fields = [
            'name', 'description',
            'previev', 'cover', 'image', 'publishet',
            'title', 'metadescription', 'propertytitle', 'propertydescription', 'slug'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'metadescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'propertytitle': forms.TextInput(attrs={'class': 'form-control'}),
            'propertydescription': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'publishet': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем атрибуты для файловых полей
        self.fields['previev'].widget.attrs.update({'class': 'form-control'})
        self.fields['cover'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

class TagsForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = TagsBlogs
        fields = [
            'name', 'description',
            'previev', 'cover', 'image', 'publishet',
            'title', 'metadescription', 'propertytitle', 'propertydescription', 'slug'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'metadescription': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'propertytitle': forms.TextInput(attrs={'class': 'form-control'}),
            'propertydescription': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'publishet': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем атрибуты для файловых полей
        self.fields['previev'].widget.attrs.update({'class': 'form-control'})
        self.fields['cover'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})