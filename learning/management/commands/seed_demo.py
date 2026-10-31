from django.core.management.base import BaseCommand
from django.db import transaction
from learning.models import Course, Lesson


class Command(BaseCommand):
    help = 'Adiciona cursos demonstrativos sem substituir conteúdos existentes.'

    @transaction.atomic
    def handle(self, *args, **options):
        examples = [
            ('web', 'Introdução ao desenvolvimento web', 'Dá os primeiros passos e cria páginas para a internet.', 'PROGRAMAÇÃO', 'orange', '</>', ['Bem-vindo ao desenvolvimento web', 'Como funciona a web', 'A tua primeira página HTML', 'Conhecer o CSS']),
            ('design', 'Design para o mundo digital', 'Aprende a transformar boas ideias em experiências visuais.', 'CRIATIVIDADE', 'purple', '✳', ['O que é design digital?', 'Princípios visuais', 'Cor e tipografia', 'Criar a tua primeira composição']),
            ('business', 'Empreender com propósito', 'Transforma a tua ideia num negócio com impacto.', 'NEGÓCIOS', 'green', '↗', ['Toda a ideia começa com um problema', 'Conhece o teu público', 'Da ideia ao modelo de negócio', 'Os primeiros passos']),
            ('digital', 'Competências digitais essenciais', 'Domina as ferramentas digitais para o dia a dia.', 'TECNOLOGIA', 'blue', '⌘', ['Começar no mundo digital', 'Navegar com segurança', 'Ferramentas de produtividade', 'Comunicar online']),
        ]
        for slug, title, description, category, color, icon, lessons in examples:
            course, created = Course.objects.get_or_create(slug=slug, defaults={'title': title, 'description': description, 'category': category, 'color': color, 'icon': icon, 'published': True})
            if not created:
                self.stdout.write(f'Ignorado: {slug} já existe.')
                continue
            for index, lesson_title in enumerate(lessons, 1):
                Lesson.objects.create(course=course, title=lesson_title, order=index, published=True, content='Este é um conteúdo de demonstração. Edita esta aula no painel administrativo para adicionar o material de aprendizagem.')
            self.stdout.write(self.style.SUCCESS(f'Criado: {title}'))
