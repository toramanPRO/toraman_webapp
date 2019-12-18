from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from cat.models import Project, TranslationMemory

from .forms import PasswordResetForm, SetPasswordForm, UserForm
from .models import PasswordResetToken

import random
import string
# Create your views here.

def homepage(request):
    context = {
        'version_number': settings.VERSION
    }
    return render(request, 'homepage.html', context)

def log_in(request):
    form = AuthenticationForm(data=request.POST or None)
    context = {
        'form': form,
    }

    if 'next' in request.GET:
        context['next'] = request.GET['next']

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if 'next' in context:
                    return HttpResponseRedirect(context['next'])
                else:
                    return redirect('homepage')

    return render(request, 'login.html', context)

@login_required()
def log_out(request):
    logout(request)
    return redirect('homepage')

def register(request):
    form = UserForm(data=request.POST or None)
    context = {
        'form': form,
    }

    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()

            return redirect('homepage')

    return render(request, 'register.html', context)

def reset_password(request):
    form = PasswordResetForm(data=request.POST or None)
    context = {
        'form': form,
    }

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']

            user = User.objects.filter(email=email)

            if len(user) == 1:
                user = user[0]

                token = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(64))
                while len(PasswordResetToken.objects.filter(token=token)) > 0:
                    token = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(64))

                for password_reset_token in PasswordResetToken.objects.filter(user=user):
                    password_reset_token.delete()

                password_reset_token = PasswordResetToken()
                password_reset_token.token = token
                password_reset_token.pin = random.randint(1000, 9999)
                password_reset_token.user = user
                password_reset_token.save()

                password_reset_url = settings.ALLOWED_HOSTS[0] + password_reset_token.get_absolute_url()

                context['email_sent'] = True
                context['password_reset_pin'] = password_reset_token.pin
                context['password_reset_url'] = password_reset_url

                plaintext_email = render_to_string('email/password-reset.txt', context)
                html_email = render_to_string('email/password-reset.html', context)

                send_mail(
                    'Password reset e-mail for {0}'.format(password_reset_token.user.username),
                    plaintext_email,
                    settings.DEFAULT_FROM_EMAIL,
                    [password_reset_token.user.email],
                    html_message=html_email,
                    fail_silently=False,
                )

            else:
                context['errors'] = ['No user associated with that e-mail address.']

            return render(request, 'password-reset.html', context)

    else:

        return render(request, 'password-reset.html', context)

def set_password(request, token):
    password_reset_token = PasswordResetToken.objects.get(token=token)

    form = SetPasswordForm(data=request.POST or None)

    context = {'form': form}

    if request.method == 'POST':
        if form.is_valid():
            if form.cleaned_data['password1'] == form.cleaned_data['password2']:
                if form.cleaned_data['pin'] == password_reset_token.pin:
                    user = User.objects.get(username=password_reset_token.user.username)
                    user.set_password(form.cleaned_data['password1'])
                    user.save()

                    password_reset_token.delete()

                    return redirect('login')
                else:
                    context['errors'] = ['Pin is incorrect.']
            else:
                context['errors'] = ['Passwords do not match.']

    return render(request, 'set-password.html', context)

def user_dashboard(request, username):
    if username == request.user.username:
        context = {
            'user_can_add_projects': request.user.has_perm('cat.add_project'),
            'user_can_add_tms': request.user.has_perm('cat.add_translationmemory'),
            'user_projects': Project.objects.filter(Q(user=request.user)|Q(translator=request.user)).order_by('-id'),
            'user_tms': TranslationMemory.objects.filter(user=request.user).order_by('-id'),
        }
        response = render(request, 'user-dashboard.html', context)
    else:
        response = HttpResponse('The user either does not exist or is not public.')
        response.status_code = 404

    return response
