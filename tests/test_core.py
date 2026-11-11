import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from sql_plan_lens.core import inspect, validate_query, LensError
from sql_plan_lens.cli import main

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'data.sqlite'
        with sqlite3.connect(self.db) as c:
            c.execute('CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER, amount INTEGER)')
            c.executemany('INSERT INTO orders(customer_id,amount) VALUES(?,?)', [(i % 10, i) for i in range(100)])
    def tearDown(self):
        self.tmp.cleanup()
    def test_scan(self):
        r = inspect(self.db, 'SELECT * FROM orders WHERE customer_id = 2')
        self.assertTrue(r['scans'])
        self.assertEqual(r['suggestions'][0]['column'], 'customer_id')
    def test_indexed(self):
        with sqlite3.connect(self.db) as c:
            c.execute('CREATE INDEX ix ON orders(customer_id)')
        r = inspect(self.db, 'SELECT * FROM orders WHERE customer_id = 2')
        self.assertTrue(r['searches'])
        self.assertFalse(r['scans'])
    def test_pk_search(self):
        self.assertTrue(inspect(self.db, 'SELECT * FROM orders WHERE id = 2')['searches'])
    def test_no_where(self):
        self.assertFalse(inspect(self.db, 'SELECT * FROM orders')['suggestions'])
    def test_original_unchanged(self):
        before = self.db.read_bytes()
        inspect(self.db, 'SELECT * FROM orders WHERE customer_id = 2')
        self.assertEqual(before, self.db.read_bytes())
    def test_missing_db(self):
        with self.assertRaises(LensError):
            inspect('/tmp/not-a-real-db-999.sqlite', 'SELECT 1')
    def test_bad_table(self):
        with self.assertRaises(LensError):
            inspect(self.db, 'SELECT * FROM nonexistent')
    def test_cli_json(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = main(['--db', str(self.db), '--query', 'SELECT * FROM orders', '--json'])
        self.assertEqual(rc, 0)
        self.assertIn('plan', json.loads(out.getvalue()))
    def test_cli_error(self):
        with contextlib.redirect_stderr(io.StringIO()):
            rc = main(['--db', str(self.db), '--query', 'DROP TABLE orders'])
        self.assertEqual(rc, 2)
    def test_query_file(self):
        q = Path(self.tmp.name) / 'query.sql'
        q.write_text('SELECT * FROM orders')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--db', str(self.db), '--query-file', str(q)]), 0)
    def test_reject_unsafe(self):
        for q in ['DELETE FROM orders', 'SELECT * FROM orders; DROP TABLE orders', 'SELECT 1 -- comment', 'WITH x AS (SELECT 1) SELECT * FROM x', 'SELECT * FROM orders WHERE id=?', 'PRAGMA table_info(orders)', 'SELECT 1 /* comment */', 'SELECT 1;', '', 'SELECT 1 FROM orders WHERE id=:id']:
            with self.subTest(q=q), self.assertRaises(LensError):
                validate_query(q)
    def test_empty_query(self):
        with self.assertRaises(LensError):
            validate_query(' ')
    def test_length(self):
        with self.assertRaises(LensError):
            validate_query('SELECT ' + ('a' * 10001))

if __name__ == '__main__':
    unittest.main()
