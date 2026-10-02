"""Google Maps Scraper Entry Point

Run this file to start the Google Maps scraper:
    python main.py
"""

import sys
import importlib

# Import scraper module dynamically to support filenames with spaces
scraper_module = importlib.import_module("Google maps scraper")
run_scraper = scraper_module.run_scraper


def main():
    print("=" * 50)
    print("           Google Maps Business Scraper           ")
    print("=" * 50)
    try:
        run_scraper()
    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit(0)


if __name__ == "__main__":
    main()
