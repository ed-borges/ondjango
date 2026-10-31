from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.decorators.clickjacking import xframe_options_exempt
from learning import views

login_view = auth_views.LoginView.as_view(template_name='learning/auth.html', redirect_authenticated_user=True)
if settings.DEBUG:
    login_view = xframe_options_exempt(login_view)

urlpatterns = [
    path('', views.home, name='home'),
    path('conta/criar/', views.register, name='register'),
    path('conta/entrar/', login_view, name='login'),
    path('conta/sair/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('api/paths/', views.learning_paths, name='learning_paths'),
    path('api/courses/', views.catalog, name='catalog'),
    path('api/progress/', views.progress, name='progress'),
    path('api/exercises/<int:exercise_id>/evaluate/', views.evaluate_exercise, name='evaluate_exercise'),
    path('api/lessons/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
    path('admin/', admin.site.urls),
]
