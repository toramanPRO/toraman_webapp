from django import forms
from .models import Project, TranslationMemory

class AssignProjectToTranslatorForm(forms.Form):
    file_ids = forms.CharField(label='File Indices',
                                widget=forms.TextInput(attrs={'placeholder': '1;2;3;4'}),
                                required=True)
    translator = forms.CharField(label='Translator\'s Username',
                                widget=forms.TextInput(attrs={'placeholder': 'Translator\'s Username'}),
                                required=True)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'source_language', 'target_language')

    source_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    translation_memory = forms.CharField(widget=forms.Select(attrs={'required': True}))


class TranslationMemoryForm(forms.ModelForm):
    class Meta:
        model = TranslationMemory
        fields = ('title', 'source_language', 'target_language')
