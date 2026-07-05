"""
AliExpress adapter.

LIVE MODE: requires an approved AliExpress Open Platform / dropshipping
API account (openservice.aliexpress.com). Set ALIEXPRESS_APP_KEY and
ALIEXPRESS_APP_SECRET to activate.
"""
import config
from database import get_db
from adapters.base import MarketplaceAdapter


class AliExpressAdapter(MarketplaceAdapter):
    name = "AliExpress"

    @property
    def is_live(self) -> bool:
        return bool(config.ALIEXPRESS_APP_KEY and config.ALIEXPRESS_APP_SECRET)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        if self.is_live:
            return self._search_live(query, limit)
        return self._search_mock(query, limit)

    def _search_mock(self, query: str, limit: int) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            """SELECT * FROM products WHERE marketplace = 'AliExpress'
               AND (title LIKE ? OR category LIKE ?)
               ORDER BY trend_score DESC LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _search_live(self, query: str, limit: int) -> list[dict]:
        """
        Template (aliexpress-sdk style signed REST call):

        import requests, time, hashlib
        params = {
            "app_key": config.ALIEXPRESS_APP_KEY,
            "method": "aliexpress.affiliate.product.query",
            "keywords": query,
            "page_size": limit,
            "timestamp": int(time.time() * 1000),
            "sign_method": "md5",
        }
        params["sign"] = _sign(params, config.ALIEXPRESS_APP_SECRET)
        resp = requests.get("https://api-sg.aliexpress.com/sync", params=params)
        # ... normalize resp.json() products into the standard dict shape
        """
        return self._search_mock(query, limit)
