from django import forms
from django.core.validators import FileExtensionValidator
from multiupload.fields import MultiFileField


from .models import TicketComment,  Ticket


class TicketCommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Написать комментарий'}))
    files = MultiFileField(required=False, max_num=10, attrs={'class': 'form-control cursor-pointer form-file'})

    class Meta:
        model = TicketComment
        fields = ['content', 'files']


    def clean_files(self):
        files = self.cleaned_data.get('files')
        if files:
            for file in files:
                try:
                    FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])(file)
                except forms.ValidationError:
                    self.add_error('files', f"Файл '{file.name}' имеет недопустимое расширение.")
        return files




class TicketWithCommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Написать комментарий'}))
    files = MultiFileField(required=False, max_num=10, attrs={'class': 'form-control cursor-pointer form-file'})

    class Meta:
        model = Ticket
        fields = ['themas']
        widgets = {
            'themas': forms.TextInput(attrs={'class': 'form-control input-default', 'placeholder': 'Тема'}),
        }

    def clean_files(self):
        files = self.cleaned_data.get('files')
        if files:
            for file in files:
                try:
                    FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])(file)
                except forms.ValidationError:
                    self.add_error('files', f"Файл '{file.name}' имеет недопустимое расширение.")
        return files