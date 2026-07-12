"""World Waters Field Journal deterministic command engine.

The engine preserves the original project's compact cmd()/new_game() shape,
seeded PRNG, batch play, JSON saves, shop, travel, inventory, and blind build.
All playable content comes from our bilingual real_world_data module.
"""
import copy
import json
import os
import re

from real_world_data import BAITS as _BAITS
from real_world_data import CONDITIONS as _CONDITIONS
from real_world_data import EPISODES as _EPISODES
from real_world_data import FISH as _FISH
from real_world_data import LOCATIONS as _LOCATIONS
from real_world_data import RELATIONSHIPS as _RELATIONSHIPS
from real_world_data import SURFACE_JUNK as _SURFACE_JUNK
from real_world_data import STORIES as _STORIES
from real_world_data import WILDLIFE as _WILDLIFE


def _imul(a, b):
    return ((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF)) & 0xFFFFFFFF


class _Rng:
    """Mulberry32: stable across supported Python versions."""
    def __init__(self, state, calls=0):
        self.state = state & 0xFFFFFFFF
        self.calls = calls

    def random(self):
        self.calls += 1
        a = (self.state + 0x6D2B79F5) & 0xFFFFFFFF
        self.state = a
        t = _imul(a ^ (a >> 15), 1 | a)
        t = ((t + _imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    def rint(self, low, high):
        return low + int(self.random() * (high - low + 1))


_DEFAULT_SEED = 0x9E3779B9
RARITY = {
    "common": {"label": "Common", "weight": 1000, "bonus": 20, "rank": 0},
    "uncommon": {"label": "Uncommon", "weight": 350, "bonus": 20, "rank": 1},
    "rare": {"label": "Rare", "weight": 90, "bonus": 25, "rank": 2},
    "epic": {"label": "Epic", "weight": 22, "bonus": 30, "rank": 3},
    "legendary": {"label": "Legendary", "weight": 5, "bonus": 40, "rank": 4},
    "mythic": {"label": "Mythic", "weight": 1, "bonus": 50, "rank": 5},
}
SEASONS = {
    "spring": {"id": "spring", "name": "Spring", "name_en": "Spring", "name_zh": "春季", "order": 0, "tag_weight_mult": {"migratory": 1.15}},
    "summer": {"id": "summer", "name": "Summer", "name_en": "Summer", "name_zh": "夏季", "order": 1, "tag_weight_mult": {"tropical": 1.15}},
    "autumn": {"id": "autumn", "name": "Autumn", "name_en": "Autumn", "name_zh": "秋季", "order": 2, "tag_weight_mult": {"migratory": 1.2}},
    "winter": {"id": "winter", "name": "Winter", "name_en": "Winter", "name_zh": "冬季", "order": 3, "tag_weight_mult": {"coldwater": 1.2}},
}
LOCATIONS = copy.deepcopy(_LOCATIONS)
FISH = copy.deepcopy(_FISH)
BAITS = copy.deepcopy(_BAITS)
_REAL_WORLD_JUNK = copy.deepcopy(_SURFACE_JUNK)
_REAL_WORLD_CONDITIONS = copy.deepcopy(_CONDITIONS)
EPISODES = copy.deepcopy(_EPISODES)
RELATIONSHIPS = copy.deepcopy(_RELATIONSHIPS)
WILDLIFE = copy.deepcopy(_WILDLIFE)
STORIES = copy.deepcopy(_STORIES)

_SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fishing_save.json")
_IO_WARN = ""
S = None


def _new_state(seed=_DEFAULT_SEED):
    seed = int(seed) & 0xFFFFFFFF
    return {
        "version": 2, "language": "zh", "seed": seed, "rngState": seed, "rngCalls": 0,
        "turn": 0, "season_id": "spring", "season_length": 20,
        "season_started_turn": 0, "points": 200,
        "location_id": "colorado_headwaters",
        "unlocked_locations": ["colorado_headwaters"],
        "bait_inventory": {"earthworm": 8}, "catch_inventory": [],
        "encyclopedia": {}, "field_observations": {}, "legacy_archive_count": 0,
        "location_stats": {"colorado_headwaters": {"first_visit_turn": 0, "visits": 1,
            "casts": 0, "fish": 0, "empty": 0, "objects": 0, "wildlife": 0,
            "cleanup": 0, "species_seen": [], "wildlife_seen": []}},
        "stats": {"total_casts": 0, "total_caught": 0, "released": 0,
                  "empty_casts": 0, "debris_removed": 0, "wildlife_observations": 0},
    }


def _is_en():
    return S is not None and S.get("language") == "en"


def _bi(zh, en):
    return en if _is_en() else zh


def _field(record, base):
    suffix = "en" if _is_en() else "zh"
    return record.get("%s_%s" % (base, suffix), record.get(base, ""))


def _name(record):
    return _field(record, "name")


def _save():
    global _IO_WARN
    try:
        with open(_SAVE, "w", encoding="utf-8") as handle:
            json.dump(S, handle, ensure_ascii=False, indent=2)
    except Exception as exc:
        _IO_WARN = "⚠️ Save write failed: %s" % exc


def _load():
    global S, _IO_WARN
    if S is not None:
        return S
    if os.path.exists(_SAVE):
        try:
            with open(_SAVE, "r", encoding="utf-8") as handle:
                S = json.load(handle)
        except Exception as exc:
            try:
                os.replace(_SAVE, _SAVE + ".corrupt")
            except Exception:
                pass
            S = _new_state()
            _IO_WARN = "⚠️ Unreadable save archived: %s" % exc
    else:
        S = _new_state()
    _migrate_state()
    return S


def _migrate_state():
    """Convert old fantasy ids without allowing stale references to survive."""
    global _IO_WARN
    defaults = _new_state(S.get("seed", _DEFAULT_SEED))
    for key, value in defaults.items():
        S.setdefault(key, copy.deepcopy(value))
    for key, value in defaults["stats"].items():
        S.setdefault("stats", {}).setdefault(key, value)

    old_enc = [fid for fid in S["encyclopedia"] if fid not in FISH]
    old_catches = [c for c in S["catch_inventory"] if c.get("fish_id") not in FISH]
    old_baits = [bid for bid in S["bait_inventory"] if bid not in BAITS]
    archived = len(old_enc) + len(old_catches) + sum(S["bait_inventory"].get(bid, 0) for bid in old_baits)
    if archived:
        S["legacy_archive_count"] = S.get("legacy_archive_count", 0) + archived
        S["encyclopedia"] = {fid: e for fid, e in S["encyclopedia"].items() if fid in FISH}
        S["catch_inventory"] = [c for c in S["catch_inventory"] if c.get("fish_id") in FISH]
        S["bait_inventory"] = {bid: n for bid, n in S["bait_inventory"].items() if bid in BAITS and n > 0}
        S["bait_inventory"]["earthworm"] = S["bait_inventory"].get("earthworm", 0) + 8
        _IO_WARN = _bi("📚 已归档%d条不兼容的幻想时代记录，并补发8条蚯蚓。", "📚 Archived %d incompatible fantasy-era record(s); granted 8 earthworms.") % archived
    S["unlocked_locations"] = [lid for lid in S["unlocked_locations"] if lid in LOCATIONS]
    if "colorado_headwaters" not in S["unlocked_locations"]:
        S["unlocked_locations"].append("colorado_headwaters")
    if S.get("location_id") not in LOCATIONS:
        S["location_id"] = "colorado_headwaters"
        _IO_WARN = (_IO_WARN + "\n" if _IO_WARN else "") + _bi("现实野外版已将当前位置迁移到科罗拉多源流。", "Moved to Colorado headwaters for the field edition.")
    S["version"] = 2


def _current_condition(location_id=None):
    location_id = location_id or S["location_id"]
    pool = _REAL_WORLD_CONDITIONS.get(location_id, [])
    if not pool:
        return {"name_zh": "水况稳定", "name_en": "Steady water", "fact_zh": "当前没有显著变化。", "tag_weight_mult": {}}
    salt = sum((i + 1) * ord(ch) for i, ch in enumerate(location_id))
    index = (int(S["seed"]) + int(S["turn"]) // 4 + salt) % len(pool)
    return pool[index]


def _location_stat(location_id=None):
    location_id = location_id or S["location_id"]
    return S["location_stats"].setdefault(location_id, {
        "first_visit_turn": S["turn"], "visits": 0, "casts": 0, "fish": 0,
        "empty": 0, "objects": 0, "wildlife": 0, "cleanup": 0,
        "species_seen": [], "wildlife_seen": []})


def _current_time():
    """Eight-action field day: each phase lasts two actions."""
    phases = [
        {"id": "dawn", "name_zh": "黎明", "name_en": "Dawn", "fact_zh": "光线快速变化，低光活动与日间活动可能短暂重叠。", "fact_en": "Rapidly changing light can briefly overlap low-light and daytime activity.", "tag_weight_mult": {"low_light": 1.25, "daylight": 1.1}},
        {"id": "day", "name_zh": "白昼", "name_en": "Day", "fact_zh": "强光提高视觉觅食机会，也可能让警觉的鱼退向遮蔽物。", "fact_en": "Bright light aids visual feeding but may push wary fish toward cover.", "tag_weight_mult": {"daylight": 1.35, "nocturnal": 0.65}},
        {"id": "dusk", "name_zh": "黄昏", "name_en": "Dusk", "fact_zh": "光照下降会改变捕食距离与活动边界，但不会保证咬口。", "fact_en": "Falling light changes detection distance and activity boundaries but never guarantees a bite.", "tag_weight_mult": {"low_light": 1.4, "nocturnal": 1.15}},
        {"id": "night", "name_zh": "夜间", "name_en": "Night", "fact_zh": "视觉之外的嗅觉、侧线和电感受等线索相对更重要。", "fact_en": "Scent, lateral-line sensing, and electroreception become relatively more useful than vision.", "tag_weight_mult": {"nocturnal": 1.55, "daylight": 0.6, "vertical_migrant": 1.25}},
    ]
    return phases[(S["turn"] // 2) % len(phases)]


def _current_episode(location_id=None):
    """Longer ecological phase: twelve actions, no PRNG consumption."""
    location_id = location_id or S["location_id"]
    pool = EPISODES[location_id]
    salt = sum((i + 3) * ord(ch) for i, ch in enumerate(location_id))
    return pool[(int(S["seed"]) + int(S["turn"]) // 12 + salt) % len(pool)]


def _eligible(fish, location_id, season_id):
    return location_id in fish["locations"] and season_id in fish["seasons"]


def _weight(fish, bait_id):
    loc = LOCATIONS[S["location_id"]]
    season = SEASONS[S["season_id"]]
    bait = BAITS[bait_id]
    condition = _current_condition()
    time_phase = _current_time()
    episode = _current_episode()
    weight = RARITY[fish["rarity"]]["weight"] * fish.get("individual_weight", 1.0)
    for tag in fish.get("tags", []):
        weight *= loc.get("tag_weight_mult", {}).get(tag, 1.0)
        weight *= season.get("tag_weight_mult", {}).get(tag, 1.0)
        weight *= bait["effects"].get("tag_weight_mult", {}).get(tag, 1.0)
        weight *= condition.get("tag_weight_mult", {}).get(tag, 1.0)
        weight *= time_phase.get("tag_weight_mult", {}).get(tag, 1.0)
        weight *= episode.get("tag_weight_mult", {}).get(tag, 1.0)
    weight *= bait["effects"].get("rarity_weight_mult", {}).get(fish["rarity"], 1.0)
    return weight


def _weighted_pick(rng, items, weights):
    total = sum(weights)
    needle = rng.random() * total
    upto = 0.0
    for item, weight in zip(items, weights):
        upto += weight
        if needle <= upto:
            return item
    return items[-1]


def _roll_size(rng, fish):
    low, high = fish["size_min"], fish["size_max"]
    return round(low + (high - low) * (rng.random() + rng.random()) / 2, 1)


def _value(fish, size):
    midpoint = (fish["size_min"] + fish["size_max"]) / 2
    return max(1, round(fish["base_value"] * (size / midpoint) ** 1.5))


def _advance_season():
    if S["turn"] - S["season_started_turn"] < S["season_length"]:
        return ""
    ordered = sorted(SEASONS.values(), key=lambda item: item["order"])
    next_season = ordered[(SEASONS[S["season_id"]]["order"] + 1) % len(ordered)]
    previous = SEASONS[S["season_id"]]["name"]
    S["season_id"] = next_season["id"]
    S["season_started_turn"] = S["turn"]
    return _bi("🍃 %s结束，%s开始；鱼群活动随季节改变。\n" % (previous, next_season["name_zh"]),
               "🍃 %s ends and %s begins; fish activity changes with the season.\n" % (previous, next_season["name_en"]))


def _record(fish, size, value):
    first = fish["id"] not in S["encyclopedia"]
    if first:
        S["encyclopedia"][fish["id"]] = {
            "discovered": True, "first_caught_turn": S["turn"], "count": 0,
            "max_size": 0, "total_value_earned": 0,
            "identification": "pending" if fish.get("quiz") else "verified",
            "misidentifications": 0, "first_size": size, "min_size": size,
            "locations_seen": [], "times_seen": [],
        }
    entry = S["encyclopedia"][fish["id"]]
    entry["count"] += 1
    entry.setdefault("first_size", size)
    entry["min_size"] = min(entry.get("min_size", size), size)
    entry["max_size"] = max(entry["max_size"], size)
    if S["location_id"] not in entry.setdefault("locations_seen", []):
        entry["locations_seen"].append(S["location_id"])
    time_id = _current_time()["id"]
    if time_id not in entry.setdefault("times_seen", []):
        entry["times_seen"].append(time_id)
    entry["total_value_earned"] += value
    S["stats"]["total_caught"] += 1
    local = _location_stat(); local["fish"] += 1
    if fish["id"] not in local["species_seen"]:
        local["species_seen"].append(fish["id"])
    if fish.get("release_only"):
        instance = "obs_%03d" % S["stats"]["total_caught"]
        S["stats"]["released"] += 1
    else:
        instance = "c_%03d" % S["stats"]["total_caught"]
        S["catch_inventory"].append({"instance_id": instance, "fish_id": fish["id"], "size": size, "value": value})
    if first:
        S["points"] += RARITY[fish["rarity"]]["bonus"]
    elif entry["count"] == 2:
        S["points"] += 5
    elif entry["count"] == 3:
        S["points"] += 10
    return instance, first


def _record_catch(fish, size, value):
    """Compatibility contract retained for existing integrations and tests."""
    instance, first = _record(fish, size, value)
    bonus = RARITY[fish["rarity"]]["bonus"] if first else 0
    return instance, first, bonus


def _format_catch(fish, size, value, instance, first):
    prefix = "🆕" if first else ("✦" if RARITY[fish["rarity"]]["rank"] >= 2 else "·")
    display_name = fish["name_en"] if _is_en() else (fish["name_zh"] + " / " + fish["name_en"])
    lines = ["%s %s · %s · %scm · %d pts" %
             (prefix, display_name, RARITY[fish["rarity"]]["label"], size, value)]
    if first:
        lines.append("🔬 " + _field(fish, "science_fact"))
        lines.append(_bi("首次观察 +%d pts", "First observation +%d pts") % RARITY[fish["rarity"]]["bonus"])
    if fish.get("release_only"):
        lines.append(_bi("📷 测量、辨认并原地放流；记录号 %s，不进入鱼篓。", "📷 Measured, identified, and released in place; record %s never enters the creel.") % instance)
    elif first:
        lines.append(_bi("记录号 %s，暂存鱼篓。", "Record %s is temporarily retained in the creel.") % instance)
    if first and fish.get("quiz"):
        lines.append(_bi("🔎 待鉴定：identify %s", "🔎 Identification pending: identify %s") % fish["id"])
    count = S["encyclopedia"][fish["id"]]["count"]
    if count == 2:
        lines.append(_bi("◉ 观察等级提升：熟悉 +5 pts", "◉ Observation level: Familiar +5 pts"))
    elif count == 3:
        lines.append(_bi("◎ 观察等级提升：深入观察 +10 pts；新的生态关系可能已经解锁。", "◎ Observation level: Studied +10 pts; a new ecological relationship may be available."))
    return "\n".join(lines)


def _observation_level(entry):
    if entry.get("identification") == "pending":
        return "待鉴定", "Pending ID"
    if entry.get("count", 0) >= 3:
        return "深入观察", "Studied"
    if entry.get("count", 0) >= 2:
        return "熟悉", "Familiar"
    return "初见", "First observation"


def _cast_step(rng, bait_id):
    if bait_id not in BAITS:
        return {"kind": "error", "text": _bi("没有这种饵：%s", "No such bait: %s") % bait_id, "consumed": False}
    if S["bait_inventory"].get(bait_id, 0) <= 0:
        return {"kind": "error", "text": _bi("%s已经用完。", "%s is depleted.") % _name(BAITS[bait_id]), "consumed": False}
    S["bait_inventory"][bait_id] -= 1
    S["turn"] += 1
    S["stats"]["total_casts"] += 1
    _location_stat()["casts"] += 1
    season_line = _advance_season()
    loc = LOCATIONS[S["location_id"]]

    # A real cast can be quiet even when target species are present.
    episode = _current_episode()
    if rng.random() < 0.10 * episode.get("empty_mult", 1.0):
        S["stats"]["empty_casts"] += 1
        _location_stat()["empty"] += 1
        return {"kind": "empty", "consumed": True,
                "text": season_line + _bi("〰 浮漂没有形成可靠咬口。空杆也是水况记录。", "〰 The float shows no reliable bite. An empty cast is still a water observation.")}
    wildlife_pool = [item for item in WILDLIFE.values()
                     if S["location_id"] in item["locations"] and S["season_id"] in item["seasons"]]
    if wildlife_pool and rng.random() < 0.08 * episode.get("wildlife_mult", 1.0):
        observed = wildlife_pool[rng.rint(0, len(wildlife_pool) - 1)]
        key = "wildlife|%s" % observed["id"]
        note = S["field_observations"].setdefault(key, {
            "location_id": S["location_id"], "wildlife_id": observed["id"],
            "name": observed["name_zh"], "name_en": observed["name_en"],
            "category": "wildlife", "count": 0, "human_debris": False})
        note["count"] += 1
        S["stats"]["wildlife_observations"] += 1
        local = _location_stat(); local["wildlife"] += 1
        if observed["id"] not in local["wildlife_seen"]:
            local["wildlife_seen"].append(observed["id"])
        return {"kind": "wildlife", "consumed": True,
                "text": season_line + (_bi("🔭 野外观察：%s / %s\n%s\n只记录，不接近、不投喂、不捕捉。",
                    "🔭 Wildlife observation: %s\n%s\nRecord only: do not approach, feed, or capture.") % (
                    (observed["name_en"], _field(observed, "fact")) if _is_en()
                    else (observed["name_zh"], observed["name_en"], _field(observed, "fact"))))}
    junk_chance = loc["junk_chance_base"] * BAITS[bait_id]["effects"].get("junk_chance_mult", 1.0) * episode.get("junk_mult", 1.0)
    if rng.random() < junk_chance:
        pool = _REAL_WORLD_JUNK[S["location_id"]]
        found = pool[rng.rint(0, len(pool) - 1)]
        human_debris = any(word in found for word in ("废", "塑料", "鱼线", "渔网", "凉鞋", "铝罐", "船绳"))
        if human_debris:
            S["stats"]["debris_removed"] += 1
            _location_stat()["cleanup"] += 1
        _location_stat()["objects"] += 1
        key = "%s|%s" % (S["location_id"], found)
        note = S["field_observations"].setdefault(key, {"location_id": S["location_id"], "name": found, "count": 0, "human_debris": human_debris})
        note["count"] += 1
        return {"kind": "junk", "consumed": True,
                "text": season_line + (_bi("🪣 你拉上来%s。%s", "🪣 You retrieve %s. %s") % (
                    found if not _is_en() else "a location-specific field object",
                    (_bi("已从水域移除并记入清理日志。", "It was removed from the water and logged as cleanup.") if human_debris
                     else _bi("它也属于这片水域的自然记录。", "It is also part of this habitat record."))))}

    pool = [f for f in FISH.values() if _eligible(f, S["location_id"], S["season_id"])]
    if not pool:
        S["stats"]["empty_casts"] += 1
        _location_stat()["empty"] += 1
        return {"kind": "empty", "consumed": True, "text": season_line + _bi("〰 当前季节没有适合这种调查方式的目标物种。", "〰 No target species is available for this survey method in the current season.")}
    fish = _weighted_pick(rng, pool, [_weight(f, bait_id) for f in pool])
    size = _roll_size(rng, fish)
    value = _value(fish, size)
    instance, first = _record(fish, size, value)
    return {"kind": "fish", "consumed": True, "first": first,
            "rare": RARITY[fish["rarity"]]["rank"] >= RARITY["rare"]["rank"],
            "text": season_line + _format_catch(fish, size, value, instance, first)}


def _available_bait():
    available = [bid for bid, count in S["bait_inventory"].items() if count > 0 and bid in BAITS]
    return min(available, key=lambda bid: BAITS[bid]["cost"]) if available else None


def _c_cast(bait_id=None, times=1, stop=None):
    times = max(1, min(20, int(times)))
    stop = set(stop or [])
    rng = _Rng(S["rngState"], S["rngCalls"])
    results = []
    for _ in range(times):
        chosen = bait_id or _available_bait()
        if not chosen:
            results.append({"kind": "error", "text": _bi("没有可用鱼饵，请先去 shop。", "No bait remains; visit shop first."), "consumed": False})
            break
        result = _cast_step(rng, chosen)
        results.append(result)
        if not result["consumed"]:
            break
        if ("new" in stop and result.get("first")) or ("rare" in stop and result.get("rare")) or ("event" in stop and result["kind"] in ("junk", "wildlife")):
            break
    S["rngState"], S["rngCalls"] = rng.state, rng.calls
    if len(results) == 1:
        return results[0]["text"]
    highlights = [r["text"] for r in results if r.get("first") or r.get("rare")]
    counts = {kind: sum(r["kind"] == kind for r in results) for kind in ("fish", "empty", "junk", "wildlife")}
    summary = _bi("🎣 批量抛竿 %d次：鱼%d · 空杆%d · 物件%d · 野外观察%d",
                  "🎣 Batch %d: fish %d · empty %d · objects %d · wildlife %d") % (len(results), counts["fish"], counts["empty"], counts["junk"], counts["wildlife"])
    return summary + (("\n\n" + "\n——\n".join(highlights)) if highlights else "")


def _c_status():
    bait = _bi("、", ", ").join("%s×%d" % (_name(BAITS[bid]), n) for bid, n in S["bait_inventory"].items() if bid in BAITS and n > 0) or _bi("无", "none")
    condition = _current_condition()
    episode = _current_episode()
    template = _bi("[状态] %d pts | %s · %s | 第%d回合 | 图鉴%d/%d\n生态：%s | 时段：%s | 水况：%s | 鱼饵：%s\n鱼篓%d | 空杆%d | 保护放流%d | 野外观察%d | 清理废弃物%d",
                   "[Status] %d pts | %s · %s | turn %d | encyclopedia %d/%d\nEpisode: %s | Time: %s | Water: %s | Bait: %s\nCreel %d | empty %d | released %d | wildlife %d | debris removed %d")
    return template % (
                S["points"], _name(LOCATIONS[S["location_id"]]), _field(SEASONS[S["season_id"]], "name"),
                S["turn"], len(S["encyclopedia"]), len(FISH), _field(episode, "name"), _field(_current_time(), "name"), _field(condition, "name"), bait,
                len(S["catch_inventory"]), S["stats"]["empty_casts"], S["stats"]["released"], S["stats"]["wildlife_observations"], S["stats"]["debris_removed"])


def _c_conditions():
    condition = _current_condition()
    time_phase = _current_time()
    episode = _current_episode()
    effects = "、".join("%s ×%s" % pair for pair in condition.get("tag_weight_mult", {}).items()) or "无显著偏向"
    time_effects = "、".join("%s ×%s" % pair for pair in time_phase.get("tag_weight_mult", {}).items()) or "无显著偏向"
    if _is_en():
        return "[Environment]\nEcological episode: %s\n%s\n\nWater: %s\n%s\nWater weights: %s\n\nTime: %s\n%s\nTime weights: %s\nEpisode changes every twelve actions, water every four, and time every two; inspection consumes no random draw." % (
            episode["name_en"], episode["fact_en"], condition["name_en"], condition["fact_en"], effects, time_phase["name_en"], time_phase["fact_en"], time_effects)
    return "[环境观察]\n生态阶段：%s / %s\n%s\n\n水况：%s / %s\n%s\n水况权重：%s\n\n时段：%s / %s\n%s\n时段权重：%s\n生态阶段每12个行动、水况每4个行动、时段每2个行动变化；查看环境不消耗随机数。" % (
        episode["name_zh"], episode["name_en"], episode["fact_zh"],
        condition["name_zh"], condition["name_en"], condition["fact_zh"], effects,
        time_phase["name_zh"], time_phase["name_en"], time_phase["fact_zh"], time_effects)


def _c_shop():
    lines = [_bi("[调查补给]", "[Field supplies]")]
    for bait in BAITS.values():
        lines.append("%s · %s · %d pts — %s" % (bait["id"], _name(bait), bait["cost"], _field(bait, "description")))
    return "\n".join(lines)


def _c_buy(bait_id, qty=1):
    if bait_id not in BAITS:
        return _bi("没有这种补给：%s", "No such supply: %s") % bait_id
    qty = max(1, min(100, int(qty)))
    cost = BAITS[bait_id]["cost"] * qty
    if cost > S["points"]:
        return _bi("点数不足：需要%d，当前%d。", "Not enough points: need %d, have %d.") % (cost, S["points"])
    S["points"] -= cost
    S["bait_inventory"][bait_id] = S["bait_inventory"].get(bait_id, 0) + qty
    return _bi("购入%s×%d，花费%d pts。", "Bought %s×%d for %d pts.") % (_name(BAITS[bait_id]), qty, cost)


def _c_goto(location_id=None):
    if not location_id:
        lines = [_bi("[世界水域]", "[World waters]")]
        for loc in LOCATIONS.values():
            state = _bi("已解锁", "unlocked") if loc["id"] in S["unlocked_locations"] else "%d pts" % loc["unlock_cost"]
            display = "%s / %s" % (loc["name_zh"], loc["name_en"]) if not _is_en() else loc["name_en"]
            lines.append("%s · %s · %s" % (loc["id"], display, state))
        return "\n".join(lines)
    if location_id not in LOCATIONS:
        return _bi("没有这个地点：%s", "No such location: %s") % location_id
    loc = LOCATIONS[location_id]
    if location_id not in S["unlocked_locations"]:
        if S["points"] < loc["unlock_cost"]:
            return _bi("解锁%s需要%d pts，当前%d。", "Unlocking %s needs %d pts; you have %d.") % (_name(loc), loc["unlock_cost"], S["points"])
        S["points"] -= loc["unlock_cost"]
        S["unlocked_locations"].append(location_id)
    S["location_id"] = location_id
    local = _location_stat(location_id)
    local["visits"] += 1
    return _bi("抵达%s / %s。\n%s" % (loc["name_zh"], loc["name_en"], loc["description_zh"]),
               "Arrived at %s.\n%s" % (loc["name_en"], loc["description_en"]))


def _c_passport():
    visited = [(lid, data) for lid, data in S.get("location_stats", {}).items() if lid in LOCATIONS and data.get("visits", 0) > 0]
    lines = [_bi("[世界水域护照] %d/%d枚地点章", "[World Waters Passport] %d/%d location stamps") % (len(visited), len(LOCATIONS))]
    for location_id, data in visited:
        loc = LOCATIONS[location_id]
        if _is_en():
            lines.append("\n◉ %s · first turn %d · visits %d" % (loc["name_en"], data["first_visit_turn"], data["visits"]))
            lines.append("  casts %d · species %d · wildlife %d · empty %d · objects %d · cleanup %d" % (
                data["casts"], len(data["species_seen"]), len(data["wildlife_seen"]), data["empty"], data["objects"], data["cleanup"]))
        else:
            lines.append("\n◉ %s / %s · 首访第%d回合 · 到访%d次" % (loc["name_zh"], loc["name_en"], data["first_visit_turn"], data["visits"]))
            lines.append("  抛竿%d · 物种%d · 野生动物%d · 空杆%d · 物件%d · 清理%d" % (
                data["casts"], len(data["species_seen"]), len(data["wildlife_seen"]), data["empty"], data["objects"], data["cleanup"]))
    if len(visited) < len(LOCATIONS):
        lines.append(_bi("\n尚有%d片水域没有盖章。", "\n%d water(s) remain unstamped.") % (len(LOCATIONS) - len(visited)))
    return "\n".join(lines)


def _c_stories():
    unlocked = [story for story in STORIES
                if S.get("location_stats", {}).get(story["location_id"], {}).get("casts", 0) >= story["casts_required"]]
    disclaimer = _bi("⚠ 原创虚构营火故事；不是物种事实、概率提示或当地传统记录。",
                     "⚠ Original fictional campfire stories; not species facts, probability hints, or records of local tradition.")
    lines = [_bi("[水边故事册] %d/%d", "[Waterside storybook] %d/%d") % (len(unlocked), len(STORIES)), disclaimer]
    for story in unlocked:
        lines.append("\n◇ %s\n%s" % (_field(story, "title"), _field(story, "text")))
    if len(unlocked) < len(STORIES):
        lines.append(_bi("\n继续在不同水域调查，另有%d篇故事尚未解锁。", "\nContinue surveying different waters; %d story or stories remain locked.") % (len(STORIES) - len(unlocked)))
    return "\n".join(lines)


def _c_inventory():
    if not S["catch_inventory"]:
        return _bi("[鱼篓] 空。保护物种只存在观察日志中。", "[Creel] Empty. Protected species exist only in the observation journal.")
    lines = [_bi("[鱼篓]", "[Creel]")]
    for catch in S["catch_inventory"]:
        fish = FISH[catch["fish_id"]]
        lines.append("%s · %s %scm · %d pts" % (catch["instance_id"], _name(fish), catch["size"], catch["value"]))
    return "\n".join(lines)


def _c_sell(target):
    if not target:
        return _bi("用法：sell all | sell <catch_id> | sell species <fish_id>", "Usage: sell all | sell <catch_id> | sell species <fish_id>")
    if target == "all":
        sold = list(S["catch_inventory"])
    elif target.startswith("species "):
        fish_id = target.split(None, 1)[1]
        sold = [c for c in S["catch_inventory"] if c["fish_id"] == fish_id]
    else:
        sold = [c for c in S["catch_inventory"] if c["instance_id"] == target]
    if not sold:
        return _bi("没有符合条件的可出售记录。", "No retainable record matches that target.")
    ids = {c["instance_id"] for c in sold}
    S["catch_inventory"] = [c for c in S["catch_inventory"] if c["instance_id"] not in ids]
    gained = sum(c["value"] for c in sold)
    S["points"] += gained
    return _bi("出售%d条可留存渔获，获得%d pts。图鉴观察仍然保留。", "Sold %d retainable catch(es) for %d pts. Field observations remain in the journal.") % (len(sold), gained)


def _c_encyclopedia():
    lines = [_bi("[物种图鉴] %d/%d", "[Species encyclopedia] %d/%d") % (len(S["encyclopedia"]), len(FISH))]
    for fish in FISH.values():
        if fish["id"] not in S["encyclopedia"]:
            continue
        entry = S["encyclopedia"][fish["id"]]
        mark = "✔" if entry.get("identification", "verified") == "verified" else "?"
        level_zh, level_en = _observation_level(entry)
        if _is_en():
            lines.append("%s %s · %s · %d observations · max %scm" % (mark, fish["name_en"], level_en, entry["count"], entry["max_size"]))
        else:
            lines.append("%s %s / %s · %s · %d次 · 最大%scm" % (mark, fish["name_zh"], fish["name_en"], level_zh, entry["count"], entry["max_size"]))
    if len(lines) == 1:
        lines.append(_bi("还没有物种观察。", "No species observations yet."))
    return "\n".join(lines)


def _c_journal():
    seen = [f for f in FISH.values() if f["id"] in S["encyclopedia"]]
    native = sum(f.get("native_status") == "native" for f in seen)
    introduced = sum(f.get("native_status") == "introduced" for f in seen)
    corrections = sum(S["encyclopedia"][f["id"]].get("misidentifications", 0) for f in seen)
    pending = sum(S["encyclopedia"][f["id"]].get("identification") == "pending" for f in seen)
    studied = sum(_observation_level(S["encyclopedia"][f["id"]])[0] == "深入观察" for f in seen)
    observations = sorted(S.get("field_observations", {}).values(), key=lambda item: (-item["count"], item["name"]))
    object_lines = ""
    if observations:
        object_lines = _bi("\n[非鱼类发现]\n", "\n[Non-fish observations]\n") + "\n".join("%s %s · %s%s ×%d" % (
            "🔭" if item.get("category") == "wildlife" else ("🧹" if item.get("human_debris") else "◦"),
            _name(LOCATIONS[item["location_id"]]),
            (item.get("name_en") or ("removed human debris" if item.get("human_debris") else "natural field object")) if _is_en() else item["name"],
            (" / " + item["name_en"]) if item.get("name_en") and not _is_en() else "", item["count"]
        ) for item in observations[:12])
    template = _bi("[观察日志] 物种%d/%d · 原生%d · 引入%d · 待鉴定%d · 深入观察%d\n保护放流%d · 野外观察%d · 纠错%d · 空杆%d · 清理废弃物%d\n用 identify <fish_id> 学习鉴别，用 look <fish_id> 阅读科普。",
                   "[Observation journal] species %d/%d · native %d · introduced %d · pending ID %d · studied %d\nreleased %d · wildlife %d · corrections %d · empty casts %d · debris removed %d\nUse identify <fish_id> to study field marks and look <fish_id> for science notes.")
    return ((template) % (
                len(seen), len(FISH), native, introduced, pending, studied, S["stats"]["released"], S["stats"]["wildlife_observations"],
                corrections, S["stats"]["empty_casts"], S["stats"]["debris_removed"])) + object_lines


def _relationship_unlocked(relationship):
    minimum = relationship.get("min_count", 1)
    return all(S["encyclopedia"].get(fid, {}).get("count", 0) >= minimum for fid in relationship["requires"])


def _c_ecosystem():
    unlocked = [rel for rel in RELATIONSHIPS if _relationship_unlocked(rel)]
    lines = [_bi("[生态关系网] %d/%d 已解锁", "[Ecological relationships] %d/%d unlocked") % (len(unlocked), len(RELATIONSHIPS))]
    if not unlocked:
        lines.append(_bi("继续在同一生态系统中重复观察不同物种，关系证据才会浮现。", "Repeat observations of different species within one ecosystem to reveal relationship evidence."))
    for rel in unlocked:
        loc = LOCATIONS[rel["location_id"]]
        lines.append("\n◆ %s" % ((rel["title_zh"] + " / " + rel["title_en"]) if not _is_en() else rel["title_en"]))
        lines.append("  %s · %s" % (_name(loc), rel["type"]))
        lines.append("  " + _field(rel, "fact"))
    locked = len(RELATIONSHIPS) - len(unlocked)
    if locked:
        lines.append(_bi("\n另有%d条关系仍缺少重复观察证据。", "\n%d relationship(s) still lack repeated-observation evidence.") % locked)
    return "\n".join(lines)


def _c_identify(fish_id, choice=None):
    fish = FISH.get(fish_id)
    if not fish:
        return _bi("没有这个物种 id：%s", "No such species id: %s") % fish_id
    entry = S["encyclopedia"].get(fish_id)
    if not entry:
        return _bi("尚未观察到这个物种。", "This species has not been observed yet.")
    quiz = fish.get("quiz")
    if not quiz:
        entry["identification"] = "verified"
        return _bi("%s不需要额外纠错题，记录已确认。", "%s requires no additional correction exercise; the record is verified.") % _name(fish)
    if choice is None:
        choices = quiz["choices_en"] if _is_en() else quiz["choices_zh"]
        options = "\n".join("  %d. %s" % (i + 1, text) for i, text in enumerate(choices))
        return _bi("[物种鉴定] %s\n%s\n%s\n回答：identify %s <编号>", "[Species identification] %s\n%s\n%s\nAnswer: identify %s <number>") % (
            _name(fish), quiz["question_en"] if _is_en() else quiz["question_zh"], options, fish_id)
    if not 1 <= choice <= len(quiz["choices_zh"]):
        return _bi("选项应为1-%d。", "Choose an option from 1-%d.") % len(quiz["choices_zh"])
    if choice == quiz["answer"]:
        first_verify = entry.get("identification") != "verified"
        entry["identification"] = "verified"
        if first_verify:
            S["points"] += 10
        explanation = quiz["explanation_en"] if _is_en() else quiz["explanation_zh"]
        reward = _bi("\n观察奖励 +10 pts", "\nObservation reward +10 pts") if first_verify else ""
        return _bi("✅ 鉴定确认：%s\n%s%s", "✅ Identification verified: %s\n%s%s") % (_name(fish), explanation, reward)
    entry["misidentifications"] = entry.get("misidentifications", 0) + 1
    entry["identification"] = "pending"
    return _bi("↺ 需要修正：%s\n误判已写入观察日志。", "↺ Correction needed: %s\nThe misidentification is recorded in the journal.") % (quiz["wrong_en"] if _is_en() else quiz["wrong_zh"])


def _find(table, query):
    if query in table:
        return table[query]
    query = query.casefold()
    for item in table.values():
        if query in (str(item.get("name", "")).casefold(), str(item.get("name_en", "")).casefold(), str(item.get("name_zh", "")).casefold()):
            return item
    return None


def _c_look(query):
    fish = _find(FISH, query)
    if fish:
        if fish["id"] not in S["encyclopedia"]:
            return _bi("??? · 尚未观察到该物种。", "??? · This species has not been observed.")
        origins = ({"native": "native", "introduced": "introduced", "endemic": "endemic"} if _is_en() else {"native": "原生", "introduced": "引入", "endemic": "特有"})
        origin = origins.get(fish.get("native_status"), fish.get("native_status", _bi("未记录", "unrecorded")))
        level_zh, level_en = _observation_level(S["encyclopedia"][fish["id"]])
        if _is_en():
            return ("%s (%s)\nObservation level: %s\n🔬 %s\n🔎 %s\n🌿 %s · %s%s\nSpecies range %s-%scm\nYour records: first %scm · min %scm · max %scm · places %d · day phases %d") % (
                fish["name_en"], fish["latin"], level_en, fish["science_fact_en"], fish["identification_en"], origin,
                fish["conservation"], " · observe and release only" if fish.get("release_only") else "", fish["size_min"], fish["size_max"],
                S["encyclopedia"][fish["id"]].get("first_size", S["encyclopedia"][fish["id"]]["max_size"]),
                S["encyclopedia"][fish["id"]].get("min_size", S["encyclopedia"][fish["id"]]["max_size"]), S["encyclopedia"][fish["id"]]["max_size"],
                len(S["encyclopedia"][fish["id"]].get("locations_seen", [])), len(S["encyclopedia"][fish["id"]].get("times_seen", [])))
        return ("%s / %s (%s)\n观察等级：%s / %s\n🔬 %s\n🔎 %s\n🌿 %s · %s%s\n物种体长 %s-%scm\n你的记录：首次%scm · 最小%scm · 最大%scm · 地点%d · 时段%d") % (
            fish["name_zh"], fish["name_en"], fish["latin"], level_zh, level_en, fish["science_fact_zh"], fish["identification_zh"], origin,
            fish["conservation"], " · 仅观察放流" if fish.get("release_only") else "", fish["size_min"], fish["size_max"],
            S["encyclopedia"][fish["id"]].get("first_size", S["encyclopedia"][fish["id"]]["max_size"]),
            S["encyclopedia"][fish["id"]].get("min_size", S["encyclopedia"][fish["id"]]["max_size"]), S["encyclopedia"][fish["id"]]["max_size"],
            len(S["encyclopedia"][fish["id"]].get("locations_seen", [])), len(S["encyclopedia"][fish["id"]].get("times_seen", [])))
    loc = _find(LOCATIONS, query)
    if loc:
        return _bi("%s / %s\n%s\n生境：%s" % (loc["name_zh"], loc["name_en"], loc["description_zh"], loc["biome"]),
                   "%s\n%s\nHabitat: %s" % (loc["name_en"], loc["description_en"], loc["biome"]))
    bait = _find(BAITS, query)
    if bait:
        return _bi("%s / %s · %d pts\n%s" % (bait["name"], bait["name_en"], bait["cost"], bait["description"]),
                   "%s · %d pts\n%s" % (bait["name_en"], bait["cost"], bait["description_en"]))
    wildlife = _find(WILDLIFE, query)
    if wildlife:
        if "wildlife|%s" % wildlife["id"] not in S.get("field_observations", {}):
            return _bi("??? · 尚未在野外观察到该生物。", "??? · This organism has not been observed in the field.")
        return _bi("%s / %s · %s\n%s\n状态：%s · 仅观察" % (wildlife["name_zh"], wildlife["name_en"], wildlife["group"], wildlife["fact_zh"], wildlife["status"]),
                   "%s · %s\n%s\nStatus: %s · observation only" % (wildlife["name_en"], wildlife["group"], wildlife["fact_en"], wildlife["status"]))
    return _bi("没有这个对象：%s", "No such object: %s") % query


_HELP_ZH = """🌍🎣 World Waters Field Journal
命令：
  language zh|en                 切换并保存界面语言
  status                         当前地点、水况、补给与观察统计
  conditions                     当前水况及其生态影响
  shop | buy <bait_id> [qty]     调查补给
  cast [bait_id] [N] [stop=...]  抛竿1-20次；stop=new,rare,event
  goto | goto <location_id>      世界水域与旅行解锁
  passport                       地点章、首访与各水域调查统计
  stories                        明确标注为原创虚构的营火故事册
  inventory | sell ...           管理可留存渔获
  encyclopedia | journal         图鉴与观察日志
  ecosystem                      已解锁的食物、栖息地、洄游与保护关系
  identify <fish_id> [choice]    纠错鉴定
  look <id_or_name>              阅读物种、地点或饵的科普记录
可用分号批量执行最多8条命令。空杆、自然物与废弃物同样是调查结果。"""

_HELP_EN = """🌍🎣 World Waters Field Journal
Commands:
  language zh|en                 Switch and save the interface language
  status                         Location, environment, supplies, and statistics
  conditions                     Current water and time effects
  shop | buy <bait_id> [qty]     Field supplies
  cast [bait_id] [N] [stop=...]  Cast 1-20 times; stop=new,rare,event
  goto | goto <location_id>      World waters and travel unlocks
  passport                       Location stamps and per-water survey records
  stories                        Original fiction, explicitly separate from science records
  inventory | sell ...           Manage retainable catches
  encyclopedia | journal         Species and observation journals
  ecosystem                      Unlocked food, habitat, migration, and conservation links
  identify <fish_id> [choice]    Corrective identification
  look <id_or_name>              Read species, place, bait, or wildlife notes
Use semicolons to batch up to eight commands. Empty casts, natural objects, debris, and wildlife are all valid field results."""


def _help():
    return _HELP_EN if _is_en() else _HELP_ZH


def _c_language(language=None):
    if language not in ("zh", "en"):
        return _bi("当前语言：中文。用法：language zh|en", "Current language: English. Usage: language zh|en")
    S["language"] = language
    return "Interface language saved as English." if language == "en" else "界面语言已保存为中文。"


def _run_one(line):
    parts = line.strip().split()
    if not parts:
        return _help()
    command, args = parts[0].lower(), parts[1:]
    try:
        if command in ("help", "h"):
            return _help()
        if command in ("language", "lang"):
            return _c_language(args[0].lower() if args else None)
        if command in ("status", "s"):
            return _c_status()
        if command in ("conditions", "water"):
            return _c_conditions()
        if command == "shop":
            return _c_shop()
        if command == "buy":
            return _c_buy(args[0] if args else "", int(args[1]) if len(args) > 1 else 1)
        if command in ("cast", "c"):
            bait_id = next((arg for arg in args if arg in BAITS), None)
            times = next((int(arg) for arg in args if arg.isdigit()), 1)
            stop = next((arg[5:].split(",") for arg in args if arg.startswith("stop=")), [])
            return _c_cast(bait_id, times, stop)
        if command in ("goto", "go"):
            return _c_goto(args[0] if args else None)
        if command in ("passport", "pass"):
            return _c_passport()
        if command in ("stories", "story"):
            return _c_stories()
        if command in ("inventory", "inv", "i"):
            return _c_inventory()
        if command == "sell":
            return _c_sell(" ".join(args))
        if command in ("encyclopedia", "enc", "e"):
            return _c_encyclopedia()
        if command in ("journal", "j"):
            return _c_journal()
        if command in ("ecosystem", "eco"):
            return _c_ecosystem()
        if command in ("identify", "id"):
            choice = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
            return _c_identify(args[0] if args else "", choice)
        if command in ("look", "l"):
            return _c_look(" ".join(args))
        return _bi("未知命令：%s。使用 help 查看命令。", "Unknown command: %s. Use help for commands.") % command
    except (ValueError, IndexError) as exc:
        return _bi("命令参数无法解析：%s", "Could not parse command arguments: %s") % exc


def _state_json():
    return "📊 " + json.dumps({
        "pts": S["points"], "loc": _name(LOCATIONS[S["location_id"]]),
        "sea": _field(SEASONS[S["season_id"]], "name"), "turn": S["turn"],
        "enc": "%d/%d" % (len(S["encyclopedia"]), len(FISH)),
        "bait": {bid: n for bid, n in S["bait_inventory"].items() if n > 0},
        "hold": len(S["catch_inventory"]), "released": S["stats"]["released"],
    }, ensure_ascii=False)


def cmd(line=""):
    """Run one command or a semicolon/newline batch and always return text."""
    global _IO_WARN
    _load()
    commands = [part.strip() for part in re.split(r"[;\n]+", line or "") if part.strip()]
    if not commands:
        output = _help()
    else:
        output = "\n\n".join(("▶ %s\n" % item if len(commands) > 1 else "") + _run_one(item) for item in commands[:8])
        if len(commands) > 8:
            output += _bi("\n\n最多执行8条；其余%d条已忽略。", "\n\nOnly eight commands run at once; %d extra ignored.") % (len(commands) - 8)
    _save()
    if _IO_WARN:
        output += "\n" + _IO_WARN
        _IO_WARN = ""
    return output + "\n" + _state_json()


def new_game(seed=_DEFAULT_SEED):
    global S
    S = _new_state(seed)
    _save()
    return _bi("World Waters新调查已开始（seed %d）。使用 help 查看命令。", "A new World Waters survey has begun (seed %d). Use help for commands.") % S["seed"]
