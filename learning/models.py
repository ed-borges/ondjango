from django.conf import settings
from django.db import models, transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .video import validate_video_url
from .storage import PrivateVideoStorage, video_upload_path


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

    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='autor', null=True, blank=True, on_delete=models.SET_NULL, related_name='authored_courses')
    slug = models.SlugField('identificador', unique=True, help_text='Mantém este identificador estável para preservar o progresso local.')
    title = models.CharField('título', max_length=200)
    description = models.TextField('descrição')
    title_en = models.CharField('título em inglês', max_length=200, blank=True)
    description_en = models.TextField('descrição em inglês', blank=True)
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
        permissions = [('can_author', 'Pode criar e gerir os próprios cursos')]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name='curso', related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField('título', max_length=200)
    content = models.TextField('conteúdo', help_text='Texto simples; HTML não é interpretado.')
    title_en = models.CharField('título em inglês', max_length=200, blank=True)
    content_en = models.TextField('conteúdo em inglês', blank=True, help_text='Texto simples; HTML não é interpretado.')
    video_url = models.URLField('link da videoaula', blank=True, max_length=2048, validators=[validate_video_url], help_text='Opcional: link HTTPS do YouTube ou Vimeo, ou link direto MP4/WebM. O vídeo deve estar acessível aos alunos.')
    video_file = models.FileField('ficheiro de vídeo', storage=PrivateVideoStorage(), upload_to=video_upload_path, blank=True, max_length=255)
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


class Exercise(models.Model):
    class Language(models.TextChoices):
        PYTHON = 'python', 'Python'
        JAVASCRIPT = 'javascript', 'JavaScript'
        JAVA = 'java', 'Java'
        CSHARP = 'csharp', 'C#'
        RUBY = 'ruby', 'Ruby'

    lesson = models.ForeignKey(Lesson, verbose_name='aula', related_name='exercises', on_delete=models.CASCADE)
    title_pt = models.CharField('título em português', max_length=200)
    description_pt = models.TextField('enunciado em português')
    title_en = models.CharField('título em inglês', max_length=200, blank=True)
    description_en = models.TextField('enunciado em inglês', blank=True)
    language = models.CharField('linguagem de programação', max_length=20, choices=Language.choices)
    starter_code = models.TextField('código inicial', blank=True)
    private_tests = models.TextField('testes privados', blank=True, help_text='JSON privado: lista de até 3 objetos com stdin e expected_stdout. Nunca incluído no catálogo público.')
    order = models.PositiveIntegerField('ordem', default=1)
    published = models.BooleanField('publicado', default=False)

    class Meta:
        ordering = ['order', 'pk']
        verbose_name = 'exercício'
        verbose_name_plural = 'exercícios'

    def __str__(self):
        return self.title_pt


class LearningPath(models.Model):
    slug = models.SlugField('identificador', unique=True)
    title = models.CharField('título', max_length=200)
    description = models.TextField('descrição')
    title_en = models.CharField('título em inglês', max_length=200, blank=True)
    description_en = models.TextField('descrição em inglês', blank=True)
    published = models.BooleanField('publicada', default=False)
    courses = models.ManyToManyField(Course, through='LearningPathCourse', related_name='learning_paths')

    class Meta:
        ordering = ['title', 'pk']
        verbose_name = 'trilha'
        verbose_name_plural = 'trilhas'

    def __str__(self):
        return self.title


class LearningPathCourse(models.Model):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='steps', verbose_name='trilha')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='path_steps', verbose_name='curso')
    order = models.PositiveIntegerField('ordem', default=1)

    class Meta:
        ordering = ['order', 'pk']
        constraints = [
            models.UniqueConstraint(fields=['path', 'course'], name='unique_course_in_path'),
            models.UniqueConstraint(fields=['path', 'order'], name='unique_order_in_path'),
        ]
        verbose_name = 'etapa da trilha'
        verbose_name_plural = 'etapas da trilha'

    def __str__(self):
        return f'{self.path}: {self.course}'


@receiver(post_delete, sender=Lesson)
def delete_lesson_video_after_commit(sender, instance, **kwargs):
    name = instance.video_file.name
    if name:
        storage = instance._meta.get_field('video_file').storage
        transaction.on_commit(lambda: storage.delete(name))


class LabCooldown(models.Model):
    """Shared per-user submission cooldown; stores no code or private tests."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True, related_name='lab_cooldown')
    next_allowed_at = models.DateTimeField()
