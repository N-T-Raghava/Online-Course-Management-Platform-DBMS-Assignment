from sqlalchemy import text
from sqlalchemy.engine import Engine


def sync_postgres_serial_sequences(engine: Engine) -> None:
    """Find serial/nextval columns in public schema and set their sequences
    to the table MAX(column) to avoid duplicate-key errors after restores.

    This is safe to call at startup; it will silently skip columns
    without a sequence.
    """
    try:
        with engine.connect() as conn:
            serial_sql = text("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE column_default LIKE 'nextval(%' AND table_schema = 'public'
            """)
            rows = conn.execute(serial_sql).mappings().fetchall()
            if not rows:
                return

            for row in rows:
                table = row['table_name']
                column = row['column_name']
                seq_sql = text("SELECT pg_get_serial_sequence(:table, :column) AS seqname")
                seq_row = conn.execute(seq_sql, {"table": table, "column": column}).mappings().fetchone()
                seqname = seq_row['seqname'] if seq_row is not None else None
                if not seqname:
                    continue

                # Build a setval call that sets sequence to max(column) or 1
                setval_sql = text(
                    f"SELECT setval(:seqname, COALESCE((SELECT MAX({column}) FROM {table}), 1), true)"
                )
                try:
                    conn.execute(setval_sql, {"seqname": seqname})
                except Exception:
                    # ignore individual failures
                    continue
    except Exception:
        # Do not raise on startup; we prefer the app to continue running
        return
