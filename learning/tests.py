from django.test import TestCase
from django.urls import reverse
from django.contrib.staticfiles import finders


class HomeTests(TestCase):
    def test_home_serves_prototype(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ondjango')
        self.assertContains(response, '/static/learning/main.js')

    def test_assets_exist(self):
        self.assertIsNotNone(finders.find('learning/main.js'))
        self.assertIsNotNone(finders.find('learning/style.css'))


from django.core.management import call_command
from .models import Course, Lesson


class CatalogTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(slug='publico', title='Curso público', description='Descrição', category=Course.Category.TECNOLOGIA, published=True)
        self.draft = Course.objects.create(slug='rascunho', title='Curso privado', description='Descrição', category=Course.Category.TECNOLOGIA)
        Lesson.objects.create(course=self.course, title='Segunda', content='Texto 2', order=2, published=True)
        Lesson.objects.create(course=self.course, title='Primeira', content='<script>texto</script>', order=1, published=True)
        Lesson.objects.create(course=self.course, title='Rascunho', content='Segredo', order=0)
        Lesson.objects.create(course=self.draft, title='Privada', content='Segredo', published=True)

    def test_only_published_courses_and_lessons_are_returned_in_order(self):
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        courses = response.json()['courses']
        self.assertEqual(len(courses), 1)
        self.assertEqual([lesson['title'] for lesson in courses[0]['lessons']], ['Primeira', 'Segunda'])
        self.assertNotIn('Segredo', response.content.decode())

    def test_catalog_rejects_post(self):
        self.assertEqual(self.client.post(reverse('catalog')).status_code, 405)

    def test_admin_requires_login(self):
        self.assertEqual(self.client.get('/admin/learning/course/').status_code, 302)

    def test_demo_seed_is_idempotent_and_does_not_overwrite(self):
        call_command('seed_demo', verbosity=0)
        demo = Course.objects.get(slug='web')
        demo.title = 'Alterado'
        demo.save()
        call_command('seed_demo', verbosity=0)
        self.assertEqual(Course.objects.get(slug='web').title, 'Alterado')
        self.assertEqual(Lesson.objects.filter(course=demo).count(), 4)


from django.contrib.auth import get_user_model
from django.test import Client
from .models import LessonCompletion


class AccountsAndProgressTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='aluno', password='Senhasegura123!')
        self.other = get_user_model().objects.create_user(username='outra', password='Senhasegura123!')
        self.course = Course.objects.create(slug='curso', title='Curso', description='Descrição', category=Course.Category.TECNOLOGIA, published=True)
        self.lesson = Lesson.objects.create(course=self.course, title='Aula', content='Conteúdo', published=True)
        self.draft = Lesson.objects.create(course=self.course, title='Rascunho', content='Segredo')

    def test_registration_login_and_logout(self):
        response = self.client.post(reverse('register'), {'username': 'nova', 'password1': 'UmaSenhaSegura789!', 'password2': 'UmaSenhaSegura789!'})
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(self.client.get(reverse('progress')).json()['authenticated'])
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('home'))
        self.assertFalse(self.client.get(reverse('progress')).json()['authenticated'])
        self.assertRedirects(self.client.post(reverse('login'), {'username': 'nova', 'password': 'UmaSenhaSegura789!'}), reverse('home'))

    def test_invalid_registration_does_not_create_user(self):
        response = self.client.post(reverse('register'), {'username': 'nova', 'password1': '123', 'password2': '123'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username='nova').exists())

    def test_progress_is_private_idempotent_and_shared_across_sessions(self):
        self.assertEqual(self.client.post(reverse('complete_lesson', args=[self.lesson.pk])).status_code, 401)
        self.client.force_login(self.user)
        for _ in range(2):
            self.assertEqual(self.client.post(reverse('complete_lesson', args=[self.lesson.pk])).status_code, 200)
        self.assertEqual(LessonCompletion.objects.count(), 1)
        second_device = Client()
        second_device.force_login(self.user)
        self.assertEqual(second_device.get(reverse('progress')).json()['completed'], [self.lesson.pk])
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('progress')).json()['completed'], [])

    def test_unpublished_lessons_and_courses_cannot_be_completed(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse('complete_lesson', args=[self.draft.pk])).status_code, 404)
        self.course.published = False
        self.course.save()
        self.assertEqual(self.client.post(reverse('complete_lesson', args=[self.lesson.pk])).status_code, 404)

    def test_csrf_is_required_for_completion(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        url = reverse('complete_lesson', args=[self.lesson.pk])
        self.assertEqual(client.post(url).status_code, 403)
        client.get(reverse('home'))
        token = client.cookies['csrftoken'].value
        self.assertEqual(client.post(url, HTTP_X_CSRFTOKEN=token).status_code, 200)
