import json
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Course, Exercise, LabCooldown, Lesson
from .runner import RunnerError, language_ids, run_test, runner_configured


@override_settings(LAB_RUNNER_ENABLED=True, LAB_RUNNER_URL='https://sandbox.example.test', LAB_RUNNER_TOKEN='secret')
class LabPhaseTwoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('lab', password='PasswordSecure123!')
        course = Course.objects.create(slug='test-lab', title='Course', description='Description', category=Course.Category.PROGRAMACAO, published=True)
        lesson = Lesson.objects.create(course=course, title='Lesson', content='Text', published=True)
        self.exercise = Exercise.objects.create(lesson=lesson, title_pt='Test', description_pt='Prompt', language='python', published=True, private_tests=json.dumps([{'stdin': 'private', 'expected_stdout': 'secret'}]))
        self.url = reverse('evaluate_exercise', args=[self.exercise.pk])
        self.client.force_login(self.user)

    @patch('learning.runner.run_test', return_value=True)
    def test_cooldown_is_shared_across_sessions_and_expires(self, runner):
        other = Client()
        other.force_login(self.user)
        payload = json.dumps({'code': 'print(1)'})
        self.assertEqual(self.client.post(self.url, payload, content_type='application/json').status_code, 200)
        response = other.post(self.url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response['Retry-After'], '30')
        LabCooldown.objects.filter(user=self.user).update(next_allowed_at=timezone.now() - timedelta(seconds=1))
        self.assertEqual(other.post(self.url, payload, content_type='application/json').status_code, 200)
        self.assertEqual(runner.call_count, 2)
        self.assertNotIn('secret', response.content.decode())

    @patch('learning.runner.run_test', side_effect=RunnerError('private diagnostic'))
    def test_runner_failure_does_not_leak_and_consumes_cooldown(self, runner):
        payload = json.dumps({'code': 'print(1)'})
        response = self.client.post(self.url, payload, content_type='application/json')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'error': 'runner_unavailable'})
        self.assertEqual(self.client.post(self.url, payload, content_type='application/json').status_code, 429)

    @override_settings(LAB_LANGUAGE_IDS='{"python": 71}')
    def test_incomplete_mapping_disables_both_catalog_and_endpoint(self):
        self.assertFalse(self.client.get(reverse('catalog')).json()['runner_enabled'])
        self.assertEqual(self.client.post(self.url, json.dumps({'code': 'x'}), content_type='application/json').status_code, 503)
        self.assertFalse(LabCooldown.objects.filter(user=self.user).exists())

    @override_settings(LAB_RUNNER_URL='https://sandbox.example.test:8443')
    def test_invalid_runner_url_fails_closed(self):
        self.assertFalse(runner_configured())
        self.assertFalse(self.client.get(reverse('catalog')).json()['runner_enabled'])

    @override_settings(LAB_LANGUAGE_IDS='{"python":1,"javascript":2,"java":3,"csharp":4,"ruby":5}')
    @patch('learning.runner.urllib.request.build_opener')
    def test_all_language_ids_configurable(self, opener):
        response = opener.return_value.open.return_value.__enter__.return_value
        response.read.return_value = b'{"status":{"id":3}}'
        for name, expected in [('python',1), ('javascript',2), ('java',3), ('csharp',4), ('ruby',5)]:
            self.assertTrue(run_test(name, 'code', '', ''))
            payload = json.loads(opener.return_value.open.call_args.args[0].data)
            self.assertEqual(payload['language_id'], expected)
        self.assertEqual(len(language_ids()), 5)

    @patch('learning.runner.urllib.request.build_opener')
    def test_pending_internal_and_unknown_statuses_are_infrastructure_errors(self, opener):
        response = opener.return_value.open.return_value.__enter__.return_value
        for status in [1, 2, 13, 14, 99, True]:
            response.read.return_value = json.dumps({'status': {'id': status}}).encode()
            with self.subTest(status=status), self.assertRaises(RunnerError):
                run_test('python', 'code', '', '')
        response.read.return_value = b'{"status":{"id":4}}'
        self.assertFalse(run_test('python', 'code', '', ''))


from io import StringIO
from django.core.management import call_command, CommandError


class LabVerificationCommandTests(TestCase):
    def test_requires_explicit_confirmation_and_enabled_runner(self):
        with self.assertRaises(CommandError):
            call_command('verify_lab', stdout=StringIO())
        with override_settings(LAB_RUNNER_ENABLED=False):
            with self.assertRaises(CommandError):
                call_command('verify_lab', confirm_isolated=True, stdout=StringIO())

    @override_settings(LAB_RUNNER_ENABLED=True, LAB_RUNNER_URL='https://sandbox.example.test', LAB_RUNNER_TOKEN='secret')
    @patch('learning.management.commands.verify_lab.run_test', return_value=True)
    def test_verification_uses_only_five_fixed_programs(self, runner):
        output = StringIO()
        call_command('verify_lab', confirm_isolated=True, stdout=output)
        self.assertEqual(runner.call_count, 5)
        self.assertEqual([call.args[0] for call in runner.call_args_list], ['python', 'javascript', 'java', 'csharp', 'ruby'])
        self.assertIn('NÃO comprova isolamento', output.getvalue())

    @override_settings(LAB_RUNNER_ENABLED=True, LAB_RUNNER_URL='https://sandbox.example.test', LAB_RUNNER_TOKEN='secret')
    @patch('learning.management.commands.verify_lab.run_test', return_value=False)
    def test_verification_fails_when_runtime_does_not_pass(self, runner):
        with self.assertRaises(CommandError):
            call_command('verify_lab', confirm_isolated=True, stdout=StringIO())
