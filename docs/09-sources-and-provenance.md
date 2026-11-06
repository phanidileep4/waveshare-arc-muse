# Sources and provenance

## Primary technical sources

| Source | Role |
|---|---|
| [Pinned Muse ESP32 README](https://github.com/facebookincubator/muse-gadget-sdk/blob/463bd2a05380fea4211b0099ad0f70933c108b20/esp32/README.md) | Toolchain, pairing, text-note behavior, experimental live calls |
| [Pinned Muse build/agent instructions](https://github.com/facebookincubator/muse-gadget-sdk/blob/463bd2a05380fea4211b0099ad0f70933c108b20/esp32/AGENTS.md) | Build, configuration, host tests, flash precautions |
| [Pinned board guide](https://github.com/facebookincubator/muse-gadget-sdk/blob/463bd2a05380fea4211b0099ad0f70933c108b20/esp32/devices/README.md) | Supported boards and feature matrix |
| [1.75C overlay](https://github.com/facebookincubator/muse-gadget-sdk/blob/463bd2a05380fea4211b0099ad0f70933c108b20/esp32/devices/sdkconfig.muse-waveshare-s3-175c) | Exact target, flash and PSRAM settings |
| [Pinned board driver](https://github.com/facebookincubator/muse-gadget-sdk/blob/463bd2a05380fea4211b0099ad0f70933c108b20/esp32/components/muse/boards/board_waveshare_s3_175c.c) | Display, codec and button mapping |
| [Muse Kconfig](https://github.com/facebookincubator/muse-gadget-sdk/blob/463bd2a05380fea4211b0099ad0f70933c108b20/esp32/components/muse/Kconfig) | Live voice and static-buffer option |
| [Muse linker fragment](https://github.com/facebookincubator/muse-gadget-sdk/blob/463bd2a05380fea4211b0099ad0f70933c108b20/esp32/components/muse/linker.lf) | Actual buffer placement into external RAM |
| [Muse chat session](https://github.com/facebookincubator/muse-gadget-sdk/blob/463bd2a05380fea4211b0099ad0f70933c108b20/esp32/components/muse/muse_chat_session.cpp) | Timed-silence note replies; VM connection errors |
| [Muse application](https://github.com/facebookincubator/muse-gadget-sdk/blob/463bd2a05380fea4211b0099ad0f70933c108b20/esp32/main/app.c) | VM lookup stack, pairing/Wi-Fi workflow |
| [ESP-IDF v6.0.3](https://github.com/espressif/esp-idf/tree/v6.0.3) | Exact toolchain and reason-code definitions |
| [ESP32-S3 specifications](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/product-overview.html) | 2.4 GHz Wi-Fi |
| [Wi-Fi station scenarios](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/wifi-driver/station-scenarios.html) | Authentication timeout interpretation; version may advance |
| [Vendor 1.75C documentation](https://docs.waveshare.com/ESP32-S3-Touch-AMOLED-1.75C) | Exact hardware and battery interface |
| [Waveshare recovery release](https://github.com/waveshareteam/ESP32-S3-Touch-AMOLED-1.75C/releases/tag/v1.0.1) | Factory recovery asset and digest |
| [eero band pause](https://eero.com/support/articles/how-do-i-temporarily-hide-the-5-and-6-ghz-bands) | Official 2.4 GHz setup troubleshooting |
| [eero encryption](https://eero.com/support/articles/what-is-wpa3) | Standard / Hybrid / Enhanced meanings |
| [eero guest network](https://www.eero.com/support/articles/how-do-i-share-my-eero-network-with-guests) | Guest setup |

## Conversation evidence

The owner supplied the earlier ChatGPT reference “Muse Gadgets Overview,” ID `6ac18130-e038-83e9-a54a-fd3a79610513`. Retrieval returned six final exchanges and three attached screenshots, with no older cursor. The text was reviewed for this record. Older unreturned conversation content is unavailable. The prior images are preserved only in the private archive; no new board/flasher conclusions were invented from unavailable earlier images.

The current working session supplied actual shell outputs, build artifacts, generated configurations, serial logs and user acceptance responses. This repository summarizes those outputs and preserves sanitized machine-readable manifests. Raw logs are kept locally because they can contain network names, server identifiers, transcripts and credentials.

## Evidence strength

- **Measured/observed:** file hashes, chip-reported flash, compilation, image validation, written-data verification, logged memory sizes, connection codes, HTTP 200 and audio-frame counters.
- **User confirmed:** final pairing success, microphone/text functionality, audible live speech, router model and selected WPA2 setting.
- **Source supported:** note-mode silence, short-tap behavior, internal stack size and PSRAM linker option.
- **Not isolated:** root cause of the original eero authentication/security failures and exact single intervention leading to Wi-Fi success.
- **Unverified:** battery capacity/fit/polarity/runtime, every possible Muse service feature, OpenAI integration and destructive recovery restoration.

Some earlier assistant explanations were corrected after reading code or actual logs. The final guide incorporates corrections; the chronology retains why they were necessary.
