# Changelog

## World Waters field edition — 2026-07

- Forked the MIT-licensed deterministic command architecture from
  `tutusagi/ai-fishing-game` and preserved attribution.
- Replaced all playable fantasy locations, species, treasure, bait, event, and
  dive content with an original real-world ecology field journal.
- Added English canonical data with Chinese-default narration.
- Added Colorado, Hokkaido, Cape, Amazon, Lake Baikal, and Mekong habitats.
- Added real species records with Latin names, bilingual science notes,
  identification marks, origin, and educational conservation flags.
- Added automatic photo-release rules for protected/research-only wildlife.
- Added corrective identification exercises and persistent misidentification
  counts rather than treating the first guess as automatically correct.
- Added deterministic local water conditions that alter activity weighting
  without consuming the game PRNG.
- Added genuine empty casts, local natural-object/debris pools, and cleanup
  records.
- Added safe migration that archives incompatible fantasy-era ids.
- Rebuilt the readable engine so no legacy fantasy tables remain embedded.
- Added formal data-integrity, migration, release, correction, and determinism
  tests.

The game remains reproducible within a version: identical seed and command
sequence produce identical output.
