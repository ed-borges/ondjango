from django.contrib import admin
from .models import Course, Lesson, Exercise


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
    list_display = ('title', 'course', 'order', 'published')
    list_filter = ('published', 'course')
    search_fields = ('title', 'content')


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title_pt', 'lesson', 'language', 'order', 'published')
    list_filter = ('published', 'language')
    search_fields = ('title_pt', 'title_en', 'lesson__title')
    fieldsets = (
        (None, {'fields': ('lesson', 'language', 'order', 'published')}),
        ('Português', {'fields': ('title_pt', 'description_pt')}),
        ('Inglês (opcional)', {'fields': ('title_en', 'description_en')}),
        ('Código', {'fields': ('starter_code', 'private_tests')}),
    )
