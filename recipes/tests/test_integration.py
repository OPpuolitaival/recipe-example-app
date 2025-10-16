"""
Integration tests for Recipe application.

Tests full workflows and interactions between components.
"""

from django.test import TestCase, Client
from django.urls import reverse
from recipes.models import Recipe, Ingredient, RecipeIngredient


class RecipeCRUDWorkflowTest(TestCase):
    """Test complete CRUD workflow for recipes."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_full_recipe_crud_workflow(self):
        """Test creating, viewing, editing, and deleting a recipe."""

        # 1. CREATE: Create a new recipe
        create_url = reverse('recipe_create')
        create_data = {
            'name': 'Integration Test Recipe',
            'description': 'Testing full workflow',
            'instructions': 'Step 1\nStep 2\nStep 3',
            'prep_time': 15,
            'cook_time': 30,
            'servings': 4,

            'recipe_ingredients-TOTAL_FORMS': '2',
            'recipe_ingredients-INITIAL_FORMS': '0',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',

            'recipe_ingredients-0-ingredient_name': 'Flour',
            'recipe_ingredients-0-quantity': '2 cups',
            'recipe_ingredients-0-id': '',

            'recipe_ingredients-1-ingredient_name': 'Sugar',
            'recipe_ingredients-1-quantity': '1 cup',
            'recipe_ingredients-1-id': '',
        }

        response = self.client.post(create_url, create_data)
        self.assertEqual(response.status_code, 302)

        # Verify recipe was created
        recipe = Recipe.objects.get(name='Integration Test Recipe')
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.prep_time, 15)
        self.assertEqual(recipe.cook_time, 30)

        # Verify ingredients were created
        self.assertEqual(recipe.recipe_ingredients.count(), 2)
        self.assertEqual(Ingredient.objects.count(), 2)

        # 2. READ: View the recipe
        detail_url = reverse('recipe_detail', kwargs={'pk': recipe.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Recipe')
        self.assertContains(response, 'Flour')
        self.assertContains(response, 'Sugar')

        # 3. UPDATE: Edit the recipe
        edit_url = reverse('recipe_edit', kwargs={'pk': recipe.pk})

        # Get existing recipe ingredient IDs
        recipe_ingredients = list(recipe.recipe_ingredients.all())

        edit_data = {
            'name': 'Updated Integration Recipe',
            'description': 'Updated description',
            'instructions': 'Updated instructions',
            'prep_time': 20,
            'cook_time': 40,
            'servings': 6,

            'recipe_ingredients-TOTAL_FORMS': '3',
            'recipe_ingredients-INITIAL_FORMS': '2',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',

            # Update first ingredient (Flour) with new quantity
            'recipe_ingredients-0-ingredient_name': 'Flour',
            'recipe_ingredients-0-quantity': '3 cups',
            'recipe_ingredients-0-id': str(recipe_ingredients[0].id),

            # Keep second ingredient (Sugar)
            'recipe_ingredients-1-ingredient_name': 'Sugar',
            'recipe_ingredients-1-quantity': '1 cup',
            'recipe_ingredients-1-id': str(recipe_ingredients[1].id),

            # Add new ingredient (Milk)
            'recipe_ingredients-2-ingredient_name': 'Milk',
            'recipe_ingredients-2-quantity': '500 ml',
            'recipe_ingredients-2-id': '',
        }

        response = self.client.post(edit_url, edit_data)
        self.assertEqual(response.status_code, 302)

        # Verify recipe was updated
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, 'Updated Integration Recipe')
        self.assertEqual(recipe.prep_time, 20)

        # Verify ingredients were updated (2 original + 1 new = 3)
        self.assertEqual(recipe.recipe_ingredients.count(), 3)

        # 4. DELETE: Delete the recipe
        delete_url = reverse('recipe_delete', kwargs={'pk': recipe.pk})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 200)

        # Verify recipe was deleted
        self.assertEqual(Recipe.objects.filter(pk=recipe.pk).count(), 0)

        # Verify recipe ingredients were deleted (cascade)
        self.assertEqual(RecipeIngredient.objects.filter(recipe_id=recipe.pk).count(), 0)

        # But ingredients should still exist
        self.assertGreater(Ingredient.objects.count(), 0)


class RecipeSearchWorkflowTest(TestCase):
    """Test recipe search workflows."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create recipe with Milk
        self.recipe1 = Recipe.objects.create(
            name='Pancakes',
            instructions='Make pancakes',
            prep_time=10,
            cook_time=15,
            servings=4
        )
        milk = Ingredient.objects.create(name='Milk')
        eggs = Ingredient.objects.create(name='Eggs')
        RecipeIngredient.objects.create(recipe=self.recipe1, ingredient=milk, quantity='2 dl')
        RecipeIngredient.objects.create(recipe=self.recipe1, ingredient=eggs, quantity='2 pcs')

        # Create recipe with Eggs only
        self.recipe2 = Recipe.objects.create(
            name='Omelette',
            instructions='Make omelette',
            prep_time=5,
            cook_time=10,
            servings=2
        )
        RecipeIngredient.objects.create(recipe=self.recipe2, ingredient=eggs, quantity='3 pcs')

    def test_search_by_single_ingredient(self):
        """Test searching recipes by single ingredient."""
        search_url = reverse('recipe_search')

        # Search for Milk
        response = self.client.get(search_url, {'ingredient': 'Milk'})
        self.assertContains(response, 'Pancakes')
        self.assertNotContains(response, 'Omelette')

        # Search for Eggs
        response = self.client.get(search_url, {'ingredient': 'Eggs'})
        self.assertContains(response, 'Pancakes')
        self.assertContains(response, 'Omelette')

    def test_search_shows_all_without_query(self):
        """Test search without query shows all recipes."""
        search_url = reverse('recipe_search')
        response = self.client.get(search_url)

        self.assertContains(response, 'Pancakes')
        self.assertContains(response, 'Omelette')


class RecipeWithMultipleIngredientsTest(TestCase):
    """Test recipes with multiple ingredients."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_create_recipe_with_many_ingredients(self):
        """Test creating a recipe with many ingredients."""
        create_url = reverse('recipe_create')

        # Create recipe with 5 ingredients
        data = {
            'name': 'Complex Recipe',
            'instructions': 'Complex instructions',
            'prep_time': 30,
            'cook_time': 60,
            'servings': 8,

            'recipe_ingredients-TOTAL_FORMS': '5',
            'recipe_ingredients-INITIAL_FORMS': '0',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',
        }

        # Add 5 ingredients
        ingredients = [
            ('Flour', '500 g'),
            ('Sugar', '200 g'),
            ('Butter', '150 g'),
            ('Eggs', '4 pcs'),
            ('Vanilla', '1 tsp'),
        ]

        for i, (name, quantity) in enumerate(ingredients):
            data[f'recipe_ingredients-{i}-ingredient_name'] = name
            data[f'recipe_ingredients-{i}-quantity'] = quantity
            data[f'recipe_ingredients-{i}-id'] = ''

        response = self.client.post(create_url, data)
        self.assertEqual(response.status_code, 302)

        # Verify all ingredients were created
        recipe = Recipe.objects.get(name='Complex Recipe')
        self.assertEqual(recipe.recipe_ingredients.count(), 5)

        # Verify each ingredient exists
        ingredient_names = [ri.ingredient.name for ri in recipe.recipe_ingredients.all()]
        for name, _ in ingredients:
            self.assertIn(name, ingredient_names)


class HTMXWorkflowTest(TestCase):
    """Test HTMX-specific workflows."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

    def test_htmx_delete_returns_redirect_header(self):
        """Test HTMX delete returns HX-Redirect header."""
        recipe = Recipe.objects.create(
            name='To Delete',
            instructions='Test',
            prep_time=10,
            cook_time=20,
            servings=4
        )

        delete_url = reverse('recipe_delete', kwargs={'pk': recipe.pk})
        response = self.client.delete(delete_url)

        # Should have HX-Redirect header
        self.assertIn('HX-Redirect', response)
        self.assertEqual(response['HX-Redirect'], '/')

    def test_htmx_search_updates_fragment(self):
        """Test HTMX search returns HTML fragment."""
        Recipe.objects.create(
            name='Test Recipe',
            instructions='Test',
            prep_time=10,
            cook_time=20,
            servings=4
        )

        search_url = reverse('recipe_search')
        response = self.client.get(search_url)

        # Should use fragment template
        self.assertTemplateUsed(response, 'includes/recipe_card_list.html')

        # Should not include full page structure
        self.assertNotContains(response, '<html>')
        self.assertNotContains(response, '<head>')
