import pandas as pd
import time
from datetime import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Create the debug and summary folders if they don't exist
if not os.path.exists("debug"):
    os.makedirs("debug")
if not os.path.exists("summary"):
    os.makedirs("summary")

# List of products to track
products_to_track = [
    {"name": "Notebook", "search_term": "notebook"}
]

# Brazilian marketplaces with their specific URL formats and CSS selectors
marketplaces = [
    {
        "name": "KaBuM",
        "search_url": "https://www.kabum.com.br/busca/{}",
        "price_selector": ".sc-57f0fd6e-2.hjJfoh.priceCard",  # Updated selector
        "title_selector": ".sc-d99ca57-0.iRparH",
    },
    {
        "name": "Magazine Luiza",
        "search_url": "https://www.magazineluiza.com.br/busca/{}/",
        "price_selector": "[data-testid='price-value']",  # Updated selector
        "title_selector": ".productTitle",
    },
    {
        "name": "Mercado Livre (Search 1)",
        "search_url": "https://lista.mercadolivre.com.br/{}#D[A:{}]",
        "price_selector": ".andes-money-amount__fraction",
        "title_selector": ".ui-search-item__title",
    },
    {
        "name": "Mercado Livre (Search 2)",
        "search_url": "https://lista.mercadolivre.com.br/{}?sb=all_mercadolibre#D[A:{}]",
        "price_selector": ".andes-money-amount__fraction",
        "title_selector": ".ui-search-item__title",
    },
    {
        "name": "Lenovo Brasil",
        "search_url": "https://www.lenovo.com/br/pt/search?fq=&text={}&rows=20&sort=relevance",
        "price_selector": ".price-title",  # Updated selector
        "title_selector": ".product-name",
    },
    {
        "name": "Dell Brasil",
        "search_url": "https://www.dell.com/pt-br/search/{}",
        "price_selector": ".ps-dell-price",
        "title_selector": ".ps-title",
    }
]

# Set up the Selenium WebDriver with headless options
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Add realistic user agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Initialize the webdriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Main scraping function
def scrape_marketplaces():
    results = []
    driver = setup_driver()
    
    try:
        for product in products_to_track:
            for marketplace in marketplaces:
                try:
                    print(f"Scraping {product['name']} from {marketplace['name']}...")
                    
                    # Format the URL with the search term
                    if "mercadolivre" in marketplace["search_url"]:
                        # Handle Mercado Livre's special URL format
                        url = marketplace["search_url"].format(product["search_term"], product["search_term"])
                    else:
                        url = marketplace["search_url"].format(product["search_term"])
                    
                    # Navigate to the URL
                    driver.get(url)
                    
                    # Wait for page to load (adjust timeout as needed)
                    wait = WebDriverWait(driver, 10)
                    
                    # Save the page source to a file for debugging
                    with open(f"debug/{marketplace['name']}_{product['name']}_debug.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                        print(f"Debug information saved to debug/{marketplace['name']}_{product['name']}_debug.html")
                    
                    # Extract the first product title - wait for it to appear
                    try:
                        title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, marketplace["title_selector"])))
                        title = title_element.text.strip()
                    except TimeoutException:
                        print(f"Title element not found for {marketplace['name']}")
                        title = "Not found"
                    
                    # Extract the price
                    try:
                        price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, marketplace["price_selector"])))
                        price_text = price_element.text.strip()
                    except TimeoutException:
                        print(f"Price element not found for {marketplace['name']}")
                        price_text = "Not found"
                    
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
                    
                    # Take a screenshot for visual verification
                    driver.save_screenshot(f"debug/{marketplace['name']}_{product['name']}_screenshot.png")
                    
                    # Random delay between requests (3-7 seconds)
                    delay = 3 + (time.time() % 4)
                    print(f"Waiting {delay:.1f} seconds before next request...")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"Error scraping {product['name']} from {marketplace['name']}: {e}")
    
    finally:
        # Always close the driver properly
        driver.quit()
    
    return results

if __name__ == "__main__":
    # Run the scraper
    results = scrape_marketplaces()
    
    # Convert to DataFrame and save
    if results:
        df = pd.DataFrame(results)
        print("\nResults summary:")
        print(df[["product", "marketplace", "title", "price"]])
        df.to_csv("summary/brazil_laptop_price_comparison.csv", index=False)
        print("\nScraping completed! Results saved to summary/brazil_laptop_price_comparison.csv")
    else:
        print("No results were found. Check the debug files for more information.")