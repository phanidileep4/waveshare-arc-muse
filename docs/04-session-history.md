# Recorded chronology

Dates use America/Chicago. Logs contain device uptime and the host's local timestamps; exact wall-clock sequencing across midnight should not be inferred from filenames alone.

## Available prior ChatGPT conversation

Reference: “Muse Gadgets Overview,” conversation `6ac18130-e038-83e9-a54a-fd3a79610513`.

The retrieval service returned only six late exchanges and three image attachments, with no older-page cursor. They establish that:

- The Mac recognized native USB JTAG/serial on a `cu.usbmodem` port.
- A web install/erase page incorrectly showed ESP32-C5; installation was stopped.
- The offered Waveshare 1.85C was not the purchased 1.75C.
- The chosen recovery route was a manual official Muse build for 1.75C.
- A 16 MiB Xiaozhi file had a recorded SHA-256; factory recovery was moved into the original Arc folder.
- The next user request was to build Muse after recovery preparation.

Some previous assistant statements were premature: a matching serial port did not identify the board; the 16 MiB backup was not complete; the 1.75C could not simply be selected in the observed web-flasher UI. The later verification and manual build supersede those statements. Earlier original setup details are not available, and this repository does not invent a full verbatim transcript.

## November 5–6, 2026: verification and first Muse build

1. Found original recovery files and both 16 MiB and 32 MiB Xiaozhi backups on the Mac.
2. Recomputed hashes; confirmed the 32 MiB backup's first half matched the original and its upper half contained data.
3. Compared the factory image to official GitHub release asset size and SHA-256.
4. Queried the connected chip: ESP32-S3 rev 0.2, 32 MB flash, embedded 8 MB PSRAM. Secure Boot/encryption were off.
5. Compared all 32 MiB of the backup against device flash: digest matched.
6. Cloned official Muse and pinned IDF v6.0.3; installed Mac build prerequisites, compiler tools and Python packages.
7. Read the local Muse SDK token from the owner-specified private file without printing it; built exact 1.75C defaults.
8. First text-mode build succeeded with 48% of the 4 MiB application slot free. Image hash/checksum passed.
9. Ran the official host suite; resolved Mac host compatibility errors on focused reruns; recorded remaining skips.
10. Waited for explicit user confirmation before firmware writes.
11. Initialized only the new Muse NVS region for the Xiaozhi migration; wrote/verified the split images.
12. Boot reached 466 × 466 UI ready; audio codecs opened; BLE setup advertised. Wi-Fi/account pairing were still pending.

## Wi-Fi and account-pairing troubleshooting

The app appeared stuck on connecting. Serial inspection distinguished Bluetooth confirmation, Wi-Fi attempts, actual IP connection and account pairing. Auth timeout reason 2 and security compatibility reason 210 were observed. Band pausing, WPA2 checks, restart and guest-network attempts did not provide a single conclusive router fix. Device-side Wi-Fi eventually connected; completing the app's account setup afterward finished pairing. The owner then verified microphone input and written replies.

## Missing spoken replies and the OpenAI decision

Speaker enabled/volume 100 plus audible local tones suggested the speaker path could function. Source inspection showed the default note mode is deliberately text-only. An experimental live build was prepared and 122 targeted tests passed. The owner considered a fuller OpenAI implementation.

The initial OpenAI direction proposed a Mac service, secure server-side key and a USB first audio milestone to avoid guest-network isolation. A small scaffold and local Python dependencies were prepared; **no API key was supplied, no OpenAI API call was made, and no OpenAI firmware was compiled or installed**.

The owner then explicitly deferred OpenAI for 3–5 days and authorized the Muse voice update.

## Live voice deployment and final fix

1. Confirmed current Wi-Fi and pairing; privately backed up `0x11000..0x1efff` (NVS + OTA state, 56 KiB).
2. Installed the first live build without erasing NVS. Wi-Fi and pairing survived, but Muse chat/voice could not connect.
3. Diagnosed insufficient contiguous internal memory for the VM-lookup task.
4. Enabled the official `MUSE_STATIC_BUFFERS_IN_PSRAM` setting, rebuilt, verified the unchanged partition layout and installed the corrected live build under the same user-authorized update.
5. Startup created the VM task and connected Muse. No source patch was needed.
6. A held-button test still produced a note; gesture timing was explained.
7. A bounded test used a quick button event, accepted HTTP 200, reached live, completed responses, played 583 frames without drops/bad audio and ended with server confirmation.
8. The owner answered **“Yes, I heard Muse.”** This is the final audible-speech acceptance result.

## Physical assembly and battery discussion

The owner supplied an open-case photo. It showed the 1.75C Rev 1.1 board, BAT connector, speaker and a pouch battery with a white 3M release liner. The yellow tape must remain: it is insulation, not an adhesive liner. The cover was closed with the liner retained. No verified fit/polarity/charge-current measurements were supplied. Capacity was tentatively 500 mAh; runtime examples were conditional calculations, not measured battery life.

## Repository preservation

At the owner's request, this repository preserves reproducible source pins, final configuration, guides, troubleshooting and sanitized evidence. Personal binaries/dumps remain local. No new hardware writes are part of documenting the project.
