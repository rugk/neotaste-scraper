"""
This tool allows you to scrape restaurant deal information from
NeoTaste's city-specific restaurant pages.
You can filter and retrieve restaurant deals, including
”event-deals“ (marked with 🌟), and export the data to
different formats: text, JSON, or HTML.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

# Constants
BASE_URL = "https://neotaste.com"


def get_city_url(city_slug: str, lang: str = "de") -> str:
    """Construct full URL for the given city with the specified language."""
    return f"{BASE_URL}/{lang}/restaurants/{city_slug}"


@dataclass
class Deal:
    """A parsed deal from a restaurant card."""
    text: str
    component: str
    deal_type: str  # 'flash', 'event', 'flash+event', 'other'


def extract_deals_from_card(card: Tag,
                            filter_mode: Optional[str] = None
                            ) -> Optional[Dict[str, Any]]:
    """Extract deals from a single restaurant card.

    filter_mode may be one of: None (no filter), 'events' (only 🌟),
    'flash' (only flash deals), 'special' (events OR flash).
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

    deals: List[Deal] = []
    for el in deal_elements:
        text = el.get_text(strip=True)
        if not text:
            continue
        component = el.get('data-sentry-component', '')
        # small heuristic for flash detection: component name or inner html may indicate flash
        inner_html = str(el).lower()
        is_flash = (
            ('flashdeal' in component.lower())
            or ('flashdeal' in inner_html)
            or ('⚡' in text)
            or ('bolt' in inner_html)
        )
        # event detection: emoji or component/inner html marker
        is_event = (
            ('eventdeal' in component.lower())
            or ('eventdeal' in inner_html)
            or ('🌟' in text)
        )
        # determine combined deal_type
        if is_flash and is_event:
            deal_type = 'flash+event'
        elif is_flash:
            deal_type = 'flash'
        elif is_event:
            deal_type = 'event'
        else:
            deal_type = 'other'

        deals.append(Deal(text=text, component=component, deal_type=deal_type))

    # Normalize filter_mode values
    if isinstance(filter_mode, bool):
        filter_mode = 'events' if filter_mode else None

    if filter_mode == 'events':
        # Keep only event deals detected by heuristic
        deals = [d for d in deals if d.deal_type in ('event', 'flash+event')]
    elif filter_mode == 'flash':
        deals = [d for d in deals if d.deal_type in ('flash', 'flash+event')]
    elif filter_mode == 'special':
        deals = [d for d in deals if d.deal_type != 'other']

    # Convert to plain list of strings for output
    deals = [d.text for d in deals]

    if not deals:
        return None  # Return None if no deals match the filter

    return {"restaurant": name, "deals": deals, "link": link}


def fetch_deals_from_city(city_slug: str, filter_mode: Optional[str] = None, lang: str = "de") -> List[Dict[str, Any]]:
    """Scrape deals from a specific city and optionally filter deals.

    filter_mode may be None or one of 'events','flash','special'.
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
        # Support legacy callers passing filter_events keyword by letting extract handle it
        result = extract_deals_from_card(card, filter_mode)
        if result:
            results.append(result)

    return results


def fetch_all_cities(lang: str = "de") -> List[Dict[str, str]]:
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
