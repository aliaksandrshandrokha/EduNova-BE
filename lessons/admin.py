from django.contrib import admin
from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['topic', 'subject', 'grade_level', 'user', 'is_public', 'created_at']
    list_filter = ['subject', 'grade_level', 'is_public', 'created_at']
    search_fields = ['topic', 'subject', 'description', 'slug']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'topic', 'subject', 'grade_level', 'duration_minutes', 'slug')
        }),
        ('Content', {
            'fields': ('description', 'summary', 'activities', 'questions')
        }),
        ('Media', {
            'fields': ('image_urls', 'video_links')
        }),
        ('Settings', {
            'fields': ('is_public',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

