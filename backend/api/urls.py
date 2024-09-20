from django.urls import path, include

from rest_framework.routers import DefaultRouter

from api.views import (TagViewSet, RecipeViewSet,
                       IngredientViewSet, FavoriteViewSet)
from users.views import UserViewSet


api_v1 = DefaultRouter()
api_v1.register(r'users', UserViewSet, basename='users')
api_v1.register(r'tags', TagViewSet, basename='tags')
api_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
api_v1.register(r'recipes', RecipeViewSet, basename='recipes')
api_v1.register(
    r'recipes/(?P<recipes_id>\d+)/favorite',
    FavoriteViewSet, basename='favorite'
)

urlpatterns = [
    path('', include(api_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
