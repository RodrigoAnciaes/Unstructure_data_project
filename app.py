from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import time
import re
from datetime import datetime
import os
import threading
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Store scraping progress
scraping_progress = {}

# Create necessary folders
for folder in ["debug", "summary", "static", "templates"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Import functions from ws.py
def extract_price(price_text):
    """Extract price as float from various Brazilian price formats."""
    if not price_text or price_text.strip() == "Not found":
        return None
    
    cleaned_text = re.sub(r'\b(ou|preço|price|valor|de|por|até)\b', '', price_text.lower())
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    price_patterns = [
        (r'r\$?\s*(\d{1,3}(?:\.\d{3})*),(\d{2})', 'brazilian_comma'),
        (r'(\d{1,3}(?:\.\d{3})*),(\d{2})', 'brazilian_comma'),
        (r'(\d+)\.(\d{2})(?!\d)', 'us_decimal'),
        (r'(\d{1,3}(?:\.\d{3})+)(?!\d)', 'thousand_separator'),
        (r'(\d+)', 'plain_number')
    ]
    
    for pattern, format_type in price_patterns:
        match = re.search(pattern, cleaned_text)
        if match:
            if format_type == 'brazilian_comma':
                integer_part = match.group(1).replace('.', '')
                decimal_part = match.group(2)
                price_value = float(f"{integer_part}.{decimal_part}")
                return price_value
            elif format_type == 'us_decimal':
                price_value = float(f"{match.group(1)}.{match.group(2)}")
                return price_value
            elif format_type == 'thousand_separator':
                number_str = match.group(1).replace('.', '')
                price_value = float(number_str)
                return price_value
            elif format_type == 'plain_number':
                price_value = float(match.group(1))
                return price_value
    
    numbers = re.findall(r'\d+', cleaned_text)
    if numbers:
        number_values = [int(num) for num in numbers]
        largest_number = max(number_values)
        
        if largest_number < 100 and len(numbers) > 1:
            combined = ''.join(numbers)
            if len(combined) >= 3:
                return float(combined)
        
        return float(largest_number)
    
    return None

marketplaces = [
    {
        "name": "KaBuM",
        "search_url": "https://www.kabum.com.br/busca/{}",
        "price_selector": ".sc-57f0fd6e-2.hjJfoh.priceCard",
        "title_selector": ".nameCard",
    },
    {
        "name": "Magazine Luiza",
        "search_url": "https://www.magazineluiza.com.br/busca/{}/",
        "price_selector": "[data-testid='price-value']",
        "title_selector": 'h2[data-testid="product-title"]',
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

def setup_driver():
    """Setup Chrome WebDriver with optimized options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-webgl")
    chrome_options.add_argument("--disable-webgl2")
    chrome_options.add_argument("--disable-3d-apis")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-images")
    
    service = Service(ChromeDriverManager().install())
    service.log_path = os.devnull
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_single_marketplace(driver, marketplace, product_name, product_display_name, marketplace_index, total_marketplaces, session_id):
    """Scrape a single marketplace and update progress."""
    try:
        # Update progress
        scraping_progress[session_id]['current_marketplace'] = marketplace['name']
        scraping_progress[session_id]['current_index'] = marketplace_index
        
        if "mercadolivre" in marketplace["search_url"]:
            url = marketplace["search_url"].format(product_name, product_name)
        else:
            url = marketplace["search_url"].format(product_name)
        
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        # Extract product title
        try:
            title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, marketplace["title_selector"])))
            title = title_element.text.strip()
        except TimeoutException:
            title = "Not found"
        
        # Extract price
        price_text = "Not found"
        price_value = None
        try:
            price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, marketplace["price_selector"])))
            price_text = price_element.text.strip()
            price_value = extract_price(price_text)
        except TimeoutException:
            pass
        
        result = {
            "timestamp": datetime.now(),
            "product": product_display_name,
            "marketplace": marketplace["name"],
            "title": title,
            "raw_price_text": price_text,
            "price": price_value,
            "url": url
        }
        
        # Update progress with result
        scraping_progress[session_id]['results'].append(result)
        
        # Random delay
        delay = 0 + (time.time() % 4)
        time.sleep(delay)
        
        return result
        
    except Exception as e:
        scraping_progress[session_id]['errors'].append(f"Error scraping {marketplace['name']}: {str(e)}")
        return None

def scrape_mercado_livre(driver, product_name, product_display_name, marketplace_index, total_marketplaces, session_id):
    """Try both Mercado Livre search methods."""
    mercado_livre_searches = [
        {
            "name": "Mercado Livre",
            "search_url": "https://lista.mercadolivre.com.br/{}#D[A:{}]",
            "price_selector": ".andes-money-amount__fraction",
            "title_selector": "a.poly-component__title",
        },
        {
            "name": "Mercado Livre",
            "search_url": "https://lista.mercadolivre.com.br/{}?sb=all_mercadolibre#D[A:{}]",
            "price_selector": ".andes-money-amount__fraction",
            "title_selector": "a.poly-component__title",
        }
    ]
    
    for search_config in mercado_livre_searches:
        result = scrape_single_marketplace(
            driver, search_config, product_name, product_display_name, 
            marketplace_index, total_marketplaces, session_id
        )
        
        if result and (result['title'] != 'Not found' or result['price'] is not None):
            result['marketplace'] = "Mercado Livre"
            return result
    
    return None

def scrape_marketplaces_async(product_name, session_id):
    """Scrape marketplaces asynchronously."""
    product_display_name = product_name.title()
    results = []
    driver = setup_driver()
    
    regular_marketplaces = [m for m in marketplaces if "mercadolivre" not in m["search_url"]]
    total_sources = len(regular_marketplaces) + 1
    
    scraping_progress[session_id] = {
        'status': 'running',
        'total': total_sources,
        'current_index': 0,
        'current_marketplace': '',
        'results': [],
        'errors': [],
        'start_time': datetime.now()
    }
    
    try:
        # Scrape regular marketplaces
        for i, marketplace in enumerate(regular_marketplaces, 1):
            result = scrape_single_marketplace(
                driver, marketplace, product_name, product_display_name, i, total_sources, session_id
            )
            if result:
                results.append(result)
        
        # Handle Mercado Livre
        mercado_result = scrape_mercado_livre(
            driver, product_name, product_display_name, len(regular_marketplaces) + 1, total_sources, session_id
        )
        if mercado_result:
            results.append(mercado_result)
        
        # Save results
        if results:
            df = pd.DataFrame(results)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary/{product_name}_{timestamp}_price_comparison.csv"
            df.to_csv(filename, index=False)
            
            # Calculate statistics
            valid_prices_df = df[df['price'].notna()]
            stats = {}
            if not valid_prices_df.empty:
                stats = {
                    'average': valid_prices_df['price'].mean(),
                    'minimum': valid_prices_df['price'].min(),
                    'maximum': valid_prices_df['price'].max(),
                    'best_deal': valid_prices_df.loc[valid_prices_df['price'].idxmin()].to_dict()
                }
            
            scraping_progress[session_id]['status'] = 'completed'
            scraping_progress[session_id]['filename'] = filename
            scraping_progress[session_id]['stats'] = stats
        else:
            scraping_progress[session_id]['status'] = 'no_results'
    
    except Exception as e:
        scraping_progress[session_id]['status'] = 'error'
        scraping_progress[session_id]['error'] = str(e)
    
    finally:
        driver.quit()
        scraping_progress[session_id]['end_time'] = datetime.now()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Start a new search."""
    data = request.json
    product_name = data.get('product', '').strip().lower()
    
    if not product_name or len(product_name) < 2:
        return jsonify({'error': 'Product name must be at least 2 characters long'}), 400
    
    # Generate session ID
    session_id = f"{product_name}_{int(time.time())}"
    
    # Start scraping in background thread
    thread = threading.Thread(target=scrape_marketplaces_async, args=(product_name, session_id))
    thread.start()
    
    return jsonify({'session_id': session_id, 'product': product_name})

@app.route('/progress/<session_id>')
def get_progress(session_id):
    """Get scraping progress."""
    if session_id not in scraping_progress:
        return jsonify({'error': 'Session not found'}), 404
    
    progress = scraping_progress[session_id]
    return jsonify(progress)

@app.route('/download/<filename>')
def download_csv(filename):
    """Download the CSV file."""
    filepath = f"summary/{filename}"
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)