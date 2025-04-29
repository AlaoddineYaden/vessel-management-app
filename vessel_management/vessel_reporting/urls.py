from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportViewSet,
    SavedReportViewSet,
    ReportScheduleViewSet,
    DashboardMetricViewSet
)

router = DefaultRouter()
router.register(r'reports', ReportViewSet)
router.register(r'saved-reports', SavedReportViewSet)
router.register(r'schedules', ReportScheduleViewSet)
router.register(r'metrics', DashboardMetricViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 