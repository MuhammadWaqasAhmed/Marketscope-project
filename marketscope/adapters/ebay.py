"""
eBay adapter.

LIVE MODE: register a free developer application at developer.ebay.com,
then generate an OAuth client credentials token for the Browse API
(GET /buy/browse/v1/item_summary/search). Set EBAY_CLIENT_ID and
EBAY_CLIENT_SECRET to activate.
"""
import config
from database import get_db
from adapters.base import MarketplaceAdapter


class EbayAdapter(MarketplaceAdapter):
    name = "eBay"

    @property
    def is_live(self) -> bool:
        return bool(config.EBAY_CLIENT_ID and config.EBAY_CLIENT_SECRET)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        if self.is_live:
            return self._search_live(query, limit)
        return self._search_mock(query, limit)

    def _search_mock(self, query: str, limit: int) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            """SELECT * FROM products WHERE marketplace = 'eBay'
               AND (title LIKE ? OR category LIKE ?)
               ORDER BY trend_score DESC LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _search_live(self, query: str, limit: int) -> list[dict]:
        """
        Template:

        import requests
        token = _get_oauth_token()  # client_credentials grant, cached + refreshed
        resp = requests.get(
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"q": query, "limit": limit},
        )
        items = resp.json().get("itemSummaries", [])
        # ... normalize each item into the standard dict shape
        """
        return self._search_mock(query, limit)
