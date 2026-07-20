"""Download AppWorld's task data bundle and verify its integrity.

The appworld library version is pinned in the Dockerfile, but the data it uses
lives in a separate S3 object, so a build could otherwise pick up data other
than the release this eval was validated against. This downloads the bundle and
checks it against a pinned SHA-256; the Dockerfile unpacks it only if this
succeeds. Standard library only: it runs during the image build.
"""

import hashlib
import os
import sys
import urllib.request

BUNDLE_URL = "https://s3.us-west-2.amazonaws.com/appworld.dev/data-0.1.0.bundle"
BUNDLE_SHA256 = "fd9f9608c2ec71ed0ac25c3633a738b9129a318a129e31230425b9188e508250"


def sha256_of(file_path: str) -> str:
    digest = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(bundle_path: str) -> None:
    os.makedirs(os.path.dirname(bundle_path), exist_ok=True)

    print(f"Downloading {BUNDLE_URL}")
    urllib.request.urlretrieve(BUNDLE_URL, bundle_path)

    actual_sha256 = sha256_of(bundle_path)
    if actual_sha256 != BUNDLE_SHA256:
        os.remove(bundle_path)
        sys.exit(
            "AppWorld data bundle failed its integrity check.\n"
            f"  expected sha256: {BUNDLE_SHA256}\n"
            f"  actual sha256:   {actual_sha256}"
        )
    print(f"Verified sha256 {actual_sha256}")


if __name__ == "__main__":
    main(sys.argv[1])
