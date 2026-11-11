# Architecture

CLI (argparse) -> validate_query -> sqlite3 mode=ro with authorizer -> EXPLAIN QUERY PLAN -> plan classification -> candidate index heuristic -> text or JSON.

Core: src/sql_plan_lens/core.py. CLI: src/sql_plan_lens/cli.py. Fixture: examples/make_fixture.py. Tests: tests/test_core.py.

Safety: restricted SELECT syntax, readonly URI, sqlite3 authorizer; original query results are never executed. Limitations: regex is not a full parser; not a security boundary for hostile databases; no timing benchmark; no automatic index application.
