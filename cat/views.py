from django.shortcuts import render, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse

import re
import os
import time

from html import escape
from lxml import etree

from toraman import SourceFile, BilingualFile, nsmap

from .forms import ProjectForm
from .models import Project
# Create your views here.

@login_required()
def bilingual_file(request, user_id, project_id, source_file):
    assert user_id == request.user.id
    user_project = Project.objects.get(id=project_id)
    assert user_project.user == request.user

    bf = BilingualFile(os.path.join(user_project.get_source_dir(), (source_file + '.xml')))

    if request.method == 'POST':
        target_segment = re.findall(r'<tag[\s\S]+?class="([\s\S]+?)">([\s\S]+?)</tag>|([^<^>]+)',
                                    request.POST['target_segment'])
        target_segment_xml = etree.Element('{{{0}}}target'.format(nsmap['toraman']))
        for element in target_segment:
            if element[0]:
                tag = element[0].split()
                tag.insert(0, element[1][len(tag[0]):])
                target_segment_xml.append(etree.Element('{{{0}}}{1}'.format(nsmap['toraman'], tag[1])))
                target_segment_xml[-1].attrib['no'] = tag[0]
                if len(tag) > 2:
                    target_segment_xml[-1].attrib['type'] = tag[2]
            elif element[2]:
                target_segment_xml.append(etree.Element('{{{0}}}text'.format(nsmap['toraman'])))
                target_segment_xml[-1].text = element[2]
        segment_status = request.POST['segment_status']
        paragraph_no = int(request.POST['paragraph_no'])
        segment_no = int(request.POST['segment_no'])

        bf.update_segment(segment_status, target_segment_xml, paragraph_no, segment_no)
        bf.save(user_project.get_source_dir())
        
        return HttpResponse('Segment #{0} submitted successfully.'.format(segment_no),
                            content_type='text/plain')

    else:
        def segment_to_html(source_or_target_segment):
            segment_html = ''
            for sub_elem in source_or_target_segment:
                if sub_elem.tag.endswith('}text'):
                    segment_html += escape(sub_elem.text)
                else:
                    tag = etree.Element('tag')
                    tag.attrib['contenteditable'] = 'false'
                    tag.attrib['class'] = sub_elem.tag.split('}')[-1]
                    tag.text = tag.attrib['class']
                    if 'type' in sub_elem.attrib:
                        tag.attrib['class'] += ' ' + sub_elem.attrib['type']

                    if 'no' in sub_elem.attrib:
                        tag.text += sub_elem.attrib['no']

                    segment_html += etree.tostring(tag).decode()

            return segment_html
            
        paragraphs = (paragraph for paragraph in bf.paragraphs)
        segments = []
        for paragraph in paragraphs:
            for segment in paragraph:
                source_segment = segment_to_html(segment[0])
                target_segment = segment_to_html(segment[2])
                segment_status = segment[1]
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
        }

        return render(request, 'bilingual_file.html', context)


@login_required()
def download_target_file(request, user_id, project_id, source_file):
    assert user_id == request.user.id
    user_project = Project.objects.get(id=project_id)
    assert user_project.user == request.user

    bf = BilingualFile(os.path.join(user_project.get_source_dir(), (source_file + '.xml')))
    bf.generate_target_translation(os.path.join(user_project.get_source_dir(), source_file),
                                    os.path.join(user_project.get_source_dir(), 'target')
                                    )
    target_file_path = os.path.join(user_project.get_source_dir(), 'target', source_file)

    response = FileResponse(open(target_file_path, 'rb'))
    response['Content-Disposition'] = 'attachment; filename={0}'.format(source_file)
    response['Content-Length'] = os.path.getsize(target_file_path)

    return response


@login_required()
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
                if not uploaded_file.name.lower().endswith('.docx'):
                    context['errors'].append('File format of "{0}" is not supported.'.format(uploaded_file.name))

            if context['errors']:
                return render(request, 'new_project.html', context)
            else:
                submitted_project = form.save(commit=False)
                submitted_project.user = request.user
                submitted_project.source_files = ';'.join([uploaded_file.name for uploaded_file in uploaded_files])
                submitted_project.save()

                source_files_dir = submitted_project.get_source_dir()
                os.makedirs(source_files_dir)

                time.sleep(0.5)

                for uploaded_file in uploaded_files:
                    with open(os.path.join(source_files_dir, uploaded_file.name), 'wb+') as output_file:
                        for line in uploaded_file:
                            output_file.write(line)

                for source_file in submitted_project.source_files.split(';'):
                    sf = SourceFile(os.path.join(source_files_dir, source_file))
                    sf.write_bilingual_file(source_files_dir)

                return redirect(submitted_project)
        else:
            return render(request, 'new_project.html', context)
    else:
        return render(request, 'new_project.html', context)


@login_required()
def project(request, user_id, project_id):
    assert user_id == request.user.id
    user_project = Project.objects.get(id=project_id)
    assert user_project.user == request.user

    context = {
        'user_project': Project.objects.get(id=project_id),
        'source_files': user_project.source_files.split(';'),
    }

    return render(request, 'project.html', context)
