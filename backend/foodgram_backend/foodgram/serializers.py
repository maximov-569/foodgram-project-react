from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from drf_base64.fields import Base64ImageField
from users.serializers import CustomUserSerializer

from users.models import User, Subscription

from foodgram.models import (Tag, Ingredient, Recipe, IngredientToRecipe,
                             Favorite, ShoppingCart)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    """recipes = ShortRecipeSerializer(many=True)"""
    recipes = serializers.SerializerMethodField()

    class Meta:
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count',
                  )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj).all()

        print(self.context['request'].user)

        if self.context['request'].query_params:
            recipes_limit = int(
                self.context['request'].query_params['recipes_limit'])
            queryset = queryset[:recipes_limit:]

        serializer = ShortRecipeSerializer(
            queryset, many=True, context=self.context)

        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientToRecipeSerializer(
        many=True, read_only=True, source='ingredient')

    author = CustomUserSerializer(many=False, read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')
        model = Recipe

    def get_is_favorited(self, obj):
        if not self.context['request'].user.is_anonymous:
            return Favorite.objects.filter(
                recipe=obj, user=self.context['request'].user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if not self.context['request'].user.is_anonymous:
            return ShoppingCart.objects.filter(
                recipes=obj, user=self.context['request'].user).exists()
        return False


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'amount')
        extra_kwargs = {'amount': {'required': True},
                        'id': {'required': True}}


class AddRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True, allow_empty=False, allow_null=False)

    ingredients = AddIngredientToRecipeSerializer(
        many=True, allow_null=False, allow_empty=False)

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name', 'text',
                  'cooking_time', 'image',)

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')
        if ingredients:
            for item in ingredients:
                if item.get('amount') <= 0:
                    raise ValidationError(
                        detail='Amount should be greater than 0.')

        cooking_time = attrs.get('cooking_time')
        if cooking_time:
            if cooking_time <= 0:
                raise ValidationError(
                    detail='Cooking time should be greater than 0.')

        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data, author=self.context['request'].user)
        recipe.tags.set(tags)

        to_save = []
        for item in ingredients:
            to_save.append(
                IngredientToRecipe(
                    ingredient=item['id'],
                    amount=item['amount'], recipe=recipe)
            )
        IngredientToRecipe.objects.bulk_create(to_save)

        return recipe

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)

        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)

        if "ingredients" in validated_data:
            ingredients = validated_data.pop('ingredients')
            IngredientToRecipe.objects.filter(
                recipe=instance,
                ingredient__in=instance.ingredients.all()).delete()

            to_save = []
            for item in ingredients:
                to_save.append(
                    IngredientToRecipe(
                        ingredient=item['id'],
                        amount=item['amount'], recipe=instance)
                )
            IngredientToRecipe.objects.bulk_create(to_save)
        instance.save()
        return instance
