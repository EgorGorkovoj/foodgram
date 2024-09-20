from django.contrib import admin

from api.models import Tag, Ingredient


class ApiTagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class ApiIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


admin.site.register(Tag, ApiTagAdmin)
admin.site.register(Ingredient, ApiIngredientAdmin)
