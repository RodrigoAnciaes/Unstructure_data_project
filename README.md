# Brazilian Marketplace Price Scraper

A comprehensive Python web scraper that searches for products across multiple Brazilian e-commerce marketplaces and compares prices in real-time. Available as both a command-line tool and a modern web application. Get the best deals by automatically checking prices from major Brazilian retailers.

## Features

### Core Functionality
- **Multi-marketplace Comparison**: Automatically searches across 5 major Brazilian retailers
- **Smart Price Parsing**: Handles various Brazilian price formats (R$ 1.234,56, etc.)
- **Intelligent Error Handling**: Resilient scraping with fallback strategies for Mercado Livre
- **Real-time Progress Tracking**: Live updates during the scraping process
- **Comprehensive Results**: Price statistics, best deals identification, and product information

### Two Interface Options
1. **Command-Line Interface** (`ws.py`): Traditional terminal-based interaction
2. **Web Application** (`app.py`): Modern browser-based interface with real-time updates

### Data & Debugging
- **CSV Export**: Detailed results with timestamps and metadata
- **Debug Support**: Saves screenshots and HTML sources for troubleshooting
- **Price Statistics**: Average, minimum, maximum prices with best deal highlighting

## Supported Marketplaces

- **KaBuM** - Electronics and computer hardware specialist
- **Magazine Luiza** - Major Brazilian retail chain
- **Mercado Livre** - Brazil's largest marketplace (with intelligent fallback search)
- **Lenovo Brasil** - Official Lenovo store
- **Dell Brasil** - Official Dell store


## Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RodrigoAnciaes/Unstructure_data_project.git
   cd Unstructure_data_project
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Usage Options

#### Option 1: Web Application (Recommended)

1. **Start the web server:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Use the intuitive web interface:**
   - Enter product name in the search box
   - Watch real-time progress updates
   - View interactive results with statistics
   - Download CSV reports with one click

#### Option 2: Command-Line Interface

1. **Run the terminal version:**
   ```bash
   python ws.py
   ```

2. **Follow the interactive prompts:**
   ```
   === Brazilian Marketplace Price Scraper ===
   Enter the product you want to search for: notebook
   📦 You want to search for: 'notebook'
   Is this correct? (y/n): y
   ```

## Sample Output

### Web Interface
- **Real-time Progress Bar**: Visual indication of scraping progress
- **Interactive Results Cards**: Hover effects and best deal highlighting
- **Price Statistics Dashboard**: Average, min, max prices at a glance
- **One-click CSV Download**: Instant access to detailed data

### Command-Line Interface
```
🔍 Starting to scrape 'Notebook' from 5 sources...
============================================================
[1/5] Scraping KaBuM...
  ✅ Found product: MacBook Air Apple 13", M1, CPU 8 Núcleos...
  💰 Price: R$ 5.899,00
  ⏱️  Waiting 4.2 seconds...

📈 PRICE STATISTICS:
   Average: R$ 3.578,40
   Minimum: R$ 1.399,00
   Maximum: R$ 5.899,00
   🏆 Best deal: Magazine Luiza - R$ 1.399,00
```

## Project Structure

```
Unstructure_data_project/
├── ws.py                           # Command-line scraper
├── app.py                          # Flask web application
├── requirements.txt                # Python dependencies
├── templates/
│   └── index.html                 # Web interface template
├── summary/                       # CSV results (auto-created)
│   ├── notebook_20250529_*.csv   # Sample results
│   └── brazil_laptop_*.csv       # Sample results
├── debug/                         # Debug outputs (auto-created)
│   ├── *.html                     # Page sources
│   └── *.png                      # Screenshots
├── README.md                      # This documentation
├── LICENSE                        # MIT License
├── .gitignore                     # Git ignore rules
└── .gitattributes                 # Git attributes
```

## Technical Implementation

### Web Scraping Engine
- **Selenium WebDriver**: Chrome browser automation with optimized settings
- **Headless Operation**: Faster execution without GUI overhead
- **Anti-Detection Measures**: Realistic user agents and browsing patterns
- **Error Recovery**: Automatic retry mechanisms and graceful degradation

### Price Parsing Intelligence
The scraper handles multiple Brazilian currency formats:
- `R$ 1.234,56` (Standard Brazilian format)
- `1.234,56` (Without currency symbol)
- `1234.56` (US format with exactly 2 decimals)
- `1.779` (Thousand separators only)
- `1799` (Plain numbers)

### Performance Optimizations
- **Headless Browser**: No GUI rendering for faster execution
- **Image Blocking**: Reduced bandwidth and loading times
- **GPU Acceleration Disabled**: Eliminates compatibility warnings
- **Smart Delays**: Random intervals (3-7s) to avoid rate limiting
- **Concurrent Processing**: Asynchronous scraping with progress tracking

### Web Application Features
- **Flask Backend**: Lightweight Python web framework
- **Real-time Updates**: WebSocket-like polling for live progress
- **Responsive Design**: Mobile-friendly interface
- **Background Processing**: Non-blocking scraping with threading
- **Session Management**: Multiple concurrent searches supported

## Sample Results Data

Recent scraping results show competitive pricing across marketplaces:

| Marketplace | Product Example | Price Range |
|-------------|----------------|-------------|
| KaBuM | MacBook Air M1 | R$ 5.899,00 |
| Magazine Luiza | Samsung Chromebook | R$ 1.399,00 |
| Mercado Livre | Lenovo ThinkPad T480 | R$ 1.779,00 |
| Lenovo Brasil | IdeaPad 1i | R$ 2.816,99 |
| Dell Brasil | Inspiron 15 | R$ 3.998,00 |

## Advanced Configuration

### Adding New Marketplaces
Edit the `marketplaces` list in either `ws.py` or `app.py`:

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

### Web Application Customization
- **Port Configuration**: Change port in `app.py` (default: 5000)
- **Styling**: Modify CSS in `templates/index.html`
- **Progress Polling**: Adjust update frequency in JavaScript

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.