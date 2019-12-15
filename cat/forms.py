from django import forms
from .models import Project, TranslationMemory

class AssignProjectToTranslatorForm(forms.Form):
    translator = forms.CharField(label='Translator\'s Username', required=True)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'source_language', 'target_language')

    source_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    translation_memory = forms.CharField(widget=forms.Select)


class TranslationMemoryForm(forms.ModelForm):
    class Meta:
        model = TranslationMemory
        fields = ('title', 'source_language', 'target_language')
