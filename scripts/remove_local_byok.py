"""Remove one local BYOK secret and its non-secret metadata."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sasteratech_runtime.local_control import CredentialUnavailable, WindowsKeyringCredentialStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--credential-id", required=True)
    args = parser.parse_args()
    store = WindowsKeyringCredentialStore(ROOT / "state" / "local_byok_metadata.db")
    try:
        store.delete(args.credential_id)
    except CredentialUnavailable:
        raise SystemExit("Credential was already absent; no change made.")
    finally:
        store.close()
    print("Credential deleted from Windows Credential Manager and local metadata.")


if __name__ == "__main__":
    main()
