from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import KnowledgeEntity, KnowledgeRelation, Regulation, Case
from .serializers import (
    KnowledgeEntitySerializer, KnowledgeRelationSerializer,
    RegulationSerializer, CaseSerializer
)


class KnowledgeEntityViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeEntity.objects.filter(is_deleted=False)
    serializer_class = KnowledgeEntitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['entity_type']
    search_fields = ['entity_name', 'entity_code', 'description']
    ordering_fields = ['created_at']
    ordering = ['entity_type', 'entity_name']


class KnowledgeRelationViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeRelation.objects.filter(is_deleted=False)
    serializer_class = KnowledgeRelationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['source_entity', 'target_entity', 'relation_type']
    ordering_fields = ['confidence', 'created_at']
    ordering = ['-confidence']


class RegulationViewSet(viewsets.ModelViewSet):
    queryset = Regulation.objects.filter(is_deleted=False, is_active=True)
    serializer_class = RegulationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['regulation_type', 'is_active']
    search_fields = ['title', 'regulation_no', 'content']
    ordering_fields = ['publish_date', 'effective_date']
    ordering = ['-publish_date']


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.filter(is_deleted=False)
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['case_type']
    search_fields = ['case_title', 'case_no', 'case_summary']
    ordering_fields = ['judge_date']
    ordering = ['-judge_date']

