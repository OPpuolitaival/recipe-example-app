"""
Django management command to generate test data for the recipe application.

Usage:
    python manage.py generate_test_data [--recipes N] [--clear]

Options:
    --recipes N : Number of recipes to generate (default: 10)
    --clear     : Clear existing data before generating new data
"""

from django.core.management.base import BaseCommand
from recipes.models import Recipe, Ingredient, RecipeIngredient
import random


class Command(BaseCommand):
    help = 'Generate test data for the recipe application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipes',
            type=int,
            default=10,
            help='Number of recipes to generate (default: 10)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new data'
        )

    def handle(self, *args, **options):
        num_recipes = options['recipes']
        clear_data = options['clear']

        # Clear existing data if requested
        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            RecipeIngredient.objects.all().delete()
            Recipe.objects.all().delete()
            Ingredient.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Data cleared'))

        self.stdout.write(f'Generating {num_recipes} test recipes...')

        # Create ingredients
        ingredients_data = [
            'Maito', 'Muna', 'Vehnäjauho', 'Sokeri', 'Suola', 'Voi',
            'Kananmuna', 'Sipuli', 'Valkosipuli', 'Tomaatti', 'Peruna',
            'Porkkana', 'Kaali', 'Paprika', 'Kurkku', 'Salaatti',
            'Riisi', 'Pasta', 'Kana', 'Naudanliha', 'Sianliha', 'Kala',
            'Öljy', 'Kerma', 'Juusto', 'Jogurtti', 'Appelsiini', 'Omena',
            'Banaani', 'Mansikka', 'Mustikka', 'Vadelma', 'Sitruuna',
            'Porkkanamehujauhe', 'Vaniljasokeri', 'Leivinjauhe', 'Hunaja',
            'Kaakaojauhe', 'Suklaa', 'Rypsiöljy', 'Oliiviöljy',
        ]

        ingredients = []
        for name in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(name=name)
            ingredients.append(ingredient)

        self.stdout.write(f'✓ Created {len(ingredients)} ingredients')

        # Recipe templates with Finnish recipes
        recipe_templates = [
            {
                'name': 'Pannukakku',
                'description': 'Perinteinen suomalainen uunipannukakku',
                'instructions': '1. Vatkaa munat ja sokeri\n2. Lisää maito ja vehnäjauho\n3. Kaada uunivuokaan\n4. Paista 200°C noin 30 minuuttia',
                'prep_time': 10,
                'cook_time': 30,
                'servings': 4,
                'ingredients': [
                    ('Muna', '3 kpl'),
                    ('Maito', '5 dl'),
                    ('Vehnäjauho', '2 dl'),
                    ('Sokeri', '2 rkl'),
                    ('Suola', '1 tl'),
                ]
            },
            {
                'name': 'Lihapullat',
                'description': 'Mehevät lihapullat perinteiseen tapaan',
                'instructions': '1. Sekoita jauheliha, muna ja korppujauho\n2. Mausta suolalla ja pippurilla\n3. Pyörittele palloja\n4. Paista pannulla ruskean värisiksi',
                'prep_time': 15,
                'cook_time': 20,
                'servings': 4,
                'ingredients': [
                    ('Naudanliha', '400 g'),
                    ('Muna', '1 kpl'),
                    ('Sipuli', '1 kpl'),
                    ('Suola', '1 tl'),
                ]
            },
            {
                'name': 'Kalakeitto',
                'description': 'Kermainen kalakeitto',
                'instructions': '1. Keitä perunat\n2. Lisää kala ja kerma\n3. Mausta suolalla ja tillillä\n4. Keitä kunnes kala on kypsää',
                'prep_time': 15,
                'cook_time': 25,
                'servings': 6,
                'ingredients': [
                    ('Kala', '500 g'),
                    ('Peruna', '6 kpl'),
                    ('Kerma', '2 dl'),
                    ('Sipuli', '1 kpl'),
                    ('Suola', '2 tl'),
                ]
            },
            {
                'name': 'Kaalilaatikko',
                'description': 'Suomalainen perinneruoka',
                'instructions': '1. Hauduta kaali\n2. Sekoita jauheliha, riisi ja kaali\n3. Kaada vuokaan\n4. Paista uunissa 175°C noin 1 tunti',
                'prep_time': 20,
                'cook_time': 60,
                'servings': 6,
                'ingredients': [
                    ('Kaali', '1 kg'),
                    ('Naudanliha', '400 g'),
                    ('Riisi', '2 dl'),
                    ('Sipuli', '1 kpl'),
                    ('Suola', '2 tl'),
                ]
            },
            {
                'name': 'Lohikeitto',
                'description': 'Kermainen lohikeitto',
                'instructions': '1. Keitä perunat ja porkkana\n2. Lisää lohi\n3. Kaada kerma ja mausta\n4. Anna kiehua hetki',
                'prep_time': 10,
                'cook_time': 20,
                'servings': 4,
                'ingredients': [
                    ('Kala', '300 g'),
                    ('Peruna', '4 kpl'),
                    ('Porkkana', '2 kpl'),
                    ('Kerma', '2 dl'),
                    ('Suola', '1 tl'),
                ]
            },
            {
                'name': 'Makaroonilaatikko',
                'description': 'Helppo arkiruoka',
                'instructions': '1. Keitä makaronit\n2. Sekoita jauheliha, makaronit ja maito\n3. Kaada vuokaan\n4. Paista 200°C noin 30 minuuttia',
                'prep_time': 15,
                'cook_time': 30,
                'servings': 6,
                'ingredients': [
                    ('Pasta', '400 g'),
                    ('Naudanliha', '500 g'),
                    ('Maito', '3 dl'),
                    ('Muna', '2 kpl'),
                    ('Suola', '1 tl'),
                ]
            },
            {
                'name': 'Hernekeitto',
                'description': 'Perinteinen hernekeitto',
                'instructions': '1. Liota herneet yön yli\n2. Keitä herneet ja liha vedessä\n3. Lisää sipuli ja mausteet\n4. Keitä kunnes pehmeää',
                'prep_time': 10,
                'cook_time': 120,
                'servings': 6,
                'ingredients': [
                    ('Sianliha', '400 g'),
                    ('Sipuli', '2 kpl'),
                    ('Suola', '2 tl'),
                ]
            },
            {
                'name': 'Mustikkapiirakka',
                'description': 'Kesäinen mustikkapiirakka',
                'instructions': '1. Vatkaa taikina\n2. Kaada vuokaan\n3. Lisää mustikat\n4. Paista 200°C noin 40 minuuttia',
                'prep_time': 15,
                'cook_time': 40,
                'servings': 8,
                'ingredients': [
                    ('Mustikka', '3 dl'),
                    ('Vehnäjauho', '3 dl'),
                    ('Sokeri', '2 dl'),
                    ('Muna', '2 kpl'),
                    ('Maito', '2 dl'),
                ]
            },
            {
                'name': 'Lihapyörykät',
                'description': 'Pieniä lihapullia kastikkeessa',
                'instructions': '1. Valmista lihapullat\n2. Paista pannulla\n3. Tee kermainen kastike\n4. Hauduta yhdessä',
                'prep_time': 20,
                'cook_time': 25,
                'servings': 4,
                'ingredients': [
                    ('Naudanliha', '500 g'),
                    ('Sipuli', '1 kpl'),
                    ('Muna', '1 kpl'),
                    ('Kerma', '2 dl'),
                    ('Suola', '1 tl'),
                ]
            },
            {
                'name': 'Perunasalaatti',
                'description': 'Raikas kesäsalaatti',
                'instructions': '1. Keitä perunat\n2. Pilko vihannekset\n3. Sekoita kastike\n4. Yhdistä ainekset',
                'prep_time': 15,
                'cook_time': 20,
                'servings': 6,
                'ingredients': [
                    ('Peruna', '8 kpl'),
                    ('Kurkku', '1 kpl'),
                    ('Tomaatti', '2 kpl'),
                    ('Sipuli', '1 kpl'),
                    ('Kerma', '1 dl'),
                ]
            },
        ]

        # Generate recipes
        created_count = 0
        for i in range(num_recipes):
            # Pick a random template
            template = random.choice(recipe_templates)

            # Add some variation to the name
            suffix = ['', ' (Mummin resepti)', ' (Helppo versio)', ' (Perinteinen)', ' (Nopea)']
            name = template['name'] + random.choice(suffix)

            # Create recipe
            recipe = Recipe.objects.create(
                name=name,
                description=template['description'],
                instructions=template['instructions'],
                prep_time=template['prep_time'] + random.randint(-5, 5),
                cook_time=template['cook_time'] + random.randint(-10, 10),
                servings=template['servings'] + random.randint(-2, 2),
            )

            # Add ingredients to recipe
            for ing_name, quantity in template['ingredients']:
                try:
                    ingredient = Ingredient.objects.get(name=ing_name)
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=quantity
                    )
                except Ingredient.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Ingredient not found: {ing_name}')
                    )

            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully generated {created_count} recipes with ingredients!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Total recipes in database: {Recipe.objects.count()}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Total ingredients in database: {Ingredient.objects.count()}'
            )
        )
