import tempfile
from pathlib import Path
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from .models import Course, Lesson


MP4 = b'\x00\x00\x00\x18ftypisom' + b'test video data'


class AuthorTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.field = Lesson._meta.get_field('video_file')
        old_storage = self.field.storage
        self.field.storage = FileSystemStorage(location=self.temp.name)
        self.addCleanup(setattr, self.field, 'storage', old_storage)
        User = get_user_model()
        self.author = User.objects.create_user('autor1', password='StrongPassword123!')
        self.other = User.objects.create_user('autor2', password='StrongPassword123!')
        self.student = User.objects.create_user('aluno', password='StrongPassword123!')
        permission = Permission.objects.get(content_type__app_label='learning', codename='can_author')
        self.author.user_permissions.add(permission)
        self.other.user_permissions.add(permission)
        self.course = Course.objects.create(slug='meu-curso', title='Meu curso', description='Descrição', category=Course.Category.PROGRAMACAO, author=self.author)
        self.lesson = Lesson.objects.create(course=self.course, title='Aula', content='Texto')
        self.url = reverse('author_lesson_edit', args=[self.course.pk, self.lesson.pk])
        self.data = {'title': 'Aula', 'content': 'Texto', 'order': 1, 'video_url': ''}

    def video(self, name='lesson.mp4', data=MP4):
        return SimpleUploadedFile(name, data, content_type='video/mp4')

    def test_permissions_and_owner_isolation(self):
        self.assertRedirects(self.client.get(reverse('author_dashboard')), reverse('login') + '?next=/autor/')
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse('author_dashboard')).status_code, 403)
        self.assertEqual(self.client.post(reverse('author_course_create'), {}).status_code, 403)
        self.client.force_login(self.other)
        for url in (reverse('author_course_edit', args=[self.course.pk]), self.url, reverse('author_lesson_create', args=[self.course.pk])):
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, self.data).status_code, 404)
        self.assertNotContains(self.client.get(reverse('author_dashboard')), 'Meu curso')

    def test_author_creates_course_with_immutable_owner(self):
        self.client.force_login(self.author)
        response = self.client.post(reverse('author_course_create'), {
            'title': 'Novo', 'slug': 'novo', 'description': 'Descrição', 'category': Course.Category.PROGRAMACAO,
            'level': 'Iniciante', 'author': self.other.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Course.objects.get(slug='novo').author, self.author)

    def test_upload_draft_access_and_published_playback_with_ranges(self):
        self.client.force_login(self.author)
        response = self.client.post(self.url, {**self.data, 'video_file': self.video()})
        self.assertEqual(response.status_code, 302)
        self.lesson.refresh_from_db()
        self.assertTrue(self.lesson.video_file.name)
        self.assertTrue(Path(self.temp.name, self.lesson.video_file.name).exists())
        self.assertContains(self.client.get(self.url), 'Esta aula já tem um vídeo enviado.')
        video_url = reverse('lesson_video', args=[self.lesson.pk])
        self.assertEqual(self.client.get(video_url, HTTP_RANGE='bytes=4-7').status_code, 206)
        owner_response = self.client.get(video_url, HTTP_RANGE='bytes=4-7')
        self.assertEqual(b''.join(owner_response.streaming_content), MP4[4:8])
        self.client.logout()
        self.assertEqual(self.client.get(video_url).status_code, 404)
        self.lesson.published = True
        self.lesson.save()
        self.assertEqual(self.client.get(video_url).status_code, 404)  # Course is still a draft.
        self.course.published = True
        self.course.save()
        response = self.client.get(video_url, HTTP_RANGE='bytes=0-3')
        self.assertEqual(response.status_code, 206)
        self.assertEqual(response['Content-Range'], f'bytes 0-3/{len(MP4)}')
        self.assertEqual(b''.join(response.streaming_content), MP4[:4])
        self.assertEqual(self.client.get(video_url, HTTP_RANGE='bytes=99999-').status_code, 416)
        self.assertEqual(self.client.head(video_url)['Content-Length'], str(len(MP4)))
        self.assertEqual(self.client.get(reverse('catalog')).json()['courses'][0]['lessons'][0]['video']['url'], video_url)

    def test_invalid_file_oversize_and_conflicting_sources_rejected(self):
        self.client.force_login(self.author)
        response = self.client.post(self.url, {**self.data, 'video_file': self.video(data=b'<html>not video</html>')})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usa um ficheiro MP4 ou WebM válido.')
        with override_settings(MAX_VIDEO_BYTES=10):
            response = self.client.post(self.url, {**self.data, 'video_file': self.video()})
            self.assertContains(response, 'O ficheiro não pode ultrapassar 100 MB.')
        response = self.client.post(self.url, {**self.data, 'video_url': 'https://vimeo.com/123', 'video_file': self.video()})
        self.assertContains(response, 'Escolhe apenas um vídeo enviado ou um link externo por aula.')
        self.lesson.refresh_from_db()
        self.assertFalse(self.lesson.video_file)

    def test_replace_and_remove_file_after_commit(self):
        self.client.force_login(self.author)
        self.client.post(self.url, {**self.data, 'video_file': self.video()})
        self.lesson.refresh_from_db()
        old = self.lesson.video_file.name
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.client.post(self.url, {**self.data, 'video_file': self.video()}).status_code, 302)
        self.lesson.refresh_from_db()
        replacement = self.lesson.video_file.name
        self.assertNotEqual(old, replacement)
        self.assertFalse(Path(self.temp.name, old).exists())
        with self.captureOnCommitCallbacks(execute=True):
            self.assertEqual(self.client.post(self.url, {**self.data, 'remove_video': 'on'}).status_code, 302)
        self.lesson.refresh_from_db()
        self.assertFalse(self.lesson.video_file)
        self.assertFalse(Path(self.temp.name, replacement).exists())

    def test_csrf_protects_upload(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.author)
        self.assertEqual(client.post(self.url, {**self.data, 'video_file': self.video()}).status_code, 403)
        client.get(self.url)
        token = client.cookies['csrftoken'].value
        self.assertEqual(client.post(self.url, {**self.data, 'video_file': self.video()}, HTTP_X_CSRFTOKEN=token).status_code, 302)

    def test_deleting_lesson_cleans_video_after_commit(self):
        self.client.force_login(self.author)
        self.client.post(self.url, {**self.data, 'video_file': self.video()})
        self.lesson.refresh_from_db()
        name = self.lesson.video_file.name
        with self.captureOnCommitCallbacks(execute=True):
            self.lesson.delete()
        self.assertFalse(Path(self.temp.name, name).exists())

    def test_range_suffix_and_malformed_requests(self):
        self.client.force_login(self.author)
        self.client.post(self.url, {**self.data, 'video_file': self.video()})
        url = reverse('lesson_video', args=[self.lesson.pk])
        response = self.client.get(url, HTTP_RANGE='bytes=-4')
        self.assertEqual(response.status_code, 206)
        self.assertEqual(b''.join(response.streaming_content), MP4[-4:])
        self.assertEqual(self.client.get(url, HTTP_RANGE='bytes=0-1,4-5').status_code, 416)
        self.assertEqual(self.client.get(url, HTTP_RANGE='bytes=' + '9' * 100 + '-').status_code, 416)

    def test_author_manages_exercises_only_in_owned_lessons(self):
        from .models import Exercise
        self.client.force_login(self.author)
        create_url = reverse('author_exercise_create', args=[self.course.pk, self.lesson.pk])
        data = {'title_pt': 'Soma', 'description_pt': 'Somar', 'title_en': 'Sum', 'description_en': 'Add', 'language': 'python', 'starter_code': '', 'private_tests': '[{"stdin":"2", "expected_stdout":"2"}]', 'order': '1', 'published': 'on', 'lesson': '9999'}
        self.assertEqual(self.client.post(create_url, data).status_code, 302)
        exercise = Exercise.objects.get(title_pt='Soma')
        self.assertEqual(exercise.lesson_id, self.lesson.id)
        self.assertContains(self.client.get(reverse('author_dashboard')), 'Soma')
        edit_url = reverse('author_exercise_edit', args=[self.course.pk, self.lesson.pk, exercise.pk])
        response = self.client.post(edit_url, {**data, 'title_pt': 'Nova soma', 'private_tests': 'invalido'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Os testes privados devem ser JSON válido.')
        exercise.refresh_from_db()
        self.assertEqual(exercise.title_pt, 'Soma')
        self.assertEqual(self.client.post(edit_url, {**data, 'title_pt': 'Nova soma'}).status_code, 302)
        exercise.refresh_from_db()
        self.assertEqual(exercise.title_pt, 'Nova soma')
        self.client.force_login(self.other)
        for url in (create_url, edit_url):
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, data).status_code, 404)
        self.client.force_login(self.student)
        self.assertEqual(self.client.post(create_url, data).status_code, 403)

    def test_exercise_private_tests_not_in_public_catalog(self):
        from .models import Exercise
        self.course.published = True
        self.course.save()
        self.lesson.published = True
        self.lesson.save()
        Exercise.objects.create(lesson=self.lesson, title_pt='A', description_pt='B', language='python', private_tests='[{"stdin":"", "expected_stdout":"SUPERSECRETO"}]', published=True)
        response = self.client.get(reverse('catalog'))
        self.assertNotContains(response, 'SUPERSECRETO')

    def test_csrf_protects_exercise_editor(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.author)
        url = reverse('author_exercise_create', args=[self.course.pk, self.lesson.pk])
        data = {'title_pt': 'A', 'description_pt': 'B', 'language': 'python', 'order': 1}
        self.assertEqual(client.post(url, data).status_code, 403)
        client.get(url)
        self.assertEqual(client.post(url, data, HTTP_X_CSRFTOKEN=client.cookies['csrftoken'].value).status_code, 302)

    def test_author_to_student_published_course_flow(self):
        self.client.force_login(self.author)
        course_data = {'title': 'Curso pronto', 'slug': 'curso-pronto', 'description': 'Conteúdo', 'title_en': 'Ready course', 'description_en': 'Content', 'category': Course.Category.PROGRAMACAO, 'level': 'Iniciante', 'published': 'on'}
        self.assertEqual(self.client.post(reverse('author_course_create'), course_data).status_code, 302)
        course = Course.objects.get(slug='curso-pronto')
        lesson_url = reverse('author_lesson_create', args=[course.pk])
        self.assertEqual(self.client.post(lesson_url, {'title': 'Lição', 'content': 'Texto', 'title_en': 'Lesson', 'content_en': 'Text', 'order': 1, 'published': 'on'}).status_code, 302)
        lesson = course.lessons.get()
        exercise_url = reverse('author_exercise_create', args=[course.pk, lesson.pk])
        exercise_data = {'title_pt': 'Exercício', 'description_pt': 'Enunciado', 'language': 'python', 'order': 1, 'published': 'on', 'private_tests': '[{"stdin":"", "expected_stdout":"SEGREDO"}]'}
        self.assertEqual(self.client.post(exercise_url, exercise_data).status_code, 302)
        self.client.force_login(self.student)
        result = self.client.get(reverse('catalog'))
        course_payload = next(c for c in result.json()['courses'] if c['id'] == 'curso-pronto')
        self.assertEqual(course_payload['lessons'][0]['exercises'][0]['title'], 'Exercício')
        self.assertNotContains(result, 'SEGREDO')
        self.assertEqual(self.client.post(reverse('complete_lesson', args=[lesson.pk])).status_code, 200)
        another_device = Client()
        another_device.force_login(self.student)
        self.assertIn(lesson.pk, another_device.get(reverse('progress')).json()['completed'])
