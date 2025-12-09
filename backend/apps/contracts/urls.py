from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContractViewSet, TemplateViewSet, UserHabitViewSet, FileUploadView

router = DefaultRouter()
router.register(r'contracts', ContractViewSet, basename='contract')
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'habits', UserHabitViewSet, basename='habit')

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('', include(router.urls)),
]

