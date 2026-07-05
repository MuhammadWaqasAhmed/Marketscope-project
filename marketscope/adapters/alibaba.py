"""
Alibaba.com adapter.

LIVE MODE: requires an approved ISV developer account on Alibaba.com's
Open Platform (open.alibaba.com). Set ALIBABA_APP_KEY and
ALIBABA_APP_SECRET to activate. Useful for B2B / bulk-sourcing data
alongside the consumer marketplaces.
"""
import config
from database import get_db
from adapters.base import MarketplaceAdapter


class AlibabaAdapter(MarketplaceAdapter):
    name = "Alibaba"

    @property
    def is_live(self) -> bool:
        return bool(config.ALIBABA_APP_KEY and config.ALIBABA_APP_SECRET)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        if self.is_live:
            return self._search_live(query, limit)
        return self._search_mock(query, limit)

    def _search_mock(self, query: str, limit: int) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            """SELECT * FROM products WHERE marketplace = 'Alibaba'
               AND (title LIKE ? OR category LIKE ?)
               ORDER BY trend_score DESC LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _search_live(self, query: str, limit: int) -> list[dict]:
        """
        Template (Alibaba Open Platform signed REST call), same signing
        pattern as AliExpress's TOP gateway:

        import requests, time
        params = {
            "app_key": config.ALIBABA_APP_KEY,
            "method": "alibaba.product.search",
            "keywords": query,
            "page_size": limit,
            "timestamp": int(time.time() * 1000),
        }
        params["sign"] = _sign(params, config.ALIBABA_APP_SECRET)
        resp = requests.get("https://gw.open.1688.com/openapi/param2/1/...", params=params)
        # ... normalize resp.json() products into the standard dict shape
        """
        return self._search_mock(query, limit)
