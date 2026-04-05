"""
Lead Filters Module
Provides filtering functions for scraped leads data.
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class FilterManager:
    """Manages filtering operations on leads data."""

    @staticmethod
    def filter_no_website(leads: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Filter leads that have no website listed.
        
        Args:
            leads: List of lead dictionaries
            
        Returns:
            List of leads where website == "N/A"
        """
        filtered = [lead for lead in leads if lead.get("website", "N/A") == "N/A"]
        logger.info(f"Filtered to {len(filtered)} leads with no website (from {len(leads)} total)")
        return filtered

    @staticmethod
    def filter_by_rating(
        leads: List[Dict[str, any]],
        min_rating: float
    ) -> List[Dict[str, any]]:
        """
        Filter leads by minimum rating threshold.
        
        Args:
            leads: List of lead dictionaries
            min_rating: Minimum rating required (0-5)
            
        Returns:
            List of leads with rating >= min_rating
        """
        if not 0 <= min_rating <= 5:
            raise ValueError(f"Rating must be between 0 and 5, got {min_rating}")
        
        filtered = [
            lead for lead in leads
            if float(lead.get("rating", 0)) >= min_rating
        ]
        logger.info(
            f"Filtered to {len(filtered)} leads with rating >= {min_rating} "
            f"(from {len(leads)} total)"
        )
        return filtered

    @staticmethod
    def filter_by_category(
        leads: List[Dict[str, any]],
        category_keyword: str
    ) -> List[Dict[str, any]]:
        """
        Filter leads by category using case-insensitive matching.
        
        Args:
            leads: List of lead dictionaries
            category_keyword: Keyword to match in category field
            
        Returns:
            List of leads matching the category keyword
        """
        keyword_lower = category_keyword.lower()
        filtered = [
            lead for lead in leads
            if keyword_lower in lead.get("category", "").lower()
        ]
        logger.info(
            f"Filtered to {len(filtered)} leads matching category '{category_keyword}' "
            f"(from {len(leads)} total)"
        )
        return filtered

    @staticmethod
    def filter_by_name(
        leads: List[Dict[str, any]],
        name_keyword: str
    ) -> List[Dict[str, any]]:
        """
        Filter leads by business name using case-insensitive matching.
        
        Args:
            leads: List of lead dictionaries
            name_keyword: Keyword to match in business name
            
        Returns:
            List of leads matching the name keyword
        """
        keyword_lower = name_keyword.lower()
        filtered = [
            lead for lead in leads
            if keyword_lower in lead.get("name", "").lower()
        ]
        logger.info(
            f"Filtered to {len(filtered)} leads matching name '{name_keyword}' "
            f"(from {len(leads)} total)"
        )
        return filtered

    @staticmethod
    def filter_has_phone(leads: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Filter leads that have a phone number listed.
        
        Args:
            leads: List of lead dictionaries
            
        Returns:
            List of leads with phone != "N/A"
        """
        filtered = [lead for lead in leads if lead.get("phone", "N/A") != "N/A"]
        logger.info(f"Filtered to {len(filtered)} leads with phone number (from {len(leads)} total)")
        return filtered

    @staticmethod
    def apply_filters(
        leads: List[Dict[str, any]],
        **filter_kwargs
    ) -> List[Dict[str, any]]:
        """
        Apply multiple filters at once.
        
        Args:
            leads: List of lead dictionaries
            **filter_kwargs: Filter parameters
                - no_website: bool - Filter out leads with websites
                - min_rating: float - Minimum rating threshold
                - category: str - Category keyword filter
                - has_phone: bool - Filter for leads with phone numbers
                
        Returns:
            Filtered list of leads
        """
        filtered_leads = leads.copy()

        if filter_kwargs.get("no_website", False):
            filtered_leads = FilterManager.filter_no_website(filtered_leads)

        if "min_rating" in filter_kwargs:
            filtered_leads = FilterManager.filter_by_rating(
                filtered_leads,
                filter_kwargs["min_rating"]
            )

        if "category" in filter_kwargs:
            filtered_leads = FilterManager.filter_by_category(
                filtered_leads,
                filter_kwargs["category"]
            )

        if filter_kwargs.get("has_phone", False):
            filtered_leads = FilterManager.filter_has_phone(filtered_leads)

        return filtered_leads
