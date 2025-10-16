import time
import pytest


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_create_recipe_and_search(page, live_server):
    # Go to home page
    page.goto(live_server.url + "/")

    # Navigate to create page via header nav
    page.get_by_role("link", name="Uusi resepti").click()

    # Use a unique recipe name to avoid collisions
    unique_suffix = str(int(time.time()))
    recipe_name = f"Testi Resepti {unique_suffix}"
    ingredient_name = f"TestiAines {unique_suffix}"

    # Fill basic fields by labels (Finnish labels from forms)
    page.get_by_label("Reseptin nimi").fill(recipe_name)
    page.get_by_label("Kuvaus").fill("Lyhyt kuvaus testiä varten")

    # Optional numeric fields (keep small integers to satisfy potential validators)
    page.get_by_label("Valmistusaika (min)").fill("5")
    page.get_by_label("Kypsennysaika (min)").fill("10")
    page.get_by_label("Annokset").fill("2")

    # Fill first ingredient row (formset shows several empty rows; get_by_label picks the first)
    page.get_by_label("Raaka-aine").first.fill(ingredient_name)
    page.get_by_label("Määrä").first.fill("1 kpl")

    # Instructions
    page.get_by_label("Valmistusohjeet").fill("Sekoita ainekset ja nauti.")

    # Submit the form
    page.get_by_role("button", name="Luo resepti").click()

    # Verify we were redirected to detail page that shows the recipe name as heading
    page.get_by_role("heading", name=recipe_name).wait_for()

    # Go back to list
    page.get_by_role("link", name="Takaisin listaan").click()

    # On the list page, use the ingredient search bar (HTMX updates the list)
    search_input = page.locator("#ingredient-search")
    search_input.fill(ingredient_name)

    # Wait for the recipe to appear in the filtered list. The cards include the recipe name.
    page.get_by_text(recipe_name, exact=False).first.wait_for()

    # As an extra assertion, ensure at least one card with the name exists
    matches = page.get_by_text(recipe_name)
    assert matches.count() >= 1
