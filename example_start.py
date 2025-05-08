import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

# List of products to track (you could also read this from a file)
products_to_track = [
    {"name": "Wireless Headphones", "search_term": "wireless+headphones"},
    {"name": "Gaming Monitor", "search_term": "gaming+monitor+144hz"}
]

# List of marketplaces to check
marketplaces = [
    {
        "name": "Example Store",
        "search_url": "https://www.examplestore.com/search?q={}",
        "price_selector": ".product-price",  # CSS selector for price element
        "title_selector": ".product-title",  # CSS selector for title element
    }
    # Add more marketplaces here
]

results = []

# Simple headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Loop through each product and marketplace
for product in products_to_track:
    for marketplace in marketplaces:
        try:
            # Format the URL with the search term
            url = marketplace["search_url"].format(product["search_term"])
            
            # Send the request
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract the first product (you might want to improve this logic)
            title_element = soup.select_one(marketplace["title_selector"])
            price_element = soup.select_one(marketplace["price_selector"])
            
            # Extract text and clean up
            title = title_element.text.strip() if title_element else "Not found"
            price_text = price_element.text.strip() if price_element else "Not found"
            
            # Add to results
            results.append({
                "timestamp": datetime.now(),
                "product": product["name"],
                "marketplace": marketplace["name"],
                "title": title,
                "price": price_text,
                "url": url
            })
            
            # Be nice to the server - add delay between requests
            time.sleep(2)
            
        except Exception as e:
            print(f"Error scraping {product['name']} from {marketplace['name']}: {e}")

# Convert to DataFrame and save
df = pd.DataFrame(results)
df.to_csv("price_comparison_results.csv", index=False)
print("Scraping completed!")