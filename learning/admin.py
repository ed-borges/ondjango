from django.contrib import admin
from django.db import transaction
from .models import Course, Lesson, Exercise, LearningPath, LearningPathCourse
from .forms import ExerciseAdminForm, AdminLessonForm


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('title', 'order', 'published')
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published', 'created_at')
    list_filter = ('published', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = AdminLessonForm
    list_display = ('title', 'course', 'order', 'has_video', 'published')
    list_filter = ('published', 'course')
    search_fields = ('title', 'content')

    @admin.display(boolean=True, description='Vídeo')
    def has_video(self, obj):
        return bool(obj.video_url or obj.video_file)

    def save_model(self, request, obj, form, change):
        old_name = Lesson.objects.get(pk=obj.pk).video_file.name if change else ''
        super().save_model(request, obj, form, change)
        if old_name and old_name != obj.video_file.name:
            storage = obj._meta.get_field('video_file').storage
            transaction.on_commit(lambda: storage.delete(old_name))


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    form = ExerciseAdminForm
    list_display = ('title_pt', 'lesson', 'language', 'order', 'published')
    list_filter = ('published', 'language')
    search_fields = ('title_pt', 'title_en', 'lesson__title')
    fieldsets = (
        (None, {'fields': ('lesson', 'language', 'order', 'published')}),
        ('Português', {'fields': ('title_pt', 'description_pt')}),
        ('Inglês (opcional)', {'fields': ('title_en', 'description_en')}),
        ('Código', {'fields': ('starter_code', 'private_tests')}),
    )



class LearningPathCourseInline(admin.TabularInline):
    model = LearningPathCourse
    extra = 0
    ordering = ('order',)


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'published')
    list_filter = ('published',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LearningPathCourseInline]
