from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.urls import reverse

import os
# Create your models here.


class Project(models.Model):
    title = models.CharField(max_length=60)
    source_language = models.CharField(max_length=60)
    target_language = models.CharField(max_length=60)
    source_files = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('project', args=[str(self.user.id), str(self.id)])

    def get_project_path(self):
        return os.path.join(settings.USER_PROJECT_ROOT, str(self.user.id), str(self.id))

    def get_source_dir(self):
        return os.path.join(settings.USER_PROJECT_ROOT, str(self.user.id), str(self.id), self.source_language)

    def get_target_dir(self):
        return os.path.join(settings.USER_PROJECT_ROOT, str(self.user.id), str(self.id), self.target_language)
