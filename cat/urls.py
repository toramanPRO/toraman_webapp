from django.urls import path

from . import views

urlpatterns = [
    path('project/<int:user_id>/<int:project_id>/<str:source_file>', views.bilingual_file, name='bilingual-file'),
    path('project/<int:user_id>/<int:project_id>/download/<str:source_file>', views.download_target_file, name='download-target-file'),
    path('new-project', views.new_project, name='new-project'),
    path('project/<int:user_id>/<int:project_id>', views.project, name='project'),
]
