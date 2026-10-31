from django.conf import settings
from django.db import models


class Course(models.Model):
    class Category(models.TextChoices):
        PROGRAMACAO = 'PROGRAMAÇÃO', 'Programação'
        CRIATIVIDADE = 'CRIATIVIDADE', 'Criatividade'
        NEGOCIOS = 'NEGÓCIOS', 'Negócios'
        TECNOLOGIA = 'TECNOLOGIA', 'Tecnologia'

    class Color(models.TextChoices):
        ORANGE = 'orange', 'Laranja'
        PURPLE = 'purple', 'Roxo'
        GREEN = 'green', 'Verde'
        BLUE = 'blue', 'Azul'

    slug = models.SlugField('identificador', unique=True, help_text='Mantém este identificador estável para preservar o progresso local.')
    title = models.CharField('título', max_length=200)
    description = models.TextField('descrição')
    category = models.CharField('categoria', max_length=30, choices=Category.choices)
    level = models.CharField('nível', max_length=50, default='Iniciante')
    duration = models.CharField('duração estimada', max_length=50, blank=True)
    icon = models.CharField('símbolo', max_length=20, default='✳')
    color = models.CharField('cor', max_length=20, choices=Color.choices, default=Color.ORANGE)
    published = models.BooleanField('publicado', default=False)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'pk']
        verbose_name = 'curso'
        verbose_name_plural = 'cursos'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name='curso', related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField('título', max_length=200)
    content = models.TextField('conteúdo', help_text='Texto simples; HTML não é interpretado.')
    order = models.PositiveIntegerField('ordem', default=1)
    published = models.BooleanField('publicada', default=False)

    class Meta:
        ordering = ['order', 'pk']
        verbose_name = 'aula'
        verbose_name_plural = 'aulas'

    def __str__(self):
        return self.title


class LessonCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_completions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'lesson'], name='unique_user_lesson_completion')]
        verbose_name = 'aula concluída'
        verbose_name_plural = 'aulas concluídas'
