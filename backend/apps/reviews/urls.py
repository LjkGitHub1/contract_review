from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReviewTaskViewSet, ReviewResultViewSet, ReviewOpinionViewSet,
    ReviewCycleViewSet, ReviewFocusConfigViewSet, ReviewAISuggestionViewSet,
    AIModelConfigViewSet
)

router = DefaultRouter()
router.register(r'tasks', ReviewTaskViewSet, basename='review-task')
router.register(r'results', ReviewResultViewSet, basename='review-result')
router.register(r'opinions', ReviewOpinionViewSet, basename='review-opinion')
router.register(r'cycles', ReviewCycleViewSet, basename='review-cycle')
router.register(r'focus-configs', ReviewFocusConfigViewSet, basename='review-focus-config')
router.register(r'ai-suggestions', ReviewAISuggestionViewSet, basename='review-ai-suggestion')
router.register(r'ai-model-configs', AIModelConfigViewSet, basename='ai-model-config')

urlpatterns = [
    path('', include(router.urls)),
]

