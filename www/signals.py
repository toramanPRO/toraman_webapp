from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def new_user_registration_callback(sender, instance, created, **kwargs):
    if (created and hasattr(settings, 'USERS_CAN_ADD_PROJECTS_BY_DEFAULT')
    and settings.USERS_CAN_ADD_PROJECTS_BY_DEFAULT):
        user = instance
        user.user_permissions.add(Permission.objects.get(name='Can add project'))
        user.user_permissions.add(Permission.objects.get(name='Can add Translation Memory'))
