"""
Django models for Recipe Management Application

This module contains the database models for managing recipes, ingredients,
and the relationships between them.
"""

from django.db import models
from django.urls import reverse


class Recipe(models.Model):
    """
    Model representing a recipe.

    Attributes:
        name: Recipe name (max 200 characters)
        description: Short description of the recipe
        instructions: Detailed cooking instructions
        prep_time: Preparation time in minutes
        cook_time: Cooking time in minutes
        servings: Number of servings the recipe makes
        created_at: Timestamp when recipe was created
        updated_at: Timestamp when recipe was last updated
    """
    name = models.CharField(max_length=200, verbose_name="Nimi")
    description = models.TextField(blank=True, verbose_name="Kuvaus")
    instructions = models.TextField(verbose_name="Valmistusohjeet")
    prep_time = models.PositiveIntegerField(
        verbose_name="Valmistusaika",
        help_text="Minuutteina"
    )
    cook_time = models.PositiveIntegerField(
        verbose_name="Kypsennysaika",
        help_text="Minuutteina"
    )
    servings = models.PositiveIntegerField(verbose_name="Annokset")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Luotu")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Päivitetty")

    class Meta:
        ordering = ['-created_at']  # Newest first
        verbose_name = 'Resepti'
        verbose_name_plural = 'Reseptit'

    def __str__(self):
        """String representation of the recipe."""
        return self.name

    def get_absolute_url(self):
        """Returns the URL to access a detail view for this recipe."""
        return reverse('recipe_detail', kwargs={'pk': self.pk})

    @property
    def total_time(self):
        """Calculate total time (prep + cook) in minutes."""
        return self.prep_time + self.cook_time


class Ingredient(models.Model):
    """
    Model representing an ingredient.

    Ingredients are stored separately to avoid duplication and allow
    for searching recipes by ingredient.

    Attributes:
        name: Unique ingredient name
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nimi"
    )

    class Meta:
        ordering = ['name']  # Alphabetical order
        verbose_name = 'Raaka-aine'
        verbose_name_plural = 'Raaka-aineet'

    def __str__(self):
        """String representation of the ingredient."""
        return self.name


class RecipeIngredient(models.Model):
    """
    Model representing the relationship between recipes and ingredients.

    This is a through model that connects recipes with ingredients and
    includes the quantity needed for the recipe.

    Attributes:
        recipe: Foreign key to Recipe
        ingredient: Foreign key to Ingredient
        quantity: Amount of ingredient needed (e.g., "2 dl", "500 g")
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name="Resepti"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Raaka-aine"
    )
    quantity = models.CharField(
        max_length=50,
        verbose_name="Määrä",
        help_text="esim. '2 dl', '500 g', '1 kpl'"
    )

    class Meta:
        unique_together = ['recipe', 'ingredient']  # No duplicate ingredients per recipe
        verbose_name = 'Reseptin raaka-aine'
        verbose_name_plural = 'Reseptin raaka-aineet'

    def __str__(self):
        """String representation of the recipe ingredient."""
        return f"{self.quantity} {self.ingredient.name}"
