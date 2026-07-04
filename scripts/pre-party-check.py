#!/usr/bin/env python3
"""Pre-party verification: smoke-test production and print a host checklist."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("SITE_URL", "https://cowboy-disco-party.vercel.app")

CHECKLIST = [
    f"Send invites: {BASE}/invite.html",
    f"Party kit: {BASE}/party-kit.html",
    f"Print pack: {BASE}/print-pack.html",
    f"Mobile test (cellular): {BASE}/mobile-test.html",
    "Post QR sign at the entrance",
    "Hang the Cowboy Disco Saloon sign on the door",
    f"Party night run-of-show: {BASE}/party-night.html",
    f"Open TV slideshow: {BASE}/slideshow.html",
    f"Host dashboard: {BASE}/host.html",
]


def main() -> int:
    print(f"Pre-party check for {BASE}\n")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "smoke-test.py")],
        env={**os.environ, "SITE_URL": BASE},
        check=False,
    )

    print("\nHost checklist:")
    for i, item in enumerate(CHECKLIST, 1):
        print(f"  {i}. {item}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
