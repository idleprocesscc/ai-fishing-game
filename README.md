# 🌍🎣 World Waters Field Journal

A deterministic, bilingual ecology game for AI players. Travel through real
aquatic habitats, cast a line, identify species from field marks, release
protected wildlife, record changing water conditions, and learn why each
organism belongs where it was found.

This project keeps the compact command engine and reproducible random model of
`tutusagi/ai-fishing-game`, but replaces its fantasy content with our own
real-world field-journal system.

## Language design

- **English is canonical** for ids, scientific names, research notes, and
  maintainable open-source data.
- **Chinese is the default player experience** for narration and concise
  science explanations.
- Species records retain both `*_en` and `*_zh` fields so a complete English
  interface can be added without rewriting the world database.

## Current world

The first field edition contains 9 habitats and 26 real species:

- Colorado Rocky Mountain headwaters and foothills reservoir
- Hokkaido forest river and rocky coast
- Cape Peninsula kelp forest and Cape offshore water
- Amazon flooded forest
- Lake Baikal littoral
- Mekong mainstem

Every location has its own debris/natural-object pool and deterministic water
conditions. Snowmelt, clear low water, flood pulses, tributary plumes,
upwelling, and current-mixing zones alter the activity weights of species
already present in the habitat; they never create impossible species.

## Field-journal mechanics

### Identification, including mistakes

Some newly observed species enter the journal as `pending`. Use:

```text
identify rainbow_trout
identify rainbow_trout 1
```

An incorrect answer is recorded as a corrected misidentification and explains
which field mark was unreliable. A correct answer verifies the entry. The
system emphasizes combinations of traits rather than color or body size alone.

### Conservation and release

Species marked `release_only` generate observation ids such as `obs_003`.
They award journal credit but never enter the sale inventory. This includes
protected or research-only encounters such as Colorado River cutthroat trout,
Mekong giant catfish, giant barb, Baikal sturgeon, and small golomyanka.

The game deliberately distinguishes broad educational conservation flags from
real fishing permission. It is not a substitute for current local regulations.

### Empty casts and unexpected objects

A cast can produce a fish, no bite, a natural object, or human debris. Object
pools are local: a Baikal amphipod molt, an Amazon fruit stone, discarded line,
a kelp holdfast, or an old glass-float fragment each tells a different habitat
story. Pulling up no fish is a valid field result.

### Dynamic water observations

```text
conditions
```

shows the current deterministic water/weather phase, its ecological
explanation, and the tags whose activity weights it changes. Conditions rotate
every four actions without consuming the game PRNG, so identical seeds and
commands remain reproducible.

## Commands

| Command | Purpose |
| --- | --- |
| `help` | Show the in-game command guide. |
| `status` | Show points, location, season, water condition, bait, and progress. |
| `conditions` | Explain the current water state and ecological weighting. |
| `shop` / `buy <bait_id> [qty]` | Inspect or buy field tackle. |
| `cast [bait_id] [N] [stop=...]` | Cast once or in a deterministic batch. |
| `goto` / `goto <location_id>` | List or travel to real habitats. |
| `inventory` / `sell ...` | Manage retainable catches; release-only observations never appear here. |
| `encyclopedia` | Show discovery and verification status. |
| `journal` | Show native/introduced counts, releases, and corrected mistakes. |
| `identify <fish_id> [choice]` | Study and verify an observed species. |
| `look <id>` | Read the bilingual name, Latin name, field marks, ecology, and conservation note. |

Commands may be batched with semicolons. `cast 10 stop=new,rare` is useful for
AI play because it saves context while stopping at meaningful observations.

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | Deterministic command engine and field-journal mechanics. |
| `real_world_data.py` | Readable bilingual habitats, species, objects, water conditions, and quizzes. |
| `fishing.py` | Generated single-file blind-play build for an AI player. |
| `build_blind.py` | Bundles the engine and data module into `fishing.py`. |
| `tool-schema.json` | Structured tool schema for an MCP/tool wrapper. |
| `test_real_world.py` | Data-integrity, release, correction, and determinism tests. |
| `SOURCES.md` | Research provenance and content policy. |

## Quick start

Python 3.8+ with no third-party dependencies:

```python
import engine

print(engine.new_game(2026))
print(engine.cmd("status"))
print(engine.cmd("conditions"))
print(engine.cmd("cast 10 stop=new"))
print(engine.cmd("journal"))
```

To let an AI discover content without reading tables, give it `fishing.py` and
ask it to use only `cmd()` and `new_game()`.

## Development

```bash
python -m unittest -v test_real_world.py
python build_blind.py
python -m py_compile engine.py real_world_data.py fishing.py
```

`fishing.py` is generated and should be rebuilt after any engine or world-data
change. Existing fantasy-version saves migrate to the Colorado headwaters while
compatible counters are retained.

## Attribution and license

Forked from [`tutusagi/ai-fishing-game`](https://github.com/tutusagi/ai-fishing-game).
The original architecture and this derivative are available under the MIT
License; see `LICENSE`. The original copyright notice is retained.
