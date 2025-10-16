"""
Unit tests for Recipe application views.

Tests all view functions including HTMX endpoints.
"""

from django.test import TestCase, Client
from django.urls import reverse
from recipes.models import Recipe, Ingredient, RecipeIngredient


class RecipeListViewTest(TestCase):
    """Test cases for recipe_list view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.url = reverse('recipe_list')

    def test_recipe_list_get_returns_200(self):
        """Test GET request returns 200 OK."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_recipe_list_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'recipe_list.html')

    def test_recipe_list_shows_all_recipes(self):
        """Test view shows all recipes."""
        Recipe.objects.create(
            name='Recipe 1',
            instructions='Test',
            prep_time=10,
            cook_time=20,
            servings=4
        )
        Recipe.objects.create(
            name='Recipe 2',
            instructions='Test',
            prep_time=15,
            cook_time=25,
            servings=2
        )

        response = self.client.get(self.url)
        self.assertEqual(len(response.context['recipes']), 2)

    def test_recipe_list_empty_shows_message(self):
        """Test empty list shows appropriate message."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Ei vielä reseptejä')

    def test_recipe_list_context_contains_recipes(self):
        """Test context contains recipes queryset."""
        response = self.client.get(self.url)
        self.assertIn('recipes', response.context)


class RecipeDetailViewTest(TestCase):
    """Test cases for recipe_detail view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            description='Test description',
            instructions='Test instructions',
            prep_time=10,
            cook_time=20,
            servings=4
        )
        self.ingredient = Ingredient.objects.create(name='Test Ingredient')
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity='100 g'
        )
        self.url = reverse('recipe_detail', kwargs={'pk': self.recipe.pk})

    def test_recipe_detail_get_returns_200(self):
        """Test GET request returns 200 OK."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'recipe_detail.html')

    def test_recipe_detail_shows_recipe_name(self):
        """Test view displays recipe name."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Test Recipe')

    def test_recipe_detail_shows_ingredients(self):
        """Test view displays ingredients."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Test Ingredient')
        self.assertContains(response, '100 g')

    def test_recipe_detail_404_for_nonexistent(self):
        """Test view returns 404 for non-existent recipe."""
        url = reverse('recipe_detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_context_contains_recipe(self):
        """Test context contains recipe object."""
        response = self.client.get(self.url)
        self.assertIn('recipe', response.context)
        self.assertEqual(response.context['recipe'].name, 'Test Recipe')


class RecipeCreateViewTest(TestCase):
    """Test cases for recipe_create view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.url = reverse('recipe_create')

    def test_recipe_create_get_returns_200(self):
        """Test GET request returns 200 OK (shows form)."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_recipe_create_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'recipe_form.html')

    def test_recipe_create_post_with_valid_data(self):
        """Test POST with valid data creates recipe."""
        data = {
            'name': 'New Recipe',
            'description': 'New description',
            'instructions': 'New instructions',
            'prep_time': 15,
            'cook_time': 30,
            'servings': 4,

            # Formset data
            'recipe_ingredients-TOTAL_FORMS': '1',
            'recipe_ingredients-INITIAL_FORMS': '0',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',

            'recipe_ingredients-0-ingredient_name': 'Test Ingredient',
            'recipe_ingredients-0-quantity': '200 g',
            'recipe_ingredients-0-id': '',
        }

        response = self.client.post(self.url, data)

        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)

        # Recipe should be created
        self.assertEqual(Recipe.objects.count(), 1)
        recipe = Recipe.objects.first()
        self.assertEqual(recipe.name, 'New Recipe')

        # Ingredient should be created
        self.assertEqual(Ingredient.objects.count(), 1)
        self.assertEqual(RecipeIngredient.objects.count(), 1)

    def test_recipe_create_post_redirects_to_detail(self):
        """Test POST redirects to recipe detail page."""
        data = {
            'name': 'New Recipe',
            'instructions': 'Instructions',
            'prep_time': 10,
            'cook_time': 20,
            'servings': 2,

            'recipe_ingredients-TOTAL_FORMS': '1',
            'recipe_ingredients-INITIAL_FORMS': '0',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',

            'recipe_ingredients-0-ingredient_name': 'Ingredient',
            'recipe_ingredients-0-quantity': '100 g',
            'recipe_ingredients-0-id': '',
        }

        response = self.client.post(self.url, data)
        recipe = Recipe.objects.first()
        expected_url = reverse('recipe_detail', kwargs={'pk': recipe.pk})
        self.assertRedirects(response, expected_url)

    def test_recipe_create_post_with_invalid_data(self):
        """Test POST with invalid data shows errors."""
        data = {
            'name': '',  # Invalid: empty name
            'instructions': 'Test',
            'prep_time': 10,
            'cook_time': 20,
            'servings': 2,

            'recipe_ingredients-TOTAL_FORMS': '1',
            'recipe_ingredients-INITIAL_FORMS': '0',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',

            'recipe_ingredients-0-ingredient_name': 'Ingredient',
            'recipe_ingredients-0-quantity': '100 g',
            'recipe_ingredients-0-id': '',
        }

        response = self.client.post(self.url, data)

        # Should not redirect (stays on form)
        self.assertEqual(response.status_code, 200)

        # No recipe should be created
        self.assertEqual(Recipe.objects.count(), 0)

    def test_recipe_create_context_has_form_and_formset(self):
        """Test GET context contains form and formset."""
        response = self.client.get(self.url)
        self.assertIn('form', response.context)
        self.assertIn('formset', response.context)
        self.assertEqual(response.context['action'], 'create')


class RecipeEditViewTest(TestCase):
    """Test cases for recipe_edit view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.recipe = Recipe.objects.create(
            name='Original Recipe',
            instructions='Original instructions',
            prep_time=10,
            cook_time=20,
            servings=4
        )
        self.ingredient = Ingredient.objects.create(name='Original Ingredient')
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity='100 g'
        )
        self.url = reverse('recipe_edit', kwargs={'pk': self.recipe.pk})

    def test_recipe_edit_get_returns_200(self):
        """Test GET request returns 200 OK."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_recipe_edit_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'recipe_form.html')

    def test_recipe_edit_get_shows_prefilled_form(self):
        """Test GET shows form with existing data."""
        response = self.client.get(self.url)
        self.assertContains(response, 'Original Recipe')
        self.assertContains(response, 'Original instructions')

    def test_recipe_edit_post_updates_recipe(self):
        """Test POST updates recipe."""
        # Get the existing recipe ingredient ID
        recipe_ingredient = self.recipe.recipe_ingredients.first()

        data = {
            'name': 'Updated Recipe',
            'instructions': 'Updated instructions',
            'prep_time': 15,
            'cook_time': 25,
            'servings': 6,

            'recipe_ingredients-TOTAL_FORMS': '1',
            'recipe_ingredients-INITIAL_FORMS': '1',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',

            'recipe_ingredients-0-ingredient_name': 'Updated Ingredient',
            'recipe_ingredients-0-quantity': '200 g',
            'recipe_ingredients-0-id': str(recipe_ingredient.id),
        }

        response = self.client.post(self.url, data)

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Recipe should be updated
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.name, 'Updated Recipe')
        self.assertEqual(self.recipe.prep_time, 15)

    def test_recipe_edit_post_redirects_to_detail(self):
        """Test POST redirects to detail page."""
        # Get the existing recipe ingredient ID
        recipe_ingredient = self.recipe.recipe_ingredients.first()

        data = {
            'name': 'Updated',
            'instructions': 'Updated',
            'prep_time': 10,
            'cook_time': 20,
            'servings': 2,

            'recipe_ingredients-TOTAL_FORMS': '1',
            'recipe_ingredients-INITIAL_FORMS': '1',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',

            'recipe_ingredients-0-ingredient_name': 'Ingredient',
            'recipe_ingredients-0-quantity': '100 g',
            'recipe_ingredients-0-id': str(recipe_ingredient.id),
        }

        response = self.client.post(self.url, data)
        expected_url = reverse('recipe_detail', kwargs={'pk': self.recipe.pk})
        self.assertRedirects(response, expected_url)

    def test_recipe_edit_404_for_nonexistent(self):
        """Test view returns 404 for non-existent recipe."""
        url = reverse('recipe_edit', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_recipe_edit_context_has_recipe(self):
        """Test context contains recipe being edited."""
        response = self.client.get(self.url)
        self.assertIn('recipe', response.context)
        self.assertEqual(response.context['action'], 'edit')


class RecipeDeleteViewTest(TestCase):
    """Test cases for recipe_delete view (HTMX)."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.recipe = Recipe.objects.create(
            name='To Delete',
            instructions='Test',
            prep_time=10,
            cook_time=20,
            servings=4
        )
        self.url = reverse('recipe_delete', kwargs={'pk': self.recipe.pk})

    def test_recipe_delete_with_delete_method(self):
        """Test DELETE request removes recipe."""
        response = self.client.delete(self.url)

        # Should return 200 with HX-Redirect header
        self.assertEqual(response.status_code, 200)
        self.assertIn('HX-Redirect', response)
        self.assertEqual(response['HX-Redirect'], '/')

        # Recipe should be deleted
        self.assertEqual(Recipe.objects.count(), 0)

    def test_recipe_delete_cascades_to_ingredients(self):
        """Test deleting recipe also deletes recipe ingredients."""
        ingredient = Ingredient.objects.create(name='Test')
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=ingredient,
            quantity='100 g'
        )

        self.client.delete(self.url)

        # RecipeIngredient should be deleted
        self.assertEqual(RecipeIngredient.objects.count(), 0)

        # But Ingredient should still exist
        self.assertEqual(Ingredient.objects.count(), 1)

    def test_recipe_delete_with_get_redirects(self):
        """Test GET request redirects to list."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('recipe_list'))

    def test_recipe_delete_404_for_nonexistent(self):
        """Test DELETE returns 404 for non-existent recipe."""
        url = reverse('recipe_delete', kwargs={'pk': 99999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)


class RecipeSearchViewTest(TestCase):
    """Test cases for recipe_search view (HTMX)."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.url = reverse('recipe_search')

        # Create recipes with ingredients
        self.recipe1 = Recipe.objects.create(
            name='Pancakes',
            instructions='Test',
            prep_time=10,
            cook_time=20,
            servings=4
        )
        milk = Ingredient.objects.create(name='Milk')
        RecipeIngredient.objects.create(
            recipe=self.recipe1,
            ingredient=milk,
            quantity='2 dl'
        )

        self.recipe2 = Recipe.objects.create(
            name='Soup',
            instructions='Test',
            prep_time=15,
            cook_time=30,
            servings=6
        )
        water = Ingredient.objects.create(name='Water')
        RecipeIngredient.objects.create(
            recipe=self.recipe2,
            ingredient=water,
            quantity='1 L'
        )

    def test_recipe_search_with_query_filters_recipes(self):
        """Test search with ingredient query filters recipes."""
        response = self.client.get(self.url, {'ingredient': 'Milk'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pancakes')
        self.assertNotContains(response, 'Soup')

    def test_recipe_search_without_query_returns_all(self):
        """Test search without query returns all recipes."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pancakes')
        self.assertContains(response, 'Soup')

    def test_recipe_search_case_insensitive(self):
        """Test search is case insensitive."""
        response = self.client.get(self.url, {'ingredient': 'milk'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pancakes')

    def test_recipe_search_partial_match(self):
        """Test search matches partial ingredient names."""
        response = self.client.get(self.url, {'ingredient': 'Mil'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pancakes')

    def test_recipe_search_uses_correct_template(self):
        """Test view uses correct template fragment."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'includes/recipe_card_list.html')

    def test_recipe_search_no_results(self):
        """Test search with no matching results."""
        response = self.client.get(self.url, {'ingredient': 'NonExistent'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ei reseptejä')
