from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import ComparisonTask, ComparisonDiff
from .serializers import ComparisonTaskSerializer, ComparisonDiffSerializer


class ComparisonTaskViewSet(viewsets.ModelViewSet):
    queryset = ComparisonTask.objects.all()
    serializer_class = ComparisonTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['task_type', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class ComparisonDiffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ComparisonDiff.objects.all()
    serializer_class = ComparisonDiffSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['comparison_task', 'diff_type', 'diff_level', 'risk_level']
    ordering_fields = ['risk_level', 'created_at']
    ordering = ['-risk_level']

