import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

# create the debug folder if it does not exist
import os
if not os.path.exists("debug"):
    os.makedirs("debug")
if not os.path.exists("summary"):
    os.makedirs("summary")

# List of products to track (using your search terms)
products_to_track = [
    {"name": "Laptop", "search_term": "laptop"},
    {"name": "Notebook", "search_term": "notebook"}
]

# Brazilian marketplaces with their specific URL formats and CSS selectors
# Note: These selectors are educated guesses and might need adjustment after testing
marketplaces = [
    {
        "name": "KaBuM",
        "search_url": "https://www.kabum.com.br/busca/{}",
        "price_selector": ".sc-6889e656-2.bHcxc",  # Approximate selector
        "title_selector": ".sc-d99ca57-0.iRparH",  # Approximate selector
    },
    {
        "name": "Magazine Luiza",
        "search_url": "https://www.magazineluiza.com.br/busca/{}/",
        "price_selector": ".price-template__text",  # Approximate selector
        "title_selector": ".productTitle",  # Approximate selector
    },
    {
        "name": "Mercado Livre (Search 1)",
        "search_url": "https://lista.mercadolivre.com.br/{}#D[A:{}]",
        "price_selector": ".andes-money-amount__fraction",  # Approximate selector
        "title_selector": ".ui-search-item__title",  # Approximate selector
    },
    {
        "name": "Mercado Livre (Search 2)",
        "search_url": "https://lista.mercadolivre.com.br/{}?sb=all_mercadolibre#D[A:{}]",
        "price_selector": ".andes-money-amount__fraction",  # Same as above
        "title_selector": ".ui-search-item__title",  # Same as above
    },
    {
        "name": "Lenovo Brasil",
        "search_url": "https://www.lenovo.com/br/pt/search?fq=&text={}&rows=20&sort=relevance",
        "price_selector": ".final-price",  # Approximate selector
        "title_selector": ".product-name",  # Approximate selector
    },
    {
        "name": "Dell Brasil",
        "search_url": "https://www.dell.com/pt-br/search/{}",
        "price_selector": ".ps-dell-price",  # Approximate selector
        "title_selector": ".ps-title",  # Approximate selector
    }
]

results = []

# More realistic headers to help avoid detection
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Loop through each product and marketplace
for product in products_to_track:
    for marketplace in marketplaces:
        try:
            print(f"Scraping {product['name']} from {marketplace['name']}...")
            
            # Format the URL with the search term
            if "mercadolivre" in marketplace["search_url"]:
                # Handle Mercado Livre's special URL format which needs the search term twice
                url = marketplace["search_url"].format(product["search_term"], product["search_term"])
            else:
                url = marketplace["search_url"].format(product["search_term"])
            
            # Send the request
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # save into a file for debugging
            with open(f"debug/{marketplace['name']}_debug.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
                print(f"Debug information saved to debug/{marketplace['name']}_debug.html")

            # Extract the first product
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
            
            print(f"Found: {title} - {price_text}")
            
            # Be nice to the servers - use a random delay between 3-7 seconds
            delay = 3 + (time.time() % 4)  # Simple way to get a number between 3-7
            print(f"Waiting {delay:.1f} seconds before next request...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"Error scraping {product['name']} from {marketplace['name']}: {e}")

# Convert to DataFrame and save
df = pd.DataFrame(results)
print("\nResults summary:")
print(df[["product", "marketplace", "title", "price"]])
df.to_csv("summary/brazil_laptop_price_comparison.csv", index=False)
print("\nScraping completed! Results saved to summary/brazil_laptop_price_comparison.csv")