from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from .models import Lesson
from .serializers import LessonSerializer, LessonPublicSerializer
from .permissions import IsLessonOwner
from .utils import generate_lesson_pdf


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing lessons.
    
    list: Get all lessons for the authenticated user
    create: Create a new lesson
    retrieve: Get a specific lesson (must be owner)
    update: Update a lesson (must be owner)
    partial_update: Partially update a lesson (must be owner)
    destroy: Delete a lesson (must be owner)
    toggle_visibility: Toggle is_public field (must be owner)
    """
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return lessons for the authenticated user only."""
        return Lesson.objects.filter(user=self.request.user)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'toggle_visibility', 'download_pdf']:
            permission_classes = [IsAuthenticated, IsLessonOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['patch'], url_path='visibility')
    def toggle_visibility(self, request, pk=None):
        """Toggle the is_public field of a lesson."""
        lesson = self.get_object()
        lesson.is_public = not lesson.is_public
        lesson.save()
        
        serializer = self.get_serializer(lesson)
        return Response({
            'message': f'Lesson visibility set to {"public" if lesson.is_public else "private"}',
            'lesson': serializer.data
        })

    @action(detail=True, methods=['get'], url_path='pdf', url_name='pdf')
    def download_pdf(self, request, pk=None):
        """
        Download lesson as PDF.
        Only the lesson owner can download.
        """
        lesson = self.get_object()
        
        # Generate PDF
        try:
            pdf_buffer = generate_lesson_pdf(lesson)
            
            # Prepare response
            response = HttpResponse(
                pdf_buffer.getvalue(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="lesson_{lesson.id}_{lesson.slug}.pdf"'
            
            return response
        except Exception as e:
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LessonPublicView(viewsets.ReadOnlyModelViewSet):
    """
    Public view for accessing public lessons by slug.
    No authentication required.
    """
    serializer_class = LessonPublicSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        """Return only public lessons."""
        return Lesson.objects.filter(is_public=True)

    def retrieve(self, request, slug=None):
        """Retrieve a public lesson by slug."""
        try:
            lesson = get_object_or_404(Lesson, slug=slug, is_public=True)
            serializer = self.get_serializer(lesson)
            return Response(serializer.data)
        except Http404:
            return Response(
                {'error': 'Lesson not found or not public'},
                status=status.HTTP_404_NOT_FOUND
            )

