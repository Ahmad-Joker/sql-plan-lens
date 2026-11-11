import argparse
import json
import sys
from .core import inspect, LensError

def main(argv=None):
    p = argparse.ArgumentParser(description='Inspect SQLite SELECT query plans without modifying the database')
    p.add_argument('--db',required=True)
    q = p.add_mutually_exclusive_group(required=True)
    q.add_argument('--query')
    q.add_argument('--query-file')
    p.add_argument('--json',action='store_true',help='Emit machine-readable JSON')
    args = p.parse_args(argv)
    try:
        if args.query_file:
            with open(args.query_file,encoding='utf-8') as fh:
                query=fh.read()
        else:
            query=args.query
        result=inspect(args.db,query)
    except (LensError,OSError,UnicodeError) as exc:
        print(f'error: {exc}',file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result,indent=2))
    else:
        print('SQL Plan Lens')
        for item in result['plan']:
            print(' - '+item['detail'])
        print(f"Full scans: {len(result['scans'])}; indexed searches: {len(result['searches'])}")
        for s in result['suggestions']:
            print('Candidate index: '+s['sql'])
        print(result['note'])
    return 0

if __name__=='__main__':
    sys.exit(main())
