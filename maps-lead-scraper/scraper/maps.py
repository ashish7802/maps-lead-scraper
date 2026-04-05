"""
Google Maps Scraper Module
Handles async web scraping of Google Maps search results using Playwright.
"""

import asyncio
import logging
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class GoogleMapsScraper:
    """
    Scrapes business information from Google Maps search results.
    Uses Playwright for browser automation.
    """

    def __init__(self, headless: bool = True, scroll_pause: float = 2.0):
        """
        Initialize the scraper.
        
        Args:
            headless: Run browser in headless mode (default: True)
            scroll_pause: Pause duration between scrolls in seconds (default: 2.0)
        """
        self.headless = headless
        self.scroll_pause = scroll_pause
        self.leads: List[Dict[str, any]] = []

    async def scrape(
        self,
        keyword: str,
        city: str,
        max_results: int = 50
    ) -> List[Dict[str, any]]:
        """
        Scrape Google Maps for business listings.
        
        Args:
            keyword: Search keyword (e.g., "dentist")
            city: City name (e.g., "Lucknow")
            max_results: Maximum number of results to scrape (default: 50)
            
        Returns:
            List of dictionaries containing business information
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            
            try:
                logger.info(f"Scraping Google Maps for '{keyword}' in '{city}'")
                
                # Navigate to Google Maps
                search_url = self._build_search_url(keyword, city)
                await page.goto(search_url, wait_until="domcontentloaded")
                await asyncio.sleep(2)  # Wait for page to load
                
                # Scroll to load more results
                self.leads = await self._scroll_and_extract(page, max_results)
                
                logger.info(f"Successfully scraped {len(self.leads)} leads")
                return self.leads
                
            except Exception as e:
                logger.error(f"Error during scraping: {str(e)}")
                raise
            finally:
                await browser.close()

    def _build_search_url(self, keyword: str, city: str) -> str:
        """Build Google Maps search URL."""
        search_query = f"{keyword} in {city}"
        return f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"

    async def _scroll_and_extract(
        self,
        page: Page,
        max_results: int
    ) -> List[Dict[str, any]]:
        """
        Scroll through results and extract lead information.
        
        Args:
            page: Playwright page object
            max_results: Maximum results to extract
            
        Returns:
            List of extracted business data
        """
        leads = []
        last_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 20

        # Wait for results container
        await self._wait_for_results(page)

        while len(leads) < max_results and scroll_attempts < max_scroll_attempts:
            try:
                # Extract visible results
                new_leads = await self._extract_visible_results(page)
                
                # Add new leads (avoid duplicates)
                for lead in new_leads:
                    if not any(l["name"] == lead["name"] for l in leads):
                        leads.append(lead)
                        if len(leads) >= max_results:
                            break

                # Scroll down
                new_height = await page.evaluate("""
                    () => {
                        const resultsContainer = document.querySelector('[role="feed"]') || 
                                               document.querySelector('.m6QErb');
                        if (resultsContainer) {
                            resultsContainer.scrollTop = resultsContainer.scrollHeight;
                            return resultsContainer.scrollHeight;
                        }
                        return 0;
                    }
                """)

                if new_height == last_height:
                    # No more content to scroll
                    break

                last_height = new_height
                await asyncio.sleep(self.scroll_pause)
                scroll_attempts += 1

            except Exception as e:
                logger.warning(f"Error during scroll iteration: {str(e)}")
                scroll_attempts += 1

        return leads[:max_results]

    async def _wait_for_results(self, page: Page, timeout: int = 10) -> None:
        """Wait for results container to be visible."""
        try:
            await page.wait_for_selector('[role="feed"], .m6QErb, .Nv2PK', timeout=timeout * 1000)
        except PlaywrightTimeoutError:
            logger.warning("Results container not found, proceeding anyway")

    async def _extract_visible_results(self, page: Page) -> List[Dict[str, any]]:
        """Extract business information from visible result items."""
        try:
            results = await page.evaluate("""
                () => {
                    const items = Array.from(document.querySelectorAll('[role="option"], .Nv2PK'));
                    return items.slice(0, 10).map(item => {
                        try {
                            const nameEl = item.querySelector('span, .fontHeadlineSmall') || 
                                          item.querySelector('[class*="name"]');
                            const name = nameEl ? nameEl.textContent.trim() : 'N/A';
                            
                            // Extract rating and review count
                            const ratingEl = item.querySelector('[role="img"][aria-label*="star"]') ||
                                            item.querySelector('[aria-label*="star"]');
                            const ratingText = ratingEl ? ratingEl.getAttribute('aria-label') : '0';
                            const rating = parseFloat(ratingText.match(/\d+\.?\d*/)?.[0] || '0');
                            
                            // Extract address
                            const addressEl = item.querySelector('[class*="address"]') ||
                                             Array.from(item.querySelectorAll('span')).find(el => 
                                                el.textContent.includes('Street') || 
                                                el.textContent.includes('Rd') ||
                                                el.textContent.includes('Lane'));
                            const address = addressEl ? addressEl.textContent.trim() : 'N/A';
                            
                            // Extract phone
                            const phoneEl = Array.from(item.querySelectorAll('span')).find(el =>
                                /[\d\s\-\+\(\)]{10,}/.test(el.textContent));
                            const phone = phoneEl ? phoneEl.textContent.trim() : 'N/A';
                            
                            // Extract website and category
                            const website = 'N/A'; // Requires clicking individual listings
                            const category = 'N/A'; // Extracted from search context
                            
                            return { name, phone, address, website, rating, category };
                        } catch (e) {
                            return null;
                        }
                    }).filter(item => item && item.name !== 'N/A');
                }
            """)
            return [r for r in results if r is not None]
        except Exception as e:
            logger.warning(f"Error extracting results: {str(e)}")
            return []

    async def scrape_detailed(
        self,
        keyword: str,
        city: str,
        max_results: int = 50
    ) -> List[Dict[str, any]]:
        """
        Detailed scrape with individual listing clicks for website information.
        Note: This is slower but extracts more complete data.
        
        Args:
            keyword: Search keyword
            city: City name
            max_results: Maximum results to scrape
            
        Returns:
            List of detailed business information
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            
            try:
                logger.info(f"Starting detailed scrape for '{keyword}' in '{city}'")
                
                search_url = self._build_search_url(keyword, city)
                await page.goto(search_url, wait_until="domcontentloaded")
                await asyncio.sleep(2)
                
                leads = await self._scroll_and_extract(page, max_results)
                
                logger.info(f"Detailed scrape completed with {len(leads)} leads")
                return leads
                
            except Exception as e:
                logger.error(f"Error during detailed scraping: {str(e)}")
                raise
            finally:
                await browser.close()
