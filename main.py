"""
This tool allows you to scrape restaurant deal information from
NeoTaste's city-specific restaurant pages.
You can filter and retrieve restaurant deals, including
”event-deals“ (marked with 🌟), and export the data to
different formats: text, JSON, or HTML.
"""
import argparse

from neotaste_scraper.data_output import (
    print_deals,
    output_json,
    output_html
)
from neotaste_scraper.neotaste_scraper import (
    fetch_deals_from_city,
    fetch_all_cities,
    get_localized_strings
)


def main():
    """Main entry point"""
    # Set up CLI argument parsing
    parser = argparse.ArgumentParser(description="NeoTaste CLI Tool")
    parser.add_argument(
        "-c", "--city", type=str, help="City to scrape (e.g., 'berlin')"
    )
    parser.add_argument(
        "-a", "--all", action="store_true", help="Scrape all available cities"
    )
    parser.add_argument(
        "-e", "--events", action="store_true", help="Filter only event deals (🌟)"
    )
    parser.add_argument(
        "-j", "--json", action="store_true", help="Output in JSON format"
    )
    parser.add_argument(
        "-H", "--html", action="store_true", help="Output in HTML format"
    )
    parser.add_argument(
        "-l", "--lang", type=str, choices=["de", "en"], default="de", help="Language (default: de)"
    )

    args = parser.parse_args()

    cities_data = {}

    if args.city:
        # Fetch and print deals for a specific city
        print(f"Fetching deals for city: {args.city}...")
        deals = fetch_deals_from_city(args.city, args.events, args.lang)
        cities_data[args.city] = deals
    elif args.all:
        # Fetch and print deals for all cities
        print("Fetching deals for all cities...")
        cities = fetch_all_cities(args.lang)
        for city in cities:
            print(f"Fetching deals for city: {city['slug']}...")
            city_deals = fetch_deals_from_city(city['slug'], args.events, args.lang)
            cities_data[city['slug']] = city_deals

    if not cities_data:
        print(get_localized_strings(args.lang)['no_deals_found'])
        return

    # Print deals in text format (default)
    print_deals(cities_data, args.lang)

    # Output in JSON format if requested
    if args.json:
        print("Outputting deals to output.json...")
        output_json(cities_data)

    # Output in HTML format if requested
    if args.html:
        print("Outputting deals to output.html...")
        output_html(cities_data, args.lang)


if __name__ == "__main__":
    main()
