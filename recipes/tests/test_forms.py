"""
Unit tests for Recipe application forms.

Tests RecipeForm, RecipeIngredientForm, and RecipeIngredientFormSet.
"""

from django.test import TestCase
from recipes.forms import RecipeForm, RecipeIngredientForm, RecipeIngredientFormSet
from recipes.models import Recipe, Ingredient, RecipeIngredient


class RecipeFormTest(TestCase):
    """Test cases for RecipeForm."""

    def test_valid_form(self):
        """Test form with all valid data."""
        form_data = {
            'name': 'Test Recipe',
            'description': 'A delicious test recipe',
            'instructions': 'Mix and cook',
            'prep_time': 15,
            'cook_time': 30,
            'servings': 4,
        }
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_required_name(self):
        """Test form with missing name field."""
        form_data = {
            'description': 'Test description',
            'instructions': 'Test instructions',
            'prep_time': 10,
            'cook_time': 20,
            'servings': 2,
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_missing_required_instructions(self):
        """Test form with missing instructions field."""
        form_data = {
            'name': 'Test Recipe',
            'prep_time': 10,
            'cook_time': 20,
            'servings': 2,
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('instructions', form.errors)

    def test_negative_prep_time(self):
        """Test form with negative prep_time."""
        form_data = {
            'name': 'Test Recipe',
            'instructions': 'Test',
            'prep_time': -5,
            'cook_time': 20,
            'servings': 2,
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('prep_time', form.errors)

    def test_negative_cook_time(self):
        """Test form with negative cook_time."""
        form_data = {
            'name': 'Test Recipe',
            'instructions': 'Test',
            'prep_time': 10,
            'cook_time': -15,
            'servings': 2,
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cook_time', form.errors)

    def test_empty_name_validation(self):
        """Test form with empty name string."""
        form_data = {
            'name': '   ',
            'instructions': 'Test',
            'prep_time': 10,
            'cook_time': 20,
            'servings': 2,
        }
        form = RecipeForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_blank_description_allowed(self):
        """Test form with blank description (should be valid)."""
        form_data = {
            'name': 'Test Recipe',
            'description': '',
            'instructions': 'Test instructions',
            'prep_time': 10,
            'cook_time': 20,
            'servings': 2,
        }
        form = RecipeForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_fields_have_labels(self):
        """Test form fields have correct labels."""
        form = RecipeForm()
        self.assertEqual(form.fields['name'].label, 'Reseptin nimi')
        self.assertEqual(form.fields['instructions'].label, 'Valmistusohjeet')


class RecipeIngredientFormTest(TestCase):
    """Test cases for RecipeIngredientForm."""

    def setUp(self):
        """Set up test data."""
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            instructions='Test',
            prep_time=10,
            cook_time=20,
            servings=4
        )

    def test_valid_form_creates_ingredient(self):
        """Test valid form creates ingredient if it doesn't exist."""
        form_data = {
            'ingredient_name': 'new ingredient',
            'quantity': '2 cups',
        }
        form = RecipeIngredientForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Save with recipe - the form's save() method creates the ingredient
        recipe_ingredient = form.save(commit=False)
        recipe_ingredient.recipe = self.recipe
        recipe_ingredient.save()

        # Check ingredient was created (capitalize() makes it 'New ingredient')
        self.assertEqual(Ingredient.objects.filter(name='New ingredient').count(), 1)

    def test_valid_form_finds_existing_ingredient(self):
        """Test valid form finds existing ingredient."""
        # Create ingredient first
        existing = Ingredient.objects.create(name='Existing Ingredient')

        form_data = {
            'ingredient_name': 'Existing Ingredient',
            'quantity': '1 kg',
        }
        form = RecipeIngredientForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Should not create duplicate
        recipe_ingredient = form.save(commit=False)
        recipe_ingredient.recipe = self.recipe
        recipe_ingredient.save()

        self.assertEqual(Ingredient.objects.filter(name='Existing Ingredient').count(), 1)

    def test_missing_ingredient_name(self):
        """Test form with missing ingredient name."""
        form_data = {
            'quantity': '100 g',
        }
        form = RecipeIngredientForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredient_name', form.errors)

    def test_empty_ingredient_name(self):
        """Test form with empty ingredient name."""
        form_data = {
            'ingredient_name': '   ',
            'quantity': '100 g',
        }
        form = RecipeIngredientForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredient_name', form.errors)

    def test_ingredient_name_capitalization(self):
        """Test ingredient name is capitalized."""
        form_data = {
            'ingredient_name': 'lowercase ingredient',
            'quantity': '50 ml',
        }
        form = RecipeIngredientForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['ingredient_name'], 'Lowercase ingredient')

    def test_form_initial_with_instance(self):
        """Test form is initialized with existing ingredient name."""
        ingredient = Ingredient.objects.create(name='Test Ingredient')
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=ingredient,
            quantity='200 g'
        )

        form = RecipeIngredientForm(instance=recipe_ingredient)
        self.assertEqual(form.fields['ingredient_name'].initial, 'Test Ingredient')


class RecipeIngredientFormSetTest(TestCase):
    """Test cases for RecipeIngredientFormSet."""

    def setUp(self):
        """Set up test data."""
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            instructions='Test',
            prep_time=10,
            cook_time=20,
            servings=4
        )

    def test_formset_with_valid_data(self):
        """Test formset with valid ingredient data."""
        formset_data = {
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

        formset = RecipeIngredientFormSet(data=formset_data, instance=self.recipe)
        self.assertTrue(formset.is_valid())

    def test_formset_minimum_one_ingredient(self):
        """Test formset requires at least one ingredient."""
        formset_data = {
            'recipe_ingredients-TOTAL_FORMS': '1',
            'recipe_ingredients-INITIAL_FORMS': '0',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',

            'recipe_ingredients-0-ingredient_name': '',
            'recipe_ingredients-0-quantity': '',
            'recipe_ingredients-0-id': '',
        }

        formset = RecipeIngredientFormSet(data=formset_data, instance=self.recipe)
        self.assertFalse(formset.is_valid())

    def test_formset_saves_ingredients(self):
        """Test formset saves ingredients correctly."""
        formset_data = {
            'recipe_ingredients-TOTAL_FORMS': '2',
            'recipe_ingredients-INITIAL_FORMS': '0',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',

            'recipe_ingredients-0-ingredient_name': 'Milk',
            'recipe_ingredients-0-quantity': '500 ml',
            'recipe_ingredients-0-id': '',

            'recipe_ingredients-1-ingredient_name': 'Eggs',
            'recipe_ingredients-1-quantity': '3 pcs',
            'recipe_ingredients-1-id': '',
        }

        formset = RecipeIngredientFormSet(data=formset_data, instance=self.recipe)
        self.assertTrue(formset.is_valid())
        formset.save()

        # Check ingredients were created
        self.assertEqual(self.recipe.recipe_ingredients.count(), 2)
        self.assertEqual(Ingredient.objects.count(), 2)

    def test_formset_can_delete(self):
        """Test formset can delete ingredients."""
        # Create existing ingredient
        ingredient = Ingredient.objects.create(name='Old Ingredient')
        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=ingredient,
            quantity='100 g'
        )

        formset_data = {
            'recipe_ingredients-TOTAL_FORMS': '1',
            'recipe_ingredients-INITIAL_FORMS': '1',
            'recipe_ingredients-MIN_NUM_FORMS': '1',
            'recipe_ingredients-MAX_NUM_FORMS': '1000',

            'recipe_ingredients-0-ingredient_name': 'Old Ingredient',
            'recipe_ingredients-0-quantity': '100 g',
            'recipe_ingredients-0-id': str(recipe_ingredient.id),
            'recipe_ingredients-0-DELETE': 'on',
        }

        formset = RecipeIngredientFormSet(data=formset_data, instance=self.recipe)
        # Note: This will fail validation because min_num=1 and we're deleting the only one
        # In real usage, there would be at least one non-deleted ingredient
        self.assertFalse(formset.is_valid())  # Should fail due to min_num validation
