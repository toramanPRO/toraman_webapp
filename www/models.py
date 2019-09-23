from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.

class PasswordResetToken(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    pin = models.IntegerField()
    token = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('set-password', args=[self.token])
