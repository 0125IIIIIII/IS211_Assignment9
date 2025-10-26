# world_happiest_countries.py
# Scraping from: https://en.wikipedia.org/wiki/World_Happiness_Report

import requests
from bs4 import BeautifulSoup
import re
import logging

logging.basicConfig(filename="scraper_debug.log", level=logging.INFO)

def extract_year_from_context(table):
    """
    Traverses upward through parent and sibling elements to find the nearest year.
    """
    current = table
    attempts = 0
    while current and attempts < 15:
        # Check previous siblings first
        sibling = current.find_previous_sibling()
        while sibling:
            text = sibling.get_text(strip=True)
            match = re.search(r"\b(20\d{2})\b", text)
            if match:
                return match.group(1)
            sibling = sibling.find_previous_sibling()

        # Then move up to the parent
        current = current.parent
        if current and current.name == "body":
            break  # stop at top-level
        attempts += 1

    logging.info("Year not found in parent tree. Using 'Unknown Year'.")
    return "Unknown Year"

def is_ranking_table(table):
    """
    Checks if the table is likely a happiness ranking table by inspecting headers.
    """
    headers = table.find_all("th")
    header_text = " ".join(h.get_text().lower() for h in headers)
    return "country" in header_text and ("score" in header_text or "rank" in header_text)

def extract_top_countries(table, limit=10):
    """
    Extracts up to `limit` valid country names from the table.
    Tries multiple columns and filters out numeric-only or N/A rows.
    """
    rows = table.find_all("tr")[1:]  # skip header
    countries = []
    for row in rows:
        cols = row.find_all("td")
        for col in cols:
            text = col.get_text(strip=True)
            if re.search(r"[A-Za-z]", text) and text.lower() != "n/a":
                if text not in countries and not re.match(r"^\d+(\.\d+)?$", text):
                    countries.append(text)
                    break
        if len(countries) == limit:
            break
    return countries

def main():
    url = "https://en.wikipedia.org/wiki/World_Happiness_Report"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to load page. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table", class_="wikitable")

    results_by_year = []

    for table in tables:
        if not is_ranking_table(table):
            continue

        year = extract_year_from_context(table)
        countries = extract_top_countries(table)

        if countries:
            results_by_year.append((year, countries))
        else:
            logging.info(f"No valid countries found for year: {year}")

    # ✅ Sort by year descending (convert year to int if possible)
    sorted_results = sorted(
        results_by_year,
        key=lambda x: int(x[0]) if x[0].isdigit() else -1,
        reverse=True
    )

    print("Top 10 Happiest Countries (Sorted by Year Descending):")
    for year, countries in sorted_results:
        print(f"\nYear: {year}")
        for country in countries:
            print(f"- {country}")
        if len(countries) < 10:
            print(f"[DEBUG] Only {len(countries)} countries found for {year}.")

if __name__ == "__main__":
    main()

