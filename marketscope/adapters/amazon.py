"""
Amazon adapter.

LIVE MODE: requires an approved Amazon Associates account. Amazon then
issues PA-API 5.0 keys (access key, secret key, partner tag) for the
Product Advertising API. Apply at affiliate-program.amazon.com.

Until AMAZON_ACCESS_KEY / AMAZON_SECRET_KEY / AMAZON_PARTNER_TAG are set,
this adapter searches the local seeded dataset instead, filtered to rows
tagged "Amazon", so the rest of the app behaves exactly as it will once
real credentials are added.
"""
import config
from database import get_db
from adapters.base import MarketplaceAdapter


class AmazonAdapter(MarketplaceAdapter):
    name = "Amazon"

    @property
    def is_live(self) -> bool:
        return bool(config.AMAZON_ACCESS_KEY and config.AMAZON_SECRET_KEY and config.AMAZON_PARTNER_TAG)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        if self.is_live:
            return self._search_live(query, limit)
        return self._search_mock(query, limit)

    def _search_mock(self, query: str, limit: int) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            """SELECT * FROM products WHERE marketplace = 'Amazon'
               AND (title LIKE ? OR category LIKE ?)
               ORDER BY trend_score DESC LIMIT ?""",
            (f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _search_live(self, query: str, limit: int) -> list[dict]:
        """
        Template for the real call (uncomment + add the `paapi5-python-sdk`
        package once you have approved credentials):

        from paapi5_python_sdk.api.default_api import DefaultApi
        from paapi5_python_sdk.search_items_request import SearchItemsRequest

        api = DefaultApi(
            access_key=config.AMAZON_ACCESS_KEY,
            secret_key=config.AMAZON_SECRET_KEY,
            host="webservices.amazon.com",
            region="us-east-1",
        )
        req = SearchItemsRequest(
            partner_tag=config.AMAZON_PARTNER_TAG,
            partner_type="Associates",
            keywords=query,
            item_count=limit,
            resources=["ItemInfo.Title", "Offers.Listings.Price",
                       "CustomerReviews.StarRating", "CustomerReviews.Count"],
        )
        response = api.search_items(req)
        # ... normalize response.search_result.items into the standard dict shape
        """
        return self._search_mock(query, limit)
