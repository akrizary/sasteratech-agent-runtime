"""Enroll one local DeepSeek BYOK credential without echoing or writing its secret."""
from getpass import getpass
from pathlib import Path
import sys

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sasteratech_runtime.local_control import WindowsKeyringCredentialStore


def main() -> None:
    secret = getpass("DeepSeek API key (hidden input; not written to this project): ").strip()
    if not secret:
        raise SystemExit("No key entered; no credential was stored.")
    store = WindowsKeyringCredentialStore(ROOT / "state" / "local_byok_metadata.db")
    try:
        metadata = store.put("deepseek", secret)
    finally:
        # Drop this local Python reference before output.
        secret = ""
        store.close()
    print("Enrollment complete.")
    print(f"credential_id={metadata.credential_id}")
    print(f"provider={metadata.provider}")
    print(f"masked_suffix={metadata.masked_suffix}")
    print("Store credential_id for the one smoke command; do not store the raw key in shell variables or files.")


if __name__ == "__main__":
    main()
