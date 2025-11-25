import requests
from bs4 import BeautifulSoup

def fetch_neotaste_deals(city_slug: str):
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

if __name__ == "__main__":
    data = fetch_neotaste_deals("nuremberg")
    for r in data:
        print(r["restaurant"])
        for d in r["deals"]:
            print(" -", d)
        print(" →", r["link"])
        print()
