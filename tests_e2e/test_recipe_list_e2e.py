import pytest


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_recipe_list_page_loads(page, live_server):
    # Navigate to the recipe list page
    await page.goto(live_server.url + "/")

    # Assert main heading is present
    heading = page.get_by_role("heading", name="Kaikki reseptit")
    await heading.wait_for()

    # Ensure page has a title (any value)
    assert await page.title() is not None
