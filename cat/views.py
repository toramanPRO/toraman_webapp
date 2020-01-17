from django.shortcuts import render, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import FileResponse, HttpResponse

import copy, json, os, re, time

from html import escape
from lxml import etree

from toraman import BilingualFile, nsmap, SourceFile
from toraman import TranslationMemory as TM
from toraman.utils import html_to_segment, segment_to_html, analyse_files

from .decorators import permission_required, project_access
from .forms import AssignProjectToTranslatorForm, ProjectForm, TranslationMemoryForm
from .models import Project, TranslationMemory
# Create your views here.

@project_access
def bilingual_file(request, user_id, project_id, source_file):
    user_project = Project.objects.get(id=project_id)

    if request.method == 'POST':
        source_segment = html_to_segment(request.POST['source_segment'], 'source')
        target_segment = html_to_segment(request.POST['target_segment'], 'target')
        segment_status = request.POST['segment_status']
        paragraph_no = int(request.POST['paragraph_no'])
        segment_no = int(request.POST['segment_no'])

        bf = BilingualFile(os.path.join(user_project.get_source_dir(), (source_file + '.xml')))
        segment_no_list = bf.update_segment(segment_status, copy.deepcopy(target_segment), paragraph_no, segment_no, str(request.user.id))
        bf.save(user_project.get_source_dir())

        if segment_status == 'Translated' and user_project.translation_memory is not None:
            user_translation_memory = TM(user_project.translation_memory.get_tm_path(),
                                        user_project.translation_memory.source_language,
                                        user_project.translation_memory.target_language)

            user_translation_memory.submit_segment(source_segment, target_segment, str(request.user.id))

        return HttpResponse(', '.join([str(segment_no) for segment_no in segment_no_list]),
                            content_type='text/plain')

    else:
        if request.GET.get('procedure') == 'lookup':
            source_segment = html_to_segment(request.GET['source_segment'], 'source')

            user_translation_memory = TM(user_project.translation_memory.get_tm_path(),
                                        user_project.translation_memory.source_language,
                                        user_project.translation_memory.target_language)

            tm_hits = [[], user_translation_memory.lookup(source_segment)]

            for tm_hit in tm_hits[1]:
                tm_hit = [{}, tm_hit]

                tm_hit[0]['levenshtein_ratio'] = '{0}%'.format(int(tm_hit[1][0]*100))
                tm_hit[0]['source'] = segment_to_html(tm_hit[1][1])
                tm_hit[0]['target'] = segment_to_html(tm_hit[1][2])

                tm_hits[0].append(tm_hit[0])
            else:
                tm_hits = tm_hits[0]

            context = {'tm_hits': tm_hits}

            return render(request, 'tm_hits.html', context)

        else:
            bf = BilingualFile(os.path.join(user_project.get_source_dir(), (source_file + '.xml')))
            paragraphs = (paragraph for paragraph in bf.paragraphs)
            segments = []
            for paragraph in paragraphs:
                for segment in paragraph:
                    source_segment = segment_to_html(segment[0])
                    target_segment = segment_to_html(segment[2])
                    if segment[1].text is not None:
                        segment_status = segment[1].text.lower()
                    else:
                        segment_status = ''
                    paragraph_no = segment[3]
                    segment_no = segment[4]

                    segment = {
                        'source': source_segment,
                        'target': target_segment,
                        'status': segment_status,
                        'paragraph_no': paragraph_no,
                        'segment_no': segment_no,
                    }

                    segments.append(segment)

            context = {

                'download_url': reverse('download-target-file', args=(user_id, project_id, source_file)),
                'project_url': user_project.get_absolute_url(),
                'segments': segments,
                'tm': user_project.translation_memory,
            }

            return render(request, 'bilingual_file.html', context)


@project_access
def download_target_file(request, user_id, project_id, source_file):
    user_project = Project.objects.get(id=project_id)

    bf = BilingualFile(os.path.join(user_project.get_source_dir(), (source_file + '.xml')))
    bf.generate_target_translation(os.path.join(user_project.get_source_dir(), source_file),
                                    user_project.get_target_dir()
                                    )
    target_file_path = os.path.join(user_project.get_target_dir(), source_file)

    response = FileResponse(open(target_file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename={0}'.format(source_file)
    response['Content-Length'] = os.path.getsize(target_file_path)

    return response


@permission_required('cat.add_project')
def new_project(request):
    form = ProjectForm(request.POST or None, request.FILES)

    context = {
        'form': form,
        'errors': [],
    }

    if request.method == 'POST':
        if form.is_valid():
            uploaded_files = request.FILES.getlist('source_files')

            for uploaded_file in uploaded_files:
                if not uploaded_file.name.lower().endswith(('.docx', '.odt')):
                    context['errors'].append('File format of "{0}" is not supported.'.format(uploaded_file.name))

            user_tm_id = form.cleaned_data['translation_memory']
            if user_tm_id.isdigit():
                try:
                    user_translation_memory = TranslationMemory.objects.get(id=user_tm_id)
                    if user_translation_memory.user != request.user:
                        context['errors'].append('This translation memory belongs to someone else.')
                    else:
                        if (form.cleaned_data['source_language'] != user_translation_memory.source_language
                        or form.cleaned_data['target_language'] != user_translation_memory.target_language):
                            context['errors'].append('The language combination of the project and the translation memory do not match.')
                except TranslationMemory.DoesNotExist:
                    context['errors'].append('This translation memory does not exist.')
            else:
                context['errors'].append('Please select a translation memory.')

            if context['errors']:
                return render(request, 'new_project.html', context)
            else:
                user_project = form.save(commit=False)
                user_project.translation_memory = user_translation_memory
                user_project.user = request.user
                user_project.source_files = ';'.join([uploaded_file.name for uploaded_file in uploaded_files])
                user_project.save()

                source_files_dir = user_project.get_source_dir()
                os.makedirs(source_files_dir)

                time.sleep(0.5)

                for uploaded_file in uploaded_files:
                    with open(os.path.join(source_files_dir, uploaded_file.name), 'wb+') as output_file:
                        for line in uploaded_file:
                            output_file.write(line)

                bf_paths = []
                for source_file in user_project.source_files.split(';'):
                    sf = SourceFile(os.path.join(source_files_dir, source_file))
                    sf.write_bilingual_file(source_files_dir)
                    bf_paths.append(os.path.join(source_files_dir, source_file + '.xml'))

                analysis_report = analyse_files(bf_paths,
                                                user_project.translation_memory.get_tm_path(),
                                                user_project.source_language,
                                                user_project.target_language)

                user_project.analysis_report = json.dumps(analysis_report)
                user_project.save()

                return redirect(user_project)
        else:
            context['errors'] = form.errors
            return render(request, 'new_project.html', context)
    else:
        return render(request, 'new_project.html', context)


@permission_required('cat.add_translationmemory')
def new_translation_memory(request):
    form = TranslationMemoryForm(request.POST or None)

    context = {
        'form': form,
        'errors': [],
    }

    if request.method == 'POST':
        if form.is_valid():
            user_translation_memory = form.save(commit=False)
            user_translation_memory.user = request.user
            user_translation_memory.save()

            user_tm_path = user_translation_memory.get_tm_path()

            if not os.path.exists(os.path.dirname(user_tm_path)):
                os.makedirs(os.path.dirname(user_tm_path))
                time.sleep(0.5)

            ttm = TM(user_tm_path,
                    user_translation_memory.source_language,
                    user_translation_memory.target_language)

            return redirect(user_translation_memory)

    return render(request, 'new_translation_memory.html', context)


@project_access
def project(request, user_id, project_id):
    user_project = Project.objects.get(id=project_id)

    context = {
        'user_is_pm': request.user.has_perm('cat.change_project'),
        'user_project': Project.objects.get(id=project_id),
        'source_files': user_project.source_files.split(';'),
    }
    if context['user_is_pm']:
        context['form'] = AssignProjectToTranslatorForm(request.POST or None)

    if request.method == 'POST':
        if not context['user_is_pm'] and not user_project.user == request.user:
            response = HttpResponse('You aren\'t authorised to modify this project.')
            response.status_code = 403

            return response

        if context['form'].is_valid():
            try:
                translator = User.objects.get(username=context['form'].cleaned_data['translator'])
                user_project.translator = translator
                user_project.save()
            except User.DoesNotExist:
                context['error'] = 'User does not exist.'

    return render(request, 'project.html', context)


@login_required()
def translation_memory(request, user_id, tm_id):
    assert user_id == request.user.id
    user_tm = TranslationMemory.objects.get(id=tm_id)
    assert user_tm.user == request.user

    user_translation_memory = TM(user_tm.get_tm_path(), user_tm.source_language, user_tm.target_language)

    context = {
        'user_tm': user_tm,
    }

    if request.method == 'POST':
        pass

    else:
        if request.GET.get('procedure') == 'lookup':
            source_segment = html_to_segment(request.GET['source_segment'], 'source')
            tm_hits = [[], user_translation_memory.lookup(source_segment)]

            for tm_hit in tm_hits[1]:
                tm_hit = [{}, tm_hit]

                tm_hit[0]['levenshtein_ratio'] = '{0}%'.format(int(tm_hit[1][0]*100))
                tm_hit[0]['source'] = segment_to_html(tm_hit[1][1])
                tm_hit[0]['target'] = segment_to_html(tm_hit[1][2])

                tm_hits[0].append(tm_hit[0])
            else:
                tm_hits = tm_hits[0]

            context['tm_hits'] = tm_hits

            return render(request, 'tm_hits.html', context)

    return render(request, 'translation_memory.html', context)


@login_required()
def translation_memory_query(request):
    user_tms = TranslationMemory.objects.filter(user=request.user,
                                                source_language=request.GET['source_language'],
                                                target_language=request.GET['target_language'])
    context = {
        'user_tms': user_tms,
    }

    return render(request, 'translation_memory_query.html', context)
