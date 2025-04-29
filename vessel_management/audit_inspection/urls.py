# audit_inspection/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'vessels', views.VesselViewSet)
router.register(r'audit-types', views.AuditTypeViewSet)
router.register(r'audits', views.AuditViewSet)
router.register(r'findings', views.AuditFindingViewSet)
router.register(r'inspection-items', views.InspectionItemViewSet)
router.register(r'inspection-checklists', views.InspectionChecklistViewSet)
router.register(r'inspections', views.InspectionViewSet)
router.register(r'inspection-results', views.InspectionResultViewSet)
router.register(r'notifications', views.AuditNotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]