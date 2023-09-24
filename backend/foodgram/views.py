from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import viewsets, mixins, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.models import (Tag, Ingredient, Recipe, Favorite, ShoppingCart,
                             IngredientToRecipe)
from foodgram.serializers import (TagSerializer, IngredientSerializer,
                                  RecipeSerializer, AddRecipeSerializer,
                                  ShortRecipeSerializer)
from foodgram.pagination import CustomWithLimitPagination
from foodgram_backend.settings import FILE_NAME
from foodgram.filters import RecipeFilter


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin):
    """ViewSet for Tag model.

    Only get method allowed."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin):
    """ViewSet for Ingredient model.

    Only get method allowed."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin):
    """ViewSet for Recipe model.

    update and destroy - reassembled to protect Recipes from
        changes that can make other users.
    get_serializer_class - provide different serializer depending on method.
    favorite() and shopping_cart() -
        implements Favorite and ShoppingCart models.
    download_shopping_cart() - download 'to buy list' depending on recipes
        that user added to shopping_cart.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomWithLimitPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user != instance.author:
            return Response({'detail': 'Only author can update recipe.'},
                            status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user != instance.author:
            return Response({"detail": "Only author can delete recipe."},
                            status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().update(request, args, kwargs)

    def get_serializer_class(self):
        return RecipeSerializer if self.request.method == "GET" else (
            AddRecipeSerializer)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if Favorite.objects.filter(
                    recipe=recipe, user=request.user).exists():
                return Response(
                    {'detail': 'Recipe already in favorite.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Favorite.objects.create(recipe=recipe, user=request.user)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Favorite.objects.filter(
                    recipe=recipe, user=request.user).exists():
                return Response(
                    {'detail': 'Recipe already not in favorite.'}
                )

            Favorite.objects.filter(recipe=recipe, user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        if not Recipe.objects.filter(id=pk).exists():
            return Response(
                {'detail': f'No such recipe with id {pk}.'},
                status=status.HTTP_400_BAD_REQUEST)
        recipe = Recipe.objects.get(id=pk)

        shopping_cart, _ = ShoppingCart.objects.get_or_create(
            user=request.user)

        if request.method == 'POST':

            if recipe in shopping_cart.recipes.all():
                return Response(
                    {"detail":
                        f'Recipe with id {pk} already in shopping cart.'},
                    status=status.HTTP_400_BAD_REQUEST)

            shopping_cart.recipes.add(recipe)
            shopping_cart.save()

            serializer = ShortRecipeSerializer(recipe)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':

            if recipe not in shopping_cart.recipes.all():
                return Response(
                    {"detail":
                        f"Recipe with id {pk} not in shopping cart."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            shopping_cart.recipes.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientToRecipe.objects
            .filter(recipe__shopping_carts__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = (f'attachment; filename={FILE_NAME}')
        return file
