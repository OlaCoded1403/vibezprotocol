# ================================================================
#  VIBEZ PROTOCOL — migrate_to_postgres.py
#  One-off: copy local SQLite data into a hosted PostgreSQL database.
#
#  Usage (from backend/, venv active):
#    python migrate_to_postgres.py --dry-run
#    python migrate_to_postgres.py --target "postgresql://user:pass@host/db?sslmode=require"
#
#  Reads the target from --target, else $TARGET_DATABASE_URL, else $DATABASE_URL.
#  Safe to re-read: refuses to run if the target already holds rows (--force
#  wipes the target tables first).
# ================================================================

import argparse
import os
import socket
import sys

for _stream in (sys.stdout, sys.stderr):  # emoji-safe on Windows cp1252 consoles
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import AdminUser, Inquiry, Project

load_dotenv()

# Order matters only if FKs are ever added; kept explicit for clarity.
TABLES = [Inquiry, Project, AdminUser]


def force_ipv4():
    """
    Some Windows machines fail an AF_UNSPEC getaddrinfo when a host publishes both
    A and AAAA records but has no working IPv6 route — the failing v6 leg takes the
    whole lookup down instead of falling back to v4. Pin lookups to IPv4.
    Local workaround only; Linux hosts (Render et al.) resolve these fine.
    """
    original = socket.getaddrinfo

    def ipv4_only(host, port, family=0, *args, **kwargs):
        return original(host, port, socket.AF_INET, *args, **kwargs)

    socket.getaddrinfo = ipv4_only


def resolve_target(cli_value: str | None) -> str:
    url = cli_value or os.getenv("TARGET_DATABASE_URL") or os.getenv("DATABASE_URL", "")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if not url:
        sys.exit("❌ No target URL. Pass --target or set TARGET_DATABASE_URL in .env")
    if not url.startswith("postgresql://"):
        sys.exit(f"❌ Target must be a postgresql:// URL, got: {url.split('://')[0]}://")
    return url


def reset_sequences(session):
    """
    Rows are inserted with their original ids, which leaves each table's identity
    sequence at 1 — the next insert would collide on the primary key. Fast-forward
    every sequence past the highest id we just wrote.
    """
    for model in TABLES:
        table = model.__tablename__
        # The third setval arg is is_called: with rows present the sequence is
        # "already used" so nextval returns max+1; on an empty table we pass false
        # so the first insert still gets id 1 rather than skipping to 2.
        session.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1), "
                f"(SELECT COUNT(*) FROM {table}) > 0)"
            )
        )
    session.commit()


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite data to PostgreSQL.")
    parser.add_argument("--target", help="postgresql:// URL of the destination database")
    parser.add_argument("--source", default="sqlite:///./vibezprotocol.db", help="source SQLite URL")
    parser.add_argument("--dry-run", action="store_true", help="report what would move, change nothing")
    parser.add_argument("--force", action="store_true", help="DELETE existing rows in the target first")
    parser.add_argument(
        "--ipv4",
        action="store_true",
        help="pin DNS to IPv4 (fixes 'could not translate host name' on Windows dual-stack)",
    )
    args = parser.parse_args()

    if args.ipv4:
        force_ipv4()

    target_url = resolve_target(args.target)

    src_engine = create_engine(args.source, connect_args={"check_same_thread": False})
    dst_engine = create_engine(target_url, pool_pre_ping=True)

    SrcSession = sessionmaker(bind=src_engine)
    DstSession = sessionmaker(bind=dst_engine)

    # Redact credentials before showing the host.
    print(f"📤 Source: {args.source}")
    print(f"📥 Target: {dst_engine.url.host}/{dst_engine.url.database}")

    with SrcSession() as src:
        counts = {m.__tablename__: src.query(m).count() for m in TABLES}
    print("   Rows to copy: " + ", ".join(f"{t}={n}" for t, n in counts.items()))

    if args.dry_run:
        print("✅ Dry run — nothing written.")
        return

    print("🔨 Creating tables on target (no-op if they exist)...")
    Base.metadata.create_all(bind=dst_engine)

    with DstSession() as dst:
        existing = {m.__tablename__: dst.query(m).count() for m in TABLES}
        if any(existing.values()):
            if not args.force:
                sys.exit(
                    f"❌ Target is not empty ({existing}). "
                    "Re-run with --force to wipe those tables first."
                )
            print(f"⚠️  --force: deleting existing target rows {existing}")
            for model in reversed(TABLES):
                dst.query(model).delete()
            dst.commit()

    for model in TABLES:
        with SrcSession() as src, DstSession() as dst:
            rows = src.query(model).all()
            for row in rows:
                # Copy mapped columns only, preserving id and created_at.
                data = {c.name: getattr(row, c.name) for c in model.__table__.columns}
                dst.add(model(**data))
            dst.commit()
            print(f"   ✅ {model.__tablename__}: {len(rows)} rows copied")

    with DstSession() as dst:
        reset_sequences(dst)
        print("   ✅ id sequences fast-forwarded")

        final = {m.__tablename__: dst.query(m).count() for m in TABLES}

    print(f"🎉 Done. Target now holds: {final}")
    if final != counts:
        sys.exit(f"⚠️  Count mismatch — expected {counts}, got {final}")


if __name__ == "__main__":
    main()
