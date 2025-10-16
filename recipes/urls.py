"""
URL configuration for recipes app.

Maps URL patterns to view functions.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.recipe_list, name='recipe_list'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/new/', views.recipe_create, name='recipe_create'),
    path('recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),

    # HTMX endpoints (return HTML fragments)
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('recipes/search/', views.recipe_search, name='recipe_search'),
    path('ingredients/autocomplete/', views.ingredient_autocomplete, name='ingredient_autocomplete'),
]
