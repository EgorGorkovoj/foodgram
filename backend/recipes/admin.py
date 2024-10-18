from django.contrib import admin

from recipes.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                            Favorites, ShoppingList, ShortLinkRecipe)


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class ApiTagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class ApiIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class ApiIngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'ingredient',
        'recipe',
        'amount'
    )
    search_fields = ('recipe__name', 'ingredient__name')


class ApiRecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    list_display = (
        'id',
        'name',
        'author',
        'favorites_amount',
    )
    search_fields = (
        'name',
        'author__username',
    )
    list_filter = ('tags__name',)
    readonly_fields = ('favorites_amount',)
    list_display_links = ('name',)

    def favorites_amount(self, obj):
        return obj.favorites.count()


class ApiFavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name',
    )


class ApiShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name',
    )


class ApiShortLinkRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'short_link',
        'original_link',
    )
    search_fields = (
        'recipe__name',
    )


admin.site.register(Tag, ApiTagAdmin)
admin.site.register(Ingredient, ApiIngredientAdmin)
admin.site.register(Recipe, ApiRecipeAdmin)
admin.site.register(
    RecipeIngredient,
    ApiIngredientsInRecipeAdmin
)
admin.site.register(Favorites, ApiFavoriteAdmin)
admin.site.register(ShoppingList, ApiShoppingListAdmin)
admin.site.register(ShortLinkRecipe, ApiShortLinkRecipeAdmin)
