#!/usr/bin/env python3
"""Generate/check a local Judge0 config without displaying generated secrets."""
import argparse
import os
import re
import secrets
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / 'judge0.conf'
TEMPLATE = HERE / 'judge0.conf.example'
SECRET_MARKERS = ('AUTH_TOKEN', 'REDIS_PASSWORD', 'POSTGRES_PASSWORD', 'SECRET_KEY')
REQUIRED = {
    'AUTHN_HEADER': 'X-Auth-Token', 'JUDGE0_TELEMETRY_ENABLE': 'false',
    'ENABLE_WAIT_RESULT': 'true', 'ENABLE_NETWORK': 'false', 'ALLOW_ENABLE_NETWORK': 'false',
    'ENABLE_ADDITIONAL_FILES': 'false', 'ENABLE_CALLBACKS': 'false',
    'ENABLE_COMPILER_OPTIONS': 'false', 'ENABLE_COMMAND_LINE_ARGUMENTS': 'false',
    'ENABLE_BATCHED_SUBMISSIONS': 'false', 'ENABLE_SUBMISSION_DELETE': 'false',
    'ALLOW_ENABLE_PER_PROCESS_AND_THREAD_TIME_LIMIT': 'false',
    'ALLOW_ENABLE_PER_PROCESS_AND_THREAD_MEMORY_LIMIT': 'false',
    'ENABLE_PER_PROCESS_AND_THREAD_TIME_LIMIT': 'false',
    'ENABLE_PER_PROCESS_AND_THREAD_MEMORY_LIMIT': 'false',
    'REDIS_HOST': 'redis', 'POSTGRES_HOST': 'db', 'POSTGRES_DB': 'judge0', 'POSTGRES_USER': 'judge0',
    'COUNT': '1', 'MAX_QUEUE_SIZE': '10',
    'CPU_TIME_LIMIT': '2', 'MAX_CPU_TIME_LIMIT': '2',
    'CPU_EXTRA_TIME': '0.5', 'MAX_CPU_EXTRA_TIME': '0.5',
    'WALL_TIME_LIMIT': '5', 'MAX_WALL_TIME_LIMIT': '5',
    'MEMORY_LIMIT': '128000', 'MAX_MEMORY_LIMIT': '128000',
    'STACK_LIMIT': '64000', 'MAX_STACK_LIMIT': '64000',
    'MAX_PROCESSES_AND_OR_THREADS': '32', 'MAX_MAX_PROCESSES_AND_OR_THREADS': '32',
    'MAX_FILE_SIZE': '1024', 'MAX_MAX_FILE_SIZE': '1024',
    'NUMBER_OF_RUNS': '1', 'MAX_NUMBER_OF_RUNS': '1',
}
SECRET_KEYS = ('AUTHN_TOKEN', 'REDIS_PASSWORD', 'POSTGRES_PASSWORD', 'SECRET_KEY_BASE')


def parse_config(text):
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            raise ValueError('Linha de configuração inválida.')
        key, value = line.split('=', 1)
        if not re.fullmatch(r'[A-Z][A-Z0-9_]*', key) or key in values:
            raise ValueError('Chave inválida ou repetida.')
        values[key] = value
    return values


def validate(text):
    values = parse_config(text)
    if any(values.get(key) != value for key, value in REQUIRED.items()):
        raise ValueError('As opções obrigatórias de proteção estão ausentes ou alteradas.')
    if any(not re.fullmatch(r'[0-9a-f]{64}', values.get(key, '')) for key in SECRET_KEYS):
        raise ValueError('Os segredos devem ser gerados com este utilitário.')
    if len({values[key] for key in SECRET_KEYS}) != len(SECRET_KEYS):
        raise ValueError('Os segredos devem ser independentes.')
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['create', 'check'])
    args = parser.parse_args()
    try:
        if args.action == 'create':
            content = TEMPLATE.read_text(encoding='utf-8')
            for marker in SECRET_MARKERS:
                content = content.replace('GENERATE_' + marker, secrets.token_hex(32))
            validate(content)
            # O_EXCL prevents accidental replacement and avoids races on creation.
            fd = os.open(CONFIG, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                stream.write(content)
            print('Configuração criada com permissões restritas; valores não exibidos.')
        else:
            validate(CONFIG.read_text(encoding='utf-8'))
            if os.stat(CONFIG).st_mode & 0o077:
                raise ValueError('Restringe as permissões do ficheiro: chmod 600 judge0.conf.')
            print('Verificação básica concluída. Isto não comprova isolamento ou segurança.')
    except (OSError, ValueError) as exc:
        # Do not print file contents or secrets.
        print(f'Não foi possível preparar/verificar a configuração: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
