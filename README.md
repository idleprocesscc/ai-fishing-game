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
- **English is also a complete playable interface.** Use `language en` or
  `language zh`; the choice persists in the JSON save. Automated coverage runs
  the entire public English command surface and rejects any leaked CJK text.

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

An eight-action field day cycles through dawn, day, dusk, and night. Each phase
lasts two actions and modestly changes tagged behaviors such as low-light,
nocturnal, daylight, or vertical-migration activity. Time is simulated rather
than tied to the player's clock, so nobody has to wait until real midnight.

Longer ecological episodes rotate every twelve actions. Insect emergence,
migration windows, persistent swell, upwelling pulses, flooded-forest
connection, littoral warming, and dry-season fragmentation can alter empty-cast,
object, wildlife, or behavior-tag weights. They are directional ecological
pressures rather than scripted guarantees.

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

### Observation depth and ecological relationships

Repeated encounters progress from `First observation` to `Familiar` and then
`Studied`. The second and third records award small observation bonuses. They
also provide the evidence needed to unlock relationships through:

```text
ecosystem
```

The relationship journal connects species to flooded-forest fruit, kelp
architecture, cold pelagic food webs, migration corridors, slow life histories,
community conservation, and river connectivity. Locked relationships reveal no
species answer list; the player must gather repeated observations first.

### Travel passport and personal records

`passport` awards a field stamp on first arrival and keeps per-water totals for
visits, casts, observed species, wildlife, empty casts, objects, and debris
cleanup. Species pages remember the first measured size, minimum and maximum,
locations observed, and day phases observed. A tiny first fish or a species
seen across several habitats can therefore be as meaningful as a size record.

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

### Wildlife is observed, never caught

Some casts pause for a separate `🔭` observation: a dipper, mayfly nymph,
Steller's sea eagle, kelp holdfast community, Baikal seal, Irrawaddy dolphin,
or another organism associated with that habitat and season. These records
never enter the creel. The game explicitly instructs the observer not to
approach, feed, or capture wildlife. Once seen, a record can be revisited with
`look <wildlife_id>` and appears in the non-fish section of `journal`.

### Dynamic water observations

```text
conditions
```

shows the current deterministic water/weather phase and time of day, their
ecological explanations, and the tags whose activity weights they change.
Ecological episodes rotate every twelve actions, water every four, and time
every two, without consuming the game PRNG, so identical seeds and commands
remain reproducible.

## Commands

| Command | Purpose |
| --- | --- |
| `language zh\|en` | Persistently switch the complete Chinese or English interface. |
| `help` | Show the in-game command guide. |
| `status` | Show points, location, season, water condition, bait, and progress. |
| `conditions` | Explain the current water state and ecological weighting. |
| `shop` / `buy <bait_id> [qty]` | Inspect or buy field tackle. |
| `cast [bait_id] [N] [stop=...]` | Cast once or in a deterministic batch. |
| `goto` / `goto <location_id>` | List or travel to real habitats. |
| `passport` | Show location stamps, first visits, and per-water survey statistics. |
| `inventory` / `sell ...` | Manage retainable catches; release-only observations never appear here. |
| `encyclopedia` | Show discovery and verification status. |
| `journal` | Show native/introduced counts, releases, wildlife, non-fish finds, and corrected mistakes. |
| `ecosystem` | Show food-web, habitat, migration, and conservation relationships supported by observations. |
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
