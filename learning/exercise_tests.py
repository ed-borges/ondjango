"""Parsing and validation of private stdin/stdout exercise test cases."""
import json


def parse_private_tests(value):
    """Return valid cases or raise ValueError; never include private data in errors."""
    try:
        cases = json.loads(value)
    except (ValueError, TypeError) as exc:
        raise ValueError('Os testes privados devem ser JSON válido.') from exc
    if not isinstance(cases, list) or not 1 <= len(cases) <= 3:
        raise ValueError('Indica entre um e três testes.')
    for case in cases:
        if (not isinstance(case, dict) or not isinstance(case.get('stdin'), str)
                or not isinstance(case.get('expected_stdout'), str)
                or len(case['stdin']) > 4000 or len(case['expected_stdout']) > 4000):
            raise ValueError('Cada teste deve ter stdin e expected_stdout como texto de até 4000 caracteres.')
    return cases
