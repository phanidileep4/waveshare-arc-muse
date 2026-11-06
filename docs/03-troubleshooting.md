# Troubleshooting and findings

## Board/USB/recovery

| Symptom / discovery | Evidence and resolution |
|---|---|
| Web flasher showed ESP32-C5 | Wrong chip. The erase/install was stopped in the prior chat. |
| Web flasher offered Waveshare 1.85C | Different LCD/pin map. We built the 1.75C AMOLED source profile manually instead. |
| `/dev/cu.usbmodem101` appeared | This was native USB JTAG/serial. It proves a USB path, not the exact board model. Recheck after reconnecting. |
| 16 MiB backup existed | Its SHA matched the prior record, but the physical chip reported 32 MB. A complete 32 MiB backup was essential. |
| Full backup validation | First 16 MiB matched the original; upper half contained data. Whole-chip `verify-flash` returned “digest matched.” |
| Factory recovery slightly smaller than 32 MiB | Its exact size/hash matched Waveshare's official release asset; it is a factory image, not a whole-device dump. |
| New esptool rejected underscore/hyphen syntax | Original v4.13.0 used `flash_id`, `image_info`, `verify_flash`; v5.6.0 uses `flash-id`, `image-info`, `verify-flash`. Use the syntax for the selected version. |

## eero Pro 7 setup

The owner identified an eero Pro 7 gateway. ISP wording was ambiguous and is not needed to explain the verified radio behavior.

Observed sequence:

1. Muse app listed/added the device but appeared stuck after password submission.
2. Device-side status showed `wifi=no_network`, `paired=false`; Bluetooth was connected and setup had failed.
3. The assistant initially suggested that no network meant no connection attempt. **Correction:** this firmware saves the network after a successful join, so this status alone does not exclude an unsuccessful attempt.
4. A fresh setup showed `advertising → confirm → confirmed`; scans found 10–11 APs.
5. Connection logs then showed repeated **reason 2 (`AUTH_EXPIRE`)**. In the driver's connect flow this can mean an authentication response timed out. It did not prove an incorrect password.
6. Temporarily pausing eero's 5/6 GHz bands did not fix setup by itself. The owner confirmed 2.4 GHz security was already **Standard (WPA2)**.
7. Later attempts reported **reason 210 (`NO_AP_FOUND_W_COMPATIBLE_SECURITY`)**. This was the driver's result, not proof that eero was actually configured as WPA3-only. Reason 36 (`STA_LEAVING`) also appeared during connection teardown/retries.
8. Restarting Arc cleared temporary scan state but did not immediately solve reason 210.
9. A guest-network trial initially appeared unsuccessful in the app. Subsequent serial status twice showed actual Wi-Fi connected with an IP, RSSI around −60 dBm, while Muse still said “Ready to pair / Not set up.”
10. The owner explained that Wi-Fi had been configured directly on the Waveshare. **Device Wi-Fi connection and Muse account pairing are separate steps.** The app still needed the network password and completion of account pairing.
11. Finishing Muse app setup succeeded; microphone input and text responses worked.

**What we can conclude:** the radio and Wi-Fi association worked; app setup and account pairing were initially incomplete. We did not isolate a single router root cause, verify the final selected SSID in the published record, or establish that guest Wi-Fi was required. Do not tell future readers that pausing bands or guest mode definitively fixed this case.

Practical checks: inspect current state before changing settings; select a 2.4 GHz network; confirm pairing physically; submit the password privately in Muse; distinguish a real IP connection from app progress text. Leave existing WPA2 settings unchanged if already correct. See [eero's band-pause](https://eero.com/support/articles/how-do-i-temporarily-hide-the-5-and-6-ghz-bands) and [encryption](https://eero.com/support/articles/what-is-wpa3) guidance for current UI details.

## Microphone works, captions appear, speaker tones work, but no spoken reply

This was expected for the **default official voice-note mode**. Speaker was enabled at 100%; the SDK's `muse_chat_session.cpp::start_tts()` intentionally substitutes timed silence for speech. The assistant should have identified this before suggesting a spoken-reply acceptance test.

Resolution: enable `CONFIG_MUSE_REALTIME_VOICE=y` and use live calls. A separate text-to-speech integration could speak note replies, but it was not implemented. Raising volume cannot make intentionally absent speech audible.

## Live-voice build shows “Can't connect” / saves notes for later

The first live build preserved Wi-Fi and pairing and reached UI ready, but Muse's own chat/voice session could not connect. The main Link session was already up.

Evidence:

- `muse_chat_session: connect failed: Can't reach Muse's server` repeated.
- At a heartbeat, internal heap was about 18 KiB total with a largest block about **7 KiB**.
- `app_hatch_vm_credentials()` creates `muse_vm` with an **8192-byte internal stack** and returns false if task creation fails. Thus available contiguous memory was insufficient for that task. The connection error was misleadingly generic.
- A note was queued as “saved note, will try again”; this was consistent with the unavailable Muse session.

Fix: set **`CONFIG_MUSE_STATIC_BUFFERS_IN_PSRAM=y`**. This is an existing SDK linker option for avatar/audio zero-initialized buffers; no official source was modified. The final build booted with **33,215 bytes free internal heap**, created the VM task and connected the Muse subscription. A later boot log showed a different instantaneous free-heap value; treat heap snapshots as observations, not guarantees.

## Live build still gives a text reply

Gesture selects the path. A logged button press lasted **2.593 seconds** and produced a voice note. A quick controlled **80 ms** press/release while awake started `/voice/realtime`, returned **HTTP 200**, reached live state, produced responses and played real audio. The owner confirmed hearing Muse.

- Wake the screen first.
- Click/release quickly; don't hold while talking.
- Wait for live listening, speak hands-free, click again to end.
- Note mode remains text-only. It is not a speaker regression.

## Mac host tests

Initial official suite: **1,015 tests run; 1 failure, 2 class setup errors, 3 skips**. The two setup errors excluded their class test bodies from execution.

| Failure | Host-only correction | Focused rerun |
|---|---|---|
| StopWatch PTT harness: Linux `-no-pie` / linker options | Remove `-no-pie`; translate `-Wl,--gc-sections` to Darwin `-Wl,-dead_strip` | 42 passed |
| Voice PE harness: cJSON `sprintf` deprecation treated as error | Permit deprecated-declarations warnings on the host | Voice-call module: 80 passed |
| Simulator incremental avatar selection | Use Ninja rather than default host generator | 3 passed |

The adapter is [scripts/mac-host-cc.py](../scripts/mac-host-cc.py). It is for host tests only, never the Xtensa compiler. All three affected groups passed. The entire initial suite was not rerun after these targeted fixes, and the original three skipped checks remain unverified. For the live feature build, the 80 voice and 42 PTT tests passed again. No firmware source patch was needed.

## Nonfatal boot messages

“GPIO ISR service already installed,” display-init overrides, touch gesture recognition disabled, and I2S full-duplex master/slave notices appeared. Startup continued through touch resolution, UI up and codec open. We did not claim these warnings were eliminated. Check for actual panics/reboot loops or failure to reach ready before treating a warning as the root cause.

## Battery placement / runtime

The capacity was reported as “looks like 500 mAh” and was not independently confirmed. The case was described as closed tightly with adhesive liner retained. Corrected guidance: no pressure on the pouch, no pinched wires, no movement, and no contact with sharp/exposed metal. A photo does not prove clearance, safe polarity, healthy battery or charge-current compatibility. See [battery notes](06-hardware-and-battery.md).
