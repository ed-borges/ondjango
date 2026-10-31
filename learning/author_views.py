import re
from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_http_methods

from .forms import AuthorCourseForm, AuthorLessonForm, AuthorExerciseForm
from .models import Course, Exercise, Lesson


def author_required(view):
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.has_perm('learning.can_author'):
            return HttpResponse('Acesso reservado a autores autorizados.', status=403)
        return view(request, *args, **kwargs)
    return wrapped


@author_required
@require_http_methods(['GET', 'HEAD'])
def dashboard(request):
    courses = Course.objects.filter(author=request.user).prefetch_related('lessons__exercises')
    return render(request, 'learning/author_dashboard.html', {'courses': courses})


@author_required
@require_http_methods(['GET', 'POST'])
def course_edit(request, course_id=None):
    course = get_object_or_404(Course, pk=course_id, author=request.user) if course_id else Course(author=request.user)
    form = AuthorCourseForm(request.POST or None, instance=course)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('author_dashboard')
    return render(request, 'learning/author_form.html', {'form': form, 'heading': 'Editar curso' if course_id else 'Criar curso'})


@author_required
@require_http_methods(['GET', 'POST'])
def lesson_edit(request, course_id, lesson_id=None):
    course = get_object_or_404(Course, pk=course_id, author=request.user)
    lesson = get_object_or_404(Lesson, pk=lesson_id, course=course) if lesson_id else Lesson(course=course)
    old_name = lesson.video_file.name if lesson.pk else ''
    form = AuthorLessonForm(request.POST or None, request.FILES or None, instance=lesson)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            saved = form.save()
            if old_name and old_name != saved.video_file.name:
                storage = saved._meta.get_field('video_file').storage
                transaction.on_commit(lambda: storage.delete(old_name))
        return redirect('author_dashboard')
    return render(request, 'learning/author_form.html', {'form': form, 'heading': 'Editar aula' if lesson_id else 'Criar aula', 'course': course})


@author_required
@require_http_methods(['GET', 'POST'])
def exercise_edit(request, course_id, lesson_id, exercise_id=None):
    course = get_object_or_404(Course, pk=course_id, author=request.user)
    lesson = get_object_or_404(Lesson, pk=lesson_id, course=course)
    exercise = get_object_or_404(Exercise, pk=exercise_id, lesson=lesson) if exercise_id else Exercise(lesson=lesson)
    form = AuthorExerciseForm(request.POST or None, instance=exercise)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('author_dashboard')
    return render(request, 'learning/author_form.html', {
        'form': form, 'heading': 'Editar exercício' if exercise_id else 'Criar exercício',
        'course': course, 'lesson': lesson, 'is_exercise': True,
    })


@require_http_methods(['GET', 'HEAD'])
def lesson_video(request, lesson_id):
    lesson = get_object_or_404(Lesson.objects.select_related('course'), pk=lesson_id)
    is_owner = request.user.is_authenticated and request.user.has_perm('learning.can_author') and lesson.course.author_id == request.user.pk
    if not ((lesson.published and lesson.course.published) or is_owner or request.user.is_superuser):
        raise Http404
    if not lesson.video_file:
        raise Http404
    try:
        file = lesson.video_file.open('rb')
        size = lesson.video_file.size
    except (FileNotFoundError, OSError):
        raise Http404
    start, end, status = 0, size - 1, 200
    requested = request.headers.get('Range')
    if requested:
        match = re.fullmatch(r'bytes=(\d{0,20})-(\d{0,20})', requested.strip())
        if not match or not (match.group(1) or match.group(2)) or size == 0:
            file.close()
            response = HttpResponse(status=416)
            response['Content-Range'] = f'bytes */{size}'
            return response
        first, last = match.groups()
        if not first:
            length = int(last)
            if length == 0:
                file.close()
                response = HttpResponse(status=416)
                response['Content-Range'] = f'bytes */{size}'
                return response
            start = max(size - length, 0)
        else:
            start = int(first)
            end = min(int(last), size - 1) if last else size - 1
        if start >= size or start > end:
            file.close()
            response = HttpResponse(status=416)
            response['Content-Range'] = f'bytes */{size}'
            return response
        status = 206
    length = max(0, end - start + 1)
    content_type = 'video/webm' if lesson.video_file.name.lower().endswith('.webm') else 'video/mp4'
    if request.method == 'HEAD':
        file.close()
        response = HttpResponse(status=status, content_type=content_type)
    else:
        file.seek(start)
        def chunks():
            remaining = length
            try:
                while remaining:
                    data = file.read(min(65536, remaining))
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
            finally:
                file.close()
        response = StreamingHttpResponse(chunks(), status=status, content_type=content_type)
    response['Content-Length'] = str(length)
    response['Accept-Ranges'] = 'bytes'
    response['X-Content-Type-Options'] = 'nosniff'
    response['Content-Security-Policy'] = "default-src 'none'; sandbox"
    response['Cache-Control'] = 'private, no-store'
    if status == 206:
        response['Content-Range'] = f'bytes {start}-{end}/{size}'
    return response


if settings.DEBUG:
    dashboard = xframe_options_exempt(dashboard)
    course_edit = xframe_options_exempt(course_edit)
    lesson_edit = xframe_options_exempt(lesson_edit)
    exercise_edit = xframe_options_exempt(exercise_edit)
