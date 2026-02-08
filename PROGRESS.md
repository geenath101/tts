# Progress Log

## Plan
1. Review UI and audio pipeline wiring.
2. Add start/stop playback controls and thread-safe stop handling.
3. Update UI to use selected PDF for audio generation.
4. Verify and summarize changes.

## Updates
- 2026-02-08: Added start/stop playback control hooks and audio stop signaling. Updated UI to start playback from the selected PDF.
- 2026-02-08: Updated UI imports to be module-safe when running via project root.
- 2026-02-08: Added standard logging configuration and replaced print statements with loggers.
- 2026-02-08: Logged the page index when starting audio playback.
- 2026-02-08: TTS now starts from the selected page (not from the beginning).
- 2026-02-08: Made stop/playback queue operations non-blocking to prevent UI freezes.
- 2026-02-08: Moved playback to a dedicated consumer thread with async start.
- 2026-02-08: Redesigned UI with header, sidebar controls, status, and file display.
