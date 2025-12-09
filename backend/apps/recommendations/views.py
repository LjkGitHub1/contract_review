from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Recommendation
from .serializers import RecommendationSerializer


class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'contract', 'recommendation_type', 'recommendation_context', 'is_accepted']
    ordering_fields = ['score', 'created_at']
    ordering = ['-score', '-created_at']

    def get_queryset(self):
        # 默认只返回当前用户的推荐
        if self.request.user.is_staff:
            return Recommendation.objects.all()
        return Recommendation.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """接受推荐"""
        recommendation = self.get_object()
        recommendation.is_accepted = True
        recommendation.save()
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝推荐"""
        recommendation = self.get_object()
        recommendation.is_accepted = False
        recommendation.save()
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)

