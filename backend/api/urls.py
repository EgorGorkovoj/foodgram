from django.urls import path, include

from rest_framework.routers import DefaultRouter

from api.views import (TagViewSet, RecipeViewSet,
                       IngredientViewSet)

router_api_v1 = DefaultRouter()
router_api_v1.register(r'tags', TagViewSet, basename='tags')
router_api_v1.register(
    r'ingredients', IngredientViewSet, basename='ingredients'
)
router_api_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_api_v1.urls)),
]
