from django.db.models.signals import pre_delete
from django.dispatch import receiver

from cat.models import Project, TranslationMemory

import os

@receiver(pre_delete, sender=Project)
def pre_delete_project_cleanup(sender, instance, **kwargs):
    user_project = instance
    user_project_path = user_project.get_project_path()

    for dirpath, dirnames, filenames in os.walk(user_project_path, topdown=False):
        for filename in filenames:
            os.remove(os.path.join(dirpath, filename))
        os.rmdir(dirpath)

@receiver(pre_delete, sender=TranslationMemory)
def pre_delete_tm_cleanup(sender, instance, **kwargs):
    user_translation_memory = instance
    user_tm_path = user_translation_memory.get_tm_path()

    os.remove(user_tm_path)
    os.rmdir(os.path.dirname(user_tm_path))
