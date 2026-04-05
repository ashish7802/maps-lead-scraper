#!/usr/bin/env python3
"""
Google Maps Lead Scraper CLI
Main entry point for the application.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional
import yaml

from scraper import GoogleMapsScraper, FilterManager, ExportManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scraper.log")
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_file: str = "config.yaml") -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config_path = Path(config_file)
    
    if not config_path.exists():
        logger.warning(f"Config file not found at {config_file}, using defaults")
        return {
            "headless": True,
            "scroll_pause": 2,
            "max_results": 50
        }
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
        logger.info(f"Loaded configuration from {config_file}")
        return config
    except Exception as e:
        logger.error(f"Error loading config file: {str(e)}")
        return {
            "headless": True,
            "scroll_pause": 2,
            "max_results": 50
        }


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Google Maps Lead Scraper - Extract business leads from Google Maps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --query "dentist" --city "Lucknow"
  python main.py --query "restaurant" --city "Delhi" --format json --min-rating 4.0
  python main.py --query "plumber" --city "Mumbai" --filter-no-website --output local_leads
        """
    )

    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Search query (e.g., 'dentist', 'restaurant')"
    )

    parser.add_argument(
        "--city",
        type=str,
        required=True,
        help="City name (e.g., 'Lucknow', 'Delhi')"
    )

    parser.add_argument(
        "--filter-no-website",
        action="store_true",
        help="Filter out businesses with websites (keep only those without)"
    )

    parser.add_argument(
        "--min-rating",
        type=float,
        default=None,
        help="Minimum rating threshold (0-5)"
    )

    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Filter by category keyword (case-insensitive)"
    )

    parser.add_argument(
        "--has-phone",
        action="store_true",
        help="Filter for leads with phone numbers only"
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["csv", "json", "both"],
        default="csv",
        help="Export format (default: csv)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="leads",
        help="Output filename without extension (default: leads)"
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=None,
        help="Maximum results to scrape (default from config)"
    )

    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Perform detailed scrape (slower but more accurate)"
    )

    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Do not export results to file (print only)"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Output directory for exported files (default: outputs)"
    )

    return parser


async def main():
    """Main application entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Merge command-line args with config
    max_results = args.max_results or config.get("max_results", 50)
    headless = config.get("headless", True)
    scroll_pause = config.get("scroll_pause", 2)

    logger.info(f"Starting Google Maps Lead Scraper")
    logger.info(f"Query: {args.query}, City: {args.city}")

    try:
        # Initialize scraper
        scraper = GoogleMapsScraper(
            headless=headless,
            scroll_pause=scroll_pause
        )

        # Scrape leads
        logger.info("Initiating scrape...")
        if args.detailed:
            leads = await scraper.scrape_detailed(args.query, args.city, max_results)
        else:
            leads = await scraper.scrape(args.query, args.city, max_results)

        if not leads:
            logger.warning("No leads were scraped")
            print("\n⚠️  No leads found for the given search criteria.")
            return

        print(f"\n✅ Scraped {len(leads)} leads")

        # Apply filters
        filter_kwargs = {}
        if args.filter_no_website:
            filter_kwargs["no_website"] = True
        if args.min_rating is not None:
            filter_kwargs["min_rating"] = args.min_rating
        if args.category:
            filter_kwargs["category"] = args.category
        if args.has_phone:
            filter_kwargs["has_phone"] = True

        if filter_kwargs:
            logger.info("Applying filters...")
            leads = FilterManager.apply_filters(leads, **filter_kwargs)
            print(f"✅ After filtering: {len(leads)} leads remain")

        if not leads:
            logger.warning("No leads remaining after filters")
            print("\n⚠️  No leads match the selected filters.")
            return

        # Export results
        if not args.no_export:
            logger.info(f"Exporting results to {args.format} format...")
            
            export_paths = {}
            
            if args.format == "csv":
                export_paths["csv"] = ExportManager.export_csv(
                    leads,
                    args.output,
                    args.output_dir
                )
            elif args.format == "json":
                export_paths["json"] = ExportManager.export_json(
                    leads,
                    args.output,
                    args.output_dir
                )
            else:  # both
                export_paths = ExportManager.export_both(
                    leads,
                    args.output,
                    args.output_dir
                )

            # Print summary
            summary = ExportManager.format_output_summary(leads, export_paths)
            print(summary)
        else:
            # Print summary without export paths
            print(f"\n{'='*60}")
            print("Export Summary (No Files Created)")
            print(f"{'='*60}")
            print(f"Total leads: {len(leads)}")
            print(f"{'='*60}\n")

        # Print sample of leads
        print("\n📋 Sample of leads (first 5):")
        print("-" * 60)
        for i, lead in enumerate(leads[:5], 1):
            print(f"\n{i}. {lead.get('name', 'N/A')}")
            print(f"   Rating: {lead.get('rating', 'N/A')} ⭐")
            print(f"   Phone: {lead.get('phone', 'N/A')}")
            print(f"   Address: {lead.get('address', 'N/A')}")
            print(f"   Website: {lead.get('website', 'N/A')}")

        logger.info("Scraping completed successfully")

    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
