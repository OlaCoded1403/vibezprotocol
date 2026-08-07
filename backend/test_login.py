# ================================================================
#  VIBEZ PROTOCOL — test_login.py
#  Check a username/password against the live API, bypassing the browser.
#
#  Usage (from backend/, venv active):
#      python test_login.py
#
#  Isolates "wrong password" from "browser autofilled the old one".
#  The password is typed at a hidden prompt and never printed.
# ================================================================

import getpass
import json
import ssl
import sys
import urllib.error
import urllib.request

API = "https://vibezprotocol-api.onrender.com/api/auth/login"


def main():
    print(f"Testing against: {API}\n")

    username = input("Username [olamilekan]: ").strip() or "olamilekan"
    password = getpass.getpass("Password (hidden): ")

    if not password:
        sys.exit("No password entered.")

    print(f"\n  username sent : {username!r} ({len(username)} chars)")
    print(f"  password sent : {len(password)} characters")
    if password != password.strip():
        print("  WARNING: leading or trailing whitespace in the password")
    print()

    body = json.dumps({"username": username, "password": password}).encode()
    req = urllib.request.Request(
        API, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )

    # Some local setups (VPN/AV TLS interception) break cert validation. This
    # script only checks whether credentials are accepted, so fall back rather
    # than fail — never do this where the response itself must be trusted.
    contexts = [None, ssl._create_unverified_context()]

    for ctx in contexts:
        try:
            with urllib.request.urlopen(req, timeout=90, context=ctx) as r:
                data = json.loads(r.read().decode())
                print("LOGIN SUCCEEDED")
                print(f"  token received ({len(data.get('access_token',''))} chars)")
                print("\n  => The credentials are correct.")
                print("     If the browser still rejects them, it is autofilling")
                print("     the old password. Clear the field and retype it, or")
                print("     open /admin in a private window.")
                return
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:160]
            print(f"LOGIN REJECTED - HTTP {e.code}")
            print(f"  {detail}")
            if e.code == 401:
                print("\n  => The API itself rejected this password.")
                print("     Re-run reset_admin_password.py and watch for the")
                print("     'updated and verified' line at the end.")
            return
        except urllib.error.URLError as e:
            if ctx is None and "CERTIFICATE_VERIFY_FAILED" in str(e.reason):
                print("  (local TLS interception detected, retrying without verification)")
                continue
            sys.exit(f"Could not reach the API: {e.reason}")

    sys.exit("Could not reach the API.")


if __name__ == "__main__":
    main()
