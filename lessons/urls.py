from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LessonViewSet, LessonPublicView

app_name = 'lessons'

# Create router for ViewSet
router = DefaultRouter()
router.register(r'lessons', LessonViewSet, basename='lesson')

urlpatterns = [
    # Public lesson endpoint (must come before router to avoid conflicts)
    path('lessons/public/<slug:slug>/', 
         LessonPublicView.as_view({'get': 'retrieve'}), 
         name='lesson-public'),
    
    # Include router URLs (handles /api/lessons/ endpoints)
    path('', include(router.urls)),
]

