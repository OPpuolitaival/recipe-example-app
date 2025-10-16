# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-based recipe management application with HTMX for dynamic UI updates. Built for educational purposes and test automation practice. Uses Finnish language in UI and documentation.

## Development Commands

### Running the Application

**Start development server:**
```bash
./run.sh
```
This script automatically installs dependencies (via uv), runs migrations, and starts the server at http://localhost:8000

**Manual commands:**
```bash
uv run python manage.py runserver              # Start dev server
uv run python manage.py migrate                # Run migrations
uv run python manage.py makemigrations         # Create new migrations
uv run python manage.py createsuperuser        # Create admin user
```

### Testing

**Run tests:**
```bash
./test_run.sh                    # All recipes tests
./test_run.sh --models           # Model tests only
./test_run.sh --views            # View tests only
./test_run.sh --forms            # Form tests only
./test_run.sh --coverage-html    # Generate HTML coverage report
./test_run.sh --parallel         # Parallel execution
./test_run.sh --failfast         # Stop on first failure
```

**Django test commands:**
```bash
uv run python manage.py test                           # All tests
uv run python manage.py test recipes.tests.test_models # Specific module
uv run python manage.py test --parallel --failfast     # Fast testing
```

### Test Data Generation

```bash
./generate_test_data.sh                # Generate 10 recipes
./generate_test_data.sh --recipes 20   # Generate 20 recipes
./generate_test_data.sh --clear        # Clear data and generate 10 recipes
```

## Architecture

### Core Models (recipes/models.py)

1. **Recipe** - Main recipe model with prep_time, cook_time, servings, instructions
2. **Ingredient** - Unique ingredient names (shared across recipes)
3. **RecipeIngredient** - Many-to-many through model linking Recipe ↔ Ingredient with quantity

Key relationships:
- Recipe has many RecipeIngredients (via `recipe_ingredients` related_name)
- RecipeIngredient links to both Recipe and Ingredient
- Ingredients are get_or_created to avoid duplicates

### Views Pattern (recipes/views.py)

**Traditional views:**
- `recipe_list` - Lists all recipes
- `recipe_detail` - Shows single recipe with prefetched ingredients
- `recipe_create` - Creates recipe with inline formset for ingredients
- `recipe_edit` - Edits recipe with inline formset

**HTMX endpoints (return HTML fragments):**
- `recipe_delete` - DELETE method, returns HX-Redirect header
- `recipe_search` - Filters recipes by ingredient name, returns recipe cards
- `ingredient_autocomplete` - Returns datalist options for ingredient suggestions

### Forms Architecture (recipes/forms.py)

**RecipeForm:**
- Standard ModelForm for Recipe
- Custom validation for name, prep_time, cook_time

**RecipeIngredientForm:**
- Uses `ingredient_name` CharField (not FK) for user input
- Automatically gets or creates Ingredient in save() method
- Normalizes ingredient names with .capitalize()

**RecipeIngredientFormSet:**
- Inline formset factory: Recipe → RecipeIngredient
- Configured with extra=5, min_num=1, can_delete=True
- Allows managing multiple ingredients in single form submission

### Template Structure

- `base.html` - Base template with HTMX script
- `recipe_list.html` - Main list with search input
- `recipe_detail.html` - Detail view with edit/delete actions
- `recipe_form.html` - Form template (handles both create and edit)
- `includes/recipe_card.html` - Single recipe card component
- `includes/recipe_card_list.html` - HTMX target for search results
- `includes/ingredient_options.html` - HTMX target for autocomplete

### HTMX Integration

Key HTMX patterns used:
- Search triggers on input with debouncing
- DELETE requests with HX-Redirect for recipe deletion
- Partial page updates by swapping HTML fragments
- Forms use JavaScript (formset.js) for dynamic ingredient rows

## Key Technical Details

**Package Manager:** This project uses `uv` (not pip). All commands should be prefixed with `uv run`.

**Database:** SQLite (db.sqlite3). Reset with: delete db.sqlite3, then run migrations.

**Language/Locale:** Finnish (fi-fi), Europe/Helsinki timezone in settings.py

**Static Files:** Served from recipes/static/ with CSS in styles.css and JS in formset.js

**URL Routing:** Project URLs in recipe_project/urls.py include recipes.urls at root path

**Admin:** Django admin configured in recipes/admin.py for all models

## Testing Structure

Tests located in `recipes/tests/`:
- `test_models.py` - Model validation, relationships, properties
- `test_views.py` - View logic and responses
- `test_forms.py` - Form validation and saving
- `test_urls.py` - URL routing
- `test_integration.py` - End-to-end workflows

Coverage reports generated in `htmlcov/` directory.

## Important Constraints

- Minimum 1 ingredient required per recipe (enforced in formset)
- Ingredient names must be unique (database constraint)
- RecipeIngredient has unique_together on (recipe, ingredient)
- Prep time and cook time must be non-negative
- Recipe name cannot be empty or whitespace-only
