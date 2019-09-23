from django.urls import path

from . import views

urlpatterns = [
    path('u/<str:username>', views.user_dashboard, name='user-page'),
    path('login', views.log_in, name='login'),
    path('logout', views.log_out, name='logout'),
    path('register', views.register, name='register'),
    path('reset-password', views.reset_password, name='password-reset'),
    path('set-password=<str:token>', views.set_password, name='set-password'),
    path('', views.homepage, name='homepage')
]
