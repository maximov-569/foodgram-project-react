from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from drf_base64.fields import Base64ImageField
from users.serializers import CustomReadUserSerializer
from users.models import User, Subscription
from foodgram.models import (Tag, Ingredient, Recipe, IngredientToRecipe,
                             Favorite, ShoppingCart)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Represents short list of fields for Recipe model for some
    specific endpoints."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for SubscriptionViewSet."""
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
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
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Through this method we can limit recipe count for
        each user in sent data."""
        queryset = Recipe.objects.filter(author=obj)

        if self.context['request'].query_params:
            recipes_limit = self.context['request'].query_params[
                'recipes_limit'
            ]
            if isinstance(recipes_limit, int) and recipes_limit > 0:
                queryset = queryset[:recipes_limit]

        serializer = ShortRecipeSerializer(
            queryset, many=True, context=self.context)

        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    class Meta:
        fields = '__all__'
        model = Tag
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient model."""

    class Meta:
        fields = '__all__'
        model = Ingredient
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    """Through this serializer implemented
    'Ingredient' + 'amount' representation."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Read recipe serializer."""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientToRecipeSerializer(
        many=True, read_only=True, source='ingredient')

    author = CustomReadUserSerializer(many=False, read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return False if user.is_anonymous else Favorite.objects.filter(
            recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return False if user.is_anonymous else ShoppingCart.objects.filter(
            recipes=obj, user=user).exists()


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    """Write recipe serializer.

    Reassembled update and create methods because recipe model have many nested
    fields.

    to_representation - uses RecipeSerializer because here some difference in
    serializing ingredients field."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientToRecipe
        fields = ('id', 'amount')
        extra_kwargs = {'amount': {'required': True},
                        'id': {'required': True}}


class AddRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True, allow_empty=False, allow_null=False, required=True)

    ingredients = AddIngredientToRecipeSerializer(
        many=True, allow_null=False, allow_empty=False, required=True)

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        partial_update = False
        fields = ('ingredients', 'tags', 'name', 'text',
                  'cooking_time', 'image',)

    def validate(self, attrs):
        ingredients = attrs.get('ingredients')
        if not ingredients:
            raise ValidationError(
                detail={'ingredients': 'field is required.'}
            )
        for item in ingredients:
            if 'id' not in item:
                raise ValidationError(
                    detail={'ingredients': {'id': 'field is required.'}}
                )
            if 'amount' not in item:
                raise ValidationError(
                    detail={'ingredients': {'amount': 'field is required.'}}
                )
            if item['amount'] <= 0:
                raise ValidationError(
                    detail={
                        'ingredients': {'amount': 'must be greater than 0.'}
                    }
                )
        unique_ingredients = set([item['id'] for item in ingredients])
        if len(ingredients) > len(unique_ingredients):
            raise ValidationError(
                detail={'ingredients': 'only unique values.'}
            )

        tags = attrs.get('tags')
        if not tags:
            raise ValidationError(
                detail={'tags': 'field is required.'}
            )
        unique_tags = set(tags)
        if len(tags) > len(unique_tags):
            raise ValidationError(
                detail={'tags': 'only unique values.'}
            )

        cooking_time = attrs.get('cooking_time')
        if cooking_time is not None and cooking_time < 1:
            raise ValidationError(
                detail={'cooking_time': 'should be greater than 0.'})

        return attrs

    @atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data, author=self.context['request'].user)
        recipe.tags.set(tags)

        to_save = [
            IngredientToRecipe(ingredient=item['id'],
                               amount=item['amount'],
                               recipe=recipe) for item in ingredients]

        IngredientToRecipe.objects.bulk_create(to_save)

        return recipe

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data

    @atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)

        tags = validated_data.pop('tags')
        instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients')
        IngredientToRecipe.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()

        to_save = [
            IngredientToRecipe(ingredient=item['id'],
                               amount=item['amount'],
                               recipe=instance) for item in ingredients]
        IngredientToRecipe.objects.bulk_create(to_save)

        instance.save()
        return instance
