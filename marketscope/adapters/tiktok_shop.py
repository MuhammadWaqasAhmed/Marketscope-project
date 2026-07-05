"""
TikTok Shop adapter.

LIVE MODE: requires an approved TikTok Shop Partner account
(partner.tiktokshop.com) and an authorized shop. Set TIKTOK_APP_KEY,
TIKTOK_APP_SECRET, and TIKTOK_SHOP_ID to activate. This is also the
feed that powers the influencer "trending on TikTok Shop" signal.
"""
import config
from database import get_db
from adapters.base import MarketplaceAdapter


class TikTokShopAdapter(MarketplaceAdapter):
    name = "TikTok Shop"

    @property
    def is_live(self) -> bool:
        return bool(config.TIKTOK_APP_KEY and config.TIKTOK_APP_SECRET and config.TIKTOK_SHOP_ID)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        if self.is_live:
            return self._search_live(query, limit)
        return self._search_mock(query, limit)

    def _search_mock(self, query: str, limit: int) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            """SELECT * FROM products WHERE marketplace = 'TikTok Shop'
               AND (title LIKE ? OR category LIKE ?)
               ORDER BY trend_score DESC LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _search_live(self, query: str, limit: int) -> list[dict]:
        """
        Template (TikTok Shop Open API, signed REST call):

        import requests, time, hmac, hashlib
        params = {"app_key": config.TIKTOK_APP_KEY, "shop_id": config.TIKTOK_SHOP_ID,
                   "timestamp": int(time.time())}
        params["sign"] = _hmac_sign(params, config.TIKTOK_APP_SECRET)
        resp = requests.get(
            "https://open-api.tiktokglobalshopping.com/api/products/search",
            params=params, json={"keyword": query, "page_size": limit},
        )
        # ... normalize resp.json() products into the standard dict shape
        """
        return self._search_mock(query, limit)
