# Changelog

## Ecological Threads

- Expanded relationship cards into a typed node-and-edge evidence graph.
- Added clue, hypothesis, and confirmed stages driven by field observations.
- Added `threads`, `clues`, `connect`, and `webs` commands plus persistent
  correction history for unsupported relationship guesses.
- Migrated saves to version 3 while preserving all existing observations.

## World Waters field edition — 2026-07

- Forked the MIT-licensed deterministic command architecture from
  `tutusagi/ai-fishing-game` and preserved attribution.
- Replaced all playable fantasy locations, species, treasure, bait, event, and
  dive content with an original real-world ecology field journal.
- Added English canonical data with Chinese-default narration.
- Added persistent `language zh|en`; both interfaces cover every public
  command, science note, correction exercise, wildlife record, and ecological
  relationship. English-mode tests reject leaked CJK text.
- Added Colorado, Hokkaido, Cape, Amazon, Lake Baikal, and Mekong habitats.
- Added real species records with Latin names, bilingual science notes,
  identification marks, origin, and educational conservation flags.
- Added automatic photo-release rules for protected/research-only wildlife.
- Added corrective identification exercises and persistent misidentification
  counts rather than treating the first guess as automatically correct.
- Added three observation-depth levels and an evidence-gated ecological
  relationship journal spanning food webs, habitat, migration, and conservation.
- Added a travel passport with first-visit stamps and per-water survey totals.
- Expanded personal species records beyond maximum size to include first and
  minimum size, observed places, and observed day phases.
- Added six unlockable original campfire stories in a separate fiction table;
  they are explicitly disclaimed, have no Latin names, and never affect odds.
- Added deterministic local water conditions that alter activity weighting
  without consuming the game PRNG.
- Added a simulated dawn/day/dusk/night cycle with behavior-specific weighting;
  it advances through actions instead of requiring real-time waiting.
- Added 18 long-cycle ecological episodes that can alter activity, empty casts,
  objects, or wildlife across twelve-action environmental phases.
- Added genuine empty casts, local natural-object/debris pools, and cleanup
  records.
- Added 18 location- and season-aware wildlife observations covering birds,
  insects, plants, algae, invertebrates, seals, whales, and river dolphins;
  wildlife is explicitly never a catch target.
- Added safe migration that archives incompatible fantasy-era ids.
- Rebuilt the readable engine so no legacy fantasy tables remain embedded.
- Added formal data-integrity, migration, release, correction, and determinism
  tests.
- Expanded the encyclopedia from 26 to 100 real fish species and the map from 9
  to 17 habitats through a separately maintainable regional data module.
- Added Colorado River canyon, Florida mangrove estuary, Norwegian fjord, Lake
  Superior, Murray–Darling, Aotearoa South Island, Chesapeake Bay, and Monterey
  Bay kelp-forest routes.
- Added eight new corrective identification exercises for easily confused
  catfish, gadoids, pike, eels, drums, and flatfishes.

The game remains reproducible within a version: identical seed and command
sequence produce identical output.
