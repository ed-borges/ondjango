"""Adapter for a separately deployed, operator-managed Judge0 sandbox.

Django never executes student code. Enabling this adapter does not replace
independent hardening and verification of the sandbox deployment.
"""
import json
import urllib.error
import urllib.request
from urllib.parse import urlsplit
from django.conf import settings


LANGUAGES = frozenset({'python', 'javascript', 'java', 'csharp', 'ruby'})


class RunnerError(Exception):
    pass


def language_ids():
    try:
        mapping = json.loads(settings.LAB_LANGUAGE_IDS)
        if (not isinstance(mapping, dict) or set(mapping) != LANGUAGES
                or any(type(value) is not int or value <= 0 for value in mapping.values())
                or len(set(mapping.values())) != len(LANGUAGES)):
            return None
        return mapping
    except (ValueError, TypeError):
        return None


def runner_configured():
    try:
        parts = urlsplit(settings.LAB_RUNNER_URL)
        return bool(settings.LAB_RUNNER_ENABLED and settings.LAB_RUNNER_TOKEN and language_ids()
                    and parts.scheme == 'https' and parts.hostname and not parts.username
                    and not parts.password and not parts.query and not parts.fragment
                    and parts.port in (None, 443))
    except (TypeError, ValueError):
        return False


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def run_test(language, code, stdin, expected):
    mapping = language_ids()
    if not mapping or language not in mapping:
        raise RunnerError('Linguagem não configurada')
    payload = {
        'language_id': mapping[language], 'source_code': code,
        'stdin': stdin, 'expected_output': expected,
        'cpu_time_limit': 2, 'wall_time_limit': 5, 'memory_limit': 128000,
        'max_processes_and_or_threads': 32, 'enable_network': False,
    }
    request = urllib.request.Request(
        settings.LAB_RUNNER_URL.rstrip('/') + '/submissions?base64_encoded=false&wait=true',
        data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json',
            'X-Auth-Token': settings.LAB_RUNNER_TOKEN}, method='POST',
    )
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=10) as response:
            raw = response.read(65537)
        if len(raw) > 65536:
            raise RunnerError('Resposta do executor demasiado grande')
        result = json.loads(raw)
        status = result['status']['id']
        # Pending, infrastructure errors and unknown statuses are not failed tests.
        if type(status) is not int or status not in range(3, 13):
            raise RunnerError('O executor não terminou corretamente')
        # No stdout, stderr, compiler output, inputs or expected output go to clients.
        return status == 3
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        raise RunnerError('Executor indisponível') from exc
