import pandas as pd
import time
import re
from datetime import datetime
import os
import sys
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

# Function to extract and normalize price from text
def extract_price(price_text):
    """
    Extract price as float from various Brazilian price formats.
    
    Args:
        price_text (str): Raw price text from website
        
    Returns:
        float: Normalized price value, or None if no price found
    """
    if not price_text or price_text.strip() == "Not found":
        return None
    
    # Remove common Portuguese words and extra whitespace
    cleaned_text = re.sub(r'\b(ou|preço|price|valor|de|por|até)\b', '', price_text.lower())
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    # Pattern to match Brazilian currency format
    # Priority order matters - more specific patterns first
    price_patterns = [
        # Brazilian format with comma as decimal separator: R$ 1.234,56 or 1.234,56
        (r'r\$?\s*(\d{1,3}(?:\.\d{3})*),(\d{2})', 'brazilian_comma'),
        (r'(\d{1,3}(?:\.\d{3})*),(\d{2})', 'brazilian_comma'),
        
        # US format with dot as decimal separator, but only if it has exactly 2 digits after dot: 1234.56
        (r'(\d+)\.(\d{2})(?!\d)', 'us_decimal'),
        
        # Numbers with dots as thousand separators (no decimal): 1.779 -> 1779
        (r'(\d{1,3}(?:\.\d{3})+)(?!\d)', 'thousand_separator'),
        
        # Plain numbers without separators: 1779
        (r'(\d+)', 'plain_number')
    ]
    
    for pattern, format_type in price_patterns:
        match = re.search(pattern, cleaned_text)
        if match:
            if format_type == 'brazilian_comma':
                # Brazilian format: 1.234,56
                integer_part = match.group(1).replace('.', '')  # Remove thousand separators
                decimal_part = match.group(2)
                price_value = float(f"{integer_part}.{decimal_part}")
                return price_value
                
            elif format_type == 'us_decimal':
                # US format: 1234.56 (only when exactly 2 decimal digits)
                price_value = float(f"{match.group(1)}.{match.group(2)}")
                return price_value
                
            elif format_type == 'thousand_separator':
                # Numbers like 1.779 where dots are thousand separators
                number_str = match.group(1).replace('.', '')  # Remove dots
                price_value = float(number_str)
                return price_value
                
            elif format_type == 'plain_number':
                # Just numbers
                price_value = float(match.group(1))
                return price_value
    
    # Final fallback: extract all numbers and use the largest one
    numbers = re.findall(r'\d+', cleaned_text)
    if numbers:
        # Convert to integers and find the largest (most likely the price)
        number_values = [int(num) for num in numbers]
        largest_number = max(number_values)
        
        # If the largest number seems too small for a laptop price, 
        # try to combine numbers intelligently
        if largest_number < 100 and len(numbers) > 1:
            # Try to construct a price from multiple parts
            combined = ''.join(numbers)
            if len(combined) >= 3:  # Reasonable price length
                return float(combined)
        
        return float(largest_number)
    
    return None

def get_product_input():
    """
    Get product name from user input with validation.
    
    Returns:
        str: Product name to search for
    """
    print("=== Brazilian Marketplace Price Scraper ===")
    print("This tool will search for products across multiple Brazilian marketplaces.")
    print("Examples: notebook, smartphone, tablet, mouse, teclado, monitor, etc.\n")
    
    while True:
        product_name = input("Enter the product you want to search for: ").strip()
        
        if not product_name:
            print("❌ Product name cannot be empty. Please try again.\n")
            continue
        
        if len(product_name) < 2:
            print("❌ Product name too short. Please enter at least 2 characters.\n")
            continue
        
        # Convert to lowercase for search
        product_name = product_name.lower()
        
        # Confirm with user
        print(f"\n📦 You want to search for: '{product_name}'")
        confirm = input("Is this correct? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes', 's', 'sim']:
            return product_name
        elif confirm in ['n', 'no', 'nao', 'não']:
            print("Let's try again.\n")
            continue
        else:
            print("Please answer with 'y' for yes or 'n' for no.\n")

# Brazilian marketplaces with their specific URL formats and CSS selectors
marketplaces = [
    {
        "name": "KaBuM",
        "search_url": "https://www.kabum.com.br/busca/{}",
        "price_selector": ".sc-57f0fd6e-2.hjJfoh.priceCard",  # Updated selector
        "title_selector": ".nameCard",
    },
    {
        "name": "Magazine Luiza",
        "search_url": "https://www.magazineluiza.com.br/busca/{}/",
        "price_selector": "[data-testid='price-value']",  # Updated selector
        "title_selector": 'h2[data-testid="product-title"]',
    },
    {
        "name": "Mercado Livre (Search 1)",
        "search_url": "https://lista.mercadolivre.com.br/{}#D[A:{}]",
        "price_selector": ".andes-money-amount__fraction",
        "title_selector": "a.poly-component__title",
    },
    {
        "name": "Mercado Livre (Search 2)",
        "search_url": "https://lista.mercadolivre.com.br/{}?sb=all_mercadolibre#D[A:{}]",
        "price_selector": ".andes-money-amount__fraction",
        "title_selector": "a.poly-component__title",
    },
    {
        "name": "Lenovo Brasil",
        "search_url": "https://www.lenovo.com/br/pt/search?fq=&text={}&rows=20&sort=relevance",
        "price_selector": ".price-title",
        "title_selector": 'a[id^="pc-title_"]',
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
def scrape_marketplaces(product_name, product_display_name=None):
    """
    Scrape marketplaces for the given product.
    
    Args:
        product_name (str): The product name to search for
        product_display_name (str): Display name for the product (optional)
    
    Returns:
        list: List of scraped product data
    """
    if product_display_name is None:
        product_display_name = product_name.title()
    
    results = []
    driver = setup_driver()
    
    print(f"\n🔍 Starting to scrape '{product_display_name}' from {len(marketplaces)} marketplaces...")
    print("=" * 60)
    
    try:
        for i, marketplace in enumerate(marketplaces, 1):
            try:
                print(f"[{i}/{len(marketplaces)}] Scraping {marketplace['name']}...")
                
                # Format the URL with the search term
                if "mercadolivre" in marketplace["search_url"]:
                    # Handle Mercado Livre's special URL format
                    url = marketplace["search_url"].format(product_name, product_name)
                else:
                    url = marketplace["search_url"].format(product_name)
                
                # Navigate to the URL
                driver.get(url)
                
                # Wait for page to load (adjust timeout as needed)
                wait = WebDriverWait(driver, 10)
                
                # Save the page source to a file for debugging
                debug_filename = f"debug/{marketplace['name']}_{product_name}_debug.html"
                with open(debug_filename, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                
                # Extract the first product title - wait for it to appear
                try:
                    title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, marketplace["title_selector"])))
                    title = title_element.text.strip()
                    print(f"  ✅ Found product: {title[:80]}{'...' if len(title) > 80 else ''}")
                except TimeoutException:
                    print(f"  ❌ Title element not found")
                    title = "Not found"
                
                # Extract the price
                price_text = "Not found"
                price_value = None
                try:
                    price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, marketplace["price_selector"])))
                    price_text = price_element.text.strip()
                    # Extract and normalize the price
                    price_value = extract_price(price_text)
                    if price_value:
                        print(f"  💰 Price: R$ {price_value:.2f}")
                    else:
                        print(f"  ⚠️  Could not parse price: '{price_text}'")
                except TimeoutException:
                    print(f"  ❌ Price element not found")
                
                # Add to results
                results.append({
                    "timestamp": datetime.now(),
                    "product": product_display_name,
                    "marketplace": marketplace["name"],
                    "title": title,
                    "raw_price_text": price_text,  # Keep original for debugging
                    "price": price_value,  # Normalized price as float
                    "url": url
                })
                
                # Take a screenshot for visual verification
                screenshot_filename = f"debug/{marketplace['name']}_{product_name}_screenshot.png"
                driver.save_screenshot(screenshot_filename)
                
                # Random delay between requests (3-7 seconds)
                delay = 3 + (time.time() % 4)
                print(f"  ⏱️  Waiting {delay:.1f} seconds...\n")
                time.sleep(delay)
                
            except Exception as e:
                print(f"  ❌ Error scraping {marketplace['name']}: {e}\n")
    
    finally:
        # Always close the driver properly
        driver.quit()
    
    return results

def display_results_summary(df, product_name):
    """
    Display a nice summary of the scraping results.
    
    Args:
        df (DataFrame): Results dataframe
        product_name (str): Name of the product searched
    """
    print("\n" + "=" * 60)
    print(f"📊 SCRAPING RESULTS SUMMARY FOR: {product_name.upper()}")
    print("=" * 60)
    
    if df.empty:
        print("❌ No results were found. Check the debug files for more information.")
        return
    
    # Count successful vs failed scrapes
    total_attempts = len(df)
    successful_titles = len(df[df['title'] != 'Not found'])
    successful_prices = len(df[df['price'].notna()])
    
    print(f"🎯 Total marketplaces scraped: {total_attempts}")
    print(f"✅ Products found: {successful_titles}/{total_attempts}")
    print(f"💰 Prices found: {successful_prices}/{total_attempts}")
    print()
    
    # Display individual results
    for _, row in df.iterrows():
        status_icon = "✅" if row['title'] != 'Not found' else "❌"
        price_text = f"R$ {row['price']:.2f}" if pd.notna(row['price']) else "Price not found"
        
        print(f"{status_icon} {row['marketplace']}: {price_text}")
        if row['title'] != 'Not found':
            title_display = row['title'][:70] + "..." if len(row['title']) > 70 else row['title']
            print(f"    📦 {title_display}")
        print()
    
    # Price statistics
    valid_prices_df = df[df['price'].notna()].copy()
    if not valid_prices_df.empty:
        print("📈 PRICE STATISTICS:")
        print(f"   Average: R$ {valid_prices_df['price'].mean():.2f}")
        print(f"   Minimum: R$ {valid_prices_df['price'].min():.2f}")
        print(f"   Maximum: R$ {valid_prices_df['price'].max():.2f}")
        
        # Find best deal
        cheapest = valid_prices_df.loc[valid_prices_df['price'].idxmin()]
        print(f"   🏆 Best deal: {cheapest['marketplace']} - R$ {cheapest['price']:.2f}")

def main():
    """
    Main function to run the scraper with user input.
    """
    try:
        # Get product name from user
        product_name = get_product_input()
        
        # Create a display-friendly version
        product_display_name = product_name.title()
        
        # Run the scraper
        results = scrape_marketplaces(product_name, product_display_name)
        
        # Convert to DataFrame and save
        if results:
            df = pd.DataFrame(results)
            
            # Save with timestamp in filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary/{product_name}_{timestamp}_price_comparison.csv"
            df.to_csv(filename, index=False)
            
            # Display results
            display_results_summary(df, product_display_name)
            
            print(f"\n💾 Results saved to: {filename}")
            print(f"🔍 Debug files saved to: debug/ folder")
            
        else:
            print("\n❌ No results were found. Check the debug files for more information.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user.")
        print("Any partial results have been saved.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Check the debug files for more information.")

if __name__ == "__main__":
    main()