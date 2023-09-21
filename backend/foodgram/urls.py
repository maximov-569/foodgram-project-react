from django.urls import path, include
from rest_framework import routers
from foodgram.views import TagViewSet, RecipeViewSet, IngredientViewSet

router_v1 = routers.DefaultRouter()
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'recipes', RecipeViewSet)
router_v1.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
]
