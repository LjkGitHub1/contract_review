from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Recommendation
from .serializers import RecommendationSerializer
from .services import RecommendationService
from apps.contracts.models import Contract
from apps.reviews.models import ReviewResult


class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'contract', 'recommendation_type', 'recommendation_context', 'is_accepted']
    ordering_fields = ['score', 'created_at']
    ordering = ['-score', '-created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recommendation_service = RecommendationService()

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

    @action(detail=False, methods=['post'])
    def recommend_clauses(self, request):
        """推荐合同条款"""
        contract_id = request.data.get('contract_id')
        context = request.data.get('context', 'drafting')
        
        if not contract_id:
            return Response({'error': 'contract_id不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            contract = Contract.objects.get(id=contract_id, is_deleted=False)
        except Contract.DoesNotExist:
            return Response({'error': '合同不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        recommendations = self.recommendation_service.recommend_clauses(
            contract=contract,
            user=request.user,
            context=context
        )
        
        return Response({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })

    @action(detail=False, methods=['post'])
    def recommend_templates(self, request):
        """推荐合同模板"""
        contract_type = request.data.get('contract_type')
        industry = request.data.get('industry', '')
        
        if not contract_type:
            return Response({'error': 'contract_type不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        recommendations = self.recommendation_service.recommend_templates(
            contract_type=contract_type,
            industry=industry,
            user=request.user
        )
        
        return Response({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })

    @action(detail=False, methods=['post'])
    def recommend_risk_responses(self, request):
        """推荐风险应对建议"""
        contract_id = request.data.get('contract_id')
        review_result_id = request.data.get('review_result_id')
        
        if not contract_id:
            return Response({'error': 'contract_id不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            contract = Contract.objects.get(id=contract_id, is_deleted=False)
        except Contract.DoesNotExist:
            return Response({'error': '合同不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        review_result = None
        if review_result_id:
            try:
                review_result = ReviewResult.objects.get(id=review_result_id)
            except ReviewResult.DoesNotExist:
                pass
        
        recommendations = self.recommendation_service.recommend_risk_responses(
            contract=contract,
            review_result=review_result,
            user=request.user
        )
        
        return Response({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })

