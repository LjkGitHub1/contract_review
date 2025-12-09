from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone

from .models import RiskIdentification
from .serializers import RiskIdentificationSerializer


class RiskIdentificationViewSet(viewsets.ModelViewSet):
    queryset = RiskIdentification.objects.all()
    serializer_class = RiskIdentificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['review_result', 'contract_id', 'risk_type', 'risk_category', 'risk_level', 'status']
    ordering_fields = ['risk_level', 'created_at']
    ordering = ['-risk_level', '-created_at']

    @action(detail=True, methods=['post'])
    def handle(self, request, pk=None):
        """处理风险"""
        risk = self.get_object()
        risk.status = 'handled'
        risk.handled_by = request.user
        risk.handled_at = timezone.now()
        risk.save()
        serializer = self.get_serializer(risk)
        return Response(serializer.data)

