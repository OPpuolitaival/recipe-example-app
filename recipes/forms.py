"""
Django forms for Recipe Management Application

This module contains forms for creating and editing recipes with their ingredients.
Uses Django formsets to handle multiple ingredients in a single form.
"""

from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, Ingredient, RecipeIngredient


class RecipeForm(forms.ModelForm):
    """
    Form for creating and editing Recipe objects.

    Includes all recipe fields except timestamps (auto-generated).
    """
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'instructions', 'prep_time', 'cook_time', 'servings']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reseptin nimi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Lyhyt kuvaus reseptistä',
                'rows': 3
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Valmistusohjeet vaihe vaiheelta',
                'rows': 8
            }),
            'prep_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'minuuttia'
            }),
            'cook_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'minuuttia'
            }),
            'servings': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'annosta'
            }),
        }
        labels = {
            'name': 'Reseptin nimi',
            'description': 'Kuvaus',
            'instructions': 'Valmistusohjeet',
            'prep_time': 'Valmistusaika (min)',
            'cook_time': 'Kypsennysaika (min)',
            'servings': 'Annokset',
        }

    def clean_name(self):
        """Validate that recipe name is not empty."""
        name = self.cleaned_data.get('name')
        if not name or name.strip() == '':
            raise forms.ValidationError('Reseptin nimi ei voi olla tyhjä.')
        return name.strip()

    def clean_prep_time(self):
        """Validate that prep time is positive."""
        prep_time = self.cleaned_data.get('prep_time')
        if prep_time and prep_time < 0:
            raise forms.ValidationError('Valmistusaika ei voi olla negatiivinen.')
        return prep_time

    def clean_cook_time(self):
        """Validate that cook time is positive."""
        cook_time = self.cleaned_data.get('cook_time')
        if cook_time and cook_time < 0:
            raise forms.ValidationError('Kypsennysaika ei voi olla negatiivinen.')
        return cook_time


class RecipeIngredientForm(forms.ModelForm):
    """
    Form for adding ingredients to a recipe.

    Allows entering ingredient name (with autocreate) and quantity.
    """
    ingredient_name = forms.CharField(
        max_length=100,
        label='Raaka-aine',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'esim. Maito'
        })
    )

    class Meta:
        model = RecipeIngredient
        fields = ['quantity']
        widgets = {
            'quantity': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'esim. 2 dl, 500 g'
            }),
        }
        labels = {
            'quantity': 'Määrä',
        }

    def __init__(self, *args, **kwargs):
        """Initialize form and set ingredient_name if editing."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.ingredient:
            self.fields['ingredient_name'].initial = self.instance.ingredient.name

    def clean_ingredient_name(self):
        """Validate and normalize ingredient name."""
        name = self.cleaned_data.get('ingredient_name')
        if not name or name.strip() == '':
            raise forms.ValidationError('Raaka-aineen nimi ei voi olla tyhjä.')
        return name.strip().capitalize()

    def save(self, commit=True):
        """
        Save the RecipeIngredient instance.

        Gets or creates the Ingredient from ingredient_name field.
        """
        instance = super().save(commit=False)
        ingredient_name = self.cleaned_data.get('ingredient_name')

        # Get or create the ingredient
        ingredient, created = Ingredient.objects.get_or_create(
            name=ingredient_name
        )
        instance.ingredient = ingredient

        if commit:
            instance.save()
        return instance


# Create inline formset for recipe ingredients
# This allows managing multiple ingredients in the recipe form
RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=5,  # Show 5 empty forms by default
    can_delete=True,  # Allow deleting ingredients
    min_num=1,  # At least 1 ingredient required
    validate_min=True,
)
