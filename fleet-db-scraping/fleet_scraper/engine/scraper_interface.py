# coding=utf-8

"""
    Scraper interface for all kinds of scrapers.

    Created:  Dmitrii Gusev, 02.05.2021
    Modified:
"""


SCRAPE_RESULT_OK = "Scraped OK!"


class ScraperInterface:
    """General data parser interface."""

    def scrap(self, cache_path: str, workers_count: int, dry_run: bool = False) -> str:
        """Scrap data from internet data source."""
        return SCRAPE_RESULT_OK
