from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProcedureCategoryViewSet, ProcedureViewSet,
    ProcedureReviewViewSet, ProcedureAcknowledgmentViewSet
)

router = DefaultRouter()
router.register(r'categories', ProcedureCategoryViewSet)
router.register(r'procedures', ProcedureViewSet)
router.register(r'reviews', ProcedureReviewViewSet)
router.register(r'acknowledgments', ProcedureAcknowledgmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
