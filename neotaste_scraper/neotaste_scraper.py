"""
This tool allows you to scrape restaurant deal information from
NeoTaste's city-specific restaurant pages.
You can filter and retrieve restaurant deals, including
”event-deals“ (marked with 🌟), and export the data to
different formats: text, JSON, or HTML.
"""

import requests
from bs4 import BeautifulSoup

# Constants
BASE_URL = "https://neotaste.com"

def get_city_url(city_slug, lang="de"):
    """Construct full URL for the given city with the specified language."""
    return f"{BASE_URL}/{lang}/restaurants/{city_slug}"

def extract_deals_from_card(card, filter_mode=None):
    """Extract deals from a single restaurant card.

    filter_mode may be one of: None (no filter), 'events' (only 🌟),
    'flash' (only flash deals), 'special' (events OR flash). For
    backward-compatibility a boolean True is interpreted as 'events'.
    """
    link = card.get("href")
    if not link.startswith("http"):
        link = BASE_URL + link

    # Restaurant name
    name_el = card.select_one("h4")
    if not name_el:
        return None  # Return None if no name is found
    name = name_el.get_text(strip=True)

    # Deal container
    deals_container = card.select_one('[data-sentry-component="RestaurantCardDeals"]')
    if not deals_container:
        return None  # Return None if no deals container is found

    # Extract deal elements generically: match any preview whose component name ends with "DealPreview"
    deal_elements = deals_container.select('[data-sentry-component$="DealPreview"]')

    deals = []
    for el in deal_elements:
        text = el.get_text(strip=True)
        if not text:
            continue
        component = el.get('data-sentry-component', '')
        # small heuristic for flash detection: component name or inner html may indicate flash
        inner_html = str(el).lower()
        is_flash = ('flashdeal' in component) or ('flashdeal' in inner_html) or ('bolt' in inner_html) or ('⚡' in text)
        deals.append({"text": text, "component": component, "is_flash": is_flash})

    # Normalize filter_mode for backwards compatibility
    if filter_mode is True:
        filter_mode = 'events'

    if filter_mode == 'events':
        # Keep only event deals marked with the star
        deals = [d for d in deals if ("🌟" in d['text'])]
    elif filter_mode == 'flash':
        deals = [d for d in deals if d.get('is_flash')]
    elif filter_mode == 'special':
        deals = [d for d in deals if ("🌟" in d['text']) or d.get('is_flash')]

    # Convert to plain list of strings for output
    deals = [d['text'] for d in deals]

    if not deals:
        return None  # Return None if no deals match the filter

    return {"restaurant": name, "deals": deals, "link": link}

def fetch_deals_from_city(city_slug: str, filter_mode=None, lang="de"):
    """Scrape deals from a specific city and optionally filter deals.

    filter_mode may be None, True/False (legacy), or one of 'events','flash','special'.
    """
    url = get_city_url(city_slug, lang)
    try:
        html = requests.get(url, timeout=10).text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Each restaurant card is an <a> with a restaurant link
    cards = soup.select("a[href*='/restaurants/']")

    for card in cards:
        result = extract_deals_from_card(card, filter_mode)
        if result:
            results.append(result)

    return results


def fetch_all_cities(lang="de"):
    """Scrape the main cities page to get a list of all cities."""
    url = f"{BASE_URL}/{lang}/restaurants"
    try:
        html = requests.get(url, timeout=10).text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    city_links = soup.select('[data-sentry-component="CitiesList"] a')

    cities = []
    for link in city_links:
        # This class should contain the city name
        city_name = link.select_one(".font-semibold")

        # Ensure the city name is extracted correctly and strip out any extra spaces
        if city_name:
            cities.append({
                "slug": link.get("href").split("/")[3],
                "name": city_name.get_text(strip=True)
            })

    return cities
