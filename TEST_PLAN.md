# Unit Testing Plan - Recipe Application

## Test Framework Options

### Option 1: Django's Built-in unittest (SUOSITELTU)
**Pros:**
- ✅ Tulee Djangon mukana, ei asennuksia
- ✅ Täysi integraatio Djangon kanssa (TestCase, Client, fixtures)
- ✅ Django-spesifiset assertit (assertContains, assertRedirects, jne.)
- ✅ Automaattinen test-tietokannan hallinta
- ✅ Virallinen ja laajasti dokumentoitu

**Cons:**
- ❌ Verbosisempi syntaksi kuin pytest
- ❌ Vähemmän plugineja

**Käyttö:**
```bash
python manage.py test
python manage.py test recipes.tests.test_models
python manage.py test --parallel
```

---

### Option 2: pytest + pytest-django
**Pros:**
- ✅ Modernimpi ja selkeämpi syntaksi
- ✅ Fixtures-systeemi on parempi
- ✅ Parametrisointi helpompaa
- ✅ Paljon plugineja (coverage, xdist, jne.)
- ✅ Paremmat virheilmoitukset

**Cons:**
- ❌ Vaatii asennuksen (pytest, pytest-django)
- ❌ Vähän monimutkaisempi setup

**Käyttö:**
```bash
pytest
pytest recipes/tests/test_models.py
pytest -v --cov=recipes
```

**Asennus:**
```bash
pip install pytest pytest-django pytest-cov
```

---

### Option 3: Django + Coverage.py
**Pros:**
- ✅ Django unittest + kattavuusraportti
- ✅ Yksinkertainen setup
- ✅ HTML-raportit

**Käyttö:**
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

---

## Suositus: Django unittest + Coverage

Aloitetaan Django:n omalla unittest-frameworkilla, koska:
1. Ei tarvitse lisäriippuvuuksia
2. Yksinkertaisin aloituspaikka
3. Voidaan siirtyä pytestiin myöhemmin tarvittaessa

---

## Test Structure

```
recipes/
├── tests/
│   ├── __init__.py
│   ├── test_models.py           # Model-testit
│   ├── test_views.py            # View-testit
│   ├── test_forms.py            # Form-testit
│   ├── test_urls.py             # URL routing -testit
│   └── test_integration.py      # Integraatiotestit
```

---

## Test Coverage Plan

### 1. Model Tests (test_models.py)

#### Recipe Model
- ✅ Reseptin luonti
- ✅ String representation (`__str__`)
- ✅ Absolute URL
- ✅ Total time calculation
- ✅ Ordering (newest first)
- ✅ Field validations (positive integers)
- ✅ Blank fields (description can be blank)
- ✅ Required fields (name, instructions)

#### Ingredient Model
- ✅ Raaka-aineen luonti
- ✅ Unique constraint
- ✅ String representation
- ✅ Ordering (alphabetical)

#### RecipeIngredient Model
- ✅ Liitoksen luonti
- ✅ String representation
- ✅ Cascade delete (recipe poistettaessa)
- ✅ Unique together constraint

**Test count: ~15-20 testiä**

---

### 2. Form Tests (test_forms.py)

#### RecipeForm
- ✅ Valid form with all fields
- ✅ Missing required fields (name, instructions)
- ✅ Invalid prep_time (negative)
- ✅ Invalid cook_time (negative)
- ✅ Empty name validation
- ✅ Form field widgets and labels

#### RecipeIngredientForm
- ✅ Valid ingredient with quantity
- ✅ Missing ingredient name
- ✅ Empty ingredient name
- ✅ Ingredient name capitalization
- ✅ Save creates/finds ingredient

#### RecipeIngredientFormSet
- ✅ Valid formset with multiple ingredients
- ✅ Minimum 1 ingredient required
- ✅ Can delete ingredients
- ✅ Extra forms shown

**Test count: ~12-15 testiä**

---

### 3. View Tests (test_views.py)

#### recipe_list
- ✅ GET returns 200
- ✅ Uses correct template
- ✅ Shows all recipes
- ✅ Empty list shows message
- ✅ Context contains recipes

#### recipe_detail
- ✅ GET returns 200
- ✅ Shows recipe details
- ✅ Shows ingredients
- ✅ 404 for non-existent recipe
- ✅ Context contains recipe

#### recipe_create
- ✅ GET returns 200 (shows form)
- ✅ POST with valid data creates recipe
- ✅ POST with valid data creates ingredients
- ✅ POST redirects to detail page
- ✅ POST with invalid data shows errors
- ✅ Form and formset in context

#### recipe_edit
- ✅ GET returns 200 with prefilled form
- ✅ POST updates recipe
- ✅ POST updates ingredients
- ✅ POST redirects to detail page
- ✅ 404 for non-existent recipe

#### recipe_delete
- ✅ DELETE removes recipe
- ✅ Returns HX-Redirect header
- ✅ Ingredients also deleted (cascade)
- ✅ GET redirects to list
- ✅ 404 for non-existent recipe

#### recipe_search (HTMX)
- ✅ GET with ingredient query filters recipes
- ✅ GET without query returns all
- ✅ Returns correct template fragment
- ✅ Case-insensitive search

**Test count: ~25-30 testiä**

---

### 4. URL Tests (test_urls.py)

- ✅ Root URL resolves to recipe_list
- ✅ Recipe detail URL resolves correctly
- ✅ Recipe create URL resolves correctly
- ✅ Recipe edit URL resolves correctly
- ✅ Recipe delete URL resolves correctly
- ✅ Recipe search URL resolves correctly
- ✅ URL reverse works for all routes

**Test count: ~7-10 testiä**

---

### 5. Integration Tests (test_integration.py)

#### Full CRUD workflow
- ✅ Create recipe → view it → edit it → delete it
- ✅ Create recipe with ingredients
- ✅ Search for recipe by ingredient
- ✅ Edit recipe changes ingredients list

#### HTMX workflows
- ✅ Search updates results
- ✅ Delete sends correct headers

**Test count: ~5-8 testiä**

---

## Total Estimated Tests: 64-83 testiä

---

## Test Data Strategy

### Fixtures (Optional)
Create `recipes/fixtures/test_data.json`:
```bash
python manage.py dumpdata recipes --indent 2 > recipes/fixtures/test_data.json
```

### Factory Pattern (In tests)
```python
def create_recipe(**kwargs):
    defaults = {
        'name': 'Test Recipe',
        'instructions': 'Test instructions',
        'prep_time': 10,
        'cook_time': 20,
        'servings': 4,
    }
    defaults.update(kwargs)
    return Recipe.objects.create(**defaults)
```

---

## Running Tests

### Basic
```bash
python manage.py test                    # All tests
python manage.py test recipes            # Only recipes app
python manage.py test recipes.tests.test_models  # Specific file
python manage.py test recipes.tests.test_models.RecipeModelTest  # Specific class
python manage.py test recipes.tests.test_models.RecipeModelTest.test_create_recipe  # Single test
```

### With options
```bash
python manage.py test --verbosity=2      # More output
python manage.py test --parallel         # Parallel execution
python manage.py test --keepdb           # Keep test database
python manage.py test --failfast         # Stop on first failure
```

### With coverage
```bash
coverage run --source='recipes' manage.py test recipes
coverage report
coverage html  # Creates htmlcov/index.html
```

---

## Test Utilities

### Custom Assertions
```python
class RecipeTestCase(TestCase):
    def assertRecipeEqual(self, recipe1, recipe2):
        self.assertEqual(recipe1.name, recipe2.name)
        self.assertEqual(recipe1.prep_time, recipe2.prep_time)
        # ...
```

### Helper Methods
```python
def create_test_recipe_with_ingredients(self):
    recipe = create_recipe()
    ingredient = Ingredient.objects.create(name='Test Ingredient')
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        quantity='1 cup'
    )
    return recipe
```

---

## CI/CD Integration (Future)

### GitHub Actions example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python manage.py test
```

---

## Test Database

Django automatically creates a test database with `test_` prefix:
- Production: `db.sqlite3`
- Testing: `test_db.sqlite3` (deleted after tests)

To inspect test database:
```bash
python manage.py test --keepdb
sqlite3 test_db.sqlite3
```

---

## Mocking Strategy

### External dependencies
```python
from unittest.mock import patch

@patch('recipes.views.some_external_call')
def test_view_with_mock(self, mock_call):
    mock_call.return_value = 'mocked value'
    # test code
```

### Django Client
```python
from django.test import Client

client = Client()
response = client.get('/recipe/1/')
self.assertEqual(response.status_code, 200)
```

---

## Coverage Goals

- **Models**: 100% (easy to achieve)
- **Forms**: 95%+
- **Views**: 85%+
- **URLs**: 100%
- **Overall**: 90%+

---

## Next Steps

1. ✅ Create test directory structure
2. ✅ Write model tests (start simple)
3. ✅ Write form tests
4. ✅ Write view tests
5. ✅ Write URL tests
6. ✅ Add integration tests
7. ✅ Add coverage reporting
8. ✅ Document test commands in README
9. 🔄 Consider pytest migration if needed

---

## Best Practices

1. **Test naming**: `test_<what>_<condition>_<expected>`
   - `test_create_recipe_without_name_fails`
   - `test_recipe_list_shows_all_recipes`

2. **One assertion per test** (when possible)

3. **Arrange-Act-Assert pattern**:
   ```python
   def test_something(self):
       # Arrange
       recipe = create_recipe()

       # Act
       result = recipe.total_time

       # Assert
       self.assertEqual(result, 30)
   ```

4. **Use setUp for common setup**:
   ```python
   def setUp(self):
       self.recipe = create_recipe()
   ```

5. **Clean test data** (Django does this automatically)

6. **Don't test Django itself** (trust the framework)

7. **Test edge cases**:
   - Empty strings
   - Negative numbers
   - None values
   - Large inputs

---

## Useful Django Test Assertions

- `assertEqual(a, b)`
- `assertTrue(x)` / `assertFalse(x)`
- `assertIn(a, b)`
- `assertRaises(Exception)`
- `assertContains(response, text)` - for HTML
- `assertRedirects(response, url)`
- `assertTemplateUsed(response, template)`
- `assertFormError(response, form, field, errors)`
- `assertQuerysetEqual(qs1, qs2)`

---

**Suositus aloittamiseen: Aloita test_models.py, sitten test_forms.py, sitten test_views.py**
