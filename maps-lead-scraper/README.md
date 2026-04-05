# 🗺️ Google Maps Lead Scraper

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Open Source](https://img.shields.io/badge/Open%20Source-Yes-brightgreen.svg)

A powerful and efficient tool to scrape business leads from Google Maps. Extract business names, phone numbers, addresses, websites, ratings, and more with ease.

## Features

- ✅ **Async Web Scraping**: Uses Playwright for fast, reliable browser automation
- ✅ **Flexible Filtering**: Filter leads by rating, website availability, category, and phone numbers
- ✅ **Multiple Export Formats**: Export results as CSV, JSON, or both
- ✅ **CLI Interface**: Simple command-line interface with powerful options
- ✅ **Configuration Management**: YAML-based configuration for default settings
- ✅ **Comprehensive Logging**: Track all operations with detailed logs
- ✅ **Production Ready**: Error handling, async support, and clean architecture

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps

1. **Clone or Download the Project**
```bash
cd maps-lead-scraper
```

2. **Create a Virtual Environment** (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Playwright Browsers**
```bash
playwright install chromium
```

## Usage

### Basic Usage

```bash
python main.py --query "dentist" --city "Lucknow"
```

### With Filtering

```bash
# Filter by minimum rating
python main.py --query "restaurant" --city "Delhi" --min-rating 4.0

# Filter for businesses without websites
python main.py --query "plumber" --city "Mumbai" --filter-no-website

# Filter for businesses with phone numbers
python main.py --query "accountant" --city "Bangalore" --has-phone
```

### Different Export Formats

```bash
# Export as JSON
python main.py --query "dentist" --city "Lucknow" --format json

# Export as both CSV and JSON
python main.py --query "dentist" --city "Lucknow" --format both

# Custom output filename
python main.py --query "dentist" --city "Lucknow" --output my_leads
```

### Advanced Options

```bash
# Set custom output directory
python main.py --query "dentist" --city "Lucknow" --output-dir ./results

# Limit maximum results
python main.py --query "dentist" --city "Lucknow" --max-results 100

# Detailed scrape (slower but more accurate)
python main.py --query "dentist" --city "Lucknow" --detailed

# Print results without saving to file
python main.py --query "dentist" --city "Lucknow" --no-export

# Combine multiple filters
python main.py --query "dentist" --city "Lucknow" \
  --filter-no-website --min-rating 3.5 --format json --output results
```

## Available CLI Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `--query` | string | ✅ | Search query (e.g., "dentist", "restaurant") |
| `--city` | string | ✅ | City name (e.g., "Lucknow", "Delhi") |
| `--format` | csv/json/both | ❌ | Export format (default: csv) |
| `--output` | string | ❌ | Output filename (default: leads) |
| `--filter-no-website` | flag | ❌ | Keep only businesses without websites |
| `--min-rating` | float | ❌ | Minimum rating threshold (0-5) |
| `--category` | string | ❌ | Filter by category keyword |
| `--has-phone` | flag | ❌ | Keep only leads with phone numbers |
| `--max-results` | int | ❌ | Maximum results to scrape |
| `--output-dir` | string | ❌ | Output directory (default: outputs) |
| `--detailed` | flag | ❌ | Perform detailed scrape |
| `--no-export` | flag | ❌ | Skip exporting to files |

## Configuration

Edit `config.yaml` to set default values:

```yaml
# Browser settings
headless: true              # Run browser in headless mode
scroll_pause: 2             # Pause between scrolls (seconds)
max_results: 50             # Default maximum results

# Export settings
output_dir: outputs         # Default output directory
```

## Output Format

### CSV Output Example
```
name,phone,address,website,rating,category
ABC Dental Clinic,+91-522-1234567,123 Main St Lucknow,https://example.com,4.5,Dentist
XYZ Dental Care,N/A,456 Park Ave Lucknow,N/A,4.2,Dentist
```

### JSON Output Example
```json
[
  {
    "name": "ABC Dental Clinic",
    "phone": "+91-522-1234567",
    "address": "123 Main St Lucknow",
    "website": "https://example.com",
    "rating": 4.5,
    "category": "Dentist"
  },
  {
    "name": "XYZ Dental Care",
    "phone": "N/A",
    "address": "456 Park Ave Lucknow",
    "website": "N/A",
    "rating": 4.2,
    "category": "Dentist"
  }
]
```

## Project Structure

```
maps-lead-scraper/
├── scraper/
│   ├── __init__.py          # Package initialization
│   ├── maps.py              # Google Maps scraper
│   ├── filters.py           # Lead filtering functions
│   └── exporter.py          # CSV/JSON export functionality
├── main.py                  # CLI entry point
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── outputs/                 # Exported leads directory
└── scraper.log              # Application logs
```

## Module Documentation

### GoogleMapsScraper (maps.py)
Handles web scraping of Google Maps using Playwright.

**Main Methods:**
- `scrape(keyword, city, max_results)` - Basic scraping
- `scrape_detailed(keyword, city, max_results)` - Detailed scraping with more information

### FilterManager (filters.py)
Provides filtering capabilities for leads.

**Available Filters:**
- `filter_no_website(leads)` - Find businesses without websites
- `filter_by_rating(leads, min_rating)` - Filter by minimum rating
- `filter_by_category(leads, category_keyword)` - Filter by category
- `filter_by_name(leads, name_keyword)` - Filter by name
- `filter_has_phone(leads)` - Keep only leads with phone numbers
- `apply_filters(leads, **kwargs)` - Apply multiple filters at once

### ExportManager (exporter.py)
Handles exporting leads to various formats.

**Available Formats:**
- `export_csv(leads, filename, output_dir)` - Export to CSV
- `export_json(leads, filename, output_dir)` - Export to JSON
- `export_both(leads, filename, output_dir)` - Export to both formats

## Logging

The application creates a `scraper.log` file with detailed logs of all operations. Check this file to troubleshoot issues.

## Performance Tips

1. **Adjust scroll_pause**: Increase if the website loads slowly, decrease for faster scraping
2. **Use max_results**: Set a reasonable limit to avoid unnecessary scraping
3. **Filter early**: Apply filters after scraping to reduce data processing
4. **Headless Mode**: Keep `headless: true` for faster performance

## Error Handling

The scraper includes comprehensive error handling:
- Connection timeouts and retries
- Invalid filter parameters validation
- File I/O error recovery
- Graceful interruption with Ctrl+C

## Limitations

- Results depend on Google Maps UI structure (may need updates if Google changes the page)
- Respects rate limiting and doesn't bypass Google's terms of service
- Website extraction may be limited due to page structure changes

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Improve documentation
- Submit pull requests

## Disclaimer

This tool is for educational and commercial use. Ensure you comply with:
- Google Maps Terms of Service
- Local laws and regulations regarding web scraping
- Website's robots.txt and terms of service
- Rate limiting and responsible use practices

## Support

For issues, questions, or suggestions:
1. Check the logs in `scraper.log`
2. Review the documentation above
3. Verify your internet connection and Google Maps accessibility
4. Ensure Playwright browsers are installed (`playwright install`)

## Changelog

### Version 1.0.0
- Initial release
- Core scraping functionality
- CSV and JSON export
- Advanced filtering options
- CLI interface
- Configuration management

---

**Made with ❤️ for lead generation and business intelligence**
