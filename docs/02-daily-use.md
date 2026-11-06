# Daily use and capabilities

## Buttons and voice

| Action | Result on this 1.75C build |
|---|---|
| Quick top-button click while awake | Start an experimental live voice call |
| Speak after the call starts | Hands-free input and spoken Muse replies |
| Click again | End the live call |
| Hold top button, speak, release | Voice note; reply is text/captions |
| Short click while asleep | May only wake Arc; retry once awake |

Leave your finger off the button while speaking in a hands-free call. A longer press selects the separate note path. In ordinary voice-note mode the official SDK intentionally paces captions with silence, even though log lines may say “audio.” A log such as `muse reply: 4.38s of audio` therefore does not by itself prove spoken content.

The owner's listening test and a call with **583 played audio frames, zero dropped/bad frames**, plus a confirmed end-call established actual spoken playback. This is the acceptance result, not merely a successful compile.

## Available now

- Live Muse conversations, voice notes and screen captions.
- Questions, explanations, brainstorming and writing assistance through the paired Muse account.
- Animated avatar and status UI on the 466 × 466 touch display.
- Screen brightness/sleep, speaker volume/mute and microphone gain controls.
- Wi-Fi reconnection and saved setup; the Mac is not the AI bridge for the installed Muse build.
- Image/display commands are compiled in, but not yet acceptance-tested in this session.
- The local-network tunnel/discovery feature is compiled in, but smart-home setup was not tested.

## Conditional or unverified

Muse account capabilities determine web research, memory, reminders, email, calendars and other connected services. These were not individually tested through Arc. The board does not independently gain access to those services merely by pairing.

If Arc uses an eero guest network, isolation can prevent discovery/control of devices on the main home network. This is relevant to a future local Mac bridge too.

Battery telemetry exists in the firmware, but a previous status query showed an unknown battery value before installation. Actual battery capacity, charging behavior, runtime and closed-case temperature have not been validated. Check [hardware notes](06-hardware-and-battery.md).

## Not enabled

- “Hey Arc” wake-word activation.
- Offline AI responses.
- OpenAI integration, custom persistent memory or custom agent tools.
- Phone-camera/video mode (`CONFIG_MUSE_VIDEO` is off).
- General-purpose external sensor/camera support merely because the board contains other chips.

## Suggested trial

Try short conversations, longer responses, waking from sleep, a Wi-Fi reconnection, mute/volume changes and battery use. Note failures with the exact on-screen message, gesture and whether captions or speech arrived. Don't publish transcripts or raw logs containing private information.

OpenAI was deferred while the owner experiences Muse for 3–5 days. No automatic reminder or migration was scheduled.
