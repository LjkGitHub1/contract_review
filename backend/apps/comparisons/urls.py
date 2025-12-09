from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComparisonTaskViewSet, ComparisonDiffViewSet

router = DefaultRouter()
router.register(r'tasks', ComparisonTaskViewSet, basename='comparison-task')
router.register(r'diffs', ComparisonDiffViewSet, basename='comparison-diff')

urlpatterns = [
    path('', include(router.urls)),
]

