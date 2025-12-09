from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone

from .models import ContractClause
from .serializers import ContractClauseSerializer


class ContractClauseViewSet(viewsets.ModelViewSet):
    queryset = ContractClause.objects.all()
    serializer_class = ContractClauseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['contract', 'contract_version', 'clause_type', 'is_confirmed']
    ordering_fields = ['start_position', 'created_at']
    ordering = ['start_position']

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """确认条款"""
        clause = self.get_object()
        clause.is_confirmed = True
        clause.confirmed_by = request.user
        clause.confirmed_at = timezone.now()
        clause.save()
        serializer = self.get_serializer(clause)
        return Response(serializer.data)

