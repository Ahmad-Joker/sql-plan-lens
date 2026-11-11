# MASTER PROMPT — SQL Plan Lens

Build a reproducible, local-first SQLite query-plan inspection CLI for junior backend and data engineers. Users supply a SQLite database and a SELECT query. Explain EXPLAIN QUERY PLAN output, flag full table scans, and suggest a candidate index based on simple equality predicates. Never modify the user's original database. Treat SQL as untrusted input and reject multiple statements, mutating operations, PRAGMA, ATTACH, EXPLAIN supplied by user, and ambiguous syntax; read-only connections and SQLite authorizer are defense in depth.

## Target users and MVP
Junior backend/data engineers learning query plans. Implement Python 3.10+ standard library, argparse CLI, sqlite3, unittest. Inputs: --db path, --query or --query-file, optional --json. Outputs: plan rows, scan/search findings, candidate index. No network, AI service, paid API, DDL execution, or actual query result execution. No benchmark or performance claim.

## Architecture and flow
CLI validates arguments -> core validates restricted SQL -> SQLite opens database mode=ro -> authorizer limits operations -> EXPLAIN QUERY PLAN -> parse SCAN/SEARCH rows -> simple WHERE equality candidate -> text/JSON report.

## User stories
As a developer I can inspect a SELECT plan without changing data; see scans and searches; obtain a clearly caveated index suggestion; export JSON for scripts; understand invalid input from a useful error.

## Implementation
1. Implement conservative validation, read-only connection, SQLite authorizer, plan inspection.
2. Add CLI text/JSON and query-file support.
3. Generate synthetic fixture.
4. Add tests for scans, indexed lookups, primary-key lookup, no predicate, unchanged DB, missing DB/table, rejected SQL, JSON, CLI error and query-file.
5. Add README, architecture, hiring sources, selection and limitations, CI.
6. Run install, compile, unittest and CLI end-to-end smoke; inspect failures, make smallest fix and rerun, with bounded retries.
7. Publish to dedicated Ahmad-Joker/sql-plan-lens branch feat/sql-plan-lens-mvp and open PR into main without merge.
8. Provide explanatory PDF covering what is actually implemented, hiring evidence, ranked ideas, architecture, sample, commands, tests, limitations, truthful CV bullet, verified GitHub links.

## Edge cases and errors
Missing files, malformed SQL, empty or oversized query, comments, semicolons, CTEs, parameters, dangerous keywords, unknown table, SQLite errors. Deliberately conservative parser can reject legitimate SELECTs and suggestions can be misleading for joins, quotes and complex expressions.

## Evidence
Official employer examples: https://careers.gevernova.com/software-engineering-intern/job/R5057006 ; https://www.kestrix.io/careers/data-engineering-automation-intern ; https://job-boards.greenhouse.io/graphcore/jobs/8894376002 . These support transferable engineering skills, not demand for this exact product.

## Honest completion
Only claim features verified in code/tests. Distinguish local test success from GitHub CI. Never claim benchmark improvements, deployed URL or merged PR.
