# Filling the database with initial data

import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

schema = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sellers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    rating REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS listings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT NOT NULL,
    price        INTEGER NOT NULL,
    category_id  INTEGER NOT NULL,
    seller_id    INTEGER NOT NULL,
    location     TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    is_active    INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories (id),
    FOREIGN KEY (seller_id)   REFERENCES sellers (id)
);
"""


CATEGORIES = [
    "Electronics", "Automobiles", "Real Estate",
    "Clothing", "Home Appliances", "Mobile Phones",
]


SELLERS = [
    ("AsilBek Trade", "Toshkent", 4.8),
    ("Nodira Shop", "Samarqand", 4.5),
    ("TechHub UZ", "Toshkent", 4.9),
    ("Bekzod Market", "Andijon", 4.2),
    ("Malika Home", "Farg'ona", 4.6),
    ("GadgetPro", "Toshkent", 4.7),
    ("Fashionista", "Buxoro", 4.3),
]


# Make it in english and add more samples
LISTINGS = [
    # title, price, category, seller, location, created_at, is_active
    ("iPhone 14 Pro 256GB",        11_500_000, "Mobile Phones",     "TechHub UZ",     "Toshkent",  "2026-05-02", 1),
    ("Samsung Galaxy S23",          8_200_000, "Mobile Phones",     "GadgetPro",      "Toshkent",  "2026-05-10", 1),
    ("MacBook Air M2",             13_900_000, "Electronics",    "TechHub UZ",     "Toshkent",  "2026-04-28", 1),
    ("Chevrolet Cobalt 2021",     130_000_000, "Automobiles",   "Bekzod Market",  "Andijon",   "2026-03-15", 1),
    ("Chevrolet Nexia 3",          95_000_000, "Automobiles",   "Bekzod Market",  "Andijon",   "2026-06-01", 1),
    ("2 xonali kvartira, Chilonzor", 780_000_000, "Real Estate", "AsilBek Trade", "Toshkent", "2026-02-20", 1),
    ("3 xonali kvartira, Yunusobod", 950_000_000, "Real Estate", "AsilBek Trade", "Toshkent", "2026-06-05", 1),
    ("Erkaklar kostyumi",             450_000, "Clothing",   "Nodira Shop",    "Samarqand", "2026-05-22", 1),
    ("Ayollar ko'ylagi",               180_000, "Clothing",   "Malika Home",    "Farg'ona",  "2026-05-25", 1),
    ("Divan, yumshoq mebel",          3_200_000, "Home Appliances",  "Malika Home",    "Farg'ona",  "2026-04-10", 1),
    ("Muzlatgich Artel",              4_100_000, "Home Appliances",  "GadgetPro",      "Toshkent",  "2026-01-18", 1),
    ("Xiaomi Redmi Note 13",          2_900_000, "Mobile Phones",    "GadgetPro",      "Toshkent",  "2026-06-11", 1),
    ("Dell Inspiron noutbuk",         7_400_000, "Electronics",   "TechHub UZ",     "Toshkent",  "2026-03-30", 0),
    ("Lenovo IdeaPad",                6_100_000, "Electronics",   "TechHub UZ",     "Toshkent",  "2026-06-14", 1),
    ("Toyota Camry 2020",            250_000_000, "Automobiles",   "Bekzod Market",  "Andijon",   "2026-02-05", 1),
    ("Toyota Land Cruiser 2021",     450_000_000, "Automobiles",   "Bekzod Market",  "Andijon",   "2026-05-30", 1),
    ("4 xonali kvartira, Mirzo Ulug'bek", 1_200_000_000, "Real Estate", "AsilBek Trade", "Toshkent", "2026-04-15", 1),
]



def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(schema)

    cur.execute("DELETE FROM listings")
    cur.execute("DELETE FROM sellers")
    cur.execute("DELETE FROM categories")

    cat_ids = {}
    for name in CATEGORIES:
        cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        cat_ids[name] = cur.lastrowid

    seller_ids = {}
    for name, city, rating in SELLERS:
        cur.execute(
            "INSERT INTO sellers (name, city, rating) VALUES (?, ?, ?)",
            (name, city, rating),
        )
        seller_ids[name] = cur.lastrowid

    for title, price, cat, seller, location, created_at, is_active in LISTINGS:
        cur.execute(
            """INSERT INTO listings
                (title, price, category_id, seller_id, location, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, price, cat_ids[cat], seller_ids[seller], location, created_at, is_active),
        )

    conn.commit()
    conn.close()
    print(f"Database is ready: {DB_PATH}")
    print(f"   categories: {len(CATEGORIES)} ta")
    print(f"   sellers:    {len(SELLERS)} ta")
    print(f"   listings:   {len(LISTINGS)} ta")


if __name__ == "__main__":
    init_db()

