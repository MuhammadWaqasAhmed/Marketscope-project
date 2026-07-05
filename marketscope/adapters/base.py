"""
Base interface every marketplace adapter implements.

This is the seam where real APIs get plugged in later. Every adapter
exposes the same `search(query, limit)` -> list[dict] contract, so the
aggregator in app.py never needs to know whether it's talking to mock
data or a live marketplace.
"""
from abc import ABC, abstractmethod


class MarketplaceAdapter(ABC):
    name: str = "Unknown"

    @property
    @abstractmethod
    def is_live(self) -> bool:
        """True once real credentials are configured for this platform."""
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, limit: int = 20) -> list[dict]:
        """Return a list of normalized product dicts:
        {title, category, marketplace, price, currency, rating, num_reviews,
         units_sold_30d, trend_score, country_code, accent, url}
        """
        raise NotImplementedError
