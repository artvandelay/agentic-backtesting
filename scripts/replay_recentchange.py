#!/usr/bin/env python3
import argparse
import json
import os
import sys

import psycopg2
import psycopg2.extras


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay stored recentchange events")
    parser.add_argument("--dsn", default=os.getenv("POSTGRES_DSN", ""))
    parser.add_argument(
        "--start-id",
        type=int,
        default=0,
        help="Start from database id (default: 0).",
    )
    parser.add_argument("--limit", type=int, default=0, help="Limit number of events.")
    parser.add_argument(
        "--output",
        default="-",
        help="Output file path or '-' for stdout (default).",
    )
    return parser


def replay_events(dsn: str, start_id: int, limit: int, output: str) -> None:
    if not dsn:
        raise SystemExit("POSTGRES_DSN must be set")
    conn = psycopg2.connect(dsn)
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = "SELECT id, event FROM recentchange_events WHERE id > %s ORDER BY id"
        params = [start_id]
        if limit > 0:
            query += " LIMIT %s"
            params.append(limit)
        cursor.execute(query, params)
        stream = sys.stdout if output == "-" else open(output, "w", encoding="utf-8")
        with stream:
            for row in cursor:
                stream.write(json.dumps(row["event"]) + "\n")
    finally:
        conn.close()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    replay_events(args.dsn, args.start_id, args.limit, args.output)


if __name__ == "__main__":
    main()
