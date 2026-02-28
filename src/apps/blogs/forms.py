from django import forms
from .models import Blogs, CategorysBlogs, TagsBlogs
from ckeditor.widgets import CKEditorWidget


class BlogForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Blogs
        fields = [
            'name', 'description', 'category', 'tags', 'resource',
            'previev', 'cover', 'image', 'publishet',
            'title', 'metadescription', 'propertytitle', 'propertydescription', 'slug'
        ]
        widgets = {
            'category': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'resource': forms.TextInput(attrs={'class': 'form-control'}),
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
        self.fields['category'].queryset = CategorysBlogs.objects.all()
        self.fields['tags'].queryset = TagsBlogs.objects.all()

        # Добавляем атрибуты для файловых полей
        self.fields['previev'].widget.attrs.update({'class': 'form-control'})
        self.fields['cover'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

class CategoriesForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Blogs
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