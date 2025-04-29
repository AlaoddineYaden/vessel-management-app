from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'nonconformities', views.NonConformityViewSet)
router.register(r'corrective-actions', views.CorrectiveActionViewSet)
router.register(r'evidence-files', views.EvidenceFileViewSet)
router.register(r'preventive-actions', views.PreventiveActionViewSet)

app_name = 'nc_module'

urlpatterns = [
    path('', include(router.urls)),
]