from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .exercise_tests import parse_private_tests
from .models import Exercise


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)


class ExerciseAdminForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = '__all__'

    def clean_private_tests(self):
        value = self.cleaned_data['private_tests']
        # Draft exercises can be saved without tests; evaluation requires them.
        if value:
            try:
                parse_private_tests(value)
            except ValueError as exc:
                raise forms.ValidationError(str(exc)) from exc
        return value


from pathlib import Path
from django.conf import settings
from .models import Course, Lesson


class AuthorCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'slug', 'description', 'title_en', 'description_en', 'category', 'level', 'published')


class AuthorLessonForm(forms.ModelForm):
    remove_video = forms.BooleanField(label='Remover vídeo enviado', required=False)

    class Meta:
        model = Lesson
        fields = ('title', 'content', 'title_en', 'content_en', 'order', 'published', 'video_url', 'video_file', 'remove_video')
        widgets = {'video_file': forms.FileInput(attrs={'accept': '.mp4,.webm,video/mp4,video/webm'})}

    def clean_video_file(self):
        video = self.cleaned_data.get('video_file')
        if not video or not hasattr(video, 'read') or not hasattr(video, 'content_type'):
            return video
        if video.size > settings.MAX_VIDEO_BYTES:
            raise forms.ValidationError('O ficheiro não pode ultrapassar 100 MB.')
        header = video.read(12)
        video.seek(0)
        extension = Path(video.name).suffix.lower()
        if not ((extension == '.mp4' and len(header) >= 12 and header[4:8] == b'ftyp') or
                (extension == '.webm' and header.startswith(b'\x1a\x45\xdf\xa3'))):
            raise forms.ValidationError('Usa um ficheiro MP4 ou WebM válido.')
        return video

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('remove_video'):
            if self.files.get('video_file'):
                raise forms.ValidationError('Não podes remover e enviar um novo vídeo ao mesmo tempo.')
            cleaned['video_file'] = False
        if cleaned.get('video_file') and cleaned.get('video_url'):
            raise forms.ValidationError('Escolhe apenas um vídeo enviado ou um link externo por aula.')
        return cleaned


class AdminLessonForm(AuthorLessonForm):
    class Meta(AuthorLessonForm.Meta):
        fields = ('course',) + AuthorLessonForm.Meta.fields


class AuthorExerciseForm(ExerciseAdminForm):
    class Meta:
        model = Exercise
        fields = ('title_pt', 'description_pt', 'title_en', 'description_en', 'language', 'starter_code', 'private_tests', 'order', 'published')
