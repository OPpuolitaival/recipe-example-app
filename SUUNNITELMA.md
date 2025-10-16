# Reseptin hallintasovellus - Projektisuunnitelma

## 1. Arkkitehtuurin kuvaus

### Backend
- **Framework**: Django 5.0+
- **Tietokanta**: SQLite3 (Django default, kevyt)
- **ORM**: Django ORM (sisäänrakennettu)
- **Templating**: Django Templates
- **Validointi**: Django Forms ja Model validation
- **Static files**: Django static files handling

### Frontend
- **Approach**: Server-side rendering + HTMX
- **HTMX**: Dynaaminen sisällön päivitys ilman JavaScriptiä
- **Styling**: Vanilla CSS (yksinkertainen)
- **No build step**: Ei tarvetta npm:lle tai bundlerille

### Kommunikaatio
- **HTML-over-the-wire** paradigma
- HTMX tekee AJAX-pyynnöt, Django palauttaa HTML-fragmentteja
- Backend portti: 8000 (Django default)
- Kaikki toimii samassa sovelluksessa (ei erillistä frontendia)

---

## 2. Tietokantakaavio ja Django Models

### Django Models (models.py)

```python
from django.db import models

class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField()
    prep_time = models.PositiveIntegerField(help_text="Minuutteina")
    cook_time = models.PositiveIntegerField(help_text="Minuutteina")
    servings = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50, help_text="esim. '2 dl', '500 g'")

    def __str__(self):
        return f"{self.quantity} {self.ingredient.name}"

    class Meta:
        unique_together = ['recipe', 'ingredient']
```

### Tietokanta (automaattisesti Django ORM:n kautta)
Django luo automaattisesti taulut migraatioiden avulla:
- `recipes_recipe`
- `recipes_ingredient`
- `recipes_recipeingredient`

### Tietokantakaavio (tekstimuodossa)

```
┌─────────────────────┐
│     recipes         │
├─────────────────────┤
│ id (PK)             │
│ name                │
│ description         │
│ instructions        │
│ prep_time           │
│ cook_time           │
│ servings            │
│ created_at          │
│ updated_at          │
└──────────┬──────────┘
           │
           │ 1:N
           │
┌──────────▼──────────────┐
│ recipe_ingredients      │
├─────────────────────────┤
│ id (PK)                 │
│ recipe_id (FK)          │
│ ingredient_id (FK)      │
│ quantity                │
└──────────┬──────────────┘
           │
           │ N:1
           │
┌──────────▼──────────┐
│    ingredients      │
├─────────────────────┤
│ id (PK)             │
│ name (UNIQUE)       │
└─────────────────────┘
```

---

## 3. URL-reitit ja Views (Django + HTMX)

### URL-reitit (urls.py)

```python
from django.urls import path
from . import views

urlpatterns = [
    # Päänäkymät
    path('', views.recipe_list, name='recipe_list'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/new/', views.recipe_create, name='recipe_create'),
    path('recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),

    # HTMX-endpointit (palauttavat HTML-fragmentteja)
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('recipes/search/', views.recipe_search, name='recipe_search'),
    path('ingredients/autocomplete/', views.ingredient_autocomplete, name='ingredient_autocomplete'),
]
```

### Views ja niiden vastuut

#### recipe_list(request)
- **URL**: `/`
- **Template**: `recipe_list.html`
- **Kuvaus**: Näyttää kaikki reseptit
- **HTMX**: Tukee hakua (`hx-get="/recipes/search/"`)

#### recipe_detail(request, pk)
- **URL**: `/recipe/<id>/`
- **Template**: `recipe_detail.html`
- **Kuvaus**: Näyttää yksittäisen reseptin täydelliset tiedot

#### recipe_create(request)
- **URL**: `/recipe/new/`
- **Template**: `recipe_form.html`
- **Kuvaus**: Lomake uuden reseptin luomiseen
- **POST**: Tallentaa reseptin ja ohjaa detaljisivulle

#### recipe_edit(request, pk)
- **URL**: `/recipe/<id>/edit/`
- **Template**: `recipe_form.html`
- **Kuvaus**: Lomake reseptin muokkaamiseen
- **POST**: Päivittää reseptin

#### recipe_delete(request, pk)
- **URL**: `/recipe/<id>/delete/`
- **Method**: DELETE (HTMX)
- **Response**: HTTP 200 + HX-Redirect header
- **Kuvaus**: Poistaa reseptin ja ohjaa listaan

#### recipe_search(request)
- **URL**: `/recipes/search/?ingredient=<nimi>`
- **Response**: HTML-fragmentti (reseptikorttilista)
- **HTMX**: Päivittää reseptilistan dynaamisesti
- **Kuvaus**: Hakee reseptit raaka-aineen mukaan

#### ingredient_autocomplete(request)
- **URL**: `/ingredients/autocomplete/?q=<haku>`
- **Response**: HTML `<option>` lista
- **HTMX**: Autocomplete-toiminto
- **Kuvaus**: Palauttaa raaka-aineehdotukset

---

## 4. Django Templates ja HTMX-integraatio

### Template-hierarkia

```
base.html (pohja kaikille sivuille)
├── recipe_list.html
│   ├── includes/recipe_card.html (partial)
│   └── includes/search_bar.html (partial)
├── recipe_detail.html
│   └── includes/ingredient_list.html (partial)
└── recipe_form.html
    └── includes/ingredient_formset.html (partial)
```

### Templatejen vastuut

#### base.html
- Perus HTML-rakenne
- Header ja navigaatio
- HTMX-skriptin lataus (`<script src="https://unpkg.com/htmx.org@1.9.10"></script>`)
- Globaalit tyylit
- {% block content %} sisällölle

#### recipe_list.html
- Listaa kaikki reseptit
- Sisältää hakukentän HTMX-attribuuteilla
- HTMX: `hx-get="/recipes/search/" hx-trigger="keyup changed delay:500ms" hx-target="#recipe-list"`
- Renderöi recipe_card.html -partiaaleja

#### includes/recipe_card.html
- Yksittäisen reseptin kortti
- Näyttää nimen, kuvauksen, ajat
- Linkki detaljisivulle

#### includes/search_bar.html
- Hakukenttä raaka-aineille
- HTMX-attribuutit dynaamiseen hakuun
- Tyhjennä-painike

#### recipe_detail.html
- Näyttää reseptin täydelliset tiedot
- Sisältää ingredient_list.html -partiaalin
- Muokkaa/Poista -painikkeet
- HTMX DELETE-painike: `hx-delete="/recipe/{{ recipe.id }}/delete/" hx-confirm="Haluatko varmasti poistaa?"`

#### includes/ingredient_list.html
- Taulukko raaka-aineista
- Määrä + nimi per rivi

#### recipe_form.html
- Django Form reseptin lisäämiseen/muokkaamiseen
- Django Formset raaka-aineille (inline formset)
- JavaScript lisää/poistaa raaka-ainerivejä dynaamisesti
- CSRF-token mukana

#### includes/ingredient_formset.html
- Yksittäinen raaka-ainerivi formsetissä
- Raaka-aineen nimi + määrä
- "Poista"-painike

### HTMX-ominaisuudet käytössä

- **hx-get**: Haku ilman sivun päivitystä
- **hx-post**: Lomakkeen lähetys
- **hx-delete**: Reseptin poisto
- **hx-target**: Mihin vastaus renderöidään
- **hx-swap**: Miten sisältö vaihdetaan (innerHTML, outerHTML)
- **hx-trigger**: Milloin pyyntö lähetetään
- **hx-confirm**: Vahvistusdialogi

---

## 5. Tiedostorakenne

```
recipe_project/                      # Django projektin juurikansio
├── manage.py                        # Django management-skripti
├── requirements.txt                 # Python-riippuvuudet
├── .gitignore
│
├── recipe_project/                  # Projektin asetuskansio
│   ├── __init__.py
│   ├── settings.py                  # Django asetukset
│   ├── urls.py                      # Pääprojektin URL-konfiguraatio
│   └── wsgi.py                      # WSGI-konfiguraatio
│
├── recipes/                         # Django app resepteille
│   ├── __init__.py
│   ├── admin.py                     # Admin-paneelin konfiguraatio
│   ├── apps.py                      # App-konfiguraatio
│   ├── models.py                    # Tietokantamallit (Recipe, Ingredient, RecipeIngredient)
│   ├── views.py                     # View-funktiot
│   ├── urls.py                      # App-tason URL-reitit
│   ├── forms.py                     # Django Forms ja Formsets
│   │
│   ├── templates/
│   │   ├── base.html                # Pohjatemplate
│   │   ├── recipe_list.html         # Reseptilista
│   │   ├── recipe_detail.html       # Reseptin yksityiskohdat
│   │   ├── recipe_form.html         # Reseptin luominen/muokkaus
│   │   └── includes/
│   │       ├── recipe_card.html     # Reseptikortti (partial)
│   │       ├── search_bar.html      # Hakupalkki (partial)
│   │       ├── ingredient_list.html # Raaka-ainelista (partial)
│   │       └── ingredient_formset.html  # Formset-rivi (partial)
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css           # Sovelluksen tyylit
│   │   └── js/
│   │       └── formset.js           # Formset dynaaminen lisäys/poisto
│   │
│   └── migrations/                  # Tietokantamigraatiot
│       └── __init__.py
│
└── db.sqlite3                       # SQLite-tietokanta (luodaan automaattisesti)
```

---

## 6. Pääominaisuudet (MVP)

### 6.1 Reseptin lisääminen
- **View**: `recipe_create`
- **Template**: `recipe_form.html`
- **Workflow**:
  1. Käyttäjä navigoi `/recipe/new/`
  2. Täyttää Django Formin (nimi, kuvaus, ohjeet, ajat, annokset)
  3. Lisää raaka-aineet formsetin avulla (JavaScript lisää rivejä)
  4. POST-pyynnöllä data lähetetään
  5. View validoi ja tallentaa (Recipe + RecipeIngredients)
  6. Redirect reseptin detaljisivulle

### 6.2 Reseptin hakeminen/selaaminen
- **View**: `recipe_list`
- **Template**: `recipe_list.html`
- **Workflow**:
  1. Käyttäjä avaa etusivun `/`
  2. Django renderöi kaikki reseptit (Recipe.objects.all())
  3. Reseptit näytetään recipe_card.html -partiaalilla
  4. Klikkaamalla korttia navigoidaan `/recipe/<id>/`
  5. `recipe_detail` view renderöi täydelliset tiedot

### 6.3 Reseptin poistaminen
- **View**: `recipe_delete`
- **HTMX**: DELETE-pyyntö
- **Workflow**:
  1. recipe_detail.html:ssä "Poista"-painike
  2. HTMX: `hx-delete="/recipe/{{ recipe.id }}/delete/" hx-confirm="Varmista"`
  3. View poistaa Recipe-objektin (cascade poistaa RecipeIngredients)
  4. Palauttaa HTTP 200 + HX-Redirect header etusivulle
  5. HTMX ohjaa käyttäjän automaattisesti

### 6.4 Reseptin muokkaaminen
- **View**: `recipe_edit`
- **Template**: `recipe_form.html`
- **Workflow**:
  1. "Muokkaa"-linkki recipe_detail.html:ssä
  2. Navigoi `/recipe/<id>/edit/`
  3. Django Form esiladataan olemassa olevalla datalla
  4. Formset näyttää nykyiset raaka-aineet
  5. POST-pyynnöllä tallennetaan muutokset
  6. Redirect takaisin detaljisivulle

### 6.5 Haku raaka-aineiden mukaan
- **View**: `recipe_search`
- **Template**: `includes/recipe_card.html` (fragmentti)
- **HTMX**: Dynaaminen haku
- **Workflow**:
  1. Hakukenttä recipe_list.html:ssä
  2. HTMX: `hx-get="/recipes/search/" hx-trigger="keyup changed delay:500ms"`
  3. Query param: `?ingredient=maito`
  4. View hakee: `Recipe.objects.filter(recipe_ingredients__ingredient__name__icontains=query)`
  5. Renderöi recipe_card-fragmentteja
  6. HTMX vaihtaa #recipe-list sisällön (ei sivun reloadausta)

---

## 7. Lisätiedot ja teknisiä huomioita

### Django Backend
- **Error handling**: Django middleware käsittelee virheet automaattisesti
- **Validation**: Django Forms ja Model validation (built-in)
- **CSRF-protection**: Django CSRF-token kaikissa lomakkeissa
- **Admin panel**: Django Admin valmis käyttöön (`/admin/`)
- **Migrations**: `python manage.py makemigrations` ja `migrate`

### HTMX Frontend
- **No build step**: HTMX ladataan CDN:stä, ei npm:ää tarvita
- **Progressive enhancement**: Toimii ilman JavaScriptia (perus HTML forms)
- **Loading indicators**: HTMX lisää automaattisesti `htmx-request` -luokan
- **Error handling**: Django palauttaa virheviestit HTML:nä, HTMX renderöi ne
- **Responsive**: Vanilla CSS, toimii mobiilissa ja työpöydällä

### Tietoturva (perus)
- **SQL Injection**: Django ORM parametrisoi kyselyt automaattisesti
- **XSS**: Django template engine escapettaa automaattisesti
- **CSRF**: Django CSRF-middleware + token lomakkeissa
- **Input validation**: Django Forms validoi kaikki syötteet

---

## 8. Asennusohjeet (lyhyt)

### Asennus ja käynnistys

```bash
# Kloonaa repositorio tai luo uusi kansio
cd recipe_project

# Luo virtuaaliympäristö
python -m venv venv
source venv/bin/activate  # macOS/Linux
# tai
venv\Scripts\activate     # Windows

# Asenna riippuvuudet
pip install -r requirements.txt

# Luo tietokanta ja aja migraatiot
python manage.py migrate

# Luo superuser (admin-käyttäjä)
python manage.py createsuperuser

# Käynnistä dev server
python manage.py runserver
```

Sovellus pyörii osoitteessa: http://localhost:8000
Admin-paneeli: http://localhost:8000/admin/

### requirements.txt

```
Django>=5.0,<5.1
```

HTMX ladataan CDN:stä, joten ei tarvitse asentaa erikseen.

---

## 9. Kehityspolku

Suositeltu toteutusjärjestys:

1. **Django-projektin alustus**:
   - Luo projekti: `django-admin startproject recipe_project`
   - Luo app: `python manage.py startapp recipes`
   - Konfiguroi settings.py

2. **Models ja migraatiot**:
   - Kirjoita Recipe, Ingredient, RecipeIngredient -modelit
   - `python manage.py makemigrations`
   - `python manage.py migrate`

3. **Admin-paneeli**:
   - Rekisteröi modelit admin.py:ssä
   - Testaa tietokannan toimivuus adminissa

4. **Base template ja static files**:
   - Luo base.html (header, navigation, HTMX-skripti)
   - Luo styles.css perustyylitykset

5. **Recipe list ja detail**:
   - recipe_list view ja template
   - recipe_card.html partial
   - recipe_detail view ja template
   - URL-reitit

6. **Recipe create ja edit**:
   - Django Forms (RecipeForm)
   - Django Formset (RecipeIngredientFormSet)
   - recipe_form.html
   - JavaScript formsetin dynaamiseen lisäykseen
   - Create ja edit viewit

7. **Recipe delete (HTMX)**:
   - recipe_delete view
   - HTMX DELETE-painike recipe_detail.html:ssä
   - HX-Redirect header

8. **Search-toiminto (HTMX)**:
   - recipe_search view
   - search_bar.html partial HTMX-attribuuteilla
   - Dynaaminen suodatus

9. **Styling ja viilaus**:
   - CSS-tyylitykset
   - Responsiivisuus
   - Loading-indikaattorit (HTMX)

10. **Dokumentaatio**:
    - README.md
    - Koodikommentit

---

## 10. HTMX + Django -esimerkkejä

### Esimerkki 1: Dynaaminen haku

**Template (recipe_list.html)**:
```html
<input type="text"
       name="ingredient"
       hx-get="{% url 'recipe_search' %}"
       hx-trigger="keyup changed delay:500ms"
       hx-target="#recipe-list"
       placeholder="Hae raaka-aineella...">

<div id="recipe-list">
  {% for recipe in recipes %}
    {% include 'includes/recipe_card.html' %}
  {% endfor %}
</div>
```

**View (views.py)**:
```python
def recipe_search(request):
    query = request.GET.get('ingredient', '')
    if query:
        recipes = Recipe.objects.filter(
            recipe_ingredients__ingredient__name__icontains=query
        ).distinct()
    else:
        recipes = Recipe.objects.all()
    return render(request, 'includes/recipe_cards_list.html', {'recipes': recipes})
```

### Esimerkki 2: Delete-toiminto

**Template (recipe_detail.html)**:
```html
<button hx-delete="{% url 'recipe_delete' recipe.id %}"
        hx-confirm="Haluatko varmasti poistaa tämän reseptin?"
        class="btn-delete">
  Poista resepti
</button>
```

**View (views.py)**:
```python
from django.http import HttpResponse

def recipe_delete(request, pk):
    if request.method == 'DELETE':
        recipe = get_object_or_404(Recipe, pk=pk)
        recipe.delete()
        response = HttpResponse(status=200)
        response['HX-Redirect'] = '/'
        return response
```

---

**Valmis suunnitelma!** Django + HTMX -ratkaisu on yksinkertainen, moderni ja sopii erinomaisesti testauksen harjoitteluun. Ei tarvitse erillistä frontendia tai build-prosessia.
