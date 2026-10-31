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
from .models import Course, Lesson, LessonCompletion, Exercise


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
        Prefetch('lessons', queryset=Lesson.objects.filter(published=True).prefetch_related(
            Prefetch('exercises', queryset=Exercise.objects.filter(published=True), to_attr='published_exercises')
        ), to_attr='published_lessons')
    )
    return JsonResponse({'runner_enabled': settings.LAB_RUNNER_ENABLED and bool(settings.LAB_RUNNER_TOKEN) and settings.LAB_RUNNER_URL.startswith('https://'), 'courses': [{
        'id': course.slug, 'title': course.title, 'description': course.description,
        'category': course.category, 'level': course.level, 'time': course.duration,
        'icon': course.icon, 'color': course.color,
        'lessons': [{
            'id': lesson.pk, 'title': lesson.title, 'content': lesson.content,
            'exercises': [{
                'id': exercise.pk, 'title': exercise.title_pt, 'description': exercise.description_pt,
                'title_en': exercise.title_en, 'description_en': exercise.description_en,
                'language': exercise.get_language_display(), 'starter_code': exercise.starter_code,
            } for exercise in lesson.published_exercises],
        } for lesson in course.published_lessons],
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


@require_POST
def evaluate_exercise(request, exercise_id):
    """Run private stdin/stdout tests on an explicitly configured external sandbox."""
    import json
    from urllib.parse import urlsplit
    from django.core.cache import cache
    from .runner import LANGUAGE_IDS, RunnerError, run_test

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication_required'}, status=401)
    if not settings.LAB_RUNNER_ENABLED:
        return JsonResponse({'error': 'runner_unavailable'}, status=503)
    parts = urlsplit(settings.LAB_RUNNER_URL)
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment or not settings.LAB_RUNNER_TOKEN:
        return JsonResponse({'error': 'runner_unavailable'}, status=503)
    try:
        exercise = Exercise.objects.get(pk=exercise_id, published=True, lesson__published=True, lesson__course__published=True)
    except Exercise.DoesNotExist:
        return JsonResponse({'error': 'not_found'}, status=404)
    if len(request.body) > 33000:
        return JsonResponse({'error': 'invalid_submission'}, status=400)
    try:
        body = json.loads(request.body)
        code = body['code']
        cases = json.loads(exercise.private_tests)
        if (not isinstance(code, str) or not code.strip() or len(code.encode('utf-8')) > 32000
                or exercise.language not in LANGUAGE_IDS or not isinstance(cases, list) or not 1 <= len(cases) <= 3
                or any(not isinstance(case, dict) or not isinstance(case.get('stdin'), str)
                       or not isinstance(case.get('expected_stdout'), str)
                       or len(case['stdin']) > 4000 or len(case['expected_stdout']) > 4000 for case in cases)):
            raise ValueError
    except (ValueError, TypeError, KeyError, UnicodeDecodeError):
        return JsonResponse({'error': 'invalid_submission_or_tests'}, status=400)
    # In production use a shared atomic cache (e.g. Redis), plus gateway rate limits.
    if not cache.add(f'lab-evaluate:{request.user.pk}', 'busy', timeout=30):
        return JsonResponse({'error': 'rate_limited'}, status=429)
    try:
        passed = sum(run_test(exercise.language, code, case['stdin'], case['expected_stdout']) for case in cases)
    except RunnerError:
        return JsonResponse({'error': 'runner_unavailable'}, status=503)
    return JsonResponse({'passed': passed, 'total': len(cases)})
