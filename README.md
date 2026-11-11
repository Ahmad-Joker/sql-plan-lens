# SQL Plan Lens

Offline, read-only SQLite query-plan inspector. Reports table scans, indexed searches, and **heuristic** candidate indexes for simple equality predicates. It never runs the SELECT result query or modifies the input database.

## Install and run

```bash
python -m pip install -e .
python examples/make_fixture.py
sql-plan-lens --db examples/demo.sqlite --query 'SELECT * FROM orders WHERE customer_id = 7'
sql-plan-lens --db examples/demo.sqlite --query 'SELECT * FROM orders WHERE customer_id = 7' --json
python -m unittest discover -s tests -v
```

Requires Python >=3.10. No paid dependencies. Fixture data is synthetic.

## Safety and limitations

Conservatively accepts one SELECT only; rejects comments, semicolons, CTEs, parameters and dangerous keywords. Opens SQLite with mode=ro and an authorizer, and only executes EXPLAIN QUERY PLAN. This is not a general SQL parser or a security sandbox. SCAN may be optimal; index suggestions are unverified and not executed. No benchmark or claimed performance improvement.

## Evidence

Official employer examples (checked Nov 2026): [GE Vernova](https://careers.gevernova.com/software-engineering-intern/job/R5057006), [Kestrix](https://www.kestrix.io/careers/data-engineering-automation-intern), [Graphcore](https://job-boards.greenhouse.io/graphcore/jobs/8894376002). They support engineering skills, not demand for this exact tool. Existing competitor: [SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html).

See [master prompt](MASTER_PROMPT.md), [architecture](docs/architecture.md), [selection](docs/selection.md), [verification](docs/verification.md).
