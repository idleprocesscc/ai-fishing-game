# Changelog

Important changes are tracked here. The game remains deterministic within a version: same seed plus same command sequence gives reproducible results.

## 2026-07-03

### Changed

- Converted player-facing terminal, tool, blind-play, and documentation text to English.
- Added an English display layer for names, descriptions, ambience, event text, and help output while preserving gameplay ids, save fields, odds, and values.

### Compatibility

- Existing `fishing_save.json` structure is preserved.
- If an older save references a location that is no longer present in the current data set, the engine moves the active location to `Moonlit Pond` and keeps the rest of the save.

## Earlier Versions

Earlier releases added batch commands, status JSON, lucky events, diving, oxygen, map fragments, underwater encounters, major dive-site choices, and balance updates.
