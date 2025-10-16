import pytest


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
def test_recipe_list_page_loads(page, live_server):
    # Navigate to the recipe list page
    page.goto(live_server.url + "/")

    # Assert main heading is present
    heading = page.get_by_role("heading", name="Kaikki reseptit")
    heading.wait_for()

    # Ensure page has a title (any value)
    assert page.title() is not None
