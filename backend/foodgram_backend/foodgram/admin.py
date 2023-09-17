from django.contrib import admin

from foodgram.models import (Tag, Recipe, Ingredient, IngredientToRecipe,
                             Favorite, ShoppingCart)


class RecipeAdmin(admin.ModelAdmin):
    search_fields = ('name', 'author__email', 'tags__slug')
    readonly_fields = ('favorited',)

    @admin.display()
    def favorited(self, obj):
        return obj.favorited.count()


class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(IngredientToRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
