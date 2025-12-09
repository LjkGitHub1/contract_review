from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import ReviewRule, RuleMatch
from .serializers import ReviewRuleSerializer, RuleMatchSerializer


class ReviewRuleViewSet(viewsets.ModelViewSet):
    queryset = ReviewRule.objects.filter(is_deleted=False, is_active=True)
    serializer_class = ReviewRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['rule_type', 'industry', 'category', 'risk_level', 'is_active']
    search_fields = ['rule_name', 'rule_code', 'description']
    ordering_fields = ['priority', 'created_at']
    ordering = ['-priority', '-created_at']


class RuleMatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuleMatch.objects.all()
    serializer_class = RuleMatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['review_task', 'rule', 'contract_id']
    ordering_fields = ['match_score', 'created_at']
    ordering = ['-match_score']

