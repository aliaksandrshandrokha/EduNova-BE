from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
import json


class Lesson(models.Model):
    """Lesson model for storing educational lesson content."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    topic = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    grade_level = models.CharField(max_length=50)
    duration_minutes = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    activities = models.JSONField(default=list, blank=True)
    questions = models.JSONField(default=list, blank=True)
    summary = models.TextField(blank=True, null=True)
    image_urls = models.JSONField(default=list, blank=True)
    video_links = models.JSONField(default=list, blank=True)
    is_public = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lessons_lesson'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_public', 'slug']),
        ]

    def __str__(self):
        return f"{self.topic} - {self.subject} ({self.grade_level})"

    def save(self, *args, **kwargs):
        """Auto-generate unique slug if not provided."""
        if not self.slug:
            base_slug = slugify(self.topic)
            self.slug = base_slug
            # Ensure uniqueness by appending UUID if slug exists
            while Lesson.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                unique_id = str(uuid.uuid4())[:8]
                self.slug = f"{base_slug}-{unique_id}"
        super().save(*args, **kwargs)

    def get_activities_list(self):
        """Helper method to get activities as list."""
        if isinstance(self.activities, str):
            try:
                return json.loads(self.activities)
            except json.JSONDecodeError:
                return []
        return self.activities or []

    def get_questions_list(self):
        """Helper method to get questions as list."""
        if isinstance(self.questions, str):
            try:
                return json.loads(self.questions)
            except json.JSONDecodeError:
                return []
        return self.questions or []

    def get_image_urls_list(self):
        """Helper method to get image URLs as list."""
        if isinstance(self.image_urls, str):
            try:
                return json.loads(self.image_urls)
            except json.JSONDecodeError:
                return []
        return self.image_urls or []

    def get_video_links_list(self):
        """Helper method to get video links as list."""
        if isinstance(self.video_links, str):
            try:
                return json.loads(self.video_links)
            except json.JSONDecodeError:
                return []
        return self.video_links or []

