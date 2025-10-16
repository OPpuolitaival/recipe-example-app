# Reseptisovellus

Yksinkertainen reseptien hallintasovellus, joka on rakennettu Django-frameworkilla ja HTMX:llä. Sovellus on suunniteltu opetustarkoituksiin ja testiautomaation harjoitteluun.

## Ominaisuudet

- ✅ Reseptien lisääminen, muokkaaminen ja poistaminen
- ✅ Raaka-aineiden hallinta formsetin avulla
- ✅ Haku raaka-aineiden mukaan (HTMX)
- ✅ Dynaaminen käyttöliittymä ilman sivun päivitystä (HTMX)
- ✅ Responsiivinen design
- ✅ Django Admin -paneeli hallintaan
- ✅ Hyvin kommentoitu koodi

## Teknologiat

### Backend
- **Django 5.0+** - Web-framework
- **SQLite** - Tietokanta (Django default)
- **Python 3.8+** - Ohjelmointikieli

### Frontend
- **HTMX 1.9.10** - Dynaaminen sisällön päivitys
- **Vanilla CSS** - Tyylitys
- **Vanilla JavaScript** - Formset-hallinta

## Projektin rakenne

```
recipe_project/
├── manage.py                    # Django management-skripti
├── requirements.txt             # Python-riippuvuudet
├── .gitignore
├── README.md
│
├── recipe_project/              # Projektin asetukset
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── recipes/                     # Reseptien hallinta-app
    ├── models.py                # Recipe, Ingredient, RecipeIngredient
    ├── views.py                 # View-funktiot
    ├── urls.py                  # URL-reitit
    ├── forms.py                 # Django Forms ja Formsets
    ├── admin.py                 # Admin-konfiguraatio
    │
    ├── templates/
    │   ├── base.html
    │   ├── recipe_list.html
    │   ├── recipe_detail.html
    │   ├── recipe_form.html
    │   └── includes/
    │       ├── recipe_card.html
    │       ├── recipe_card_list.html
    │       └── ingredient_options.html
    │
    ├── static/
    │   ├── css/
    │   │   └── styles.css
    │   └── js/
    │       └── formset.js
    │
    └── migrations/
```

## Asennus ja käyttöönotto

### Pikaohjeet (uv)

**Suositeltu tapa - käytä uv-paketinhallintaa:**

1. **Asenna uv** (jos ei ole vielä asennettu):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Käynnistä sovellus**:
```bash
./run.sh
```

Tämä skripti:
- Asentaa riippuvuudet automaattisesti
- Ajaa migraatiot
- Pyytää luomaan superuser-käyttäjän (ensimmäisellä kerralla, jos interaktiivinen terminaali)
- Käynnistää kehityspalvelimen

**Luo superuser manuaalisesti** (jos skripti ei kysynyt):
```bash
uv run python manage.py createsuperuser
```

Tai aseta ympäristömuuttujat ja aja skripti uudelleen:
```bash
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_PASSWORD=admin123
export DJANGO_SUPERUSER_EMAIL=admin@example.com
./run.sh
```

Sovellus pyörii osoitteessa: **http://localhost:8000**

Admin-paneeli: **http://localhost:8000/admin/**

---

### Perinteinen asennus (pip)

Jos et halua käyttää uv:tä:

#### 1. Kloonaa repositorio

```bash
git clone <repository-url>
cd esimerkki1
```

#### 2. Luo virtuaaliympäristö

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Asenna riippuvuudet

```bash
pip install -r requirements.txt
```

#### 4. Aja migraatiot

```bash
python manage.py migrate
```

#### 5. Luo superuser (admin-käyttäjä)

```bash
python manage.py createsuperuser
```

Seuraa ohjeita ja luo käyttäjätunnus ja salasana.

#### 6. Käynnistä kehityspalvelin

```bash
python manage.py runserver
```

Sovellus pyörii nyt osoitteessa: **http://localhost:8000**

Admin-paneeli: **http://localhost:8000/admin/**

## Käyttöohje

### Reseptien selaaminen
1. Avaa etusivu (http://localhost:8000)
2. Näet kaikki reseptit korttinäkymässä
3. Klikkaa reseptiä nähdäksesi yksityiskohdat

### Uuden reseptin luominen
1. Klikkaa "Uusi resepti" -linkkiä navigaatiossa
2. Täytä lomake:
   - Reseptin nimi (pakollinen)
   - Kuvaus
   - Valmistusaika ja kypsennysaika minuutteina
   - Annosten määrä
   - Raaka-aineet (vähintään 1)
   - Valmistusohjeet
3. Lisää raaka-aineita klikkaamalla "+ Lisää raaka-aine" -painiketta
4. Tallenna resepti

### Reseptin muokkaaminen
1. Avaa reseptin yksityiskohdat
2. Klikkaa "Muokkaa" -painiketta
3. Tee muutokset
4. Tallenna

### Reseptin poistaminen
1. Avaa reseptin yksityiskohdat
2. Klikkaa "Poista" -painiketta
3. Vahvista poisto dialogista

### Haku raaka-aineiden mukaan
1. Etusivulla kirjoita raaka-aineen nimi hakukenttään
2. Lista päivittyy automaattisesti (HTMX)
3. Tyhjennä hakukenttä nähdäksesi kaikki reseptit

## Admin-paneeli

Django Admin -paneelissa voit:
- Hallita reseptejä, raaka-aineita ja liitoksia
- Lisätä/muokata/poistaa tietueita
- Käyttää hakutoimintoja
- Suodattaa tuloksia

Kirjaudu sisään: http://localhost:8000/admin/

## Tietokantamallit

### Recipe
- `name` - Reseptin nimi
- `description` - Kuvaus
- `instructions` - Valmistusohjeet
- `prep_time` - Valmistusaika (min)
- `cook_time` - Kypsennysaika (min)
- `servings` - Annosmäärä
- `created_at` - Luontiaika
- `updated_at` - Päivitysaika

### Ingredient
- `name` - Raaka-aineen nimi (uniikki)

### RecipeIngredient
- `recipe` - Viittaus reseptiin (FK)
- `ingredient` - Viittaus raaka-aineeseen (FK)
- `quantity` - Määrä (esim. "2 dl", "500 g")

## URL-reitit

| URL | View | Kuvaus |
|-----|------|--------|
| `/` | recipe_list | Kaikki reseptit |
| `/recipe/<id>/` | recipe_detail | Reseptin yksityiskohdat |
| `/recipe/new/` | recipe_create | Luo uusi resepti |
| `/recipe/<id>/edit/` | recipe_edit | Muokkaa reseptiä |
| `/recipe/<id>/delete/` | recipe_delete | Poista resepti (HTMX) |
| `/recipes/search/` | recipe_search | Haku raaka-aineella (HTMX) |
| `/admin/` | Django Admin | Hallintapaneeli |

## Testaus

Tämä sovellus on suunniteltu yksinkertaiseksi testauksen harjoittelua varten.

### Manuaalinen testaus

1. **Reseptin CRUD-toiminnot**:
   - Luo resepti ✓
   - Lue resepti ✓
   - Päivitä resepti ✓
   - Poista resepti ✓

2. **Hakutoiminto**:
   - Hae olemassa olevalla raaka-aineella ✓
   - Hae olemattomalla raaka-aineella ✓
   - Tyhjennä haku ✓

3. **Validointi**:
   - Yritä luoda resepti ilman nimeä ✓
   - Yritä luoda resepti ilman raaka-aineita ✓

### Automaattinen testaus

Voit lisätä Django-testejä `recipes/tests.py` -tiedostoon:

```bash
python manage.py test
```

## Kehitysideoita

Sovellusta voi laajentaa seuraavilla ominaisuuksilla:

- [ ] Käyttäjäautentikointi ja -hallinta
- [ ] Reseptien kuvat
- [ ] Kategoriat ja tagit
- [ ] Suosikkireseptit
- [ ] Arvostelut ja kommentit
- [ ] Reseptien jakaminen
- [ ] Ostoslista-toiminto
- [ ] Tulostettava versio
- [ ] REST API
- [ ] Yksikkötestit

## Vianmääritys

### Tietokantavirhe
```bash
python manage.py migrate
```

### Static files eivät lataudu
```bash
python manage.py collectstatic
```

### Port on jo käytössä
```bash
# Käytä eri porttia
python manage.py runserver 8001
```

## Lisenssi

Tämä on opetusprojekti. Vapaasti käytettävissä ja muokattavissa.

## Tekijä

Luotu Django 5.0 + HTMX -harjoitusprojektina.

## Linkit

- [Django Documentation](https://docs.djangoproject.com/)
- [HTMX Documentation](https://htmx.org/docs/)
- [SUUNNITELMA.md](SUUNNITELMA.md) - Yksityiskohtainen projektisuunnitelma
