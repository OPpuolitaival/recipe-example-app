"""
Django admin configuration for Recipe Management Application

This module configures the admin interface for managing recipes,
ingredients, and recipe-ingredient relationships.
"""

from django.contrib import admin
from .models import Recipe, Ingredient, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    """
    Inline admin for RecipeIngredient.

    Allows editing recipe ingredients directly within the Recipe admin form.
    """
    model = RecipeIngredient
    extra = 3  # Show 3 empty forms by default
    autocomplete_fields = ['ingredient']  # Enable autocomplete for ingredients


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Admin configuration for Recipe model.

    Features:
    - List display with key fields
    - Search functionality
    - Filtering by dates
    - Inline ingredient editing
    """
    list_display = ['name', 'servings', 'prep_time', 'cook_time', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'description', 'instructions']
    date_hierarchy = 'created_at'
    inlines = [RecipeIngredientInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Perustiedot', {
            'fields': ('name', 'description')
        }),
        ('Valmistus', {
            'fields': ('instructions', 'prep_time', 'cook_time', 'servings')
        }),
        ('Metatiedot', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Admin configuration for Ingredient model.

    Features:
    - Simple list display
    - Search functionality
    - Autocomplete support for use in other admin forms
    """
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """
    Admin configuration for RecipeIngredient model.

    This is usually managed through the Recipe admin inline,
    but this provides a standalone view if needed.
    """
    list_display = ['recipe', 'ingredient', 'quantity']
    list_filter = ['recipe', 'ingredient']
    search_fields = ['recipe__name', 'ingredient__name']
    autocomplete_fields = ['recipe', 'ingredient']
