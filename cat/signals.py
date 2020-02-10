from django.db.models.signals import pre_delete
from django.dispatch import receiver

from cat.models import Project, ProjectFile, TranslationMemory

import os

@receiver(pre_delete, sender=Project)
def pre_delete_project_cleanup(sender, instance, **kwargs):
    user_project = instance
    user_project_path = user_project.get_project_path()

    for dirpath, dirnames, filenames in os.walk(user_project_path, topdown=False):
        for filename in filenames:
            os.remove(os.path.join(dirpath, filename))
        os.rmdir(dirpath)

@receiver(pre_delete, sender=ProjectFile)
def pre_delete_project_file_cleanup(sender, instance, **kwargs):
    user_file = instance

    if os.path.exists(user_file.source_file_path):
        os.remove(user_file.source_file_path)

    if os.path.exists(user_file.bilingual_file_path):
        os.remove(user_file.bilingual_file_path)

    target_file_path = os.path.join(user_file.project.get_target_dir(),
                                    user_file.title)

    if os.path.exists(target_file_path):
        os.remove(target_file_path)

@receiver(pre_delete, sender=TranslationMemory)
def pre_delete_tm_cleanup(sender, instance, **kwargs):
    user_translation_memory = instance
    user_tm_path = user_translation_memory.get_tm_path()

    os.remove(user_tm_path)
    os.rmdir(os.path.dirname(user_tm_path))
