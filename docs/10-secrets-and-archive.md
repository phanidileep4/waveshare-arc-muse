# Secrets, local archive and publication

The GitHub repository was initially private. The owner requested public visibility on November 6, 2026. Never commit credentials or personal flash dumps; `.local/` remains local and ignored regardless of repository visibility.

## Tracked

- Markdown guides, source pins, dependency lock and Arc-only overlays.
- Safe build/validation/upgrade helpers and meaningful safety tests.
- Historical artifact hashes, image sizes and sanitized acceptance evidence.
- This project's third-party/source attribution.

## Ignored and local only

`.local/` is restricted to the owner and ignored by Git. Its inventory links original inputs and contains private archive copies where useful:

- Whole-device Xiaozhi backups and official recovery image.
- Paired Muse NVS/OTA snapshot.
- Original text-mode and final live-voice binaries/packages, which embed the Muse SDK token.
- Generated SDK configuration and private raw logs.
- Battery HEIC/photo and prior screenshots when available.
- Deferred, unfinished OpenAI scaffold and dependency information.

The token's original file remains in place and is not copied into tracked files. The local inventory records its path without its value. No OpenAI key existed or was used. GitHub credentials remain in the user's system credential store; none are written here.

Private archive copies and the original project files are not replaced by Git. Keep a separate encrypted backup of `.local/` if migrating computers. The shareable source ZIP deliberately omits `.local/`, `.git/`, binaries and credentials.

## Before committing

Run `python3 scripts/check_repository.py`. It scans tracked/candidate project files for known credential patterns, forbidden artifacts and credential-bearing configuration assignments. It is defense in depth, not a complete DLP system. Review `git diff --cached` yourself. The repository's local pre-commit hook runs the same check.

The scripted build reads `ARC_SDK_TOKEN_FILE` from a file path, validates its shape and writes it only under `.local/build-live/sdkconfig`, mode 0600. Build output is captured in private local logs so build diagnostics cannot accidentally print a token into a shared terminal transcript.

## Hardware writes

Reading documentation, building and repository checks do not write Arc. The upgrade helper prints a plan unless all confirmation flags are provided. It requires an explicit expected MAC obtained from the actual intended device and confirmation of the exact 1.75C model; a generic S3 USB descriptor is insufficient. It backs up settings before writing. It has no whole-chip or NVS erase path.

The initial migration erase and full recovery writes are documented separately as deliberate destructive operations. The user's original request required explicit flash confirmation; that distinction should continue in future sessions.

## Maintenance

Update source pins only deliberately, retain the previously working artifact privately, and record whether a change was merely compiled or actually tested on hardware. Do not replace the historical manifests with hashes from a fresh build and imply those were the installed bytes.
