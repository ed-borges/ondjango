"""Compalg exercises can be authored, but must never reach the Judge0 runner."""
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import AuthorExerciseForm
from .models import Course, Exercise, LabCooldown, Lesson


@override_settings(LAB_RUNNER_ENABLED=True, LAB_RUNNER_URL='https://sandbox.example.test', LAB_RUNNER_TOKEN='secret')
class CompalgPreparationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('author', password='StrongPass123!')
        course = Course.objects.create(slug='algoritmos', title='Algoritmos', description='Curso', category=Course.Category.PROGRAMACAO, published=True)
        self.lesson = Lesson.objects.create(course=course, title='Aula', content='Conteúdo', published=True)
        self.exercise = Exercise.objects.create(lesson=self.lesson, title_pt='Soma', description_pt='Soma dois valores', language=Exercise.Language.ALGORITMO, published=True, private_tests=json.dumps([{'stdin': '1\n2', 'expected_stdout': '3'}]))
        self.python = Exercise.objects.create(lesson=self.lesson, title_pt='Python', description_pt='Teste', language=Exercise.Language.PYTHON, published=True)

    def test_author_can_choose_algorithm(self):
        form = AuthorExerciseForm(data={'title_pt': 'Soma', 'description_pt': 'Soma', 'language': 'algoritmo', 'order': 1})
        self.assertTrue(form.is_valid(), form.errors)
        exercise = form.save(commit=False)
        exercise.lesson = self.lesson
        exercise.save()
        self.assertEqual(exercise.language, Exercise.Language.ALGORITMO)

    def test_catalog_reports_availability_per_exercise(self):
        exercises = self.client.get(reverse('catalog')).json()['courses'][0]['lessons'][0]['exercises']
        by_id = {entry['id']: entry for entry in exercises}
        self.assertFalse(by_id[self.exercise.pk]['runner_enabled'])
        self.assertTrue(by_id[self.python.pk]['runner_enabled'])
        self.assertNotIn('private_tests', by_id[self.exercise.pk])
        with override_settings(LAB_RUNNER_ENABLED=False):
            exercises = self.client.get(reverse('catalog')).json()['courses'][0]['lessons'][0]['exercises']
            self.assertTrue(all(not entry['runner_enabled'] for entry in exercises))

    @patch('learning.runner.run_test')
    def test_algorithm_is_never_sent_to_judge0_or_charged_cooldown(self, runner):
        self.client.force_login(self.user)
        response = self.client.post(reverse('evaluate_exercise', args=[self.exercise.pk]), json.dumps({'code': 'algoritmo'}), content_type='application/json')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'error': 'runner_unavailable'})
        runner.assert_not_called()
        self.assertFalse(LabCooldown.objects.filter(user=self.user).exists())
