"""Opt-in connectivity check using fixed, trusted programs (not student code)."""
from django.core.management.base import BaseCommand, CommandError
from learning.runner import RunnerError, run_status, runner_configured


PROGRAMS = {
    'python': 'print("ondjango")',
    'javascript': 'console.log("ondjango");',
    'java': 'class Main { public static void main(String[] args) { System.out.println("ondjango"); } }',
    'csharp': 'using System; class Program { static void Main() { Console.WriteLine("ondjango"); } }',
    'ruby': 'puts "ondjango"',
}


class Command(BaseCommand):
    help = 'Testa os cinco runtimes com programas fixos num executor isolado já configurado.'

    def add_arguments(self, parser):
        parser.add_argument('--confirm-isolated', action='store_true', help='Confirma que o executor externo já foi isolado e aprovado pelo operador.')

    def handle(self, *args, **options):
        if not options['confirm_isolated']:
            raise CommandError('Revê o isolamento primeiro e executa novamente com --confirm-isolated.')
        if not runner_configured():
            raise CommandError('Executor desativado ou configuração inválida.')
        failed = []
        for language, program in PROGRAMS.items():
            try:
                accepted = run_status(language, program, '', 'ondjango\n')
                # Require a genuine wrong-answer status, not just any failure.
                rejected = run_status(language, program, '', 'resultado diferente\n')
                passed = accepted == 3 and rejected == 4
            except RunnerError:
                passed = False
            if passed:
                self.stdout.write(self.style.SUCCESS(f'{language}: OK'))
            else:
                failed.append(language)
                self.stdout.write(self.style.ERROR(f'{language}: falhou ou indisponível'))
        if failed:
            raise CommandError('Falha na verificação: ' + ', '.join(failed))
        self.stdout.write('Respostas corretas e incorretas verificadas; este teste NÃO comprova isolamento ou segurança.')
