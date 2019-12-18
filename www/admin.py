from django.contrib import admin

from .models import PasswordResetToken

# Register your models here.

admin.site.register(PasswordResetToken)
