"""SQLite persistence layer for MarketScope."""
import sqlite3
import random
import os
from datetime import datetime, timedelta

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    company TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS influencers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    primary_platform TEXT,
    handle TEXT,
    followers INTEGER DEFAULT 0,
    niche TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS influencer_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    influencer_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    handle TEXT NOT NULL,
    automation_goal TEXT,
    posting_frequency TEXT,
    ai_tone TEXT,
    auto_publish INTEGER DEFAULT 0,
    status TEXT DEFAULT 'connected',
    created_at TEXT NOT NULL,
    FOREIGN KEY (influencer_id) REFERENCES influencers (id)
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    marketplace TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT DEFAULT 'USD',
    rating REAL NOT NULL,
    num_reviews INTEGER NOT NULL,
    units_sold_30d INTEGER NOT NULL,
    trend_score REAL NOT NULL,
    country_code TEXT NOT NULL,
    accent TEXT NOT NULL,
    url TEXT
);

CREATE TABLE IF NOT EXISTS search_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    query TEXT NOT NULL,
    result_count INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
"""

MARKETPLACES = ["Amazon", "eBay", "TikTok Shop", "AliExpress", "Alibaba"]

COUNTRIES = [
    ("US", "United States", 39.8, -98.6), ("GB", "United Kingdom", 54.0, -2.0),
    ("DE", "Germany", 51.1, 10.4), ("FR", "France", 46.6, 2.2),
    ("CN", "China", 35.0, 103.8), ("JP", "Japan", 36.2, 138.2),
    ("KR", "South Korea", 36.5, 127.8), ("IN", "India", 21.1, 78.0),
    ("BR", "Brazil", -14.2, -51.9), ("MX", "Mexico", 23.6, -102.5),
    ("AU", "Australia", -25.3, 133.8), ("CA", "Canada", 56.1, -106.3),
    ("AE", "UAE", 23.4, 53.8), ("SA", "Saudi Arabia", 23.9, 45.1),
    ("PK", "Pakistan", 30.4, 69.3), ("ID", "Indonesia", -0.8, 113.9),
    ("NG", "Nigeria", 9.1, 8.7), ("ZA", "South Africa", -30.6, 22.9),
    ("ES", "Spain", 40.5, -3.7), ("IT", "Italy", 41.9, 12.6),
    ("NL", "Netherlands", 52.1, 5.3), ("PH", "Philippines", 12.9, 121.8),
    ("VN", "Vietnam", 14.1, 108.3), ("TR", "Turkey", 38.9, 35.2),
    ("PL", "Poland", 51.9, 19.1), ("TH", "Thailand", 15.9, 100.99),
]

CATEGORIES = [
    "Smart Home", "Beauty & Skincare", "Fitness Gear", "Phone Accessories",
    "Kitchen Gadgets", "Pet Supplies", "Outdoor & Camping", "Fashion Accessories",
    "Gaming Peripherals", "Baby Products", "Car Accessories", "LED & Lighting",
]

ADJ = ["Portable", "Wireless", "Mini", "Smart", "Foldable", "Rechargeable",
       "Adjustable", "Magnetic", "Ergonomic", "Eco-Friendly", "Multi-Function", "Pro"]
NOUN = ["Massager", "Diffuser", "Organizer", "Tracker", "Lamp", "Stand",
        "Charger", "Bottle", "Speaker", "Grip", "Cleaner", "Mount"]

ACCENTS = ["#22D3B8", "#FBBF24", "#60A5FA", "#F472B6", "#A78BFA"]


def get_db():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.commit()
    count = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
    if count == 0:
        _seed_products(conn)
    conn.close()


def _seed_products(conn):
    rows = []
    for _ in range(260):
        title = f"{random.choice(ADJ)} {random.choice(NOUN)}"
        category = random.choice(CATEGORIES)
        marketplace = random.choice(MARKETPLACES)
        country = random.choice(COUNTRIES)
        price = round(random.uniform(5, 120), 2)
        rating = round(random.uniform(3.4, 5.0), 1)
        reviews = random.randint(20, 18000)
        units = int(random.gammavariate(2, 800))
        trend = round(random.uniform(10, 99), 1)
        accent = random.choice(ACCENTS)
        rows.append((title, category, marketplace, price, "USD", rating,
                      reviews, units, trend, country[0], accent,
                      f"https://example.com/listing/{random.randint(100000,999999)}"))
    conn.executemany(
        """INSERT INTO products
           (title, category, marketplace, price, currency, rating, num_reviews,
            units_sold_30d, trend_score, country_code, accent, url)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", rows)
    conn.commit()


def country_lookup():
    return {c[0]: {"name": c[1], "lat": c[2], "lng": c[3]} for c in COUNTRIES}
