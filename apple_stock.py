import yfinance as yf
from bs4 import BeautifulSoup

# Get data using yfinance
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1mo")

# Convert to HTML
html_table = hist.to_html()

# Parse with BeautifulSoup
soup = BeautifulSoup(html_table, "html.parser")
rows = soup.find_all("tr")

print("Apple Historical Close Prices:")
for row in rows[1:]:  # Skip header
    cols = row.find_all("td")
    if len(cols) >= 5:
        date = cols[0].get_text(strip=True)
        close_price = cols[4].get_text(strip=True)
        print(f"{date}: {close_price}")