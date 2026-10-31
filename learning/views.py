from django.conf import settings
from django.contrib.auth import login
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import never_cache
from .forms import RegistrationForm
from .models import Course, Lesson, LessonCompletion


@ensure_csrf_cookie
def home(request):
    return render(request, 'learning/index.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'learning/auth.html', {'form': form, 'register': True})


@require_GET
def catalog(request):
    courses = Course.objects.filter(published=True).prefetch_related(
        Prefetch('lessons', queryset=Lesson.objects.filter(published=True), to_attr='published_lessons')
    )
    return JsonResponse({'courses': [{
        'id': course.slug, 'title': course.title, 'description': course.description,
        'category': course.category, 'level': course.level, 'time': course.duration,
        'icon': course.icon, 'color': course.color,
        'lessons': [{'id': lesson.pk, 'title': lesson.title, 'content': lesson.content} for lesson in course.published_lessons],
    } for course in courses]})


@never_cache
@require_GET
def progress(request):
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False})
    ids = LessonCompletion.objects.filter(user=request.user, lesson__published=True, lesson__course__published=True).values_list('lesson_id', flat=True)
    return JsonResponse({'authenticated': True, 'username': request.user.get_username(), 'completed': list(ids)})


@require_POST
def complete_lesson(request, lesson_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Inicia sessão para guardar o progresso.'}, status=401)
    try:
        lesson = Lesson.objects.get(pk=lesson_id, published=True, course__published=True)
    except Lesson.DoesNotExist:
        return JsonResponse({'error': 'Aula não encontrada.'}, status=404)
    LessonCompletion.objects.get_or_create(user=request.user, lesson=lesson)
    return JsonResponse({'completed': True})


# The hosted development preview embeds the app in a frame.
if settings.DEBUG:
    home = xframe_options_exempt(home)
    register = xframe_options_exempt(register)
