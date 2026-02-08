"""
Script to fix Postgres serial sequences after manual inserts or data restores.

Usage:
  python backend/scripts/fix_sequences.py

This script reads DATABASE_URL from the environment (same as the app),
finds all columns that use a `nextval(...)` default and sets their
associated sequence value to the current MAX(column) in the table so
future inserts won't conflict.
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print('DATABASE_URL not set in environment (.env). Aborting.')
    sys.exit(1)

engine = create_engine(DATABASE_URL)

def find_serial_columns(conn):
    sql = text("""
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE column_default LIKE 'nextval(%' AND table_schema = 'public'
    """)
    # use .mappings() so results are dict-like and addressable by column name
    return conn.execute(sql).mappings().fetchall()

def fix_sequence_for(conn, table, column):
    # Find sequence via pg_get_serial_sequence
    seq_sql = text("SELECT pg_get_serial_sequence(:table, :column) AS seqname")
    seq_row = conn.execute(seq_sql, {"table": table, "column": column}).mappings().fetchone()
    seqname = seq_row['seqname'] if seq_row is not None else None
    if not seqname:
        print(f'No sequence found for {table}.{column} — skipping')
        return False

    # Set sequence to max(column) or 1
    setval_sql = text(
        "SELECT setval(:seqname, COALESCE((SELECT MAX(" + column + ") FROM " + table + "), 1), true)"
    )

    try:
        conn.execute(setval_sql, {"seqname": seqname})
        print(f'Successfully set sequence {seqname} to table {table} max({column})')
        return True
    except Exception as e:
        print(f'Failed to set sequence for {table}.{column}: {e}')
        return False


def main():
    with engine.connect() as conn:
        serials = find_serial_columns(conn)
        if not serials:
            print('No serial columns found in public schema.')
            return

        for row in serials:
            table = row['table_name']
            column = row['column_name']
            print(f'Fixing sequence for {table}.{column}...')
            fix_sequence_for(conn, table, column)

if __name__ == '__main__':
    main()
