"""
Django views for Recipe Management Application

This module contains all view functions for displaying and managing recipes.
Uses HTMX for dynamic content updates without full page reloads.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Recipe, Ingredient, RecipeIngredient
from .forms import RecipeForm, RecipeIngredientFormSet


def recipe_list(request):
    """
    Display list of all recipes.

    Template: recipe_list.html
    Context:
        recipes: QuerySet of all Recipe objects, ordered by creation date
    """
    recipes = Recipe.objects.all()
    return render(request, 'recipe_list.html', {'recipes': recipes})


def recipe_detail(request, pk):
    """
    Display detailed view of a single recipe with all ingredients.

    Args:
        pk: Primary key of the recipe to display

    Template: recipe_detail.html
    Context:
        recipe: Recipe object with prefetched ingredients
    """
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related('recipe_ingredients__ingredient'),
        pk=pk
    )
    return render(request, 'recipe_detail.html', {'recipe': recipe})


def recipe_create(request):
    """
    Create a new recipe with ingredients.

    Handles both GET (display form) and POST (save recipe) requests.
    Uses inline formset for managing multiple ingredients.

    Template: recipe_form.html
    Context:
        form: RecipeForm instance
        formset: RecipeIngredientFormSet instance
        action: 'create' (to differentiate from edit)
    """
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        formset = RecipeIngredientFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            # Save recipe first
            recipe = form.save()

            # Save ingredients with recipe foreign key
            formset.instance = recipe
            formset.save()

            # Redirect to the newly created recipe
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
        formset = RecipeIngredientFormSet()

    return render(request, 'recipe_form.html', {
        'form': form,
        'formset': formset,
        'action': 'create'
    })


def recipe_edit(request, pk):
    """
    Edit an existing recipe and its ingredients.

    Handles both GET (display form) and POST (save changes) requests.
    Uses inline formset for managing multiple ingredients.

    Args:
        pk: Primary key of the recipe to edit

    Template: recipe_form.html
    Context:
        form: RecipeForm instance with existing data
        formset: RecipeIngredientFormSet instance with existing ingredients
        recipe: Recipe object being edited
        action: 'edit' (to differentiate from create)
    """
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)

    return render(request, 'recipe_form.html', {
        'form': form,
        'formset': formset,
        'recipe': recipe,
        'action': 'edit'
    })


def recipe_delete(request, pk):
    """
    Delete a recipe.

    HTMX endpoint: Expects DELETE method and returns HX-Redirect header.
    This allows HTMX to handle the redirect after deletion.

    Args:
        pk: Primary key of the recipe to delete

    Returns:
        HttpResponse with HX-Redirect header to recipe list
    """
    if request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe.delete()

        # Return empty response with HTMX redirect header
        response = HttpResponse(status=200)
        response['HX-Redirect'] = '/'
        return response

    # If not DELETE method, redirect to list
    return redirect('recipe_list')


def recipe_search(request):
    """
    Search recipes by ingredient name.

    HTMX endpoint: Returns HTML fragment of recipe cards based on search query.
    This is called via HTMX from the search input field.

    Query params:
        ingredient: Name (or partial name) of ingredient to search for

    Template: includes/recipe_card_list.html (fragment)
    Context:
        recipes: QuerySet of matching Recipe objects
    """
    query = request.GET.get('ingredient', '').strip()

    if query:
        # Search for recipes containing the ingredient
        recipes = Recipe.objects.filter(
            recipe_ingredients__ingredient__name__icontains=query
        ).distinct()
    else:
        # If no query, return all recipes
        recipes = Recipe.objects.all()

    # Return only the recipe cards (HTMX will swap this into the page)
    return render(request, 'includes/recipe_card_list.html', {'recipes': recipes})


def ingredient_autocomplete(request):
    """
    Autocomplete endpoint for ingredient names.

    HTMX endpoint: Returns HTML options for datalist based on search query.
    Can be used to suggest existing ingredients while typing.

    Query params:
        q: Search query for ingredient name

    Template: includes/ingredient_options.html (fragment)
    Context:
        ingredients: QuerySet of matching Ingredient objects
    """
    query = request.GET.get('q', '').strip()

    if query:
        ingredients = Ingredient.objects.filter(
            name__icontains=query
        )[:10]  # Limit to 10 suggestions
    else:
        ingredients = Ingredient.objects.none()

    return render(request, 'includes/ingredient_options.html', {
        'ingredients': ingredients
    })
