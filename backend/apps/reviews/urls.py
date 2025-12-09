from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewTaskViewSet, ReviewResultViewSet, ReviewOpinionViewSet, ReviewCycleViewSet

router = DefaultRouter()
router.register(r'tasks', ReviewTaskViewSet, basename='review-task')
router.register(r'results', ReviewResultViewSet, basename='review-result')
router.register(r'opinions', ReviewOpinionViewSet, basename='review-opinion')
router.register(r'cycles', ReviewCycleViewSet, basename='review-cycle')

urlpatterns = [
    path('', include(router.urls)),
]

