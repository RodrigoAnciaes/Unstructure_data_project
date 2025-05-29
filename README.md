# Brazilian Marketplace Price Scraper

A Python web scraper that searches for products across multiple Brazilian e-commerce marketplaces and compares prices in real-time. Get the best deals by automatically checking prices from major Brazilian retailers.

## Supported Marketplaces

- **KaBuM** - Electronics and computer hardware
- **Magazine Luiza** - General merchandise and electronics
- **Mercado Livre** - Brazil's largest marketplace (with smart fallback search)
- **Lenovo Brasil** - Official Lenovo store
- **Dell Brasil** - Official Dell store

## Features

- **Interactive Product Search**: Enter any product name via command-line interface
- **Multi-marketplace Comparison**: Automatically searches across 5 major Brazilian retailers
- **Smart Price Parsing**: Handles various Brazilian price formats (R$ 1.234,56, etc.)
- **Intelligent Error Handling**: Resilient scraping with fallback strategies
- **Detailed Results**: Price statistics, best deals identification, and product information
- **Debug Support**: Saves screenshots and HTML for troubleshooting
- **Clean Output**: User-friendly progress indicators and formatted results

## Quick Start

### Prerequisites

- Python 3.7+
- Google Chrome browser installed
- Internet connection

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RodrigoAnciaes/Unstructure_data_project.git
   cd Unstructure_data_project
   ```

2. **Install required packages:**
   ```bash
   pip install selenium pandas webdriver-manager
   ```

3. **Run the scraper:**
   ```bash
   python ws.py
   ```

### Usage Example

```
=== Brazilian Marketplace Price Scraper ===
This tool will search for products across multiple Brazilian marketplaces.
Examples: notebook, smartphone, tablet, mouse, teclado, monitor, etc.

Enter the product you want to search for: smartphone
📦 You want to search for: 'smartphone'
Is this correct? (y/n): y

🔍 Starting to scrape 'Smartphone' from 5 sources...
============================================================
[1/5] Scraping KaBuM...
  ✅ Found product: Smartphone Samsung Galaxy A54 5G 128GB...
  💰 Price: R$ 1.299,00
  ⏱️  Waiting 4.2 seconds...

[2/5] Scraping Magazine Luiza...
  ✅ Found product: Smartphone Motorola Moto G73 5G 256GB...
  💰 Price: R$ 899,00
  ⏱️  Waiting 3.8 seconds...
```

## Output

The scraper generates:

### Console Output
- Real-time progress updates
- Product titles and prices found
- Price statistics and best deals
- Error handling with user-friendly messages

### Files Generated
- **CSV Results**: `summary/[product]_[timestamp]_price_comparison.csv`
- **Debug Files**: `debug/` folder with screenshots and HTML sources
- **Price Statistics**: Average, minimum, maximum, and best deal identification

### Sample Results
```
📈 PRICE STATISTICS:
   Average: R$ 1.456,33
   Minimum: R$ 899,00
   Maximum: R$ 2.199,00
   🏆 Best deal: Magazine Luiza - R$ 899,00
```

## Technical Details

### Architecture
- **Selenium WebDriver**: Chrome browser automation
- **Pandas**: Data processing and CSV export
- **Smart CSS Selectors**: Marketplace-specific element targeting
- **Robust Price Parsing**: Handles multiple Brazilian currency formats

### Price Format Support
- `R$ 1.234,56` (Standard Brazilian format)
- `1.234,56` (Without currency symbol)
- `1234.56` (US format with 2 decimals)
- `1.779` (Thousand separators)
- `1799` (Plain numbers)

### Error Handling
- **Timeout Management**: Graceful handling of slow-loading pages
- **Stale Element Recovery**: Automatic retry for dynamic content
- **Mercado Livre Fallback**: Multiple search strategies for better success rates
- **Debug Information**: Comprehensive logging for troubleshooting

### Performance Optimizations
- **Headless Browser**: Faster execution without GUI
- **Image Blocking**: Reduced bandwidth and faster loading
- **GPU Acceleration Disabled**: Eliminates common warnings
- **Smart Delays**: Random intervals to avoid rate limiting

## Project Structure

```
Unstructure_data_project/
├── ws.py                    # Main scraper script
├── README.md               # This file
├── LICENSE                 # MIT License
├── .gitignore             # Git ignore rules
├── .gitattributes         # Git attributes
├── debug/                 # Debug outputs (auto-created)
│   ├── *.html            # Page sources
│   └── *.png             # Screenshots
└── summary/              # Results (auto-created)
    └── *.csv             # Price comparison data
```

## Configuration

### Customizing Marketplaces
Edit the `marketplaces` list in `ws.py` to add or modify retailers:

```python
marketplaces = [
    {
        "name": "Your Store",
        "search_url": "https://example.com/search/{}",
        "price_selector": ".price-class",
        "title_selector": ".title-class",
    }
]
```

### Chrome Options
The scraper includes optimized Chrome settings for:
- Headless operation
- Warning suppression
- Performance optimization
- Memory efficiency