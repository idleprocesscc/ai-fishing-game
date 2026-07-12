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
from real_world_data import FISH as _FISH
from real_world_data import LOCATIONS as _LOCATIONS
from real_world_data import RELATIONSHIPS as _RELATIONSHIPS
from real_world_data import SURFACE_JUNK as _SURFACE_JUNK


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
    "spring": {"id": "spring", "name": "Spring", "order": 0, "tag_weight_mult": {"migratory": 1.15}},
    "summer": {"id": "summer", "name": "Summer", "order": 1, "tag_weight_mult": {"tropical": 1.15}},
    "autumn": {"id": "autumn", "name": "Autumn", "order": 2, "tag_weight_mult": {"migratory": 1.2}},
    "winter": {"id": "winter", "name": "Winter", "order": 3, "tag_weight_mult": {"coldwater": 1.2}},
}
LOCATIONS = copy.deepcopy(_LOCATIONS)
FISH = copy.deepcopy(_FISH)
BAITS = copy.deepcopy(_BAITS)
_REAL_WORLD_JUNK = copy.deepcopy(_SURFACE_JUNK)
_REAL_WORLD_CONDITIONS = copy.deepcopy(_CONDITIONS)
RELATIONSHIPS = copy.deepcopy(_RELATIONSHIPS)

_SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fishing_save.json")
_IO_WARN = ""
S = None


def _new_state(seed=_DEFAULT_SEED):
    seed = int(seed) & 0xFFFFFFFF
    return {
        "version": 2, "seed": seed, "rngState": seed, "rngCalls": 0,
        "turn": 0, "season_id": "spring", "season_length": 20,
        "season_started_turn": 0, "points": 200,
        "location_id": "colorado_headwaters",
        "unlocked_locations": ["colorado_headwaters"],
        "bait_inventory": {"earthworm": 8}, "catch_inventory": [],
        "encyclopedia": {}, "field_observations": {}, "legacy_archive_count": 0,
        "stats": {"total_casts": 0, "total_caught": 0, "released": 0,
                  "empty_casts": 0, "debris_removed": 0},
    }


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
        _IO_WARN = "📚 Archived %d incompatible fantasy-era record(s); granted 8 earthworms." % archived
    S["unlocked_locations"] = [lid for lid in S["unlocked_locations"] if lid in LOCATIONS]
    if "colorado_headwaters" not in S["unlocked_locations"]:
        S["unlocked_locations"].append("colorado_headwaters")
    if S.get("location_id") not in LOCATIONS:
        S["location_id"] = "colorado_headwaters"
        _IO_WARN = (_IO_WARN + "\n" if _IO_WARN else "") + "Moved to Colorado headwaters for the field edition."
    S["version"] = 2


def _current_condition(location_id=None):
    location_id = location_id or S["location_id"]
    pool = _REAL_WORLD_CONDITIONS.get(location_id, [])
    if not pool:
        return {"name_zh": "水况稳定", "name_en": "Steady water", "fact_zh": "当前没有显著变化。", "tag_weight_mult": {}}
    salt = sum((i + 1) * ord(ch) for i, ch in enumerate(location_id))
    index = (int(S["seed"]) + int(S["turn"]) // 4 + salt) % len(pool)
    return pool[index]


def _current_time():
    """Eight-action field day: each phase lasts two actions."""
    phases = [
        {"id": "dawn", "name_zh": "黎明", "name_en": "Dawn", "fact_zh": "光线快速变化，低光活动与日间活动可能短暂重叠。", "tag_weight_mult": {"low_light": 1.25, "daylight": 1.1}},
        {"id": "day", "name_zh": "白昼", "name_en": "Day", "fact_zh": "强光提高视觉觅食机会，也可能让警觉的鱼退向遮蔽物。", "tag_weight_mult": {"daylight": 1.35, "nocturnal": 0.65}},
        {"id": "dusk", "name_zh": "黄昏", "name_en": "Dusk", "fact_zh": "光照下降会改变捕食距离与活动边界，但不会保证咬口。", "tag_weight_mult": {"low_light": 1.4, "nocturnal": 1.15}},
        {"id": "night", "name_zh": "夜间", "name_en": "Night", "fact_zh": "视觉之外的嗅觉、侧线和电感受等线索相对更重要。", "tag_weight_mult": {"nocturnal": 1.55, "daylight": 0.6, "vertical_migrant": 1.25}},
    ]
    return phases[(S["turn"] // 2) % len(phases)]


def _eligible(fish, location_id, season_id):
    return location_id in fish["locations"] and season_id in fish["seasons"]


def _weight(fish, bait_id):
    loc = LOCATIONS[S["location_id"]]
    season = SEASONS[S["season_id"]]
    bait = BAITS[bait_id]
    condition = _current_condition()
    time_phase = _current_time()
    weight = RARITY[fish["rarity"]]["weight"] * fish.get("individual_weight", 1.0)
    for tag in fish.get("tags", []):
        weight *= loc.get("tag_weight_mult", {}).get(tag, 1.0)
        weight *= season.get("tag_weight_mult", {}).get(tag, 1.0)
        weight *= bait["effects"].get("tag_weight_mult", {}).get(tag, 1.0)
        weight *= condition.get("tag_weight_mult", {}).get(tag, 1.0)
        weight *= time_phase.get("tag_weight_mult", {}).get(tag, 1.0)
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
    return "🍃 %s结束，%s开始；鱼群活动随季节改变。\n" % (previous, next_season["name"])


def _record(fish, size, value):
    first = fish["id"] not in S["encyclopedia"]
    if first:
        S["encyclopedia"][fish["id"]] = {
            "discovered": True, "first_caught_turn": S["turn"], "count": 0,
            "max_size": 0, "total_value_earned": 0,
            "identification": "pending" if fish.get("quiz") else "verified",
            "misidentifications": 0,
        }
    entry = S["encyclopedia"][fish["id"]]
    entry["count"] += 1
    entry["max_size"] = max(entry["max_size"], size)
    entry["total_value_earned"] += value
    S["stats"]["total_caught"] += 1
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
    lines = ["%s %s / %s · %s · %scm · %d pts" %
             (prefix, fish["name_zh"], fish["name_en"], RARITY[fish["rarity"]]["label"], size, value)]
    if first:
        lines.append("🔬 " + fish["science_fact_zh"])
        lines.append("首次观察 +%d pts" % RARITY[fish["rarity"]]["bonus"])
    if fish.get("release_only"):
        lines.append("📷 测量、辨认并原地放流；记录号 %s，不进入鱼篓。" % instance)
    elif first:
        lines.append("记录号 %s，暂存鱼篓。" % instance)
    if first and fish.get("quiz"):
        lines.append("🔎 待鉴定：identify %s" % fish["id"])
    count = S["encyclopedia"][fish["id"]]["count"]
    if count == 2:
        lines.append("◉ 观察等级提升：熟悉 +5 pts")
    elif count == 3:
        lines.append("◎ 观察等级提升：深入观察 +10 pts；新的生态关系可能已经解锁。")
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
        return {"kind": "error", "text": "没有这种饵：%s" % bait_id, "consumed": False}
    if S["bait_inventory"].get(bait_id, 0) <= 0:
        return {"kind": "error", "text": "%s已经用完。" % BAITS[bait_id]["name"], "consumed": False}
    S["bait_inventory"][bait_id] -= 1
    S["turn"] += 1
    S["stats"]["total_casts"] += 1
    season_line = _advance_season()
    loc = LOCATIONS[S["location_id"]]

    # A real cast can be quiet even when target species are present.
    if rng.random() < 0.10:
        S["stats"]["empty_casts"] += 1
        return {"kind": "empty", "consumed": True,
                "text": season_line + "〰 浮漂没有形成可靠咬口。空杆也是水况记录。"}
    junk_chance = loc["junk_chance_base"] * BAITS[bait_id]["effects"].get("junk_chance_mult", 1.0)
    if rng.random() < junk_chance:
        pool = _REAL_WORLD_JUNK[S["location_id"]]
        found = pool[rng.rint(0, len(pool) - 1)]
        human_debris = any(word in found for word in ("废", "塑料", "鱼线", "渔网", "凉鞋", "铝罐", "船绳"))
        if human_debris:
            S["stats"]["debris_removed"] += 1
        key = "%s|%s" % (S["location_id"], found)
        note = S["field_observations"].setdefault(key, {"location_id": S["location_id"], "name": found, "count": 0, "human_debris": human_debris})
        note["count"] += 1
        return {"kind": "junk", "consumed": True,
                "text": season_line + "🪣 你拉上来%s。%s" % (found, "已从水域移除并记入清理日志。" if human_debris else "它也属于这片水域的自然记录。")}

    pool = [f for f in FISH.values() if _eligible(f, S["location_id"], S["season_id"])]
    if not pool:
        S["stats"]["empty_casts"] += 1
        return {"kind": "empty", "consumed": True, "text": season_line + "〰 当前季节没有适合这种调查方式的目标物种。"}
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
            results.append({"kind": "error", "text": "没有可用鱼饵，请先去 shop。", "consumed": False})
            break
        result = _cast_step(rng, chosen)
        results.append(result)
        if not result["consumed"]:
            break
        if ("new" in stop and result.get("first")) or ("rare" in stop and result.get("rare")) or ("event" in stop and result["kind"] == "junk"):
            break
    S["rngState"], S["rngCalls"] = rng.state, rng.calls
    if len(results) == 1:
        return results[0]["text"]
    highlights = [r["text"] for r in results if r.get("first") or r.get("rare")]
    counts = {kind: sum(r["kind"] == kind for r in results) for kind in ("fish", "empty", "junk")}
    summary = "🎣 批量抛竿 %d次：鱼%d · 空杆%d · 其他发现%d" % (len(results), counts["fish"], counts["empty"], counts["junk"])
    return summary + (("\n\n" + "\n——\n".join(highlights)) if highlights else "")


def _c_status():
    bait = "、".join("%s×%d" % (BAITS[bid]["name"], n) for bid, n in S["bait_inventory"].items() if bid in BAITS and n > 0) or "无"
    condition = _current_condition()
    return ("[状态] %d pts | %s · %s | 第%d回合 | 图鉴%d/%d\n"
            "时段：%s | 水况：%s | 鱼饵：%s\n鱼篓%d | 空杆%d | 保护放流%d | 清理废弃物%d") % (
                S["points"], LOCATIONS[S["location_id"]]["name"], SEASONS[S["season_id"]]["name"],
                S["turn"], len(S["encyclopedia"]), len(FISH), _current_time()["name_zh"], condition["name_zh"], bait,
                len(S["catch_inventory"]), S["stats"]["empty_casts"], S["stats"]["released"], S["stats"]["debris_removed"])


def _c_conditions():
    condition = _current_condition()
    time_phase = _current_time()
    effects = "、".join("%s ×%s" % pair for pair in condition.get("tag_weight_mult", {}).items()) or "无显著偏向"
    time_effects = "、".join("%s ×%s" % pair for pair in time_phase.get("tag_weight_mult", {}).items()) or "无显著偏向"
    return "[环境观察]\n水况：%s / %s\n%s\n水况权重：%s\n\n时段：%s / %s\n%s\n时段权重：%s\n水况每4个行动、时段每2个行动变化；查看环境不消耗随机数。" % (
        condition["name_zh"], condition["name_en"], condition["fact_zh"], effects,
        time_phase["name_zh"], time_phase["name_en"], time_phase["fact_zh"], time_effects)


def _c_shop():
    lines = ["[调查补给]"]
    for bait in BAITS.values():
        lines.append("%s · %s · %d pts — %s" % (bait["id"], bait["name"], bait["cost"], bait["description"]))
    return "\n".join(lines)


def _c_buy(bait_id, qty=1):
    if bait_id not in BAITS:
        return "没有这种补给：%s" % bait_id
    qty = max(1, min(100, int(qty)))
    cost = BAITS[bait_id]["cost"] * qty
    if cost > S["points"]:
        return "点数不足：需要%d，当前%d。" % (cost, S["points"])
    S["points"] -= cost
    S["bait_inventory"][bait_id] = S["bait_inventory"].get(bait_id, 0) + qty
    return "购入%s×%d，花费%d pts。" % (BAITS[bait_id]["name"], qty, cost)


def _c_goto(location_id=None):
    if not location_id:
        lines = ["[世界水域]"]
        for loc in LOCATIONS.values():
            state = "已解锁" if loc["id"] in S["unlocked_locations"] else "%d pts" % loc["unlock_cost"]
            lines.append("%s · %s / %s · %s" % (loc["id"], loc["name_zh"], loc["name_en"], state))
        return "\n".join(lines)
    if location_id not in LOCATIONS:
        return "没有这个地点：%s" % location_id
    loc = LOCATIONS[location_id]
    if location_id not in S["unlocked_locations"]:
        if S["points"] < loc["unlock_cost"]:
            return "解锁%s需要%d pts，当前%d。" % (loc["name"], loc["unlock_cost"], S["points"])
        S["points"] -= loc["unlock_cost"]
        S["unlocked_locations"].append(location_id)
    S["location_id"] = location_id
    return "抵达%s / %s。\n%s" % (loc["name_zh"], loc["name_en"], loc["description_zh"])


def _c_inventory():
    if not S["catch_inventory"]:
        return "[鱼篓] 空。保护物种只存在观察日志中。"
    lines = ["[鱼篓]"]
    for catch in S["catch_inventory"]:
        fish = FISH[catch["fish_id"]]
        lines.append("%s · %s %scm · %d pts" % (catch["instance_id"], fish["name"], catch["size"], catch["value"]))
    return "\n".join(lines)


def _c_sell(target):
    if not target:
        return "用法：sell all | sell <catch_id> | sell species <fish_id>"
    if target == "all":
        sold = list(S["catch_inventory"])
    elif target.startswith("species "):
        fish_id = target.split(None, 1)[1]
        sold = [c for c in S["catch_inventory"] if c["fish_id"] == fish_id]
    else:
        sold = [c for c in S["catch_inventory"] if c["instance_id"] == target]
    if not sold:
        return "没有符合条件的可出售记录。"
    ids = {c["instance_id"] for c in sold}
    S["catch_inventory"] = [c for c in S["catch_inventory"] if c["instance_id"] not in ids]
    gained = sum(c["value"] for c in sold)
    S["points"] += gained
    return "出售%d条可留存渔获，获得%d pts。图鉴观察仍然保留。" % (len(sold), gained)


def _c_encyclopedia():
    lines = ["[物种图鉴] %d/%d" % (len(S["encyclopedia"]), len(FISH))]
    for fish in FISH.values():
        if fish["id"] not in S["encyclopedia"]:
            continue
        entry = S["encyclopedia"][fish["id"]]
        mark = "✔" if entry.get("identification", "verified") == "verified" else "?"
        level_zh, _ = _observation_level(entry)
        lines.append("%s %s / %s · %s · %d次 · 最大%scm" % (mark, fish["name_zh"], fish["name_en"], level_zh, entry["count"], entry["max_size"]))
    if len(lines) == 1:
        lines.append("还没有物种观察。")
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
        object_lines = "\n[非鱼类发现]\n" + "\n".join("%s %s · %s ×%d" % (
            "🧹" if item.get("human_debris") else "◦", LOCATIONS[item["location_id"]]["name"], item["name"], item["count"]
        ) for item in observations[:12])
    return (("[观察日志] 物种%d/%d · 原生%d · 引入%d · 待鉴定%d · 深入观察%d\n"
            "保护放流%d · 纠错%d · 空杆%d · 清理废弃物%d\n"
            "用 identify <fish_id> 学习鉴别，用 look <fish_id> 阅读科普。") % (
                len(seen), len(FISH), native, introduced, pending, studied, S["stats"]["released"],
                corrections, S["stats"]["empty_casts"], S["stats"]["debris_removed"])) + object_lines


def _relationship_unlocked(relationship):
    minimum = relationship.get("min_count", 1)
    return all(S["encyclopedia"].get(fid, {}).get("count", 0) >= minimum for fid in relationship["requires"])


def _c_ecosystem():
    unlocked = [rel for rel in RELATIONSHIPS if _relationship_unlocked(rel)]
    lines = ["[生态关系网] %d/%d 已解锁" % (len(unlocked), len(RELATIONSHIPS))]
    if not unlocked:
        lines.append("继续在同一生态系统中重复观察不同物种，关系证据才会浮现。")
    for rel in unlocked:
        loc = LOCATIONS[rel["location_id"]]
        lines.append("\n◆ %s / %s" % (rel["title_zh"], rel["title_en"]))
        lines.append("  %s · %s" % (loc["name_zh"], rel["type"]))
        lines.append("  " + rel["fact_zh"])
    locked = len(RELATIONSHIPS) - len(unlocked)
    if locked:
        lines.append("\n另有%d条关系仍缺少重复观察证据。" % locked)
    return "\n".join(lines)


def _c_identify(fish_id, choice=None):
    fish = FISH.get(fish_id)
    if not fish:
        return "没有这个物种 id：%s" % fish_id
    entry = S["encyclopedia"].get(fish_id)
    if not entry:
        return "尚未观察到这个物种。"
    quiz = fish.get("quiz")
    if not quiz:
        entry["identification"] = "verified"
        return "%s不需要额外纠错题，记录已确认。" % fish["name"]
    if choice is None:
        options = "\n".join("  %d. %s" % (i + 1, text) for i, text in enumerate(quiz["choices_zh"]))
        return "[物种鉴定] %s\n%s\n%s\n回答：identify %s <编号>" % (fish["name"], quiz["question_zh"], options, fish_id)
    if not 1 <= choice <= len(quiz["choices_zh"]):
        return "选项应为1-%d。" % len(quiz["choices_zh"])
    if choice == quiz["answer"]:
        first_verify = entry.get("identification") != "verified"
        entry["identification"] = "verified"
        if first_verify:
            S["points"] += 10
        return "✅ 鉴定确认：%s\n%s%s" % (fish["name"], quiz["explanation_zh"], "\n观察奖励 +10 pts" if first_verify else "")
    entry["misidentifications"] = entry.get("misidentifications", 0) + 1
    entry["identification"] = "pending"
    return "↺ 需要修正：%s\n误判已写入观察日志。" % quiz["wrong_zh"]


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
            return "??? · 尚未观察到该物种。"
        origin = {"native": "原生", "introduced": "引入", "endemic": "特有"}.get(fish.get("native_status"), fish.get("native_status", "未记录"))
        level_zh, level_en = _observation_level(S["encyclopedia"][fish["id"]])
        return ("%s / %s (%s)\n观察等级：%s / %s\n🔬 %s\n🔎 %s\n🌿 %s · %s%s\n体长 %s-%scm") % (
            fish["name_zh"], fish["name_en"], fish["latin"], level_zh, level_en,
            fish["science_fact_zh"], fish["identification_zh"], origin, fish["conservation"],
            " · 仅观察放流" if fish.get("release_only") else "", fish["size_min"], fish["size_max"])
    loc = _find(LOCATIONS, query)
    if loc:
        return "%s / %s\n%s\n生境：%s" % (loc["name_zh"], loc["name_en"], loc["description_zh"], loc["biome"])
    bait = _find(BAITS, query)
    if bait:
        return "%s / %s · %d pts\n%s" % (bait["name"], bait["name_en"], bait["cost"], bait["description"])
    return "没有这个对象：%s" % query


_HELP = """🌍🎣 World Waters Field Journal
命令：
  status                         当前地点、水况、补给与观察统计
  conditions                     当前水况及其生态影响
  shop | buy <bait_id> [qty]     调查补给
  cast [bait_id] [N] [stop=...]  抛竿1-20次；stop=new,rare,event
  goto | goto <location_id>      世界水域与旅行解锁
  inventory | sell ...           管理可留存渔获
  encyclopedia | journal         图鉴与观察日志
  ecosystem                      已解锁的食物、栖息地、洄游与保护关系
  identify <fish_id> [choice]    纠错鉴定
  look <id_or_name>              阅读物种、地点或饵的科普记录
可用分号批量执行最多8条命令。空杆、自然物与废弃物同样是调查结果。"""


def _run_one(line):
    parts = line.strip().split()
    if not parts:
        return _HELP
    command, args = parts[0].lower(), parts[1:]
    try:
        if command in ("help", "h"):
            return _HELP
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
        return "未知命令：%s。使用 help 查看命令。" % command
    except (ValueError, IndexError) as exc:
        return "命令参数无法解析：%s" % exc


def _state_json():
    return "📊 " + json.dumps({
        "pts": S["points"], "loc": LOCATIONS[S["location_id"]]["name"],
        "sea": SEASONS[S["season_id"]]["name"], "turn": S["turn"],
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
        output = _HELP
    else:
        output = "\n\n".join(("▶ %s\n" % item if len(commands) > 1 else "") + _run_one(item) for item in commands[:8])
        if len(commands) > 8:
            output += "\n\n最多执行8条；其余%d条已忽略。" % (len(commands) - 8)
    _save()
    if _IO_WARN:
        output += "\n" + _IO_WARN
        _IO_WARN = ""
    return output + "\n" + _state_json()


def new_game(seed=_DEFAULT_SEED):
    global S
    S = _new_state(seed)
    _save()
    return "World Waters新调查已开始（seed %d）。使用 help 查看命令。" % S["seed"]
