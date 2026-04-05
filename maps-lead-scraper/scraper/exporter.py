"""
Export Module
Handles exporting leads data to various formats (CSV, JSON).
"""

import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ExportManager:
    """Manages export operations for leads data."""

    DEFAULT_OUTPUT_DIR = "outputs"

    @classmethod
    def ensure_output_dir(cls, output_dir: str = DEFAULT_OUTPUT_DIR) -> Path:
        """
        Ensure output directory exists, create if necessary.
        
        Args:
            output_dir: Path to output directory
            
        Returns:
            Path object pointing to output directory
        """
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory ensured at: {path.absolute()}")
        return path

    @classmethod
    def export_csv(
        cls,
        leads: List[Dict[str, any]],
        filename: str = "leads",
        output_dir: str = DEFAULT_OUTPUT_DIR
    ) -> str:
        """
        Export leads to CSV file.
        
        Args:
            leads: List of lead dictionaries
            filename: Output filename without extension (default: "leads")
            output_dir: Output directory path (default: "outputs")
            
        Returns:
            Path to the created CSV file
        """
        if not leads:
            logger.warning("No leads to export")
            return None

        try:
            output_path = cls.ensure_output_dir(output_dir)
            csv_file = output_path / f"{filename}.csv"

            # Get all unique keys from all leads
            fieldnames = set()
            for lead in leads:
                fieldnames.update(lead.keys())
            fieldnames = sorted(list(fieldnames))

            with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(leads)

            logger.info(f"Exported {len(leads)} leads to CSV: {csv_file.absolute()}")
            return str(csv_file.absolute())

        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise

    @classmethod
    def export_json(
        cls,
        leads: List[Dict[str, any]],
        filename: str = "leads",
        output_dir: str = DEFAULT_OUTPUT_DIR,
        pretty: bool = True
    ) -> str:
        """
        Export leads to JSON file.
        
        Args:
            leads: List of lead dictionaries
            filename: Output filename without extension (default: "leads")
            output_dir: Output directory path (default: "outputs")
            pretty: Pretty-print JSON with indentation (default: True)
            
        Returns:
            Path to the created JSON file
        """
        if not leads:
            logger.warning("No leads to export")
            return None

        try:
            output_path = cls.ensure_output_dir(output_dir)
            json_file = output_path / f"{filename}.json"

            with open(json_file, "w", encoding="utf-8") as jsonfile:
                if pretty:
                    json.dump(leads, jsonfile, indent=2, ensure_ascii=False)
                else:
                    json.dump(leads, jsonfile, ensure_ascii=False)

            logger.info(f"Exported {len(leads)} leads to JSON: {json_file.absolute()}")
            return str(json_file.absolute())

        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            raise

    @classmethod
    def export_both(
        cls,
        leads: List[Dict[str, any]],
        filename: str = "leads",
        output_dir: str = DEFAULT_OUTPUT_DIR
    ) -> Dict[str, str]:
        """
        Export leads to both CSV and JSON formats.
        
        Args:
            leads: List of lead dictionaries
            filename: Output filename without extension (default: "leads")
            output_dir: Output directory path (default: "outputs")
            
        Returns:
            Dictionary with 'csv' and 'json' keys pointing to created files
        """
        results = {}
        try:
            results["csv"] = cls.export_csv(leads, filename, output_dir)
            results["json"] = cls.export_json(leads, filename, output_dir)
            logger.info(f"Exported leads to both formats")
            return results
        except Exception as e:
            logger.error(f"Error exporting to both formats: {str(e)}")
            raise

    @staticmethod
    def format_output_summary(
        leads: List[Dict[str, any]],
        export_paths: Dict[str, str] = None
    ) -> str:
        """
        Generate a formatted summary of the export operation.
        
        Args:
            leads: List of exported leads
            export_paths: Dictionary of export paths
            
        Returns:
            Formatted summary string
        """
        summary = f"\n{'='*60}\n"
        summary += f"Export Summary\n"
        summary += f"{'='*60}\n"
        summary += f"Total leads exported: {len(leads)}\n"

        if leads:
            has_website = sum(1 for l in leads if l.get("website") != "N/A")
            avg_rating = sum(float(l.get("rating", 0)) for l in leads) / len(leads) if leads else 0
            has_phone = sum(1 for l in leads if l.get("phone") != "N/A")

            summary += f"Leads with website: {has_website}\n"
            summary += f"Leads with phone: {has_phone}\n"
            summary += f"Average rating: {avg_rating:.2f}\n"

        if export_paths:
            summary += f"\nFiles created:\n"
            for format_type, path in export_paths.items():
                if path:
                    summary += f"  - {format_type.upper()}: {path}\n"

        summary += f"{'='*60}\n"
        return summary
