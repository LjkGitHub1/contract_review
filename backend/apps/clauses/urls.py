from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractClauseViewSet

router = DefaultRouter()
router.register(r'clauses', ContractClauseViewSet, basename='contract-clause')

urlpatterns = [
    path('', include(router.urls)),
]

