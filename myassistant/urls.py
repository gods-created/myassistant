from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', include('admin.urls', namespace='admin')),
    path('api/', include('api.urls', namespace='api')),
    path('silk/', include('silk.urls', namespace='silk')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
