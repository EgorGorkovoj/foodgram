from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core.views import redirect_original_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('api.urls')),
    path('s/<str:short_link>/', redirect_original_url),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (
        path('__debug__/', include(debug_toolbar.urls)),
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
