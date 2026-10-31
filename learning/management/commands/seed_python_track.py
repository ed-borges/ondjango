import json

from django.core.management.base import BaseCommand
from django.db import transaction

from learning.content.python_path import TRACK
from learning.content.python_en import TRANSLATIONS
from learning.models import Course, Exercise, Lesson, LearningPath, LearningPathCourse


class Command(BaseCommand):
    help = 'Adiciona a trilha piloto de Python sem alterar cursos existentes.'

    @transaction.atomic
    def handle(self, *args, **options):
        for item in TRACK:
            course, created = Course.objects.get_or_create(slug=item['slug'], defaults={
                'title': item['title'], 'description': item['description'],
                'title_en': TRANSLATIONS[item['slug']]['title'],
                'description_en': TRANSLATIONS[item['slug']]['description'],
                'category': Course.Category.PROGRAMACAO, 'level': item['level'],
                'color': item['color'], 'icon': 'Py', 'published': True,
            })
            if not created:
                self.stdout.write(f'Ignorado: {item["slug"]} já existe; conteúdo preservado.')
                continue
            for order, data in enumerate(item['lessons'], 1):
                translated = TRANSLATIONS[item['slug']]['lessons'][order - 1]
                lesson = Lesson.objects.create(course=course, title=data['title'], content=data['content'], title_en=translated[0], content_en=translated[1], order=order, published=True)
                title, description, starter_code, tests = data['exercise']
                Exercise.objects.create(
                    lesson=lesson, title_pt=title, description_pt=description, title_en=translated[2], description_en=translated[3],
                    language=Exercise.Language.PYTHON, starter_code=starter_code,
                    private_tests=json.dumps([{'stdin': stdin, 'expected_stdout': stdout} for stdin, stdout in tests], ensure_ascii=False),
                    published=True,
                )
            self.stdout.write(self.style.SUCCESS(f'Criado: {course.title} ({len(item["lessons"])} aulas).'))

        path, created = LearningPath.objects.get_or_create(slug='python', defaults={
            'title': 'Trilha de Python',
            'description': 'Do básico ao avançado: aprende conceitos e pratica ao teu ritmo.',
            'title_en': 'Python learning path',
            'description_en': 'From beginner to advanced: learn concepts and practise at your own pace.',
            'published': True,
        })
        if created:
            for order, item in enumerate(TRACK, 1):
                LearningPathCourse.objects.create(path=path, course=Course.objects.get(slug=item['slug']), order=order)
            self.stdout.write(self.style.SUCCESS('Trilha de Python criada.'))
        else:
            self.stdout.write('Trilha python já existe; configuração preservada.')
