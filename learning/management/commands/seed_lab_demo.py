from django.core.management.base import BaseCommand
from learning.models import Course, Exercise


class Command(BaseCommand):
    help = 'Adiciona um exercício demonstrativo à primeira aula do curso web, sem substituir dados existentes.'

    def handle(self, *args, **options):
        course = Course.objects.filter(slug='web').first()
        lesson = course.lessons.order_by('order', 'pk').first() if course else None
        if not lesson:
            self.stderr.write('Cria o curso demonstrativo primeiro com python manage.py seed_demo.')
            return
        exercise, created = Exercise.objects.get_or_create(
            lesson=lesson, title_pt='A tua primeira mensagem',
            defaults={
                'description_pt': 'Escreve um programa que mostre a mensagem Olá, Ondjango! no ecrã.',
                'title_en': 'Your first message',
                'description_en': 'Write a program that displays the message Olá, Ondjango! on screen.',
                'language': Exercise.Language.PYTHON,
                'starter_code': '# Escreve o teu código aqui\n',
                'private_tests': '[{"stdin": "", "expected_stdout": "Olá, Ondjango!\\n"}]',
                'published': True,
            },
        )
        self.stdout.write('Exercício criado.' if created else 'Exercício já existente; sem alterações.')
