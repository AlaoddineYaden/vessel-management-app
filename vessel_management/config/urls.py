from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Vessel Management API",
        default_version='v1',
        description="API for vessel management system",
        terms_of_service="https://www.vessel-management.com/terms/",
        contact=openapi.Contact(email="contact@vessel-management.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Root URL - change this to your desired landing page
    path('', RedirectView.as_view(url='/admin/', permanent=False), name='home'),
    
    # Add a specific route for /dashboard/ to see if it's being handled by Django
    path('dashboard/', RedirectView.as_view(url='/admin/', permanent=False), name='dashboard'),
    
    path('admin/', admin.site.urls),
    path('api/v1/', include('core.urls')),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/crew/', include('crew.urls')),
    path('api/v1/certificates/', include('certificates.urls')),
    path('api/v1/maintenance/', include('vessel_pms.urls')),
    path('api/v1/safety/', include('safety_procedures.urls')),
    path('api/v1/audits/', include('audit_inspection.urls')),
    path('api/v1/nc/', include('nc_module.urls')),
    path('api/v1/ism/', include('ism_compliance.urls')),
    path('api/v1/reporting/', include('vessel_reporting.urls')),
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

