import argparse
import requests
from bs4 import BeautifulSoup

def fetch_deals_from_city(city_slug: str):
    """Scrape deals from a specific city."""
    url = f"https://neotaste.com/de/restaurants/{city_slug}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    results = []

    # Each restaurant card is an <a> with a restaurant link
    cards = soup.select("a[href*='/restaurants/']")

    for card in cards:
        link = card.get("href")
        if not link.startswith("http"):
            link = "https://neotaste.com" + link

        # Restaurant name
        name_el = card.select_one("h3, h4, .font-semibold")
        if not name_el:
            continue
        name = name_el.get_text(strip=True)

        # Deal container
        deals_container = card.select_one('[data-sentry-component="RestaurantCardDeals"]')
        if not deals_container:
            continue

        # Deal preview spans
        deal_spans = deals_container.select('[data-sentry-component="RestaurantDealPreview"] span')

        deals = [
            sp.get_text(strip=True)
            for sp in deal_spans
            if sp.get_text(strip=True)
        ]

        if not deals:
            continue

        results.append({
            "restaurant": name,
            "deals": deals,
            "link": link
        })

    return results

def fetch_all_cities():
    """Scrape the main cities page to get a list of all cities."""
    url = "https://neotaste.com/de/restaurants"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    city_links = soup.select('[data-sentry-component="CitiesList"] a')
    cities = [link.get("href").split("/")[3] for link in city_links if link.get("href")]

    return cities

def print_deals(deals):
    """Print the formatted deals."""
    for r in deals:
        print(f"{r['restaurant']}")
        for d in r['deals']:
            print(f" - {d}")
        print(f" → {r['link']}")
        print()

def main():
    # Set up CLI argument parsing
    parser = argparse.ArgumentParser(description="NeoTaste CLI Tool")
    parser.add_argument(
        "-c", "--city", type=str, help="City to scrape (e.g., 'nuremberg')"
    )
    parser.add_argument(
        "-a", "--all", action="store_true", help="Scrape all available cities"
    )

    args = parser.parse_args()

    if args.city:
        # Fetch and print deals for a specific city
        print(f"Fetching deals for city: {args.city}...")
        deals = fetch_deals_from_city(args.city)
        print_deals(deals)

    elif args.all:
        # Fetch and print deals for all cities
        print("Fetching deals for all cities...")
        cities = fetch_all_cities()
        for city in cities:
            print(f"Fetching deals for city: {city}...")
            deals = fetch_deals_from_city(city)
            print_deals(deals)

    else:
        print("Please specify a city with -c or use -a to scrape all cities.")

if __name__ == "__main__":
    main()
