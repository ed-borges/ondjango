"""Tests the local smoke-test logic using fakes; no Docker or real sandbox."""
import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

DIRECTORY = Path(__file__).resolve().parent.parent / 'infra' / 'judge0'
with patch.object(sys, 'path', [str(DIRECTORY), *sys.path]):
    spec = importlib.util.spec_from_file_location('judge0_smoke_test', DIRECTORY / 'smoke_test.py')
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)


class LocalSmokeTests(SimpleTestCase):
    def mock_service(self, auth_required=True, wrong_status=4):
        calls = []
        names = {71: 'Python 3', 63: 'JavaScript Node', 62: 'Java', 51: 'C# Mono', 72: 'Ruby'}
        def send(method, path, token=None, payload=None):
            calls.append((method, path, token, payload))
            if path == '/languages' and not token:
                return (401 if auth_required else 200), None
            if path == '/languages':
                return 200, [{'id': k, 'name': v} for k, v in names.items()]
            if payload['expected_output'] == 'resultado diferente\n':
                return 201, {'status': {'id': wrong_status}}
            return 201, {'status': {'id': 3}}
        return send, calls

    def test_runs_five_fixed_languages_and_checks_wrong_answer(self):
        send, calls = self.mock_service()
        output = []
        smoke.run_checks('private-secret', smoke.DEFAULT_IDS, send=send, output=output.append)
        self.assertEqual(len(calls), 8)
        self.assertEqual([c[3]['language_id'] for c in calls[2:7]], [71, 63, 62, 51, 72])
        self.assertTrue(all(c[3]['enable_network'] is False for c in calls[2:]))
        self.assertNotIn('private-secret', '\n'.join(output))
        self.assertIn('NÃO comprova isolamento', output[-1])

    def test_refuses_unauthenticated_service(self):
        send, calls = self.mock_service(auth_required=False)
        with self.assertRaises(smoke.SmokeError):
            smoke.run_checks('secret', smoke.DEFAULT_IDS, send=send, output=lambda _: None)
        self.assertEqual(len(calls), 1)

    def test_detects_wrong_answer_that_is_not_rejected(self):
        send, _ = self.mock_service(wrong_status=3)
        with self.assertRaises(smoke.SmokeError):
            smoke.run_checks('secret', smoke.DEFAULT_IDS, send=send, output=lambda _: None)

    def test_invalid_language_mapping_is_rejected(self):
        for value in ('not json', '{"python": 1}', '{"python":1,"javascript":1,"java":3,"csharp":4,"ruby":5}'):
            with self.subTest(value=value), self.assertRaises(smoke.SmokeError):
                smoke.parse_language_ids(value)

    def test_result_with_unexpected_structure_fails_closed(self):
        self.assertIsNone(smoke.submission_status({'status': None}))
        self.assertIsNone(smoke.submission_status({'status': {'id': True}}))
