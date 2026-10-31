#!/usr/bin/env python3
"""Smoke test against localhost using fixed trusted programs only.

This is not a sandbox security test and does not run submitted student code.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

import manage_config

BASE_URL = 'http://127.0.0.1:2358'
DEFAULT_IDS = {'python': 71, 'javascript': 63, 'java': 62, 'csharp': 51, 'ruby': 72}
PROGRAMS = {
    'python': ('python', 'print("ondjango")'),
    'javascript': ('javascript', 'console.log("ondjango");'),
    'java': ('java', 'class Main { public static void main(String[] args) { System.out.println("ondjango"); } }'),
    'csharp': ('c#', 'using System; class Program { static void Main() { Console.WriteLine("ondjango"); } }'),
    'ruby': ('ruby', 'puts "ondjango"'),
}


class SmokeError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_json(method, path, token=None, payload=None):
    """Never follow redirects or connect to a non-loopback service."""
    headers = {'Accept': 'application/json'}
    data = None
    if token:
        headers['X-Auth-Token'] = token
    if payload is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=15) as response:
            status = response.status
            body = response.read(65537)
        if len(body) > 65536:
            raise SmokeError('Resposta demasiado grande.')
        return status, json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        # Return only the status; do not expose server diagnostics or headers.
        return exc.code, None
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        raise SmokeError('Não foi possível contactar ou interpretar o executor local.') from exc


def parse_language_ids(value):
    try:
        ids = json.loads(value) if value else DEFAULT_IDS
    except (TypeError, ValueError) as exc:
        raise SmokeError('LAB_LANGUAGE_IDS não é JSON válido.') from exc
    if (not isinstance(ids, dict) or set(ids) != set(PROGRAMS)
            or any(type(value) is not int or value <= 0 for value in ids.values())
            or len(set(ids.values())) != len(ids)):
        raise SmokeError('LAB_LANGUAGE_IDS precisa de cinco IDs inteiros, positivos e distintos.')
    return ids


def submission_status(result):
    if not isinstance(result, dict) or not isinstance(result.get('status'), dict):
        return None
    value = result['status'].get('id')
    return value if type(value) is int else None


def run_checks(token, ids, send=request_json, output=print):
    status, _ = send('GET', '/languages')
    if status != 401:
        raise SmokeError('A API não recusou acesso sem autenticação; interrompido.')
    output('Autenticação obrigatória: OK')
    status, languages = send('GET', '/languages', token=token)
    if status != 200 or not isinstance(languages, list):
        raise SmokeError('Não foi possível obter a lista autenticada de linguagens.')
    available = {item['id']: item.get('name', '') for item in languages if isinstance(item, dict) and type(item.get('id')) is int}
    for language, (name_fragment, _) in PROGRAMS.items():
        name = available.get(ids[language])
        if not isinstance(name, str) or name_fragment not in name.lower():
            raise SmokeError(f'ID de {language} não corresponde à linguagem esperada; confirma os IDs.')
    output('IDs das cinco linguagens: OK (versões precisam de revisão manual)')
    for language, (_, code) in PROGRAMS.items():
        payload = {
            'language_id': ids[language], 'source_code': code,
            'stdin': '', 'expected_output': 'ondjango\n',
            'cpu_time_limit': 2, 'wall_time_limit': 5, 'memory_limit': 128000,
            'max_processes_and_or_threads': 32, 'enable_network': False,
        }
        status, result = send('POST', '/submissions?base64_encoded=false&wait=true', token=token, payload=payload)
        if status not in (200, 201) or submission_status(result) != 3:
            raise SmokeError(f'Teste de {language} falhou ou não terminou; verifica runtime e limites.')
        output(f'{language}: OK')
    # A wrong expected output must not be reported as accepted.
    payload = {
        'language_id': ids['python'], 'source_code': PROGRAMS['python'][1],
        'stdin': '', 'expected_output': 'resultado diferente\n',
        'cpu_time_limit': 2, 'wall_time_limit': 5, 'memory_limit': 128000,
        'max_processes_and_or_threads': 32, 'enable_network': False,
    }
    status, result = send('POST', '/submissions?base64_encoded=false&wait=true', token=token, payload=payload)
    if status not in (200, 201) or submission_status(result) != 4:
        raise SmokeError('O teste de resposta incorreta não foi rejeitado como esperado.')
    output('Resposta incorreta: rejeitada')
    output('Verificação funcional concluída; NÃO comprova isolamento ou segurança.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--confirm-vm', action='store_true', help='Confirma que estás numa VM de teste dedicada e isolada.')
    args = parser.parse_args()
    if not args.confirm_vm:
        print('Executa apenas numa VM de teste isolada e confirma com --confirm-vm.', file=sys.stderr)
        return 1
    try:
        conf = manage_config.CONFIG
        if os.stat(conf).st_mode & 0o077:
            raise SmokeError('Restringe as permissões de judge0.conf a 0600.')
        values = manage_config.validate(conf.read_text(encoding='utf-8'))
        ids = parse_language_ids(os.environ.get('LAB_LANGUAGE_IDS'))
        run_checks(values['AUTHN_TOKEN'], ids)
    except (OSError, ValueError, SmokeError) as exc:
        print(f'Teste interrompido: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
