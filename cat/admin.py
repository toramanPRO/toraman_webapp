from django.contrib import admin

from .models import Project, TranslationMemory
# Register your models here.

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'source_language', 'target_language', 'user')

admin.site.register(Project, ProjectAdmin)

class TranslationMemoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'source_language', 'target_language', 'user')

admin.site.register(TranslationMemory, TranslationMemoryAdmin)
