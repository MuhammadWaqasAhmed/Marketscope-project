"""
MarketScope configuration.

All real marketplace credentials are read from environment variables.
Until you set them, every adapter automatically runs in MOCK mode using
realistic generated data, so the whole app works end-to-end today.

To go live with a marketplace:
  1. Get approved/registered with that platform (see notes below).
  2. Set the matching environment variable(s).
  3. Restart the app. That adapter switches itself to LIVE mode -
     nothing else in the codebase needs to change.
"""
import os

SECRET_KEY = os.environ.get("MARKETSCOPE_SECRET_KEY", "dev-secret-change-me")
DB_PATH = os.environ.get("MARKETSCOPE_DB", os.path.join(os.path.dirname(__file__), "instance", "marketscope.db"))

# ---------------------------------------------------------------------------
# Marketplace credentials. Each platform's real signup process is noted so
# you know exactly what to go get.
# ---------------------------------------------------------------------------

# Amazon Product Advertising API - requires an approved Amazon Associates
# account with qualifying sales before they issue PA-API keys.
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_PARTNER_TAG = os.environ.get("AMAZON_PARTNER_TAG")

# eBay Browse API - register a free developer app at developer.ebay.com,
# then generate an OAuth application token.
EBAY_CLIENT_ID = os.environ.get("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.environ.get("EBAY_CLIENT_SECRET")

# AliExpress Open Platform (dropshipping API) - requires an approved
# AliExpress affiliate/dropship developer account at openservice.aliexpress.com.
ALIEXPRESS_APP_KEY = os.environ.get("ALIEXPRESS_APP_KEY")
ALIEXPRESS_APP_SECRET = os.environ.get("ALIEXPRESS_APP_SECRET")

# Alibaba.com Open Platform - requires an approved ISV developer account
# at open.alibaba.com.
ALIBABA_APP_KEY = os.environ.get("ALIBABA_APP_KEY")
ALIBABA_APP_SECRET = os.environ.get("ALIBABA_APP_SECRET")

# TikTok Shop Open/Partner API - requires an approved TikTok Shop Partner
# account at partner.tiktokshop.com.
TIKTOK_APP_KEY = os.environ.get("TIKTOK_APP_KEY")
TIKTOK_APP_SECRET = os.environ.get("TIKTOK_APP_SECRET")
TIKTOK_SHOP_ID = os.environ.get("TIKTOK_SHOP_ID")
