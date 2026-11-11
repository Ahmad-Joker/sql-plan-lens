"""Generate synthetic demo data, never real customer data."""
import sqlite3
from pathlib import Path
db = Path(__file__).with_name("demo.sqlite")
with sqlite3.connect(db) as conn:
    conn.execute("DROP TABLE IF EXISTS orders")
    conn.execute("CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, amount INTEGER)")
    conn.executemany("INSERT INTO orders(customer_id, amount) VALUES (?, ?)", [(i % 100, i * 3) for i in range(5000)])
print(db)
