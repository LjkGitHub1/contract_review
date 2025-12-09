from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RiskIdentificationViewSet

router = DefaultRouter()
router.register(r'risks', RiskIdentificationViewSet, basename='risk-identification')

urlpatterns = [
    path('', include(router.urls)),
]

