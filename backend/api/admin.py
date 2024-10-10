from django.contrib import admin

from api.models import Tag, Ingredient, Recipe, RecipeIngredient


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


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',  # id
        'ingredient',
        'recipe',
        'amount'
    )
    search_fields = ('recipe__name', 'ingredient__name')


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    list_display = (
        'pk',
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

    def favorites_amount(self, obj):
        return obj.favorites.count()


admin.site.register(Tag, ApiTagAdmin)
admin.site.register(Ingredient, ApiIngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(
    RecipeIngredient,
    IngredientsInRecipeAdmin
)
# admin.site.register(Favorites, FavoriteAdmin)
# admin.site.register(ShoppingCart, ShoppingCartAdmin)

# class FavoriteAdmin(admin.ModelAdmin):
#     list_display = (
#         'pk',
#         'user',
#         'recipe'
#     )
#     search_fields = (
#         'user__username',
#         'user__email',
#         'recipe__name'
#     )


# class ShoppingCartAdmin(admin.ModelAdmin):
#     list_display = (
#         'pk',
#         'user',
#         'recipe'
#     )
#     search_fields = (
#         'user__username',
#         'user__email',
#         'recipe__name'
#     )
