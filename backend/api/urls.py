from django.urls import path, include

from rest_framework.routers import DefaultRouter

from api.views import (TagViewSet, RecipeViewSet,
                       IngredientViewSet, FavoriteViewSet)
from users.views import SubscriptionListViewSet, SubscriptionViewSet


router_api_v1 = DefaultRouter()
router_api_v1.register(
    r'users/subscriptions', SubscriptionListViewSet, basename='subscriptions'
)
router_api_v1.register(
    r'users/subscriptions/(?P<author_id>\d+)/subscribe',
    SubscriptionViewSet,
    basename='subscriptions'
)
router_api_v1.register(r'tags', TagViewSet, basename='tags')
router_api_v1.register(
    r'ingredients', IngredientViewSet, basename='ingredients'
)
router_api_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_api_v1.register(
    r'recipes/(?P<recipes_id>\d+)/favorite',
    FavoriteViewSet, basename='favorite'
)

urlpatterns = [
    path('', include(router_api_v1.urls)),
]
