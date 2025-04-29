# certificates/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CertificateViewSet, CertificateTypeViewSet, CertificateRenewalViewSet

router = DefaultRouter()
router.register(r'certificates', CertificateViewSet)
router.register(r'certificate-types', CertificateTypeViewSet)
router.register(r'certificate-renewals', CertificateRenewalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]