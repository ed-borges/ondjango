from django.test import TestCase
from django.urls import reverse
from django.contrib.staticfiles import finders


class HomeTests(TestCase):
    def test_home_serves_prototype(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ondjango')
        self.assertContains(response, '/static/learning/main.js')

    def test_assets_exist(self):
        self.assertIsNotNone(finders.find('learning/main.js'))
        self.assertIsNotNone(finders.find('learning/style.css'))


from django.core.management import call_command
from .models import Course, Lesson


class CatalogTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(slug='publico', title='Curso público', description='Descrição', category=Course.Category.TECNOLOGIA, published=True)
        self.draft = Course.objects.create(slug='rascunho', title='Curso privado', description='Descrição', category=Course.Category.TECNOLOGIA)
        Lesson.objects.create(course=self.course, title='Segunda', content='Texto 2', order=2, published=True)
        Lesson.objects.create(course=self.course, title='Primeira', content='<script>texto</script>', order=1, published=True)
        Lesson.objects.create(course=self.course, title='Rascunho', content='Segredo', order=0)
        Lesson.objects.create(course=self.draft, title='Privada', content='Segredo', published=True)

    def test_only_published_courses_and_lessons_are_returned_in_order(self):
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        courses = response.json()['courses']
        self.assertEqual(len(courses), 1)
        self.assertEqual([lesson['title'] for lesson in courses[0]['lessons']], ['Primeira', 'Segunda'])
        self.assertNotIn('Segredo', response.content.decode())

    def test_catalog_rejects_post(self):
        self.assertEqual(self.client.post(reverse('catalog')).status_code, 405)

    def test_admin_requires_login(self):
        self.assertEqual(self.client.get('/admin/learning/course/').status_code, 302)

    def test_demo_seed_is_idempotent_and_does_not_overwrite(self):
        call_command('seed_demo', verbosity=0)
        demo = Course.objects.get(slug='web')
        demo.title = 'Alterado'
        demo.save()
        call_command('seed_demo', verbosity=0)
        self.assertEqual(Course.objects.get(slug='web').title, 'Alterado')
        self.assertEqual(Lesson.objects.filter(course=demo).count(), 4)


from django.contrib.auth import get_user_model
from django.test import Client
from .models import LessonCompletion


class AccountsAndProgressTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='aluno', password='Senhasegura123!')
        self.other = get_user_model().objects.create_user(username='outra', password='Senhasegura123!')
        self.course = Course.objects.create(slug='curso', title='Curso', description='Descrição', category=Course.Category.TECNOLOGIA, published=True)
        self.lesson = Lesson.objects.create(course=self.course, title='Aula', content='Conteúdo', published=True)
        self.draft = Lesson.objects.create(course=self.course, title='Rascunho', content='Segredo')

    def test_registration_login_and_logout(self):
        response = self.client.post(reverse('register'), {'username': 'nova', 'password1': 'UmaSenhaSegura789!', 'password2': 'UmaSenhaSegura789!'})
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(self.client.get(reverse('progress')).json()['authenticated'])
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('home'))
        self.assertFalse(self.client.get(reverse('progress')).json()['authenticated'])
        self.assertRedirects(self.client.post(reverse('login'), {'username': 'nova', 'password': 'UmaSenhaSegura789!'}), reverse('home'))

    def test_invalid_registration_does_not_create_user(self):
        response = self.client.post(reverse('register'), {'username': 'nova', 'password1': '123', 'password2': '123'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username='nova').exists())

    def test_progress_is_private_idempotent_and_shared_across_sessions(self):
        self.assertEqual(self.client.post(reverse('complete_lesson', args=[self.lesson.pk])).status_code, 401)
        self.client.force_login(self.user)
        for _ in range(2):
            self.assertEqual(self.client.post(reverse('complete_lesson', args=[self.lesson.pk])).status_code, 200)
        self.assertEqual(LessonCompletion.objects.count(), 1)
        second_device = Client()
        second_device.force_login(self.user)
        self.assertEqual(second_device.get(reverse('progress')).json()['completed'], [self.lesson.pk])
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('progress')).json()['completed'], [])

    def test_unpublished_lessons_and_courses_cannot_be_completed(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse('complete_lesson', args=[self.draft.pk])).status_code, 404)
        self.course.published = False
        self.course.save()
        self.assertEqual(self.client.post(reverse('complete_lesson', args=[self.lesson.pk])).status_code, 404)

    def test_csrf_is_required_for_completion(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        url = reverse('complete_lesson', args=[self.lesson.pk])
        self.assertEqual(client.post(url).status_code, 403)
        client.get(reverse('home'))
        token = client.cookies['csrftoken'].value
        self.assertEqual(client.post(url, HTTP_X_CSRFTOKEN=token).status_code, 200)


from .models import Exercise


class ExerciseCatalogTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(slug='exercicios', title='Curso', description='Descrição', category=Course.Category.PROGRAMACAO, published=True)
        self.lesson = Lesson.objects.create(course=self.course, title='Aula', content='Conteúdo', published=True)
        self.exercise = Exercise.objects.create(lesson=self.lesson, title_pt='Olá', description_pt='Escreve uma mensagem.', title_en='Hello', description_en='Write a message.', language=Exercise.Language.PYTHON, starter_code='print("olá")', private_tests='TESTE_SECRETO', published=True)
        Exercise.objects.create(lesson=self.lesson, title_pt='Rascunho secreto', description_pt='Privado', language=Exercise.Language.RUBY)

    def test_published_exercise_is_public_but_private_tests_are_never_returned(self):
        response = self.client.get(reverse('catalog'))
        exercises = response.json()['courses'][0]['lessons'][0]['exercises']
        self.assertEqual(len(exercises), 1)
        self.assertEqual(exercises[0]['title'], 'Olá')
        self.assertEqual(exercises[0]['language'], 'Python')
        self.assertEqual(exercises[0]['title_en'], 'Hello')
        self.assertEqual(exercises[0]['description_en'], 'Write a message.')
        self.assertNotIn('TESTE_SECRETO', response.content.decode())
        self.assertNotIn('Rascunho secreto', response.content.decode())

    def test_exercises_on_unpublished_lesson_or_course_not_returned(self):
        self.lesson.published = False
        self.lesson.save()
        self.assertEqual(self.client.get(reverse('catalog')).json()['courses'][0]['lessons'], [])
        self.course.published = False
        self.course.save()
        self.assertEqual(self.client.get(reverse('catalog')).json()['courses'], [])

    def test_exercise_language_choices_include_compalg_preparation(self):
        self.assertEqual(set(Exercise.Language.values), {'python', 'javascript', 'java', 'csharp', 'ruby', 'algoritmo'})

    def test_exercise_admin_is_protected(self):
        self.assertEqual(self.client.get('/admin/learning/exercise/').status_code, 302)


class LabDemoTests(TestCase):
    def test_seed_lab_demo_is_idempotent_and_does_not_overwrite(self):
        call_command('seed_demo', verbosity=0)
        call_command('seed_lab_demo', verbosity=0)
        exercise = Exercise.objects.get(title_pt='A tua primeira mensagem')
        exercise.starter_code = 'alterado'
        exercise.save()
        call_command('seed_lab_demo', verbosity=0)
        self.assertEqual(Exercise.objects.filter(title_pt='A tua primeira mensagem').count(), 1)
        self.assertEqual(Exercise.objects.get(pk=exercise.pk).starter_code, 'alterado')


from unittest.mock import patch
from django.core.cache import cache
from django.test import override_settings
import json


@override_settings(LAB_RUNNER_ENABLED=True, LAB_RUNNER_URL='https://sandbox.example.test', LAB_RUNNER_TOKEN='secret')
class LabEvaluationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(username='labuser', password='UmaSenha123!')
        course = Course.objects.create(slug='lab', title='Lab', description='Descrição', category=Course.Category.PROGRAMACAO, published=True)
        lesson = Lesson.objects.create(course=course, title='Aula', content='Conteúdo', published=True)
        self.exercise = Exercise.objects.create(lesson=lesson, title_pt='Teste', description_pt='Teste', language=Exercise.Language.PYTHON, published=True, private_tests=json.dumps([{'stdin': 'ENTRADA_SECRETA', 'expected_stdout': 'SAIDA_SECRETA'}]))
        self.url = reverse('evaluate_exercise', args=[self.exercise.pk])

    @patch('learning.runner.run_test', return_value=True)
    def test_evaluation_and_rate_limit(self, runner):
        self.assertEqual(self.client.post(self.url, data=json.dumps({'code': 'print(1)'}), content_type='application/json').status_code, 401)
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=json.dumps({'code': 'print(1)'}), content_type='application/json')
        self.assertEqual(response.json(), {'passed': 1, 'total': 1})
        self.assertNotIn('SECRETA', response.content.decode())
        runner.assert_called_once()
        self.assertEqual(self.client.post(self.url, data=json.dumps({'code': 'print(1)'}), content_type='application/json').status_code, 429)

    def test_requires_published_and_valid_tests(self):
        self.client.force_login(self.user)
        self.exercise.published = False
        self.exercise.save()
        self.assertEqual(self.client.post(self.url, data=json.dumps({'code': 'x'}), content_type='application/json').status_code, 404)
        self.exercise.published = True
        self.exercise.private_tests = 'not json'
        self.exercise.save()
        self.assertEqual(self.client.post(self.url, data=json.dumps({'code': 'x'}), content_type='application/json').status_code, 400)

    @override_settings(LAB_RUNNER_ENABLED=False)
    def test_disabled_by_default(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(self.url).status_code, 503)


class RunnerAdapterTests(TestCase):
    @override_settings(LAB_RUNNER_URL='https://sandbox.example.test', LAB_RUNNER_TOKEN='token')
    @patch('learning.runner.urllib.request.build_opener')
    def test_runner_sends_limits_and_keeps_output_private(self, build_opener):
        from .runner import run_test
        response = build_opener.return_value.open.return_value.__enter__.return_value
        response.read.return_value = b'{"status":{"id":3},"stdout":"secret output"}'
        self.assertTrue(run_test('python', 'print(1)', 'secret input', 'secret output'))
        request = build_opener.return_value.open.call_args.args[0]
        payload = json.loads(request.data)
        self.assertFalse(payload['enable_network'])
        self.assertEqual(payload['cpu_time_limit'], 2)
        self.assertEqual(payload['language_id'], 71)


@override_settings(LAB_RUNNER_ENABLED=True, LAB_RUNNER_URL='https://sandbox.example.test', LAB_RUNNER_TOKEN='secret')
class LabCsrfTests(TestCase):
    @patch('learning.runner.run_test', return_value=True)
    def test_csrf_protection_for_evaluation(self, runner):
        cache.clear()
        user = get_user_model().objects.create_user(username='csrfuser', password='SenhaForte42!')
        course = Course.objects.create(slug='csrf', title='Curso', description='Descrição', category=Course.Category.PROGRAMACAO, published=True)
        lesson = Lesson.objects.create(course=course, title='Aula', content='Conteúdo', published=True)
        exercise = Exercise.objects.create(lesson=lesson, title_pt='Teste', description_pt='Teste', language=Exercise.Language.PYTHON, published=True, private_tests='[{"stdin":"", "expected_stdout":"ok"}]')
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        url = reverse('evaluate_exercise', args=[exercise.pk])
        self.assertEqual(client.post(url, data='{"code":"x"}', content_type='application/json').status_code, 403)
        client.get(reverse('home'))
        response = client.post(url, data='{"code":"x"}', content_type='application/json', HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value)
        self.assertEqual(response.status_code, 200)


from .forms import ExerciseAdminForm
from .exercise_tests import parse_private_tests


class PrivateTestValidationTests(TestCase):
    def setUp(self):
        course = Course.objects.create(slug='validacao', title='Curso', description='Descrição', category=Course.Category.PROGRAMACAO)
        self.lesson = Lesson.objects.create(course=course, title='Aula', content='Conteúdo')
        self.data = {'lesson': self.lesson.pk, 'title_pt': 'Exercício', 'description_pt': 'Descrição', 'language': 'python', 'order': 1}

    def test_admin_form_accepts_valid_tests_and_empty_drafts(self):
        for value in ('', '[{"stdin":"", "expected_stdout":"ok\\n"}]'):
            form = ExerciseAdminForm(data={**self.data, 'private_tests': value})
            self.assertTrue(form.is_valid(), form.errors)

    def test_admin_form_rejects_invalid_cases_without_disclosing_secret(self):
        for value in ('not json SECRET', '[]', '{}', '[{"stdin": 1, "expected_stdout": "x"}]', '[{"stdin":"x"}]', '[{"stdin":"' + 'x' * 4001 + '", "expected_stdout":"y"}]'):
            form = ExerciseAdminForm(data={**self.data, 'private_tests': value})
            self.assertFalse(form.is_valid())
            self.assertIn('private_tests', form.errors)
            self.assertNotIn('SECRET', str(form.errors))

    def test_parser_returns_cases_for_executor(self):
        cases = [{'stdin': 'entrada', 'expected_stdout': 'saída'}]
        self.assertEqual(parse_private_tests(json.dumps(cases)), cases)

    def test_admin_rejects_invalid_submission(self):
        admin = get_user_model().objects.create_superuser('admin-test', password='ExamplePassword123!')
        self.client.force_login(admin)
        response = self.client.post('/admin/learning/exercise/add/', {**self.data, 'private_tests': 'inválido'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Os testes privados devem ser JSON válido.')
        self.assertFalse(Exercise.objects.filter(title_pt='Exercício').exists())


class PhaseOneAcceptanceTests(TestCase):
    def test_account_validation_uses_chosen_django_language(self):
        self.client.cookies['django_language'] = 'en'
        response = self.client.post(reverse('register'), {'username': 'newuser', 'password1': '123', 'password2': '123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This password is too short')
        self.client.cookies['django_language'] = 'pt'
        response = self.client.post(reverse('register'), {'username': 'newuser', 'password1': '123', 'password2': '123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Esta palavra-passe é demasiado curta.')

    def test_teacher_can_publish_bilingual_course_and_student_retrieve_it(self):
        admin = get_user_model().objects.create_superuser('professor', password='StrongAdminPassword123!')
        self.client.force_login(admin)
        response = self.client.post('/admin/learning/course/add/', {
            'slug': 'curso-teste', 'title': 'Curso piloto', 'description': 'Descrição',
            'title_en': 'Pilot course', 'description_en': 'Description',
            'category': Course.Category.PROGRAMACAO, 'level': 'Iniciante', 'icon': 'Py',
            'color': Course.Color.ORANGE, 'published': 'on',
            'lessons-TOTAL_FORMS': '0', 'lessons-INITIAL_FORMS': '0',
            'lessons-MIN_NUM_FORMS': '0', 'lessons-MAX_NUM_FORMS': '1000',
        })
        self.assertEqual(response.status_code, 302, response.context and response.context.get('errors'))
        course = Course.objects.get(slug='curso-teste')
        lesson = Lesson.objects.create(course=course, title='Aula', content='Texto', title_en='Lesson', content_en='Text', published=True)
        Exercise.objects.create(lesson=lesson, title_pt='Exercício', description_pt='Enunciado', title_en='Exercise', description_en='Prompt', language=Exercise.Language.PYTHON, private_tests='[{"stdin":"", "expected_stdout":"segredo"}]', published=True)
        self.client.logout()
        response = self.client.get(reverse('catalog'))
        data = response.json()['courses'][0]
        self.assertEqual((data['title_en'], data['lessons'][0]['title_en']), ('Pilot course', 'Lesson'))
        self.assertNotIn('segredo', response.content.decode())
