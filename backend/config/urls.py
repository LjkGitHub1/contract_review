"""
URL configuration for AI智能合同审核系统 project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('apps.users.urls')),
    path('api/contracts/', include('apps.contracts.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/rules/', include('apps.rules.urls')),
    path('api/clauses/', include('apps.clauses.urls')),
    path('api/risks/', include('apps.risks.urls')),
    path('api/comparisons/', include('apps.comparisons.urls')),
    path('api/knowledge/', include('apps.knowledge.urls')),
    path('api/recommendations/', include('apps.recommendations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

