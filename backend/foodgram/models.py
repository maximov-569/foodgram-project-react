from django.db import models
from django.utils.html import format_html
from users.models import User


class Tag(models.Model):
    """Short tag allow to specify recipe and make site explore easier."""
    name = models.CharField(
        max_length=15,
        unique=True,
        null=False,
        blank=False,
    )
    color = models.CharField(
        max_length=7,
        default='#ffffff',
    )

    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            self.color,
        )

    slug = models.SlugField(
        max_length=15,
        unique=True,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ['name']


class Ingredient(models.Model):
    """Ingredient model.

    Contents info about ingredient."""
    name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
    )
    measurement_unit = models.TextField(
        max_length=15,
        blank=False,
        null=False,
    )


class Recipe(models.Model):
    """Recipe model.

    tag and ingredients - m2m fields.
    ingredients - make relations through IngredientToRecipe model."""
    author = models.ForeignKey(
        User, related_name='recipes',
        on_delete=models.CASCADE,
        blank=False,
        null=False,

    )
    name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        unique=True,
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=False,
        default=None,
        blank=False,
    )
    text = models.TextField(
        max_length=600,
        null=False,
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag, related_name='recipes',
        blank=False,
    )
    cooking_time = models.IntegerField(
        null=False,
        blank=False,
    )
    ingredients = models.ManyToManyField(
        blank=False,
        through='foodgram.IngredientToRecipe',
        through_fields=('recipe', 'ingredient'),
        related_name='recipes',
        to=Ingredient
    )
    pub_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['pub_date']


class IngredientToRecipe(models.Model):
    """Connect ingredient and recipe.

    amount - additional field, allows to provide amount of ingredient
    in related recipe.
    """
    ingredient = models.ForeignKey(
        Ingredient, related_name='recipe',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe, related_name='ingredient',
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        blank=False,
        null=False,
        default=0,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='Unique pair constraint.'
            )
        ]


class Favorite(models.Model):
    """Provide connection between user and recipe models. ALlow user to
    'keep in mind' recipes."""
    user = models.ForeignKey(
        User, related_name='favorite',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe, related_name='favorited',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )


class ShoppingCart(models.Model):
    """Additional model for recipe 'following'.
    Difference is that objects in shopping cart can be presented like
    'amount of ingredients to buy' through 'download_shopping_cart' func."""
    user = models.OneToOneField(
        User, related_name='shopping_cart',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    recipes = models.ManyToManyField(
        Recipe, related_name='shopping_carts',
    )
