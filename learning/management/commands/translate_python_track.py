from django.core.management.base import BaseCommand
from django.db import transaction
from learning.content.python_path import TRACK
from learning.content.python_en import TRANSLATIONS
from learning.models import Course, LearningPath


class Command(BaseCommand):
    help = 'Adiciona traduções inglesas da trilha piloto sem substituir dados ou traduzir conteúdo editado.'

    @transaction.atomic
    def handle(self, *args, **options):
        for source in TRACK:
            translation = TRANSLATIONS[source['slug']]
            course = Course.objects.filter(slug=source['slug']).first()
            if not course:
                self.stdout.write(f"Ignorado: {source['slug']} não existe.")
                continue
            if course.title == source['title'] and course.description == source['description'] and not course.title_en and not course.description_en:
                course.title_en, course.description_en = translation['title'], translation['description']
                course.save(update_fields=['title_en', 'description_en'])
            for order, (lesson_source, translated) in enumerate(zip(source['lessons'], translation['lessons']), 1):
                lesson = course.lessons.filter(order=order, title=lesson_source['title'], content=lesson_source['content']).first()
                if not lesson:
                    self.stdout.write(f"Ignorada: aula {order} de {source['slug']} foi alterada ou não existe.")
                    continue
                if not lesson.title_en and not lesson.content_en:
                    lesson.title_en, lesson.content_en = translated[0], translated[1]
                    lesson.save(update_fields=['title_en', 'content_en'])
                exercise_title, exercise_desc, _, _ = lesson_source['exercise']
                exercise = lesson.exercises.filter(title_pt=exercise_title, description_pt=exercise_desc).first()
                if exercise and not exercise.title_en and not exercise.description_en:
                    exercise.title_en, exercise.description_en = translated[2], translated[3]
                    exercise.save(update_fields=['title_en', 'description_en'])
        path = LearningPath.objects.filter(slug='python', title='Trilha de Python', description='Do básico ao avançado: aprende conceitos e pratica ao teu ritmo.', title_en='', description_en='').first()
        if path:
            path.title_en = 'Python learning path'
            path.description_en = 'From beginner to advanced: learn concepts and practise at your own pace.'
            path.save(update_fields=['title_en', 'description_en'])
        self.stdout.write(self.style.SUCCESS('Traduções disponíveis adicionadas; conteúdos editados foram preservados.'))
