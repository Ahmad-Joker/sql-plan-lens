"""Read-only query plan inspection; not a general SQL parser."""
import re
import sqlite3
from pathlib import Path

class LensError(ValueError):
    pass

START = re.compile(r'^\s*SELECT\b', re.I)
BLOCK = re.compile(r'\b(?:ATTACH|DETACH|PRAGMA|VACUUM|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|REPLACE|REINDEX|TRIGGER|WITH|EXPLAIN)\b', re.I)
FROM = re.compile(r'\bFROM\s+([A-Za-z_][A-Za-z_0-9]*)\b', re.I)
WHERE = re.compile(r'\bWHERE\s+(.+?)(?:\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|$)', re.I | re.S)
EQUAL = re.compile(r"\b([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(?:\d+(?:\.\d+)?|'[^']*')", re.I)

def validate_query(query):
    if not isinstance(query, str) or len(query) > 10000 or not START.match(query):
        raise LensError('Only a single SELECT statement (max 10000 characters) is supported')
    if ';' in query or '--' in query or '/*' in query or '*/' in query or BLOCK.search(query):
        raise LensError('Comments, semicolons, CTEs and potentially unsafe SQL are unsupported')
    if '?' in query or re.search(r':[A-Za-z_]', query):
        raise LensError('Parameterized queries are unsupported in this MVP')
    return query

def _authorize(action, arg1, arg2, dbname, source):
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY

def inspect(db_path, query):
    query = validate_query(query)
    path = Path(db_path)
    if not path.is_file():
        raise LensError(f'Database not found: {path}')
    try:
        con = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)
        try:
            con.set_authorizer(_authorize)
            rows = con.execute('EXPLAIN QUERY PLAN ' + query).fetchall()
        finally:
            con.close()
    except sqlite3.Error as exc:
        raise LensError(f'SQLite could not inspect the query: {exc}') from exc
    plan = [{'id':r[0], 'parent':r[1], 'detail':r[3]} for r in rows]
    scans = [r['detail'] for r in plan if re.search(r'\bSCAN\s+\w+', r['detail'], re.I)]
    searches = [r['detail'] for r in plan if 'SEARCH ' in r['detail'].upper()]
    suggestions = []
    table_match = FROM.search(query)
    where_match = WHERE.search(query)
    if scans and table_match and where_match:
        table = table_match.group(1)
        fields = [x for x in EQUAL.findall(where_match.group(1)) if x.lower() not in ('and','or')]
        if fields:
            field = fields[0]
            suggestions.append({'table':table,'column':field,'sql':f'CREATE INDEX idx_{table}_{field} ON {table}({field});', 'caveat':'Candidate only; verify schema, workload and index selectivity before applying'})
    return {'database':str(path),'query':query,'plan':plan,'scans':scans,'searches':searches,'suggestions':suggestions,'note':'SCAN can be optimal for small tables; EXPLAIN QUERY PLAN is an estimate, not a benchmark.'}
