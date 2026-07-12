# 🎣 Text Fishing for AI Players

A single-file, zero-dependency, deterministic fishing game designed for an AI player.

Buy bait, cast, catch fish by rarity odds, sell catches for points, unlock new waters, dive for underwater-only species, and fill the encyclopedia. The game state lives in `fishing_save.json`, not in chat history.

## Files

| File | Purpose |
| --- | --- |
| `engine.py` | Readable source. Public API: `cmd("command")` and `new_game(seed)`. |
| `fishing.py` | Blind-play build. The engine is packed into base64 so an AI can play without reading fish tables or probabilities. |
| `build_blind.py` | Rebuilds `fishing.py` from `engine.py`. |
| `tool-schema.json` | JSON schema for a structured `play_fishing` tool. |
| `examples/` | Integration examples. |

## Quick Start

Requires Python 3.8+.

```python
import engine          # or import fishing for the blind-play build

print(engine.cmd("help"))
print(engine.cmd("status"))
print(engine.cmd("cast"))
print(engine.cmd("cast 10"))
print(engine.cmd("cast 20 stop=rare"))
print(engine.cmd("buy basic_worm 10; cast 10"))
print(engine.new_game(2024))
```

Any input is safe: `cmd("...")` returns text instead of throwing to the caller. Save read/write problems are reported in the returned text.

## Core Commands

| Command | Effect |
| --- | --- |
| `help` | Show rules and command list. |
| `status` | Show points, location, season, bait, oxygen, inventory counts, and progress. |
| `shop` | Show bait and oxygen for sale. |
| `buy <bait_id> [qty]` | Buy bait, e.g. `buy glow_bait 2`; buy oxygen with `buy oxygen 5`. |
| `cast [bait_id] [N] [stop=new,rare,event]` | Cast once or batch-cast 1-20 times. Stop early on a new species, rare-or-better catch, or event. |
| `dive [N] [stop=...]` | Start an underwater expedition after unlocking a dive site and buying oxygen. |
| `choose <number>` | Choose at a paused major underwater site. Without a number, show choices again. |
| `surface` | End the current expedition and surface. |
| `goto` | List locations, unlock costs, and seasonal undiscovered counts. |
| `goto <location_id>` | Travel to a location; locked locations cost points. |
| `inventory` | Show catches, items, map fragments, and pending chests. |
| `sell <catch_id>`, `sell all`, `sell species <fish_id>`, `sell item <item_id>` | Sell catches or treasures for points. |
| `open <chest_uid>` | Open a pending chest. |
| `encyclopedia` | Show discovered fish and collected letters. |
| `look <id_or_name>` | Inspect a fish, location, bait, season, or item. Undiscovered fish remain hidden as `???`. |
| `A; B; C` | Run up to 8 commands in one batch, e.g. `buy basic_worm 10; cast 10`. |

## Notes for AI Integration

Use batch casts to save turns and context:

```text
cast 10
cast glow_bait 15 stop=rare
goto reed_river; cast 8 stop=new
```

Every `cmd()` result ends with a compact status line:

```text
📊 {"pts": 270, "loc": "Reed River", "sea": "Spring", "turn": 6, "enc": "5/81", "bait": {"basic_worm": 2}, "hold": 6}
```

The JSON line is usually enough for the AI to decide the next move without calling `status` again.

## Saves and Determinism

- Saves live beside the script as `fishing_save.json`.
- Deleting that file starts over.
- The PRNG is deterministic. Same seed + same command sequence = reproducible results for that version.
- Existing saves keep their ids and structure. If a save references a location no longer present in the current data set, the engine moves the player to `Moonlit Pond` and keeps the rest of the save.

## Blind Play

To let an AI play without spoilers, give it `fishing.py` and tell it to use only:

```python
import fishing
print(fishing.cmd("help"))
print(fishing.cmd("status"))
print(fishing.cmd("cast 10"))
```

`fishing.py` is encoded, not encrypted. Blind play depends on cooperation: the AI should not decode `_BLOB` or inspect the packed engine.

## Rebuilding

After changing `engine.py`, rebuild the blind-play file:

```bash
python build_blind.py
```

`fishing.py` is generated from `engine.py`, so the two stay behaviorally identical.

## License

MIT. See `LICENSE`.
