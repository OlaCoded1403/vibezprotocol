# ================================================================
#  VIBEZ PROTOCOL — reset_admin_password.py
#  Set a new admin password directly against the configured database.
#
#  Usage (from backend/, venv active):
#      python reset_admin_password.py
#
#  The password is typed at a hidden prompt — it is never passed as an
#  argument, never printed, and never written to shell history.
#  Acts on whatever DATABASE_URL points at, so run it with the same .env
#  the app uses.
# ================================================================

import getpass
import os
import sys
import time

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.models import AdminUser
from app.utils import hash_password, verify_password

load_dotenv()

MIN_LENGTH = 10
BCRYPT_MAX_BYTES = 72  # bcrypt silently truncates beyond this


def fetch_admins(db, attempts: int = 3):
    """
    Read the admin rows, retrying a transient connection failure.

    Hosted databases resolve through DNS, and a flaky resolver produces
    "could not translate host name" errors that clear on their own. A raw
    traceback here is noise, not information.
    """
    for attempt in range(1, attempts + 1):
        try:
            return db.query(AdminUser).order_by(AdminUser.id).all()
        except OperationalError as exc:
            reason = str(exc.orig).strip().splitlines()[0] if exc.orig else str(exc)
            if attempt == attempts:
                print(f"\nCould not reach the database: {reason}")
                if "translate host name" in reason or "name resolution" in reason:
                    print("That is a DNS failure, not a database outage.")
                    print("Fix: run  ipconfig /flushdns  and try again.")
                sys.exit(1)
            print(f"  connection failed (attempt {attempt}/{attempts}), retrying...")
            db.rollback()
            time.sleep(2)


def main():
    url = os.getenv("DATABASE_URL", "").strip().strip('"').strip("'")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if not url:
        sys.exit("No DATABASE_URL set. Check backend/.env")

    engine = create_engine(url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)

    where = "SQLite (local file)" if url.startswith("sqlite") else f"PostgreSQL — {engine.url.host}"
    print(f"Database: {where}")

    with Session() as db:
        admins = fetch_admins(db)
        if not admins:
            sys.exit("No admin account exists. Use POST /api/auth/setup to create one.")

        print(f"\nAdmin account{'s' if len(admins) > 1 else ''} found:")
        for a in admins:
            print(f"  [{a.id}] {a.username}")

        if len(admins) == 1:
            admin = admins[0]
        else:
            choice = input("\nWhich id to reset? ").strip()
            admin = next((a for a in admins if str(a.id) == choice), None)
            if not admin:
                sys.exit("No account with that id.")

        print(f"\nSetting a new password for '{admin.username}'.")
        print("(nothing appears as you type — that is normal)\n")

        pw1 = getpass.getpass("New password: ")
        if len(pw1) < MIN_LENGTH:
            sys.exit(f"Too short — use at least {MIN_LENGTH} characters.")
        if len(pw1.encode("utf-8")) > BCRYPT_MAX_BYTES:
            sys.exit(f"Too long — bcrypt ignores anything past {BCRYPT_MAX_BYTES} bytes.")

        pw2 = getpass.getpass("Confirm password: ")
        if pw1 != pw2:
            sys.exit("Passwords did not match. Nothing changed.")

        admin.password_hash = hash_password(pw1)
        db.commit()

        # Prove the stored hash validates the password that was just typed.
        db.refresh(admin)
        if not verify_password(pw1, admin.password_hash):
            sys.exit("Stored hash failed verification — password NOT changed reliably.")

    print(f"\nPassword updated for '{admin.username}' and verified against the stored hash.")
    print("Log in at your /admin page with the new password.")


if __name__ == "__main__":
    main()
