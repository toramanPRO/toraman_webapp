from django.urls import path

from . import views

urlpatterns = [
    path('project/<int:user_id>/<int:project_id>/<int:file_id>', views.bilingual_file, name='bilingual-file'),
    path('project/<int:user_id>/<int:project_id>/download/<int:file_id>', views.download_target_file, name='download-target-file'),
    path('new-project', views.new_project, name='new-project'),
    path('project/<int:user_id>/<int:project_id>', views.project, name='project'),
    path('translation-memory/<int:user_id>/<int:tm_id>', views.translation_memory, name='translation-memory'),
    path('new-translation-memory', views.new_translation_memory, name='new-translation-memory'),
    path('translation-memory-query', views.translation_memory_query, name='translation-memory-query'),
]
