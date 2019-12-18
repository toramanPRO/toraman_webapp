from django.http import FileResponse, HttpResponse
from django.shortcuts import render, reverse, redirect

from .models import Project

def permission_required(permission):
    def wrapper(view_func):
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(reverse('login')+'?next='+request.get_full_path())
            else:
                if request.user.has_perm(permission):
                    return view_func(request, *args, **kwargs)
                else:
                    context = {
                        'status_code': '403',
                        'error_message': 'Permission denied.'
                    }
                    return render(request, 'error.html', context, status=403)
        return wrapped
    return wrapper

def project_access(view_func):
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login')+'?next='+request.get_full_path())
        
        try:
            user_project = Project.objects.get(id=kwargs['project_id'])
        except Project.DoesNotExist:
            context = {
                'status_code': 404,
                'error_message': 'Project does not exist.'
            }
            return render(request, 'error.html', context, status=404)

        if not user_project.user == request.user and not user_project.translator == request.user:
            context = {
                'status_code': 403,
                'error_message': 'You aren\'t authorised to view this project.'
            }

            return render(request, 'error.html', context, status=403)

        if 'source_file' in kwargs and kwargs['source_file'] not in user_project.source_files.split(';'):
            context = {
                'status_code': 404,
                'error_message': 'No such file under this project.'
            }

            return render(request, 'error.html', context, status=404)

        return view_func(request, *args, **kwargs)

    return wrapped
