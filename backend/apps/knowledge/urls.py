from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KnowledgeEntityViewSet, KnowledgeRelationViewSet, RegulationViewSet, CaseViewSet

router = DefaultRouter()
router.register(r'entities', KnowledgeEntityViewSet, basename='knowledge-entity')
router.register(r'relations', KnowledgeRelationViewSet, basename='knowledge-relation')
router.register(r'regulations', RegulationViewSet, basename='regulation')
router.register(r'cases', CaseViewSet, basename='case')

urlpatterns = [
    path('', include(router.urls)),
]

