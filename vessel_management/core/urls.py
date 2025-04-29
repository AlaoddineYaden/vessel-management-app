# 11. core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VesselViewSet, SystemLogViewSet, FileViewSet

router = DefaultRouter()
router.register(r'vessels', VesselViewSet)
router.register(r'logs', SystemLogViewSet)
router.register(r'files', FileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
