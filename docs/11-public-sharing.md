# Public sharing and repository name

On November 6, 2026, the owner requested renaming `arc-companion` to `waveshare-arc-muse` and changing visibility from private to public.

## Benefits

The setup can be linked without invitations, other owners can reproduce the working configuration, and the community can contribute corrections and improvements.

## Tradeoffs

- The committed guides and history are visible to everyone. They describe the board, router model, project timeline, troubleshooting decisions and available prior-chat context.
- Anyone can read, clone and fork the repository. Making the repository private later does not retract copies or make existing public forks private.
- Future commits need the same care as today's publication. Raw serial logs, generated sdkconfig files, token-bearing binaries and flash/NVS dumps remain excluded.
- No open-source license has been selected for original project material. Public visibility is not a substitute for an explicit reuse license. Upstream Muse, ESP-IDF, vendor and asset licenses are unchanged.

## Publication check

The repository has no committed credentials, personal device MAC/IP addresses, absolute personal filesystem paths, firmware binaries, raw logs or photographs. The private archive is ignored and was not pushed. The existing secret-pattern check and commit hook remain enabled locally. This is a targeted review, not a guarantee that every possible sensitive string can be recognized automatically.

GitHub reference: [visibility consequences](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility).
