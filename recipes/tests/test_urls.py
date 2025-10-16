"""
Unit tests for Recipe application URLs.

Tests URL routing and reverse URL lookups.
"""

from django.test import TestCase
from django.urls import reverse, resolve
from recipes import views


class RecipeURLsTest(TestCase):
    """Test cases for recipe URLs."""

    def test_recipe_list_url_resolves(self):
        """Test root URL resolves to recipe_list view."""
        url = reverse('recipe_list')
        self.assertEqual(url, '/')
        self.assertEqual(resolve(url).func, views.recipe_list)

    def test_recipe_detail_url_resolves(self):
        """Test recipe detail URL resolves correctly."""
        url = reverse('recipe_detail', kwargs={'pk': 1})
        self.assertEqual(url, '/recipe/1/')
        self.assertEqual(resolve(url).func, views.recipe_detail)

    def test_recipe_create_url_resolves(self):
        """Test recipe create URL resolves correctly."""
        url = reverse('recipe_create')
        self.assertEqual(url, '/recipe/new/')
        self.assertEqual(resolve(url).func, views.recipe_create)

    def test_recipe_edit_url_resolves(self):
        """Test recipe edit URL resolves correctly."""
        url = reverse('recipe_edit', kwargs={'pk': 1})
        self.assertEqual(url, '/recipe/1/edit/')
        self.assertEqual(resolve(url).func, views.recipe_edit)

    def test_recipe_delete_url_resolves(self):
        """Test recipe delete URL resolves correctly."""
        url = reverse('recipe_delete', kwargs={'pk': 1})
        self.assertEqual(url, '/recipe/1/delete/')
        self.assertEqual(resolve(url).func, views.recipe_delete)

    def test_recipe_search_url_resolves(self):
        """Test recipe search URL resolves correctly."""
        url = reverse('recipe_search')
        self.assertEqual(url, '/recipes/search/')
        self.assertEqual(resolve(url).func, views.recipe_search)

    def test_url_reverse_with_different_ids(self):
        """Test URL reverse works with different recipe IDs."""
        for pk in [1, 10, 100, 999]:
            detail_url = reverse('recipe_detail', kwargs={'pk': pk})
            self.assertEqual(detail_url, f'/recipe/{pk}/')

            edit_url = reverse('recipe_edit', kwargs={'pk': pk})
            self.assertEqual(edit_url, f'/recipe/{pk}/edit/')

            delete_url = reverse('recipe_delete', kwargs={'pk': pk})
            self.assertEqual(delete_url, f'/recipe/{pk}/delete/')
