from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'isms', views.ISMRequirementViewSet)
router.register(r'compliance-items', views.ComplianceItemViewSet)
router.register(r'evidence', views.ComplianceEvidenceViewSet)
router.register(r'reviews', views.ComplianceReviewViewSet)
router.register(r'reports', views.ComplianceReportViewSet, basename='compliance-report')

app_name = 'ism_compliance'

urlpatterns = [
    path('', include(router.urls)),
]