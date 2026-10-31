"""Adapter for a separately deployed, operator-managed Judge0 sandbox.

Django must never execute student code itself. Enabling the adapter is not a
substitute for hardening and independently verifying the sandbox deployment.
"""
import json
import urllib.error
import urllib.request
from django.conf import settings


LANGUAGE_IDS = {'python': 71, 'javascript': 63, 'java': 62, 'csharp': 51, 'ruby': 72}


class RunnerError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def run_test(language, code, stdin, expected):
    payload = {
        'language_id': LANGUAGE_IDS[language], 'source_code': code,
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
        if not isinstance(status, int) or status in (1, 2):
            raise RunnerError('O executor não terminou o teste')
        # Never return stdout, stderr, compile output, input or expected output to clients.
        return status == 3
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError) as exc:
        raise RunnerError('Executor indisponível') from exc
