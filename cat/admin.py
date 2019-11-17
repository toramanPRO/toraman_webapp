from django.contrib import admin

from .models import Project, TranslationMemory
# Register your models here.

admin.site.register(Project)

admin.site.register(TranslationMemory)
