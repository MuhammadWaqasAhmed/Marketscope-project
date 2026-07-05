from adapters.amazon import AmazonAdapter
from adapters.ebay import EbayAdapter
from adapters.aliexpress import AliExpressAdapter
from adapters.alibaba import AlibabaAdapter
from adapters.tiktok_shop import TikTokShopAdapter

ALL_ADAPTERS = [
    AmazonAdapter(), EbayAdapter(), AliExpressAdapter(),
    AlibabaAdapter(), TikTokShopAdapter(),
]


def aggregate_search(query: str, per_source_limit: int = 12) -> list[dict]:
    """Fan out a query to every marketplace adapter and merge results."""
    results = []
    for adapter in ALL_ADAPTERS:
        try:
            results.extend(adapter.search(query, per_source_limit))
        except Exception:
            continue
    results.sort(key=lambda p: p["trend_score"], reverse=True)
    return results


def live_status() -> dict:
    return {a.name: a.is_live for a in ALL_ADAPTERS}
