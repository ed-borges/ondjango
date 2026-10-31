import io
import subprocess
import sys

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .exercise_tests import parse_private_tests
from .models import Course, Exercise, Lesson


# These are trusted reference solutions, not code submitted by a student.
REFERENCE_SOLUTIONS = [
    'print("Olá, Ondjango!")',
    'a=int(input()); b=int(input()); print(a+b)',
    'n=int(input()); print("par" if n%2==0 else "impar")',
    'n=int(input()); print(sum(range(1,n+1)))',
    'print(sum(1 for x in input().split() if int(x)>0))',
    'words=input().lower().split(); target=input().lower(); print(words.count(target))',
    'def maior(a,b):\n return max(a,b)\na=int(input()); b=int(input()); print(maior(a,b))',
    'try:\n n=int(input()); print(n*2)\nexcept ValueError:\n print("invalido")',
    'def quadrados_pares(n):\n for i in range(2,n+1,2):\n  yield i*i\nprint(sum(quadrados_pares(int(input()))))',
    'import json\nprint(json.loads(input()).get("pontos",0))',
    'from datetime import date\na=date.fromisoformat(input()); b=date.fromisoformat(input()); print((b-a).days)',
    'from decimal import Decimal, ROUND_HALF_UP\na=Decimal(input()); b=Decimal(input()); print((a+b).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))',
]


class PythonTrackTests(TestCase):
    def setUp(self):
        call_command('seed_python_track', stdout=io.StringIO())

    def test_track_structure_and_publication(self):
        slugs = ['python-basico', 'python-intermedio', 'python-avancado']
        courses = [Course.objects.get(slug=slug) for slug in slugs]
        self.assertEqual([course.level for course in courses], ['Iniciante', 'Intermédio', 'Avançado'])
        for course in courses:
            self.assertTrue(course.published)
            lessons = list(course.lessons.all())
            self.assertEqual([lesson.order for lesson in lessons], [1, 2, 3, 4])
            for lesson in lessons:
                self.assertTrue(lesson.published)
                self.assertTrue(lesson.content.strip())
                exercise = lesson.exercises.get()
                self.assertTrue(exercise.published)
                self.assertEqual(exercise.language, Exercise.Language.PYTHON)
                self.assertTrue(parse_private_tests(exercise.private_tests))

    def test_public_catalog_excludes_private_tests(self):
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['courses']), 3)
        self.assertNotIn('expected_stdout', response.content.decode())
        self.assertNotIn('private_tests', response.content.decode())

    def test_seed_is_idempotent_and_preserves_edits(self):
        course = Course.objects.get(slug='python-basico')
        lesson = course.lessons.first()
        exercise = lesson.exercises.first()
        lesson.content = 'Conteúdo editado'
        lesson.save()
        exercise.description_pt = 'Enunciado editado'
        exercise.save()
        call_command('seed_python_track', stdout=io.StringIO())
        self.assertEqual(Course.objects.count(), 3)
        self.assertEqual(Lesson.objects.count(), 12)
        self.assertEqual(Exercise.objects.count(), 12)
        lesson.refresh_from_db()
        exercise.refresh_from_db()
        self.assertEqual(lesson.content, 'Conteúdo editado')
        self.assertEqual(exercise.description_pt, 'Enunciado editado')

    def test_private_cases_match_trusted_reference_solutions(self):
        exercises = []
        for slug in ('python-basico', 'python-intermedio', 'python-avancado'):
            course = Course.objects.get(slug=slug)
            exercises.extend(lesson.exercises.get() for lesson in course.lessons.all())
        self.assertEqual(len(exercises), len(REFERENCE_SOLUTIONS))
        for exercise, solution in zip(exercises, REFERENCE_SOLUTIONS):
            for case in parse_private_tests(exercise.private_tests):
                with self.subTest(exercise=exercise.title_pt, stdin=case['stdin']):
                    # Only fixed, trusted reference solutions run in this test suite.
                    result = subprocess.run([sys.executable, '-c', solution], input=case['stdin'], text=True, capture_output=True, timeout=5, check=True)
                    self.assertEqual(result.stdout, case['expected_stdout'])


from django.db import IntegrityError, transaction
from .models import LearningPath, LearningPathCourse


class LearningPathTests(TestCase):
    def setUp(self):
        call_command('seed_python_track', stdout=io.StringIO())

    def test_published_path_contains_courses_in_recommended_order(self):
        data = self.client.get(reverse('learning_paths')).json()
        self.assertEqual(len(data['paths']), 1)
        self.assertEqual(data['paths'][0]['courses'], ['python-basico', 'python-intermedio', 'python-avancado'])

    def test_unpublished_paths_and_courses_are_hidden(self):
        path = LearningPath.objects.get(slug='python')
        Course.objects.filter(slug='python-intermedio').update(published=False)
        data = self.client.get(reverse('learning_paths')).json()
        self.assertEqual(data['paths'][0]['courses'], ['python-basico', 'python-avancado'])
        path.published = False
        path.save()
        self.assertEqual(self.client.get(reverse('learning_paths')).json()['paths'], [])

    def test_seed_does_not_overwrite_existing_path(self):
        path = LearningPath.objects.get(slug='python')
        path.title = 'Editada'
        path.published = False
        path.save()
        path.steps.filter(order=2).delete()
        call_command('seed_python_track', stdout=io.StringIO())
        path.refresh_from_db()
        self.assertEqual(path.title, 'Editada')
        self.assertFalse(path.published)
        self.assertEqual(path.steps.count(), 2)

    def test_cannot_repeat_course_or_position(self):
        path = LearningPath.objects.get(slug='python')
        course = Course.objects.get(slug='python-basico')
        with self.assertRaises(IntegrityError), transaction.atomic():
            LearningPathCourse.objects.create(path=path, course=course, order=10)
        other = Course.objects.create(slug='extra', title='Extra', description='Extra', category=Course.Category.PROGRAMACAO)
        with self.assertRaises(IntegrityError), transaction.atomic():
            LearningPathCourse.objects.create(path=path, course=other, order=1)

    def test_path_admin_requires_login(self):
        self.assertEqual(self.client.get('/admin/learning/learningpath/').status_code, 302)


class PythonTranslationTests(TestCase):
    def setUp(self):
        call_command('seed_python_track', stdout=io.StringIO())

    def test_translations_cover_pilot_and_do_not_expose_private_tests(self):
        call_command('translate_python_track', stdout=io.StringIO())
        for slug in ('python-basico', 'python-intermedio', 'python-avancado'):
            course = Course.objects.get(slug=slug)
            self.assertTrue(course.title_en)
            self.assertTrue(course.description_en)
            for lesson in course.lessons.all():
                self.assertTrue(lesson.title_en)
                self.assertTrue(lesson.content_en)
                exercise = lesson.exercises.get()
                self.assertTrue(exercise.title_en)
                self.assertTrue(exercise.description_en)
        payload = self.client.get(reverse('catalog')).json()
        self.assertEqual(payload['courses'][0]['title_en'], 'Python: beginner level')
        self.assertTrue(payload['courses'][0]['lessons'][0]['content_en'])
        self.assertNotIn('private_tests', str(payload))
        self.assertEqual(self.client.get(reverse('learning_paths')).json()['paths'][0]['title_en'], 'Python learning path')

    def test_translation_command_preserves_edited_content_and_translations(self):
        course = Course.objects.get(slug='python-basico')
        first, second = list(course.lessons.all())[:2]
        first.content = 'Conteúdo alterado por um professor'
        first.title_en = ''
        first.content_en = ''
        first.save()
        second.title_en = 'Custom translation'
        second.content_en = 'Custom content'
        second.save()
        call_command('translate_python_track', stdout=io.StringIO())
        call_command('translate_python_track', stdout=io.StringIO())
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(first.title_en, '')
        self.assertEqual(second.title_en, 'Custom translation')
        self.assertEqual(second.content_en, 'Custom content')
