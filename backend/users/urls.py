from django.urls import path, include

from users.views import UserViewSet
from core.urls import router_api_v1

router_api_v1.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router_api_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
