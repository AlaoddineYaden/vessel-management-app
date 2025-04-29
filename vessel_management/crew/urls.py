# crew/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CrewViewSet, CrewCertificateViewSet, CrewAssignmentViewSet,
    VesselViewSet, CertificateNotificationViewSet
)

router = DefaultRouter()
router.register(r'crew', CrewViewSet)
router.register(r'certificates', CrewCertificateViewSet)
router.register(r'assignments', CrewAssignmentViewSet)
router.register(r'vessels', VesselViewSet)
router.register(r'notifications', CertificateNotificationViewSet)

app_name = 'crew'

urlpatterns = [
    path('', include(router.urls)),
]