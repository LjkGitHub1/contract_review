from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewRuleViewSet, RuleMatchViewSet

router = DefaultRouter()
router.register(r'rules', ReviewRuleViewSet, basename='review-rule')
router.register(r'matches', RuleMatchViewSet, basename='rule-match')

urlpatterns = [
    path('', include(router.urls)),
]

