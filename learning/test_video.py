from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import modelform_factory
from django.test import TestCase
from django.urls import reverse

from .models import Course, Lesson
from .video import validate_video_url, video_source


class VideoURLTests(TestCase):
    def test_supported_urls_are_canonicalized(self):
        cases = {
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=12': {'kind': 'youtube', 'url': 'https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ'},
            'https://youtu.be/dQw4w9WgXcQ': {'kind': 'youtube', 'url': 'https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ'},
            'https://www.youtube.com/shorts/dQw4w9WgXcQ': {'kind': 'youtube', 'url': 'https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ'},
            'https://vimeo.com/12345': {'kind': 'vimeo', 'url': 'https://player.vimeo.com/video/12345'},
            'https://player.vimeo.com/video/12345': {'kind': 'vimeo', 'url': 'https://player.vimeo.com/video/12345'},
            'https://cdn.example.com/video.webm?token=sample': {'kind': 'file', 'url': 'https://cdn.example.com/video.webm?token=sample'},
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(video_source(url), expected)
                validate_video_url(url)
        self.assertIsNone(video_source(''))
        validate_video_url('')

    def test_unsafe_or_unsupported_urls_are_rejected(self):
        urls = [
            'http://youtube.com/watch?v=dQw4w9WgXcQ',
            'javascript:alert(1)', 'https://evil.test/watch?v=dQw4w9WgXcQ',
            'https://youtube.com.evil.test/watch?v=dQw4w9WgXcQ',
            'https://youtube.com/watch?v=bad',
            'https://youtube.com/watch?v=dQw4w9WgXcQ&v=dQw4w9WgXcQ',
            'https://vimeo.com/not-a-video', 'https://vimeo.com/123/private',
            'https://player.vimeo.com/video/123?h=secret',
            'https://user:pass@cdn.example.com/video.mp4',
            'https://cdn.example.com/video.mp4#fragment',
            'https://cdn.example.com:444/video.mp4',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertIsNone(video_source(url))
                with self.assertRaises(ValidationError):
                    validate_video_url(url)

    def test_admin_model_form_enforces_validation(self):
        course = Course.objects.create(slug='curso', title='Curso', description='Descrição', category=Course.Category.PROGRAMACAO)
        form_class = modelform_factory(Lesson, fields=['course', 'title', 'content', 'video_url'])
        form = form_class({'course': course.pk, 'title': 'Aula', 'content': 'Texto', 'video_url': 'https://evil.example/watch'})
        self.assertFalse(form.is_valid())
        self.assertIn('video_url', form.errors)
        form = form_class({'course': course.pk, 'title': 'Aula', 'content': 'Texto', 'video_url': 'https://vimeo.com/12345'})
        self.assertTrue(form.is_valid(), form.errors)


class VideoCatalogTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(slug='publico', title='Curso', description='Descrição', category=Course.Category.PROGRAMACAO, published=True)
        self.lesson = Lesson.objects.create(course=self.course, title='Aula', content='Texto', video_url='https://youtu.be/dQw4w9WgXcQ', published=True)

    def test_catalog_returns_video_for_published_lesson(self):
        response = self.client.get(reverse('catalog'))
        lesson = response.json()['courses'][0]['lessons'][0]
        self.assertEqual(lesson['video'], {'kind': 'youtube', 'url': 'https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ'})
        self.assertNotIn('youtu.be', str(lesson))

    def test_hidden_lesson_course_and_invalid_stored_video_are_not_exposed(self):
        self.lesson.published = False
        self.lesson.save()
        self.assertEqual(self.client.get(reverse('catalog')).json()['courses'][0]['lessons'], [])
        self.lesson.published = True
        self.lesson.video_url = 'javascript:alert(1)'  # Simulate invalid direct database data.
        self.lesson.save()
        self.assertIsNone(self.client.get(reverse('catalog')).json()['courses'][0]['lessons'][0]['video'])
        self.course.published = False
        self.course.save()
        self.assertEqual(self.client.get(reverse('catalog')).json()['courses'], [])

    def test_admin_can_save_video_link(self):
        admin = get_user_model().objects.create_superuser('autor', password='StrongPassword123!')
        self.client.force_login(admin)
        response = self.client.post(f'/admin/learning/lesson/{self.lesson.pk}/change/', {
            'course': self.course.pk, 'title': 'Aula', 'content': 'Texto', 'order': 1,
            'video_url': 'https://cdn.example.com/aula.mp4', 'published': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.video_url, 'https://cdn.example.com/aula.mp4')
