# Text fishing game engine for deterministic AI play.
# Public API: cmd(command) returns text; new_game(seed) resets the run.
# Same seed plus the same command sequence reproduces byte-for-byte results.
# Use fishing.py when the engine should be hidden inside a blind-play bundle.
import json, os, re

# Deterministic mulberry32 PRNG.
def _imul(a, b):
    return ((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF)) & 0xFFFFFFFF

class _Rng:
    def __init__(self, state, calls=0):
        self.state = state & 0xFFFFFFFF
        self.calls = calls
    def random(self):
        self.calls += 1
        a = (self.state + 0x6D2B79F5) & 0xFFFFFFFF
        self.state = a
        t = _imul(a ^ (a >> 15), 1 | a)
        t = ((t + _imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF) ^ t
        t &= 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    def rint(self, a, b):
        return a + int(self.random() * (b - a + 1))

_DEFAULT_SEED = 0x9e3779b9

RARITY = {
    "common": {"label": "Common", "tag": "C", "weight": 1000, "discovery_bonus": 20},
    "uncommon": {"label": "Uncommon", "tag": "U", "weight": 350, "discovery_bonus": 20},
    "rare": {"label": "Rare", "tag": "R", "weight": 90, "discovery_bonus": 20},
    "epic": {"label": "Epic", "tag": "E", "weight": 22, "discovery_bonus": 20},
    "legendary": {"label": "Legendary", "tag": "L", "weight": 5, "discovery_bonus": 20},
    "mythic": {"label": "Mythic", "tag": "M", "weight": 1, "discovery_bonus": 20},
}
SEASONS = {
    "spring": {"id": "spring", "name": "Spring", "order": 0, "description": "Warm water and new blossoms wake the shoals.", "tag_weight_mult": {"freshwater": 1.15}},
    "summer": {"id": "summer", "name": "Summer", "order": 1, "description": "High sun stirs the fire-touched waters.", "tag_weight_mult": {"fire": 1.5}},
    "autumn": {"id": "autumn", "name": "Autumn", "order": 2, "description": "Cooling currents call migrating fish back through the reeds.", "tag_weight_mult": {"nocturnal": 1.2}},
    "winter": {"id": "winter", "name": "Winter", "order": 3, "description": "The world falls quiet while frost-born creatures rise from the deep.", "tag_weight_mult": {"deepsea": 1.3}},
}
LOCATIONS = {
    "mangrove_shoal": {'id': 'mangrove_shoal', 'name': 'Mangrove Shoal', 'description': 'Mangrove Shoal is a fishing stop of braided mangrove roots and warm brackish mud, small hidden ambushes. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.1, 'tag_weight_mult': {'brackish': 1.5, 'armored': 1.3}, 'unlock_cost': 320, 'available_seasons': ['spring', 'summer', 'autumn'], 'ambience': ['Braided mangrove roots frame the water while warm brackish mud carries small rings of light past your float.', 'A distant splash vanishes near small hidden ambushes, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.', 'For a moment the whole place seems to listen back before the float moves again.'], 'character': 'Mangrove Shoal rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},
    "whispering_mire": {'id': 'whispering_mire', 'name': 'Whispering Mire', 'description': 'Whispering Mire is a fishing stop of black water and peat mist, a low murmur under the roots. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.11, 'tag_weight_mult': {'swamp': 1.6, 'nocturnal': 1.3, 'poison': 1.4}, 'unlock_cost': 200, 'available_seasons': ['spring', 'summer', 'autumn'], 'ambience': ['Black water frame the water while peat mist carries small rings of light past your float.', 'A distant splash vanishes near a low murmur under the roots, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.'], 'character': 'Whispering Mire rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},
    "starry_delta": {'id': 'starry_delta', 'name': 'Starry Delta', 'description': 'Starry Delta is a fishing stop of brackish tide lines and glowing plankton, a river mouth bright as spilled stars. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.09, 'tag_weight_mult': {'brackish': 1.3, 'glowing': 1.4, 'migratory': 1.6}, 'unlock_cost': 480, 'available_seasons': ['spring', 'autumn'], 'ambience': ['Brackish tide lines frame the water while glowing plankton carries small rings of light past your float.', 'A distant splash vanishes near a river mouth bright as spilled stars, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.'], 'character': 'Starry Delta rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},
    "sunken_ruins": {'id': 'sunken_ruins', 'name': 'Sunken Ruins', 'description': 'Sunken Ruins is a fishing stop of broken columns and cold blue tide, a drowned city remembering its bells. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.08, 'tag_weight_mult': {'deepsea': 1.4, 'ancient': 1.7, 'glowing': 1.3}, 'unlock_cost': 650, 'available_seasons': ['autumn', 'winter'], 'ambience': ['Broken columns frame the water while cold blue tide carries small rings of light past your float.', 'A distant splash vanishes near a drowned city remembering its bells, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.'], 'character': 'Sunken Ruins rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},
    "geyser_falls": {'id': 'geyser_falls', 'name': 'Geyser Falls', 'description': 'Geyser Falls is a fishing stop of steaming terraces and rainbow mineral crust, warm falls rumbling below your boots. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.1, 'tag_weight_mult': {'fire': 1.4, 'mineral': 1.6}, 'unlock_cost': 400, 'available_seasons': ['spring', 'summer', 'autumn', 'winter'], 'ambience': ['Steaming terraces frame the water while rainbow mineral crust carries small rings of light past your float.', 'A distant splash vanishes near warm falls rumbling below your boots, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.'], 'character': 'Geyser Falls rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},
    "crystal_cave": {'id': 'crystal_cave', 'name': 'Crystal Cave', 'description': 'Crystal Cave is a fishing stop of six-sided crystal pillars and clear echoes, a cave that scatters every lamp into rainbows. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.07, 'tag_weight_mult': {'crystal': 1.7, 'glowing': 1.4}, 'unlock_cost': 800, 'available_seasons': ['spring', 'summer', 'autumn', 'winter'], 'ambience': ['Six-sided crystal pillars frame the water while clear echoes carries small rings of light past your float.', 'A distant splash vanishes near a cave that scatters every lamp into rainbows, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.', 'For a moment the whole place seems to listen back before the float moves again.'], 'character': 'Crystal Cave rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},

    "moonlit_pond": {'id': 'moonlit_pond', 'name': 'Moonlit Pond', 'description': 'Moonlit Pond is a fishing stop of moonlit stones and still silver water, a hush that feels older than dusk. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.1, 'tag_weight_mult': {'freshwater': 1.2, 'nocturnal': 1.5}, 'unlock_cost': 0, 'available_seasons': ['spring', 'summer', 'autumn', 'winter'], 'ambience': ['Moonlit stones frame the water while still silver water carries small rings of light past your float.', 'A distant splash vanishes near a hush that feels older than dusk, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.'], 'character': 'Moonlit Pond rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},
    "reed_river": {'id': 'reed_river', 'name': 'Reed River', 'description': 'Reed River is a fishing stop of reed beds and clear shallows, a patient training water. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.12, 'tag_weight_mult': {'freshwater': 1.3}, 'unlock_cost': 0, 'available_seasons': ['spring', 'summer', 'autumn', 'winter'], 'ambience': ['Reed beds frame the water while clear shallows carries small rings of light past your float.', 'A distant splash vanishes near a patient training water, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.'], 'character': 'Reed River rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},
    "abyssal_trench": {'id': 'abyssal_trench', 'name': 'Abyssal Trench', 'description': 'Abyssal Trench is a fishing stop of black pressure and distant whale-song, a trench where light becomes a rumor. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.08, 'tag_weight_mult': {'deepsea': 1.5, 'glowing': 1.4}, 'unlock_cost': 300, 'available_seasons': ['spring', 'summer', 'autumn', 'winter'], 'ambience': ['Black pressure frame the water while distant whale-song carries small rings of light past your float.', 'A distant splash vanishes near a trench where light becomes a rumor, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.', 'For a moment the whole place seems to listen back before the float moves again.'], 'character': 'Abyssal Trench rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},
    "floating_lake": {'id': 'floating_lake', 'name': 'Floating Lake', 'description': 'Floating Lake is a fishing stop of cloud shadow and weightless water, a lake hanging above the world. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.09, 'tag_weight_mult': {'fantasy': 1.4, 'wind': 1.5}, 'unlock_cost': 600, 'available_seasons': ['spring', 'summer', 'autumn'], 'ambience': ['Cloud shadow frame the water while weightless water carries small rings of light past your float.', 'A distant splash vanishes near a lake hanging above the world, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.'], 'character': 'Floating Lake rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},
    "lava_spring": {'id': 'lava_spring', 'name': 'Lava Spring', 'description': 'Lava Spring is a fishing stop of orange bubbles and mineral heat, a summer spring that breathes fire. It keeps the warmth of real travel while leaving one foot in folklore.', 'junk_chance_base': 0.1, 'tag_weight_mult': {'fire': 1.6}, 'unlock_cost': 550, 'available_seasons': ['summer'], 'ambience': ['Orange bubbles frame the water while mineral heat carries small rings of light past your float.', 'A distant splash vanishes near a summer spring that breathes fire, leaving a patient ripple and the smell of wet earth.', 'Your line hums in the breeze; somewhere below, a hidden fish turns once and disappears.', "The shore settles into a traveler's quiet, half campfire comfort and half old map mystery.", 'Mineral, leaf, and salt notes drift together as the water keeps its secrets close.'], 'character': 'Lava Spring rewards patience: ordinary catches train the hand, while rare shadows make the journey worth retelling.'},
}
# Dive ambience by location and season; sampled at the top of dive results.
for _lid, _amb in json.loads(r"""{
 "reed_river": {
  "spring": [
   "You slip below Reed River in Spring; clear shallows folds around your suit, and the world above turns to a soft lantern.",
   "Under Reed River, spring light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through reed beds, breathing steadily as a patient training water opens below like a page from a travel journal."
  ],
  "summer": [
   "You slip below Reed River in Summer; clear shallows folds around your suit, and the world above turns to a soft lantern.",
   "Under Reed River, summer light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through reed beds, breathing steadily as a patient training water opens below like a page from a travel journal."
  ],
  "autumn": [
   "You slip below Reed River in Autumn; clear shallows folds around your suit, and the world above turns to a soft lantern.",
   "Under Reed River, autumn light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through reed beds, breathing steadily as a patient training water opens below like a page from a travel journal."
  ],
  "winter": [
   "You slip below Reed River in Winter; clear shallows folds around your suit, and the world above turns to a soft lantern.",
   "Under Reed River, winter light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through reed beds, breathing steadily as a patient training water opens below like a page from a travel journal."
  ]
 },
 "moonlit_pond": {
  "spring": [
   "You slip below Moonlit Pond in Spring; still silver water folds around your suit, and the world above turns to a soft lantern.",
   "Under Moonlit Pond, spring light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through moonlit stones, breathing steadily as a hush that feels older than dusk opens below like a page from a travel journal."
  ],
  "summer": [
   "You slip below Moonlit Pond in Summer; still silver water folds around your suit, and the world above turns to a soft lantern.",
   "Under Moonlit Pond, summer light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through moonlit stones, breathing steadily as a hush that feels older than dusk opens below like a page from a travel journal."
  ],
  "autumn": [
   "You slip below Moonlit Pond in Autumn; still silver water folds around your suit, and the world above turns to a soft lantern.",
   "Under Moonlit Pond, autumn light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through moonlit stones, breathing steadily as a hush that feels older than dusk opens below like a page from a travel journal."
  ],
  "winter": [
   "You slip below Moonlit Pond in Winter; still silver water folds around your suit, and the world above turns to a soft lantern.",
   "Under Moonlit Pond, winter light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through moonlit stones, breathing steadily as a hush that feels older than dusk opens below like a page from a travel journal."
  ]
 },
 "whispering_mire": {
  "spring": [
   "You slip below Whispering Mire in Spring; peat and mist folds around your suit, and the world above turns to a soft lantern.",
   "Under Whispering Mire, spring light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through black water, breathing steadily as a low murmur under the roots opens below like a page from a travel journal."
  ],
  "summer": [
   "You slip below Whispering Mire in Summer; peat and mist folds around your suit, and the world above turns to a soft lantern.",
   "Under Whispering Mire, summer light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through black water, breathing steadily as a low murmur under the roots opens below like a page from a travel journal."
  ],
  "autumn": [
   "You slip below Whispering Mire in Autumn; peat and mist folds around your suit, and the world above turns to a soft lantern.",
   "Under Whispering Mire, autumn light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through black water, breathing steadily as a low murmur under the roots opens below like a page from a travel journal."
  ]
 },
 "starry_delta": {
  "spring": [
   "You slip below Starry Delta in Spring; glowing plankton folds around your suit, and the world above turns to a soft lantern.",
   "Under Starry Delta, spring light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through brackish tide lines, breathing steadily as a river mouth bright as spilled stars opens below like a page from a travel journal."
  ],
  "autumn": [
   "You slip below Starry Delta in Autumn; glowing plankton folds around your suit, and the world above turns to a soft lantern.",
   "Under Starry Delta, autumn light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through brackish tide lines, breathing steadily as a river mouth bright as spilled stars opens below like a page from a travel journal."
  ]
 },
 "mangrove_shoal": {
  "spring": [
   "You slip below Mangrove Shoal in Spring; warm brackish mud folds around your suit, and the world above turns to a soft lantern.",
   "Under Mangrove Shoal, spring light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through braided mangrove roots, breathing steadily as small hidden ambushes opens below like a page from a travel journal."
  ],
  "summer": [
   "You slip below Mangrove Shoal in Summer; warm brackish mud folds around your suit, and the world above turns to a soft lantern.",
   "Under Mangrove Shoal, summer light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through braided mangrove roots, breathing steadily as small hidden ambushes opens below like a page from a travel journal."
  ],
  "autumn": [
   "You slip below Mangrove Shoal in Autumn; warm brackish mud folds around your suit, and the world above turns to a soft lantern.",
   "Under Mangrove Shoal, autumn light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through braided mangrove roots, breathing steadily as small hidden ambushes opens below like a page from a travel journal."
  ]
 },
 "floating_lake": {
  "spring": [
   "You slip below Floating Lake in Spring; weightless water folds around your suit, and the world above turns to a soft lantern.",
   "Under Floating Lake, spring light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through cloud shadow, breathing steadily as a lake hanging above the world opens below like a page from a travel journal."
  ],
  "summer": [
   "You slip below Floating Lake in Summer; weightless water folds around your suit, and the world above turns to a soft lantern.",
   "Under Floating Lake, summer light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through cloud shadow, breathing steadily as a lake hanging above the world opens below like a page from a travel journal."
  ],
  "autumn": [
   "You slip below Floating Lake in Autumn; weightless water folds around your suit, and the world above turns to a soft lantern.",
   "Under Floating Lake, autumn light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through cloud shadow, breathing steadily as a lake hanging above the world opens below like a page from a travel journal."
  ]
 },
 "lava_spring": {
  "summer": [
   "You slip below Lava Spring in Summer; mineral heat folds around your suit, and the world above turns to a soft lantern.",
   "Under Lava Spring, summer light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through orange bubbles, breathing steadily as a summer spring that breathes fire opens below like a page from a travel journal."
  ]
 },
 "geyser_falls": {
  "spring": [
   "You slip below Geyser Falls in Spring; rainbow mineral crust folds around your suit, and the world above turns to a soft lantern.",
   "Under Geyser Falls, spring light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through steaming terraces, breathing steadily as warm falls that rumble below your boots opens below like a page from a travel journal."
  ],
  "summer": [
   "You slip below Geyser Falls in Summer; rainbow mineral crust folds around your suit, and the world above turns to a soft lantern.",
   "Under Geyser Falls, summer light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through steaming terraces, breathing steadily as warm falls that rumble below your boots opens below like a page from a travel journal."
  ],
  "autumn": [
   "You slip below Geyser Falls in Autumn; rainbow mineral crust folds around your suit, and the world above turns to a soft lantern.",
   "Under Geyser Falls, autumn light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through steaming terraces, breathing steadily as warm falls that rumble below your boots opens below like a page from a travel journal."
  ],
  "winter": [
   "You slip below Geyser Falls in Winter; rainbow mineral crust folds around your suit, and the world above turns to a soft lantern.",
   "Under Geyser Falls, winter light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through steaming terraces, breathing steadily as warm falls that rumble below your boots opens below like a page from a travel journal."
  ]
 },
 "sunken_ruins": {
  "autumn": [
   "You slip below Sunken Ruins in Autumn; cold blue tide folds around your suit, and the world above turns to a soft lantern.",
   "Under Sunken Ruins, autumn light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through broken columns, breathing steadily as a drowned city remembering its bells opens below like a page from a travel journal."
  ],
  "winter": [
   "You slip below Sunken Ruins in Winter; cold blue tide folds around your suit, and the world above turns to a soft lantern.",
   "Under Sunken Ruins, winter light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through broken columns, breathing steadily as a drowned city remembering its bells opens below like a page from a travel journal."
  ]
 },
 "abyssal_trench": {
  "spring": [
   "You slip below Abyssal Trench in Spring; distant whale-song folds around your suit, and the world above turns to a soft lantern.",
   "Under Abyssal Trench, spring light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through black pressure, breathing steadily as a trench where light becomes a rumor opens below like a page from a travel journal."
  ],
  "summer": [
   "You slip below Abyssal Trench in Summer; distant whale-song folds around your suit, and the world above turns to a soft lantern.",
   "Under Abyssal Trench, summer light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through black pressure, breathing steadily as a trench where light becomes a rumor opens below like a page from a travel journal."
  ],
  "autumn": [
   "You slip below Abyssal Trench in Autumn; distant whale-song folds around your suit, and the world above turns to a soft lantern.",
   "Under Abyssal Trench, autumn light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through black pressure, breathing steadily as a trench where light becomes a rumor opens below like a page from a travel journal."
  ],
  "winter": [
   "You slip below Abyssal Trench in Winter; distant whale-song folds around your suit, and the world above turns to a soft lantern.",
   "Under Abyssal Trench, winter light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through black pressure, breathing steadily as a trench where light becomes a rumor opens below like a page from a travel journal."
  ]
 },
 "crystal_cave": {
  "spring": [
   "You slip below Crystal Cave in Spring; clear echoes folds around your suit, and the world above turns to a soft lantern.",
   "Under Crystal Cave, spring light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through six-sided crystal pillars, breathing steadily as a cave that scatters every lamp into rainbows opens below like a page from a travel journal."
  ],
  "summer": [
   "You slip below Crystal Cave in Summer; clear echoes folds around your suit, and the world above turns to a soft lantern.",
   "Under Crystal Cave, summer light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through six-sided crystal pillars, breathing steadily as a cave that scatters every lamp into rainbows opens below like a page from a travel journal."
  ],
  "autumn": [
   "You slip below Crystal Cave in Autumn; clear echoes folds around your suit, and the world above turns to a soft lantern.",
   "Under Crystal Cave, autumn light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through six-sided crystal pillars, breathing steadily as a cave that scatters every lamp into rainbows opens below like a page from a travel journal."
  ],
  "winter": [
   "You slip below Crystal Cave in Winter; clear echoes folds around your suit, and the world above turns to a soft lantern.",
   "Under Crystal Cave, winter light breaks into moving shards while roots, stones, and fish tracks guide your hands.",
   "You dive through six-sided crystal pillars, breathing steadily as a cave that scatters every lamp into rainbows opens below like a page from a travel journal."
  ]
 }
}""").items():
    if _lid in LOCATIONS: LOCATIONS[_lid]["dive_ambience"] = _amb

FISH = {
    "mud_carp": {'id': 'mud_carp', 'name': 'Mud Carp', 'rarity': 'common', 'description': 'A common catch shaped by freshwater. Mud Carp brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 10, 'size_max': 35, 'size_unit': 'cm', 'base_value': 6, 'locations': ['moonlit_pond', 'reed_river', 'whispering_mire', 'starry_delta'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['freshwater'], 'latin': 'Cyprinus limosus'},
    "ghost_shrimp": {'id': 'ghost_shrimp', 'name': 'Ghost Shrimp', 'rarity': 'common', 'description': 'A common catch shaped by freshwater, nocturnal. Ghost Shrimp brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 3, 'size_max': 12, 'size_unit': 'cm', 'base_value': 5, 'locations': ['moonlit_pond', 'reed_river', 'mangrove_shoal', 'whispering_mire', 'starry_delta'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['freshwater', 'nocturnal'], 'latin': 'Palaemon spectra'},
    "flicker_minnow": {'id': 'flicker_minnow', 'name': 'Flicker Minnow', 'rarity': 'common', 'description': 'A common catch shaped by freshwater, nocturnal. Flicker Minnow brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 4, 'size_max': 14, 'size_unit': 'cm', 'base_value': 4, 'locations': ['moonlit_pond', 'reed_river'], 'seasons': ['spring', 'summer', 'autumn'], 'tags': ['freshwater', 'nocturnal'], 'latin': 'Leucaspius micans'},
    "angler_fry": {'id': 'angler_fry', 'name': 'Angler Fry', 'rarity': 'common', 'description': 'A common catch shaped by deepsea, glowing. Angler Fry brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 4, 'size_max': 18, 'size_unit': 'cm', 'base_value': 7, 'locations': ['abyssal_trench', 'sunken_ruins'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['deepsea', 'glowing'], 'latin': 'Antennarius lumen'},
    "sky_skipper": {'id': 'sky_skipper', 'name': 'Sky Skipper', 'rarity': 'common', 'description': 'A common catch shaped by fantasy, wind. Sky Skipper brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 8, 'size_max': 22, 'size_unit': 'cm', 'base_value': 7, 'locations': ['floating_lake', 'starry_delta'], 'seasons': ['spring', 'summer', 'autumn'], 'tags': ['fantasy', 'wind'], 'latin': 'Exocoetus aetherius'},
    "frost_drifter": {'id': 'frost_drifter', 'name': 'Frost Drifter', 'rarity': 'common', 'description': 'A common catch shaped by fantasy, wind. Frost Drifter brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 6, 'size_max': 20, 'size_unit': 'cm', 'base_value': 6, 'locations': ['floating_lake', 'starry_delta'], 'seasons': ['autumn'], 'tags': ['fantasy', 'wind'], 'latin': 'Coregonus glacies'},
    "scorched_tetra": {'id': 'scorched_tetra', 'name': 'Scorched Tetra', 'rarity': 'common', 'description': 'A common catch shaped by fire. Scorched Tetra brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 5, 'size_max': 15, 'size_unit': 'cm', 'base_value': 8, 'locations': ['lava_spring', 'geyser_falls'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['fire'], 'latin': 'Hyphessobrycon cineris'},
    "shard_fish": {'id': 'shard_fish', 'name': 'Shard Fish', 'rarity': 'common', 'description': 'A common catch shaped by crystal, glowing. Shard Fish brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 7, 'size_max': 18, 'size_unit': 'cm', 'base_value': 7, 'locations': ['crystal_cave'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['crystal', 'glowing'], 'latin': 'Vitreochromis aculeus'},
    "jelly_phantom": {'id': 'jelly_phantom', 'name': 'Jelly Phantom', 'rarity': 'common', 'description': 'A common catch shaped by fantasy, glowing. Jelly Phantom brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 8, 'size_max': 25, 'size_unit': 'cm', 'base_value': 6, 'locations': ['floating_lake', 'crystal_cave'], 'seasons': ['spring', 'summer'], 'tags': ['fantasy', 'glowing'], 'latin': 'Cnidaria umbra'},
    "winter_cinder": {'id': 'winter_cinder', 'name': 'Winter Cinder', 'rarity': 'common', 'description': 'A common catch shaped by fire. Winter Cinder brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 5, 'size_max': 14, 'size_unit': 'cm', 'base_value': 6, 'locations': ['lava_spring', 'geyser_falls'], 'seasons': ['winter'], 'tags': ['fire'], 'latin': 'Salvelinus favilla'},
    "silver_pike": {'id': 'silver_pike', 'name': 'Silver Pike', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by freshwater. Silver Pike brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 20, 'size_max': 55, 'size_unit': 'cm', 'base_value': 26, 'locations': ['moonlit_pond', 'reed_river'], 'seasons': ['spring', 'autumn'], 'tags': ['freshwater'], 'latin': 'Esox argyronotus'},
    "dusk_eel": {'id': 'dusk_eel', 'name': 'Dusk Eel', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by freshwater, nocturnal. Dusk Eel brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 25, 'size_max': 60, 'size_unit': 'cm', 'base_value': 24, 'locations': ['moonlit_pond', 'reed_river', 'mangrove_shoal', 'whispering_mire'], 'seasons': ['spring', 'autumn'], 'tags': ['freshwater', 'nocturnal'], 'latin': 'Anguilla crepusculum'},
    "copper_bream": {'id': 'copper_bream', 'name': 'Copper Bream', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by freshwater, armored. Copper Bream brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 18, 'size_max': 45, 'size_unit': 'cm', 'base_value': 22, 'locations': ['moonlit_pond', 'reed_river', 'whispering_mire'], 'seasons': ['summer', 'autumn'], 'tags': ['freshwater', 'armored'], 'latin': 'Abramis cupreus'},
    "cinder_loach": {'id': 'cinder_loach', 'name': 'Cinder Loach', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by fire. Cinder Loach brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 10, 'size_max': 28, 'size_unit': 'cm', 'base_value': 28, 'locations': ['lava_spring', 'geyser_falls'], 'seasons': ['spring', 'summer', 'autumn'], 'tags': ['fire'], 'latin': 'Barbatula favilla'},
    "deep_sculpin": {'id': 'deep_sculpin', 'name': 'Deep Sculpin', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by deepsea, armored. Deep Sculpin brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 15, 'size_max': 40, 'size_unit': 'cm', 'base_value': 30, 'locations': ['abyssal_trench', 'sunken_ruins'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['deepsea', 'armored'], 'latin': 'Cottus abyssorum'},
    "mangrove_snapper": {'id': 'mangrove_snapper', 'name': 'Mangrove Snapper', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by brackish, armored. Mangrove Snapper brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 20, 'size_max': 50, 'size_unit': 'cm', 'base_value': 25, 'locations': ['mangrove_shoal'], 'seasons': ['spring', 'summer', 'autumn'], 'tags': ['brackish', 'armored'], 'latin': 'Lutjanus rhizophorus'},
    "winter_betta": {'id': 'winter_betta', 'name': 'Winter Betta', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by freshwater, fantasy. Winter Betta brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 12, 'size_max': 30, 'size_unit': 'cm', 'base_value': 27, 'locations': ['moonlit_pond', 'reed_river', 'floating_lake', 'starry_delta'], 'seasons': ['winter'], 'tags': ['freshwater', 'fantasy'], 'latin': 'Betta glacies'},
    "zephyr_dancer": {'id': 'zephyr_dancer', 'name': 'Zephyr Dancer', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by wind, fantasy. Zephyr Dancer brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 15, 'size_max': 40, 'size_unit': 'cm', 'base_value': 24, 'locations': ['floating_lake', 'starry_delta'], 'seasons': ['spring', 'summer', 'autumn'], 'tags': ['wind', 'fantasy'], 'latin': 'Danio zephyrus'},
    "geyser_wyrm": {'id': 'geyser_wyrm', 'name': 'Geyser Wyrm', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by fire, fantasy. Geyser Wyrm brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 30, 'size_max': 80, 'size_unit': 'cm', 'base_value': 29, 'locations': ['lava_spring', 'geyser_falls'], 'seasons': ['winter'], 'tags': ['fire', 'fantasy'], 'latin': 'Thermophis geysiris'},
    "crystal_angler": {'id': 'crystal_angler', 'name': 'Crystal Angler', 'rarity': 'rare', 'description': 'A rare catch shaped by deepsea, glowing, crystal. Crystal Angler brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 15, 'size_max': 45, 'size_unit': 'cm', 'base_value': 100, 'locations': ['crystal_cave', 'abyssal_trench'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['deepsea', 'glowing', 'crystal'], 'latin': 'Cryptopsaras crystallus'},
    "stormray": {'id': 'stormray', 'name': 'Stormray', 'rarity': 'rare', 'description': 'A rare catch shaped by fantasy, wind, electric. Stormray brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 40, 'size_max': 80, 'size_unit': 'cm', 'base_value': 110, 'locations': ['floating_lake', 'starry_delta'], 'seasons': ['spring', 'autumn'], 'tags': ['fantasy', 'wind', 'electric'], 'latin': 'Dasyatis tempestas'},
    "magma_salamander": {'id': 'magma_salamander', 'name': 'Magma Salamander', 'rarity': 'rare', 'description': 'A rare catch shaped by fire, fantasy. Magma Salamander brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 25, 'size_max': 55, 'size_unit': 'cm', 'base_value': 120, 'locations': ['lava_spring', 'geyser_falls'], 'seasons': ['spring', 'summer', 'autumn'], 'tags': ['fire', 'fantasy'], 'latin': 'Ambystoma magmaticum'},
    "void_jellyfish": {'id': 'void_jellyfish', 'name': 'Void Jellyfish', 'rarity': 'epic', 'description': 'An epic catch shaped by deepsea, glowing, shadow. Void Jellyfish brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 50, 'size_max': 90, 'size_unit': 'cm', 'base_value': 200, 'locations': ['abyssal_trench', 'sunken_ruins'], 'seasons': ['autumn', 'winter'], 'tags': ['deepsea', 'glowing', 'shadow'], 'latin': 'Umbraxerxes voidus'},
    "cloud_serpent": {'id': 'cloud_serpent', 'name': 'Cloud Serpent', 'rarity': 'epic', 'description': 'An epic catch shaped by fantasy, wind, migratory. Cloud Serpent brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 60, 'size_max': 130, 'size_unit': 'cm', 'base_value': 220, 'locations': ['floating_lake', 'starry_delta'], 'seasons': ['spring'], 'tags': ['fantasy', 'wind', 'migratory'], 'latin': 'Nephropterus nubigena'},
    "ember_barb": {'id': 'ember_barb', 'name': 'Ember Barb', 'rarity': 'epic', 'description': 'An epic catch shaped by fire, armored. Ember Barb brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 35, 'size_max': 65, 'size_unit': 'cm', 'base_value': 180, 'locations': ['lava_spring', 'geyser_falls'], 'seasons': ['summer'], 'tags': ['fire', 'armored'], 'latin': 'Barbus pruna'},
    "moon_phoenix_fish": {'id': 'moon_phoenix_fish', 'name': 'Moon Phoenix Fish', 'rarity': 'legendary', 'description': 'A legendary catch carried in dockside rumor. When Moon Phoenix Fish rises from the water, the whole trip feels larger than the map.', 'size_min': 50, 'size_max': 90, 'size_unit': 'cm', 'base_value': 450, 'locations': ['moonlit_pond'], 'seasons': ['winter'], 'tags': ['freshwater', 'nocturnal', 'fantasy'], 'latin': 'Lunapterus phoeniceus', 'rumor': 'Old anglers say Moon Phoenix Fish appears only when the season, the journey, and a little impossible luck all agree.'},
    "starwhale": {'id': 'starwhale', 'name': 'Starwhale', 'rarity': 'legendary', 'description': 'A legendary catch carried in dockside rumor. When Starwhale rises from the water, the whole trip feels larger than the map.', 'size_min': 200, 'size_max': 450, 'size_unit': 'cm', 'base_value': 480, 'locations': ['abyssal_trench', 'floating_lake'], 'seasons': ['winter'], 'tags': ['deepsea', 'fantasy', 'glowing'], 'latin': 'Cetus astralis', 'rumor': 'Old anglers say Starwhale appears only when the season, the journey, and a little impossible luck all agree.'},
    "time_eater": {'id': 'time_eater', 'name': 'Time Eater', 'rarity': 'mythic', 'description': 'A mythic catch carried in dockside rumor. When Time Eater rises from the water, the whole trip feels larger than the map.', 'size_min': 1, 'size_max': 999, 'size_unit': 'cm', 'base_value': 1000, 'locations': ['all'], 'seasons': ['all'], 'tags': ['fantasy', 'shadow', 'deepsea'], 'individual_weight': 0.3, 'latin': 'Chronoichthys devorans', 'rumor': 'Old anglers say Time Eater appears only when the season, the journey, and a little impossible luck all agree.'},
    "bog_creeper": {'id': 'bog_creeper', 'name': 'Bog Creeper', 'rarity': 'common', 'description': 'A common catch shaped by freshwater, swamp, nocturnal. Bog Creeper brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 8, 'size_max': 22, 'size_unit': 'cm', 'base_value': 7, 'locations': ['whispering_mire'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['freshwater', 'swamp', 'nocturnal'], 'latin': 'Misgurnus palustris'},
    "bloat_toadfish": {'id': 'bloat_toadfish', 'name': 'Bloat Toadfish', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by freshwater, swamp, poison. Bloat Toadfish brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 15, 'size_max': 38, 'size_unit': 'cm', 'base_value': 27, 'locations': ['whispering_mire'], 'seasons': ['spring', 'summer', 'autumn'], 'tags': ['freshwater', 'swamp', 'poison'], 'latin': 'Opsanus tumidus'},
    "wraithwood_fish": {'id': 'wraithwood_fish', 'name': 'Wraithwood Fish', 'rarity': 'rare', 'description': 'A rare catch shaped by freshwater, swamp, nocturnal. Wraithwood Fish brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 25, 'size_max': 55, 'size_unit': 'cm', 'base_value': 105, 'locations': ['whispering_mire'], 'seasons': ['spring', 'autumn'], 'tags': ['freshwater', 'swamp', 'nocturnal', 'poison'], 'latin': 'Xylopsychus umbra'},
    "star_sand_darter": {'id': 'star_sand_darter', 'name': 'Star Sand Darter', 'rarity': 'common', 'description': 'A common catch shaped by brackish, glowing, migratory. Star Sand Darter brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 6, 'size_max': 16, 'size_unit': 'cm', 'base_value': 7, 'locations': ['starry_delta'], 'seasons': ['spring', 'autumn'], 'tags': ['brackish', 'glowing', 'migratory'], 'latin': 'Ammocrypta siderea'},
    "tidal_trout": {'id': 'tidal_trout', 'name': 'Tidal Trout', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by brackish, migratory, fantasy. Tidal Trout brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 30, 'size_max': 60, 'size_unit': 'cm', 'base_value': 26, 'locations': ['starry_delta'], 'seasons': ['spring', 'autumn'], 'tags': ['brackish', 'migratory', 'fantasy'], 'latin': 'Salmo aestuarium'},
    "star_barge_whisker": {'id': 'star_barge_whisker', 'name': 'Star Barge Whisker', 'rarity': 'epic', 'description': 'An epic catch shaped by brackish, fantasy, glowing. Star Barge Whisker brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 120, 'size_max': 220, 'size_unit': 'cm', 'base_value': 220, 'locations': ['starry_delta'], 'seasons': ['spring'], 'tags': ['brackish', 'fantasy', 'glowing', 'migratory'], 'latin': 'Astroglanis grandis'},
    "urn_hermit": {'id': 'urn_hermit', 'name': 'Urn Hermit', 'rarity': 'common', 'description': 'A common catch shaped by deepsea, ancient. Urn Hermit brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 5, 'size_max': 15, 'size_unit': 'cm', 'base_value': 6, 'locations': ['sunken_ruins'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['deepsea', 'ancient'], 'latin': 'Coenobita urna'},
    "rune_cod": {'id': 'rune_cod', 'name': 'Rune Cod', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by deepsea, ancient, glowing. Rune Cod brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 30, 'size_max': 65, 'size_unit': 'cm', 'base_value': 28, 'locations': ['sunken_ruins'], 'seasons': ['autumn', 'winter'], 'tags': ['deepsea', 'ancient', 'glowing'], 'latin': 'Gadus runicus'},
    "sunken_wraith": {'id': 'sunken_wraith', 'name': 'Sunken Wraith', 'rarity': 'epic', 'description': 'An epic catch shaped by deepsea, ancient, glowing. Sunken Wraith brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 70, 'size_max': 130, 'size_unit': 'cm', 'base_value': 230, 'locations': ['sunken_ruins'], 'seasons': ['autumn', 'winter'], 'tags': ['deepsea', 'ancient', 'glowing', 'shadow'], 'latin': 'Phantomoichthys submergus'},
    "sulfur_killie": {'id': 'sulfur_killie', 'name': 'Sulfur Killie', 'rarity': 'common', 'description': 'A common catch shaped by fire, mineral. Sulfur Killie brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 4, 'size_max': 12, 'size_unit': 'cm', 'base_value': 8, 'locations': ['geyser_falls'], 'seasons': ['summer', 'autumn'], 'tags': ['fire', 'mineral'], 'latin': 'Fundulus sulpureus'},
    "steam_ray": {'id': 'steam_ray', 'name': 'Steam Ray', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by fire, mineral. Steam Ray brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 35, 'size_max': 70, 'size_unit': 'cm', 'base_value': 29, 'locations': ['geyser_falls'], 'seasons': ['spring', 'summer'], 'tags': ['fire', 'mineral'], 'latin': 'Rajella vaporis'},
    "magma_peacock_bass": {'id': 'magma_peacock_bass', 'name': 'Magma Peacock Bass', 'rarity': 'rare', 'description': 'A rare catch shaped by fire, mineral, fantasy. Magma Peacock Bass brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 28, 'size_max': 52, 'size_unit': 'cm', 'base_value': 110, 'locations': ['geyser_falls'], 'seasons': ['summer'], 'tags': ['fire', 'mineral', 'fantasy'], 'latin': 'Cichla ignis'},
    "mudskipper_perch": {'id': 'mudskipper_perch', 'name': 'Mudskipper Perch', 'rarity': 'common', 'description': 'A common catch shaped by brackish, armored. Mudskipper Perch brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 12, 'size_max': 28, 'size_unit': 'cm', 'base_value': 6, 'locations': ['mangrove_shoal'], 'seasons': ['spring', 'summer', 'autumn'], 'tags': ['brackish', 'armored'], 'latin': 'Periophthalmus lutarius'},
    "root_dragon": {'id': 'root_dragon', 'name': 'Root Dragon', 'rarity': 'rare', 'description': 'A rare catch shaped by brackish, fantasy. Root Dragon brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 40, 'size_max': 75, 'size_unit': 'cm', 'base_value': 95, 'locations': ['mangrove_shoal'], 'seasons': ['spring', 'summer'], 'tags': ['brackish', 'fantasy'], 'latin': 'Rhizophydra pneumatophora'},
    "prism_lanternfish": {'id': 'prism_lanternfish', 'name': 'Prism Lanternfish', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by crystal, glowing. Prism Lanternfish brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 10, 'size_max': 25, 'size_unit': 'cm', 'base_value': 28, 'locations': ['crystal_cave'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['crystal', 'glowing'], 'latin': 'Myctophum prismaticum'},
    "shard_shrimp": {'id': 'shard_shrimp', 'name': 'Shard Shrimp', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by crystal, armored. Shard Shrimp brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 12, 'size_max': 30, 'size_unit': 'cm', 'base_value': 30, 'locations': ['crystal_cave'], 'seasons': ['spring', 'summer', 'autumn', 'winter'], 'tags': ['crystal', 'armored'], 'latin': 'Caridina vitreus'},
    "crystal_leviathan": {'id': 'crystal_leviathan', 'name': 'Crystal Leviathan', 'rarity': 'legendary', 'description': 'A legendary catch carried in dockside rumor. When Crystal Leviathan rises from the water, the whole trip feels larger than the map.', 'size_min': 150, 'size_max': 280, 'size_unit': 'cm', 'base_value': 480, 'locations': ['crystal_cave'], 'seasons': ['winter'], 'tags': ['crystal', 'glowing', 'fantasy'], 'individual_weight': 0.6, 'latin': 'Crystallosaurus antricola', 'rumor': 'Old anglers say Crystal Leviathan appears only when the season, the journey, and a little impossible luck all agree.'},

    "crucian": {'id': 'crucian', 'name': 'Crucian', 'rarity': 'common', 'description': 'A common catch shaped by freshwater. Crucian brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 8, 'size_max': 25, 'size_unit': 'cm', 'base_value': 6, 'locations': ['moonlit_pond', 'reed_river'], 'seasons': ['all'], 'tags': ['freshwater'], 'latin': 'Carassius carassius'},
    "silver_dace": {'id': 'silver_dace', 'name': 'Silver Dace', 'rarity': 'common', 'description': 'A common catch shaped by freshwater. Silver Dace brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 6, 'size_max': 18, 'size_unit': 'cm', 'base_value': 5, 'locations': ['reed_river'], 'seasons': ['all'], 'tags': ['freshwater'], 'latin': 'Rhinichthys argenteus'},
    "reed_perch": {'id': 'reed_perch', 'name': 'Reed Perch', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by freshwater. Reed Perch brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 15, 'size_max': 40, 'size_unit': 'cm', 'base_value': 22, 'locations': ['reed_river', 'moonlit_pond'], 'seasons': ['spring', 'summer'], 'tags': ['freshwater'], 'latin': 'Perca arundinis'},
    "glow_jelly": {'id': 'glow_jelly', 'name': 'Glow Jelly', 'rarity': 'uncommon', 'description': 'An uncommon catch shaped by deepsea, glowing, nocturnal. Glow Jelly brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 10, 'size_max': 35, 'size_unit': 'cm', 'base_value': 28, 'locations': ['abyssal_trench'], 'seasons': ['all'], 'tags': ['deepsea', 'glowing', 'nocturnal'], 'latin': 'Pelagia lucida'},
    "moonscale_carp": {'id': 'moonscale_carp', 'name': 'Moonscale Carp', 'rarity': 'rare', 'description': 'A rare catch shaped by freshwater, nocturnal. Moonscale Carp brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 20, 'size_max': 60, 'size_unit': 'cm', 'base_value': 80, 'locations': ['moonlit_pond'], 'seasons': ['autumn', 'winter'], 'tags': ['freshwater', 'nocturnal'], 'latin': 'Cyprinus lunaris'},
    "ember_carp": {'id': 'ember_carp', 'name': 'Ember Carp', 'rarity': 'rare', 'description': 'A rare catch shaped by fire. Ember Carp brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 18, 'size_max': 55, 'size_unit': 'cm', 'base_value': 110, 'locations': ['lava_spring'], 'seasons': ['summer'], 'tags': ['fire'], 'latin': 'Cyprinus pruna'},
    "windveil_ray": {'id': 'windveil_ray', 'name': 'Windveil Ray', 'rarity': 'epic', 'description': 'An epic catch shaped by fantasy, wind. Windveil Ray brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 25, 'size_max': 70, 'size_unit': 'cm', 'base_value': 180, 'locations': ['floating_lake'], 'seasons': ['spring', 'summer', 'autumn'], 'tags': ['fantasy', 'wind'], 'latin': 'Velumventus aura'},
    "frostfin_eel": {'id': 'frostfin_eel', 'name': 'Frostfin Eel', 'rarity': 'epic', 'description': 'An epic catch shaped by deepsea, glowing. Frostfin Eel brings real-water grit, travel-worn charm, and a little quiet magic to the creel.', 'size_min': 30, 'size_max': 90, 'size_unit': 'cm', 'base_value': 220, 'locations': ['abyssal_trench'], 'seasons': ['winter'], 'tags': ['deepsea', 'glowing'], 'latin': 'Conger gelidus'},
    "clockwork_koi": {'id': 'clockwork_koi', 'name': 'Clockwork Koi', 'rarity': 'legendary', 'description': 'A legendary catch carried in dockside rumor. When Clockwork Koi rises from the water, the whole trip feels larger than the map.', 'size_min': 30, 'size_max': 80, 'size_unit': 'cm', 'base_value': 400, 'locations': ['floating_lake'], 'seasons': ['all'], 'tags': ['fantasy'], 'latin': 'Machina cyprinus', 'rumor': 'Old anglers say Clockwork Koi appears only when the season, the journey, and a little impossible luck all agree.'},
    "the_first_drop": {'id': 'the_first_drop', 'name': 'The First Drop', 'rarity': 'mythic', 'description': 'A mythic catch carried in dockside rumor. When The First Drop rises from the water, the whole trip feels larger than the map.', 'size_min': 1, 'size_max': 30, 'size_unit': 'cm', 'base_value': 1000, 'locations': ['all'], 'seasons': ['all'], 'individual_weight': 1.0, 'tags': ['fantasy'], 'latin': 'Primastilla primordialis', 'rumor': 'Old anglers say The First Drop appears only when the season, the journey, and a little impossible luck all agree.'},
}
# Underwater fish: dive-only catches, including capture feel text.
FISH.update({_f["id"]: _f for _f in json.loads(r"""[
 {
  "id": "reed_clinger",
  "name": "Reed Clinger",
  "rarity": "common",
  "description": "A common underwater find from the freshwater reaches. Reed Clinger keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 5,
  "size_max": 12,
  "size_unit": "cm",
  "base_value": 6,
  "locations": [
   "reed_river"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "freshwater"
  ],
  "dive": true,
  "latin": "Phragmitichthys adhaerens",
  "capture_feel": "Reed Clinger comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "mud_nibbler",
  "name": "Mud Nibbler",
  "rarity": "common",
  "description": "A common underwater find from the freshwater, nocturnal reaches. Mud Nibbler keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 4,
  "size_max": 9,
  "size_unit": "cm",
  "base_value": 5,
  "locations": [
   "reed_river"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "freshwater",
   "nocturnal"
  ],
  "dive": true,
  "latin": "Limicola occultus",
  "capture_feel": "Mud Nibbler comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "moon_catfish",
  "name": "Moon Catfish",
  "rarity": "common",
  "description": "A common underwater find from the freshwater, nocturnal reaches. Moon Catfish keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 10,
  "size_max": 20,
  "size_unit": "cm",
  "base_value": 8,
  "locations": [
   "moonlit_pond"
  ],
  "seasons": [
   "spring",
   "summer",
   "autumn"
  ],
  "tags": [
   "underwater",
   "freshwater",
   "nocturnal"
  ],
  "dive": true,
  "latin": "Silurus lunaris",
  "capture_feel": "Moon Catfish comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "shadow_snail",
  "name": "Shadow Snail",
  "rarity": "uncommon",
  "description": "An uncommon underwater find from the freshwater, nocturnal reaches. Shadow Snail keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 6,
  "size_max": 15,
  "size_unit": "cm",
  "base_value": 25,
  "locations": [
   "moonlit_pond"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "freshwater",
   "nocturnal"
  ],
  "dive": true,
  "latin": "Umbraconcha nocturna",
  "capture_feel": "Shadow Snail comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "mire_leech",
  "name": "Mire Leech",
  "rarity": "common",
  "description": "A common underwater find from the swamp, poison, nocturnal reaches. Mire Leech keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 7,
  "size_max": 14,
  "size_unit": "cm",
  "base_value": 9,
  "locations": [
   "whispering_mire"
  ],
  "seasons": [
   "spring",
   "summer",
   "autumn"
  ],
  "tags": [
   "underwater",
   "swamp",
   "poison",
   "nocturnal"
  ],
  "dive": true,
  "latin": "Hirudisalamandra palustris",
  "capture_feel": "Mire Leech comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "whisper_ray",
  "name": "Whisper Ray",
  "rarity": "rare",
  "description": "A rare underwater find from the swamp, shadow, nocturnal reaches. Whisper Ray keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 30,
  "size_max": 50,
  "size_unit": "cm",
  "base_value": 110,
  "locations": [
   "whispering_mire"
  ],
  "seasons": [
   "autumn",
   "winter"
  ],
  "tags": [
   "underwater",
   "swamp",
   "shadow",
   "nocturnal"
  ],
  "dive": true,
  "latin": "Torpedo susurrus",
  "capture_feel": "Whisper Ray comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "delta_glow_shrimp",
  "name": "Delta Glow Shrimp",
  "rarity": "uncommon",
  "description": "An uncommon underwater find from the brackish, glowing, migratory reaches. Delta Glow Shrimp keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 4,
  "size_max": 9,
  "size_unit": "cm",
  "base_value": 28,
  "locations": [
   "starry_delta"
  ],
  "seasons": [
   "spring",
   "summer"
  ],
  "tags": [
   "underwater",
   "brackish",
   "glowing",
   "migratory"
  ],
  "dive": true,
  "latin": "Lucicaris deltae",
  "capture_feel": "Delta Glow Shrimp comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "light_eel",
  "name": "Light Eel",
  "rarity": "rare",
  "description": "A rare underwater find from the brackish, glowing, migratory reaches. Light Eel keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 35,
  "size_max": 60,
  "size_unit": "cm",
  "base_value": 115,
  "locations": [
   "starry_delta"
  ],
  "seasons": [
   "spring"
  ],
  "tags": [
   "underwater",
   "brackish",
   "glowing",
   "migratory"
  ],
  "dive": true,
  "latin": "Anguilla lucis",
  "capture_feel": "Light Eel comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "mangrove_crab",
  "name": "Mangrove Crab",
  "rarity": "common",
  "description": "A common underwater find from the brackish, armored reaches. Mangrove Crab keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 5,
  "size_max": 10,
  "size_unit": "cm",
  "base_value": 8,
  "locations": [
   "mangrove_shoal"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "brackish",
   "armored"
  ],
  "dive": true,
  "latin": "Porcellana rhizophorae",
  "capture_feel": "Mangrove Crab comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "root_hider",
  "name": "Root Hider",
  "rarity": "uncommon",
  "description": "An uncommon underwater find from the brackish reaches. Root Hider keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 8,
  "size_max": 18,
  "size_unit": "cm",
  "base_value": 26,
  "locations": [
   "mangrove_shoal"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "brackish"
  ],
  "dive": true,
  "latin": "Cryptichthys radicis",
  "capture_feel": "Root Hider comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "float_bladder",
  "name": "Float Bladder",
  "rarity": "common",
  "description": "A common underwater find from the fantasy, wind reaches. Float Bladder keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 3,
  "size_max": 10,
  "size_unit": "cm",
  "base_value": 7,
  "locations": [
   "floating_lake"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "fantasy",
   "wind"
  ],
  "dive": true,
  "latin": "Vesicula aeris",
  "capture_feel": "Float Bladder comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "drift_leaf_dragon",
  "name": "Drift Leaf Dragon",
  "rarity": "uncommon",
  "description": "An uncommon underwater find from the fantasy, wind reaches. Drift Leaf Dragon keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 12,
  "size_max": 25,
  "size_unit": "cm",
  "base_value": 28,
  "locations": [
   "floating_lake"
  ],
  "seasons": [
   "spring",
   "summer"
  ],
  "tags": [
   "underwater",
   "fantasy",
   "wind"
  ],
  "dive": true,
  "latin": "Phyllopteryx ventus",
  "capture_feel": "Drift Leaf Dragon comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "lava_scale_worm",
  "name": "Lava Scale Worm",
  "rarity": "common",
  "description": "A common underwater find from the fire reaches. Lava Scale Worm keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 3,
  "size_max": 8,
  "size_unit": "cm",
  "base_value": 9,
  "locations": [
   "lava_spring"
  ],
  "seasons": [
   "summer"
  ],
  "tags": [
   "underwater",
   "fire"
  ],
  "dive": true,
  "latin": "Thermolepis igneus",
  "capture_feel": "Lava Scale Worm comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "geyser_salamander",
  "name": "Geyser Salamander",
  "rarity": "uncommon",
  "description": "An uncommon underwater find from the fire reaches. Geyser Salamander keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 15,
  "size_max": 30,
  "size_unit": "cm",
  "base_value": 30,
  "locations": [
   "lava_spring"
  ],
  "seasons": [
   "summer"
  ],
  "tags": [
   "underwater",
   "fire"
  ],
  "dive": true,
  "latin": "Ignisalamandra thermalis",
  "capture_feel": "Geyser Salamander comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "mineral_sucker",
  "name": "Mineral Sucker",
  "rarity": "common",
  "description": "A common underwater find from the mineral reaches. Mineral Sucker keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 6,
  "size_max": 14,
  "size_unit": "cm",
  "base_value": 8,
  "locations": [
   "geyser_falls"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "mineral"
  ],
  "dive": true,
  "latin": "Sulfurophilus minera",
  "capture_feel": "Mineral Sucker comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "crystal_snail",
  "name": "Crystal Snail",
  "rarity": "uncommon",
  "description": "An uncommon underwater find from the mineral, crystal reaches. Crystal Snail keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 5,
  "size_max": 12,
  "size_unit": "cm",
  "base_value": 26,
  "locations": [
   "geyser_falls"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "mineral",
   "crystal"
  ],
  "dive": true,
  "latin": "Crystalloconcha geyseris",
  "capture_feel": "Crystal Snail comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "column_moss_animal",
  "name": "Column Moss Animal",
  "rarity": "rare",
  "description": "A rare underwater find from the ancient reaches. Column Moss Animal keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 20,
  "size_max": 45,
  "size_unit": "cm",
  "base_value": 105,
  "locations": [
   "sunken_ruins"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "ancient"
  ],
  "dive": true,
  "latin": "Bryozoa columnaris",
  "capture_feel": "Column Moss Animal comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "ruin_gargoyle_fish",
  "name": "Ruin Gargoyle Fish",
  "rarity": "epic",
  "description": "An epic underwater find from the ancient, shadow reaches. Ruin Gargoyle Fish keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 80,
  "size_max": 150,
  "size_unit": "cm",
  "base_value": 230,
  "locations": [
   "sunken_ruins"
  ],
  "seasons": [
   "autumn",
   "winter"
  ],
  "tags": [
   "underwater",
   "ancient",
   "shadow"
  ],
  "dive": true,
  "latin": "Gargoylithis ruinosus",
  "capture_feel": "Ruin Gargoyle Fish comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "abyssal_dragon_maw",
  "name": "Abyssal Dragon Maw",
  "rarity": "epic",
  "description": "An epic underwater find from the deepsea, glowing reaches. Abyssal Dragon Maw keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 100,
  "size_max": 200,
  "size_unit": "cm",
  "base_value": 240,
  "locations": [
   "abyssal_trench"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "deepsea",
   "glowing"
  ],
  "dive": true,
  "latin": "Abyssobranchus draconis",
  "capture_feel": "Abyssal Dragon Maw comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "abyssal_embryo",
  "name": "Abyssal Embryo",
  "rarity": "legendary",
  "description": "A legendary underwater find from the deepsea, glowing, ancient reaches. Abyssal Embryo keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 150,
  "size_max": 250,
  "size_unit": "cm",
  "base_value": 450,
  "locations": [
   "abyssal_trench"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "deepsea",
   "glowing",
   "ancient",
   "fantasy"
  ],
  "dive": true,
  "latin": "Embryon abyssalis",
  "rumor": "Old anglers say Abyssal Embryo only shows itself when the journey, the season, and a little impossible luck agree.",
  "capture_feel": "Holding Abyssal Embryo feels like gripping moonlight, pressure, and an old travel story all at once; the water keeps trembling after it is still."
 },
 {
  "id": "crystal_cluster_shrimp",
  "name": "Crystal Cluster Shrimp",
  "rarity": "rare",
  "description": "A rare underwater find from the crystal, glowing reaches. Crystal Cluster Shrimp keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 6,
  "size_max": 15,
  "size_unit": "cm",
  "base_value": 110,
  "locations": [
   "crystal_cave"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "crystal",
   "glowing"
  ],
  "dive": true,
  "latin": "Crystallocaris spelea",
  "capture_feel": "Crystal Cluster Shrimp comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms."
 },
 {
  "id": "cave_eye",
  "name": "Cave Eye",
  "rarity": "legendary",
  "description": "A legendary underwater find from the crystal, glowing, ancient reaches. Cave Eye keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 60,
  "size_max": 120,
  "size_unit": "cm",
  "base_value": 480,
  "locations": [
   "crystal_cave"
  ],
  "seasons": [
   "all"
  ],
  "tags": [
   "underwater",
   "crystal",
   "glowing",
   "ancient",
   "fantasy"
  ],
  "dive": true,
  "latin": "Oculus crystallinus",
  "rumor": "Old anglers say Cave Eye only shows itself when the journey, the season, and a little impossible luck agree.",
  "capture_feel": "Holding Cave Eye feels like gripping moonlight, pressure, and an old travel story all at once; the water keeps trembling after it is still."
 }
]""")})
# Early economy balance: common fish values were raised without touching rarer catches.
for _f in FISH.values():
    if _f.get("rarity") == "common": _f["base_value"] += 5
BAITS = {
    "basic_worm": {"id": "basic_worm", "name": "Plain Worm", "cost": 10, "description": "A plain, reliable worm: cheap, humble, and honest enough for any first cast.", "effects": {}},
    "glow_bait": {"id": "glow_bait", "name": "Glow Bait", "cost": 35, "description": "A faint blue lure that glows in dim water and tempts nocturnal fish from cover.", "effects": {"rarity_weight_mult": {"rare": 1.5, "epic": 1.3}, "tag_weight_mult": {"nocturnal": 2.0}, "junk_chance_mult": 0.8}},
    "golden_lure": {"id": "golden_lure", "name": "Golden Lure", "cost": 80, "description": "Golden Lure is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.", "effects": {"rarity_weight_mult": {"common": 0.5, "uncommon": 0.8, "rare": 1.4, "epic": 1.6, "legendary": 2.0, "mythic": 2.0}, "junk_chance_mult": 0.7}},
}
# Oxygen tanks are dive consumables bought in the shop.
OXYGEN = {"id": "oxygen", "name": "oxygen_tank", "cost": 45, "description": "A compact oxygen tank, good for one underwater catch. Bring several for a longer dive."}
# Special events and items.
EVENTS = json.loads(r"""{
 "drift_bottle": {
  "id": "drift_bottle",
  "name": "Drift Bottle",
  "type": "bottle",
  "weight": 145,
  "unique": true,
  "description": "A wave-worn glass bottle bumps your float, carrying a stranger's note from another shore.",
  "messages": [
   "To whoever finds this bottle: may your next cast land where the water is kind and strange.",
   "I left before dawn with wet boots and a happy heart. Keep the note, and trust the quiet pools.",
   "Some journeys are measured in miles; the best ones are measured in ripples after the float goes under.",
   "If this reaches another angler, know that the moon was bright tonight and the fish were braver than I was.",
   "To whoever finds this bottle: may your next cast land where the water is kind and strange.",
   "I left before dawn with wet boots and a happy heart. Keep the note, and trust the quiet pools."
  ],
  "rewards": {
   "fragment": 1
  }
 },
 "floating_coral_pearl": {
  "id": "floating_coral_pearl",
  "name": "Floating Coral Pearl",
  "type": "treasure",
  "weight": 18,
  "description": "Floating Coral Pearl is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "rewards": {
   "items": [
    {
     "id": "coral_pearl",
     "qty": 1
    }
   ]
  }
 },
 "ambergris_chunk": {
  "id": "ambergris_chunk",
  "name": "Ambergris Chunk",
  "type": "treasure",
  "weight": 10,
  "description": "Ambergris Chunk is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "rewards": {
   "items": [
    {
     "id": "ambergris",
     "qty": 1
    }
   ]
  }
 },
 "rusty_chest": {
  "id": "rusty_chest",
  "name": "Rusty Chest",
  "type": "chest",
  "weight": 25,
  "description": "A sealed chest lifted from silt and shell, heavy with old water and the promise of something useful.",
  "lock": {
   "or_points": 80
  },
  "loot_table": [
   {
    "weight": 60,
    "reward": {
     "points_range": [
      100,
      200
     ]
    }
   },
   {
    "weight": 15,
    "reward": {
     "items": [
      {
       "id": "ancient_key",
       "qty": 1
      }
     ]
    }
   },
   {
    "weight": 15,
    "reward": {
     "items": [
      {
       "id": "gem_sapphire",
       "qty": 1
      }
     ]
    }
   },
   {
    "weight": 5,
    "reward": {
     "bait": [
      {
       "id": "golden_lure",
       "qty": 1
      }
     ]
    }
   },
   {
    "weight": 5,
    "reward": {
     "items": [
      {
       "id": "shipwreck_coin",
       "qty": 1
      }
     ]
    }
   },
   {
    "weight": 20,
    "reward": {
     "fragment": 1
    }
   },
   {
    "weight": 3,
    "reward": {
     "map": 1
    }
   }
  ]
 },
 "barnacle_chest": {
  "id": "barnacle_chest",
  "name": "Barnacle Chest",
  "type": "chest",
  "weight": 20,
  "description": "A sealed chest lifted from silt and shell, heavy with old water and the promise of something useful.",
  "lock": {
   "or_points": 60
  },
  "loot_table": [
   {
    "weight": 50,
    "reward": {
     "points_range": [
      80,
      180
     ]
    }
   },
   {
    "weight": 30,
    "reward": {
     "items": [
      {
       "id": "moonstone",
       "qty": 1
      }
     ]
    }
   },
   {
    "weight": 20,
    "reward": {
     "bait": [
      {
       "id": "glow_bait",
       "qty": 3
      }
     ]
    }
   },
   {
    "weight": 20,
    "reward": {
     "fragment": 1
    }
   },
   {
    "weight": 2,
    "reward": {
     "map": 1
    }
   }
  ]
 },
 "ancient_captain_chest": {
  "id": "ancient_captain_chest",
  "name": "Ancient Captain Chest",
  "type": "chest",
  "weight": 8,
  "description": "A sealed chest lifted from silt and shell, heavy with old water and the promise of something useful.",
  "lock": {
   "requires_item": "ancient_key",
   "or_points": 200
  },
  "loot_table": [
   {
    "weight": 40,
    "reward": {
     "points_range": [
      150,
      300
     ]
    }
   },
   {
    "weight": 35,
    "reward": {
     "items": [
      {
       "id": "moonstone",
       "qty": 1
      },
      {
       "id": "gem_sapphire",
       "qty": 1
      }
     ]
    }
   },
   {
    "weight": 25,
    "reward": {
     "bait": [
      {
       "id": "golden_lure",
       "qty": 2
      }
     ]
    }
   },
   {
    "weight": 15,
    "reward": {
     "fragment": 1
    }
   },
   {
    "weight": 5,
    "reward": {
     "map": 1
    }
   }
  ]
 }
}""")
ITEMS = json.loads(r"""{
 "coral_pearl": {
  "id": "coral_pearl",
  "name": "Coral Pearl",
  "type": "treasure",
  "description": "Coral Pearl is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 150,
  "sellable": true
 },
 "gem_sapphire": {
  "id": "gem_sapphire",
  "name": "Gem Sapphire",
  "type": "treasure",
  "description": "Gem Sapphire is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 300,
  "sellable": true
 },
 "moonstone": {
  "id": "moonstone",
  "name": "Moonstone",
  "type": "treasure",
  "description": "Moonstone is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 450,
  "sellable": true
 },
 "ambergris": {
  "id": "ambergris",
  "name": "Ambergris",
  "type": "treasure",
  "description": "Ambergris is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 500,
  "sellable": true
 },
 "shipwreck_coin": {
  "id": "shipwreck_coin",
  "name": "Shipwreck Coin",
  "type": "treasure",
  "description": "Shipwreck Coin is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 200,
  "sellable": true
 },
 "coral_crown": {
  "id": "coral_crown",
  "name": "Coral Crown",
  "type": "treasure",
  "description": "Coral Crown is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 280,
  "sellable": true
 },
 "mermaid_tear": {
  "id": "mermaid_tear",
  "name": "Mermaid Tear",
  "type": "treasure",
  "description": "Mermaid Tear is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 420,
  "sellable": true
 },
 "ancient_relic": {
  "id": "ancient_relic",
  "name": "Ancient Relic",
  "type": "treasure",
  "description": "Ancient Relic is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 340,
  "sellable": true
 },
 "ancient_key": {
  "id": "ancient_key",
  "name": "Ancient Key",
  "type": "key",
  "description": "Ancient Key is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 0,
  "sellable": false
 }
}""")
# Dive-only chest; awarded by underwater luck events.
DIVE_EVENTS = json.loads(r"""{
 "seafloor_vault": {
  "id": "seafloor_vault",
  "name": "Seafloor Vault",
  "type": "chest",
  "description": "A sealed chest lifted from silt and shell, heavy with old water and the promise of something useful.",
  "lock": {
   "or_points": 120
  },
  "loot_table": [
   {
    "weight": 35,
    "reward": {
     "points_range": [
      180,
      350
     ]
    }
   },
   {
    "weight": 22,
    "reward": {
     "items": [
      {
       "id": "mermaid_tear",
       "qty": 1
      }
     ]
    }
   },
   {
    "weight": 20,
    "reward": {
     "items": [
      {
       "id": "coral_crown",
       "qty": 1
      },
      {
       "id": "coral_pearl",
       "qty": 1
      }
     ]
    }
   },
   {
    "weight": 13,
    "reward": {
     "oxygen": 5
    }
   },
   {
    "weight": 10,
    "reward": {
     "items": [
      {
       "id": "ancient_relic",
       "qty": 1
      },
      {
       "id": "gem_sapphire",
       "qty": 1
      }
     ]
    }
   },
   {
    "weight": 12,
    "reward": {
     "fragment": 1
    }
   },
   {
    "weight": 6,
    "reward": {
     "map": 1
    }
   }
  ]
 }
}""")

# Underwater encounter data; rewards are resolved by the common grant path.
ITEMS.update(json.loads(r"""{
 "giant_clam_pearl": {
  "id": "giant_clam_pearl",
  "name": "Giant Clam Pearl",
  "type": "treasure",
  "description": "Giant Clam Pearl is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 380,
  "sellable": true
 },
 "icebound_chart": {
  "id": "icebound_chart",
  "name": "Icebound Chart",
  "type": "treasure",
  "description": "Icebound Chart is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 480,
  "sellable": true
 },
 "siren_scale": {
  "id": "siren_scale",
  "name": "Siren Scale",
  "type": "treasure",
  "description": "Siren Scale is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 350,
  "sellable": true
 },
 "salt_crystal_rose": {
  "id": "salt_crystal_rose",
  "name": "Salt Crystal Rose",
  "type": "treasure",
  "description": "Salt Crystal Rose is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 200,
  "sellable": true
 },
 "lighthouse_lens_shard": {
  "id": "lighthouse_lens_shard",
  "name": "Lighthouse Lens Shard",
  "type": "treasure",
  "description": "Lighthouse Lens Shard is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 180,
  "sellable": true
 },
 "dragon_king_scale": {
  "id": "dragon_king_scale",
  "name": "Dragon King Scale",
  "type": "treasure",
  "description": "Dragon King Scale is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 850,
  "sellable": true
 },
 "abyss_black_pearl": {
  "id": "abyss_black_pearl",
  "name": "Abyss Black Pearl",
  "type": "treasure",
  "description": "Abyss Black Pearl is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 400,
  "sellable": true
 },
 "whale_bone_pearl": {
  "id": "whale_bone_pearl",
  "name": "Whale Bone Pearl",
  "type": "treasure",
  "description": "Whale Bone Pearl is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 380,
  "sellable": true
 },
 "ancient_sea_page": {
  "id": "ancient_sea_page",
  "name": "Ancient Sea Page",
  "type": "treasure",
  "description": "Ancient Sea Page is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 320,
  "sellable": true
 },
 "jellyfish_heart": {
  "id": "jellyfish_heart",
  "name": "Jellyfish Heart",
  "type": "treasure",
  "description": "Jellyfish Heart is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 550,
  "sellable": true
 },
 "altar_blood_jade": {
  "id": "altar_blood_jade",
  "name": "Altar Blood Jade",
  "type": "treasure",
  "description": "Altar Blood Jade is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 600,
  "sellable": true
 },
 "lost_bell": {
  "id": "lost_bell",
  "name": "Lost Bell",
  "type": "treasure",
  "description": "Lost Bell is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 900,
  "sellable": true
 }
}"""))
DIVE_ENCOUNTERS = json.loads(r"""[
 {
  "emoji": "🪸",
  "id": "coral_palace",
  "name": "Coral Palace",
  "weight": 10,
  "text": "Coral Palace rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
  "reward": {
   "item_pool": [
    {
     "id": "coral_pearl",
     "weight": 3
    },
    {
     "id": "coral_crown",
     "weight": 1
    }
   ]
  }
 },
 {
  "emoji": "🧜‍♀️",
  "id": "mermaid_palace",
  "name": "Mermaid Palace",
  "weight": 6,
  "text": "Mermaid Palace rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
  "reward": {
   "item_pool": [
    {
     "id": "mermaid_tear",
     "weight": 2
    },
    {
     "id": "moonstone",
     "weight": 2
    },
    {
     "id": "ambergris",
     "weight": 1
    }
   ]
  }
 },
 {
  "emoji": "🏛️",
  "id": "ancient_ruins",
  "name": "Ancient Ruins",
  "weight": 8,
  "text": "Ancient Ruins rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
  "reward": {
   "items": [
    {
     "id": "ancient_relic",
     "qty": 1
    }
   ],
   "points_range": [
    40,
    120
   ]
  }
 },
 {
  "emoji": "🧰",
  "id": "deep_vault",
  "name": "Deep Vault",
  "weight": 5,
  "branch": true,
  "intro": "Deep Vault opens ahead, vivid with pressure, old stone, and the feeling that the map has folded into myth.",
  "options": [
   {
    "label": "Follow the glimmer",
    "oxygen": 2,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "items": [
       {
        "id": "vault_golden_chest",
        "qty": 1
       }
      ]
     }
    }
   },
   {
    "label": "Follow the glimmer",
    "oxygen": 1,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "points_range": [
       80,
       200
      ],
      "item_pool": [
       {
        "id": "coral_pearl",
        "weight": 2
       },
       {
        "id": "gem_sapphire",
        "weight": 1
       }
      ]
     }
    }
   },
   {
    "label": "Follow the glimmer",
    "oxygen": 0,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {}
    }
   }
  ]
 },
 {
  "emoji": "🚢",
  "id": "shipwreck_graveyard",
  "name": "Shipwreck Graveyard",
  "weight": 5,
  "branch": true,
  "intro": "Shipwreck Graveyard opens ahead, vivid with pressure, old stone, and the feeling that the map has folded into myth.",
  "options": [
   {
    "label": "Follow the glimmer",
    "oxygen": 2,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "items": [
       {
        "id": "star_astrolabe",
        "qty": 1
       }
      ],
      "chest": "seafloor_vault"
     }
    }
   },
   {
    "label": "Follow the glimmer",
    "oxygen": 1,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "fish": "silverflash_fish",
      "points_range": [
       30,
       80
      ]
     }
    }
   },
   {
    "label": "Follow the glimmer",
    "oxygen": 0,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {}
    }
   }
  ]
 },
 {
  "id": "giant_clam",
  "name": "Giant Clam",
  "weight": 9,
  "text": "Giant Clam rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
  "reward": {
   "oxygen": 1,
   "item_pool": [
    {
     "id": "giant_clam_pearl",
     "weight": 5
    },
    {
     "id": "coral_pearl",
     "weight": 3
    }
   ]
  }
 },
 {
  "id": "jellyfish_dome",
  "name": "Jellyfish Dome",
  "weight": 7,
  "text": "Jellyfish Dome rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
  "reward": {
   "items": [
    {
     "id": "jellyfish_heart",
     "qty": 1
    }
   ],
   "oxygen": 1
  }
 },
 {
  "id": "whale_fall",
  "name": "Whale Fall",
  "weight": 7,
  "text": "Whale Fall rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
  "reward": {
   "points_range": [
    30,
    60
   ],
   "item_pool": [
    {
     "id": "whale_bone_pearl",
     "weight": 4
    },
    {
     "id": "ambergris",
     "weight": 2
    },
    {
     "id": "moonstone",
     "weight": 1
    }
   ]
  }
 },
 {
  "id": "siren_lair",
  "name": "Siren Lair",
  "weight": 6,
  "text": "Siren Lair rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
  "reward": {
   "oxygen": 2,
   "item_pool": [
    {
     "id": "siren_scale",
     "weight": 4
    },
    {
     "id": "mermaid_tear",
     "weight": 3
    },
    {
     "id": "coral_pearl",
     "weight": 2
    }
   ]
  }
 },
 {
  "emoji": "⛩️",
  "id": "sacrificial_altar",
  "name": "Sacrificial Altar",
  "weight": 5,
  "branch": true,
  "intro": "Sacrificial Altar opens ahead, vivid with pressure, old stone, and the feeling that the map has folded into myth.",
  "options": [
   {
    "label": "Follow the glimmer",
    "oxygen": 1,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "fish": "altar_spirit_bream"
     }
    }
   },
   {
    "label": "Follow the glimmer",
    "oxygen": 1,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "items": [
       {
        "id": "altar_blood_jade",
        "qty": 1
       }
      ]
     }
    }
   },
   {
    "label": "Follow the glimmer",
    "oxygen": 0,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {}
    }
   }
  ]
 },
 {
  "emoji": "🕳️",
  "id": "abyss_crevice",
  "name": "Abyss Crevice",
  "weight": 5,
  "branch": true,
  "intro": "Abyss Crevice opens ahead, vivid with pressure, old stone, and the feeling that the map has folded into myth.",
  "options": [
   {
    "label": "Follow the glimmer",
    "oxygen": 2,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "items": [
       {
        "id": "abyss_night_stone",
        "qty": 1
       }
      ],
      "fish": "crevice_blind_eel"
     }
    }
   },
   {
    "label": "Follow the glimmer",
    "oxygen": 1,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "item_pool": [
       {
        "id": "abyss_black_pearl",
        "weight": 3
       },
       {
        "id": "gem_sapphire",
        "weight": 1
       }
      ]
     }
    }
   },
   {
    "label": "Follow the glimmer",
    "oxygen": 0,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {}
    }
   }
  ]
 },
 {
  "id": "ancient_chart_room",
  "name": "Ancient Chart Room",
  "weight": 5,
  "text": "Ancient Chart Room rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
  "reward": {
   "points_range": [
    40,
    90
   ],
   "chest": "seafloor_vault"
  }
 },
 {
  "id": "sunken_belfry",
  "name": "Sunken Belfry",
  "weight": 5,
  "text": "Sunken Belfry rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
  "reward": {
   "items": [
    {
     "id": "lost_bell",
     "qty": 1
    }
   ]
  }
 },
 {
  "emoji": "🐉",
  "id": "dragon_king_palace",
  "name": "Dragon King Palace",
  "weight": 5,
  "branch": true,
  "intro": "Dragon King Palace opens ahead, vivid with pressure, old stone, and the feeling that the map has folded into myth.",
  "options": [
   {
    "label": "Follow the glimmer",
    "oxygen": 3,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "items": [
       {
        "id": "dragon_king_scale",
        "qty": 1
       }
      ],
      "fish": "scale_guardian"
     }
    }
   },
   {
    "label": "Follow the glimmer",
    "oxygen": 1,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "items": [
       {
        "id": "dragon_eye_pearl",
        "qty": 1
       }
      ],
      "points_range": [
       100,
       250
      ]
     }
    }
   },
   {
    "label": "Follow the glimmer",
    "oxygen": 0,
    "outcome": {
     "text": "Unnamed Wonder rises out of the journey: water brightens, old stone answers, and you come away with something worth remembering.",
     "reward": {
      "points_range": [
       30,
       80
      ]
     }
    }
   }
  ]
 }
]""")
ITEMS.update(json.loads(r"""{
 "abyss_night_stone": {
  "id": "abyss_night_stone",
  "name": "Abyss Night Stone",
  "type": "treasure",
  "description": "Abyss Night Stone is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 650,
  "sellable": true
 },
 "star_astrolabe": {
  "id": "star_astrolabe",
  "name": "Captain's Astrolabe",
  "type": "treasure",
  "description": "Captain's Astrolabe is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 500,
  "sellable": true
 },
 "vault_golden_chest": {
  "id": "vault_golden_chest",
  "name": "Deepsea Auric Casket",
  "type": "treasure",
  "description": "Deepsea Auric Casket is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 800,
  "sellable": true
 },
 "dragon_eye_pearl": {
  "id": "dragon_eye_pearl",
  "name": "Dragon Eye Pearl",
  "type": "treasure",
  "description": "Dragon Eye Pearl is a keepsake from the deeper journey, carrying cold water, warm campfire rumor, and a faint impossible glow.",
  "value": 950,
  "sellable": true
 }
}"""))
FISH.update(json.loads(r"""{
 "crevice_blind_eel": {
  "id": "crevice_blind_eel",
  "name": "Crevice Blind Eel",
  "rarity": "epic",
  "description": "An epic underwater find from the deepsea, shadow reaches. Crevice Blind Eel keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 45,
  "size_max": 80,
  "size_unit": "cm",
  "base_value": 260,
  "tags": [
   "underwater",
   "deepsea",
   "shadow"
  ],
  "dive": true,
  "latin": "Abyssoanguis anophthalmus",
  "capture_feel": "Crevice Blind Eel comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms.",
  "branch_only": true,
  "locations": [
   "all"
  ],
  "seasons": [
   "all"
  ]
 },
 "silverflash_fish": {
  "id": "silverflash_fish",
  "name": "Silverflash Fish",
  "rarity": "rare",
  "description": "A rare underwater find from the shoal, shipwreck reaches. Silverflash Fish keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 15,
  "size_max": 25,
  "size_unit": "cm",
  "base_value": 120,
  "tags": [
   "underwater",
   "shoal",
   "shipwreck"
  ],
  "dive": true,
  "latin": "Argentimicris naufragus",
  "capture_feel": "Silverflash Fish comes up cool and lively in your hands, slick with silt, mineral light, or deepwater chill, leaving the memory of the place on your palms.",
  "branch_only": true,
  "locations": [
   "all"
  ],
  "seasons": [
   "all"
  ]
 },
 "altar_spirit_bream": {
  "id": "altar_spirit_bream",
  "name": "Altar Spirit Bream",
  "rarity": "legendary",
  "description": "A legendary underwater find from the spirit, altar reaches. Altar Spirit Bream keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 30,
  "size_max": 45,
  "size_unit": "cm",
  "base_value": 400,
  "tags": [
   "underwater",
   "spirit",
   "altar"
  ],
  "dive": true,
  "latin": "Sacrificium aurora",
  "capture_feel": "Holding Altar Spirit Bream feels like gripping moonlight, pressure, and an old travel story all at once; the water keeps trembling after it is still.",
  "branch_only": true,
  "locations": [
   "all"
  ],
  "seasons": [
   "all"
  ]
 },
 "scale_guardian": {
  "id": "scale_guardian",
  "name": "Scale Guardian",
  "rarity": "legendary",
  "description": "A legendary underwater find from the dragon, armored reaches. Scale Guardian keeps close to roots, stone, or shadow, making every dive feel like a small expedition.",
  "size_min": 70,
  "size_max": 120,
  "size_unit": "cm",
  "base_value": 500,
  "tags": [
   "underwater",
   "dragon",
   "armored"
  ],
  "dive": true,
  "latin": "Squamatocustos draconis",
  "capture_feel": "Holding Scale Guardian feels like gripping moonlight, pressure, and an old travel story all at once; the water keeps trembling after it is still.",
  "branch_only": true,
  "locations": [
   "all"
  ],
  "seasons": [
   "all"
  ]
 }
}"""))

def _title_from_id(v):
    return " ".join(p.capitalize() for p in str(v).replace("-", "_").split("_") if p)

def _apply_english_display():
    RARITY.update({
        "common": {**RARITY["common"], "label": "Common"},
        "uncommon": {**RARITY["uncommon"], "label": "Uncommon"},
        "rare": {**RARITY["rare"], "label": "Rare"},
        "epic": {**RARITY["epic"], "label": "Epic"},
        "legendary": {**RARITY["legendary"], "label": "Legendary"},
        "mythic": {**RARITY["mythic"], "label": "Mythic"},
    })
    season_text = {
        "spring": ("Spring", "Warm water wakes the shallows, and freshwater fish grow bold."),
        "summer": ("Summer", "Heat shimmers over the banks, stirring fire-touched waters."),
        "autumn": ("Autumn", "Cool currents bring migration, deep colors, and night feeders."),
        "winter": ("Winter", "The surface quiets while cold-water and deep-sea species rise."),
    }
    for sid, (name, desc) in season_text.items():
        SEASONS[sid]["name"] = name
        SEASONS[sid]["description"] = desc
    loc_text = {
        "moonlit_pond": ("Moonlit Pond", "A quiet pond under permanent dusk, silvered by moonlight and small ripples."),
        "reed_river": ("Reed River", "A clear, slow river bordered by reeds; a friendly place to practice."),
        "abyssal_trench": ("Abyssal Trench", "A blue-black trench where pressure, cold, and faint lights gather."),
        "floating_lake": ("Floating Lake", "A lake suspended above the clouds, with wind moving beneath the water."),
        "lava_spring": ("Lava Spring", "A boiling orange spring where heat-proof creatures circle the vents. Summer only."),
        "mangrove_shoal": ("Mangrove Shoal", "A brackish maze of mangrove roots, mudflats, and ambush hunters."),
        "whispering_mire": ("Whispering Mire", "A foggy black-water marsh where bubbles rise from rotten wood."),
        "starry_delta": ("Starry Delta", "A luminous river delta where migrating schools make the shallows glow."),
        "sunken_ruins": ("Sunken Ruins", "Broken towers and old stone streets lie under blue-green water."),
        "geyser_falls": ("Geyser Falls", "Warm falls and mineral terraces fed by restless geysers."),
        "crystal_cave": ("Crystal Cave", "A cool cavern of prisms, echoes, and glass-clear pools."),
    }
    for lid, loc in LOCATIONS.items():
        name, desc = loc_text.get(lid, (_title_from_id(lid), "A distinct fishing ground with its own seasonal table."))
        loc["name"] = name
        loc["description"] = desc
        loc["character"] = "The water here has its own rhythm; change season or location when discoveries slow down."
        loc["ambience"] = [
            "The water shifts quietly around your line.",
            "A small current wrinkles the surface, then smooths out again.",
            "For a moment, the whole place seems to listen.",
        ]
        loc["dive_ambience"] = {sid: [
            "You slip below the surface at %s; the %s light fades into a muted underwater hush." % (name, SEASONS[sid]["name"].lower()),
            "You descend through %s water, watching shapes gather beyond the reach of easy sight." % SEASONS[sid]["name"].lower(),
        ] for sid in loc.get("available_seasons", [])}
    bait_text = {
        "basic_worm": ("Basic Worm", "Cheap, plain bait with no special effect."),
        "glow_bait": ("Glow Bait", "A blue-glowing bait that favors nocturnal and rarer fish."),
        "golden_lure": ("Golden Lure", "A bright lure that suppresses small bites and improves rare-fish odds."),
    }
    for bid, bait in BAITS.items():
        bait["name"], bait["description"] = bait_text.get(bid, (_title_from_id(bid), "Fishing bait."))
    OXYGEN["name"] = "Oxygen Tank"
    OXYGEN["description"] = "Compressed air for one dive step. Bring several tanks for longer expeditions."
    for fish in FISH.values():
        fish["name"] = _title_from_id(fish["id"])
        tags = ", ".join(fish.get("tags", [])[:4]) or "open water"
        mode = "underwater-only " if fish.get("dive") else ""
        article = "An" if mode else "A"
        fish["description"] = "%s %s%s catch associated with %s habitats." % (article, mode, RARITY[fish["rarity"]]["label"].lower(), tags)
        if fish.get("capture_feel"):
            fish["capture_feel"] = "It fights with a strange, memorable pull before settling in your hands."
        if fish.get("rumor"):
            fish["rumor"] = "Old anglers insist this species changes the luck of whoever lands it."
    event_text = {
        "drift_bottle": ("Drift Bottle", "A glass bottle taps your float, carrying a note from somewhere far away."),
        "floating_coral_pearl": ("Floating Coral Pearl", "A pink pearl rides the chop like a tiny coral flower."),
        "ambergris_chunk": ("Ambergris Chunk", "A waxy pale lump drifts close, perfuming the air."),
        "rusty_chest": ("Rusty Chest", "An old iron-bound chest breaks the surface, its lock red with rust."),
        "barnacle_chest": ("Barnacle Chest", "A stone chest wrapped in barnacles rises heavily beside your line."),
        "ancient_captain_chest": ("Ancient Captain's Chest", "A dark bronze chest carved with anchors and sea beasts emerges from deep water."),
    }
    bottle_notes = [
        "(The note says: May your next cast be the one worth remembering.)",
        "(The bottle holds one line: The sea delivered this to the right hands.)",
        "(A crooked fish is drawn on the note, followed by: I fished all day and caught only this bottle.)",
        "(The bottle is empty. Consider it a greeting from the water.)",
        "(The note says: May what you seek answer back.)",
        "(A half-ruined chart is inside, but the marked coast has washed away.)",
    ]
    for eid, ev in EVENTS.items():
        ev["name"], ev["description"] = event_text.get(eid, (_title_from_id(eid), "A surprise event interrupts the water."))
        if ev.get("messages"):
            ev["messages"] = bottle_notes[:len(ev["messages"])]
    for eid, ev in DIVE_EVENTS.items():
        ev["name"] = "Seafloor Vault"
        ev["description"] = "A bronze chest is wedged into the seabed, sealed but gleaming at the seams."
    for item in ITEMS.values():
        item["name"] = _title_from_id(item["id"])
        item["description"] = "A valuable find from the water, kept by id for save compatibility."
    for enc in DIVE_ENCOUNTERS:
        enc["name"] = _title_from_id(enc["id"])
        if enc.get("text"):
            enc["text"] = "You discover %s during the dive and search it carefully." % enc["name"].lower()
        if enc.get("intro"):
            enc["intro"] = "A major underwater site appears: %s. You pause and choose how much air to risk." % enc["name"]
        for i, opt in enumerate(enc.get("options", []), 1):
            labels = ["Take the richest prize", "Search quickly", "Leave it undisturbed"]
            opt["label"] = labels[i - 1] if i <= len(labels) else "Choose route %d" % i
            opt.setdefault("outcome", {})["text"] = "You commit to the choice, spend the required air, and return with whatever the site yields."

_apply_english_display()

# Replace the original fantasy tables with our bilingual real-world field pack.
# The engine remains deterministic; only canonical content and field-journal
# metadata change here.
from real_world_data import install as _install_real_world
_install_real_world(globals())
_DIVE_ENC_BY_ID = {e["id"]: e for e in DIVE_ENCOUNTERS}
_DIVE_BRANCH_IDS = {e["id"] for e in DIVE_ENCOUNTERS if e.get("branch")}   # Major ruin encounters pause the expedition for a choice.


_SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ".", "fishing_save.json")
_IO_WARN = ""   # One-shot save I/O warning appended to command output.

def _new_state(seed=_DEFAULT_SEED):
    seed = int(seed) & 0xFFFFFFFF
    return {"version": 1, "seed": seed, "rngState": seed, "rngCalls": 0, "turn": 0,
            "season_id": "spring", "season_length": 20, "season_started_turn": 0,
            "points": 200, "location_id": "colorado_headwaters", "unlocked_locations": ["colorado_headwaters"],
            "bait_inventory": {"earthworm": 8}, "catch_inventory": [], "items": {}, "pending_chests": [], "seen_letters": {},
            "encyclopedia": {}, "stats": {"total_casts": 0, "total_caught": 0, "total_chests": 0, "total_dives": 0}, "local_dry": 0,
            "fever": 0, "free_bait": 0,    # Active luck-event buffs.
            "oxygen": 0, "oxygen_ever": False,   # Oxygen tanks are dive consumables bought in the shop.
            "dive_unlocked": [], "map_fragments": {}}   # Unlocked dive locations and local map-fragment progress.

S = None
def _load():
    global S, _IO_WARN
    if S is not None:
        return S
    if os.path.exists(_SAVE):
        try:
            with open(_SAVE, "r", encoding="utf-8") as f:
                S = json.load(f)
        except Exception as e:
            # If an existing save is unreadable, back it up before starting fresh.
            try: os.replace(_SAVE, _SAVE + ".corrupt")
            except Exception: pass
            S = _new_state()
            _IO_WARN = "⚠️ Save read failed (%s). The bad save was backed up as %s, and a new game was started." % (e, os.path.basename(_SAVE) + ".corrupt")
    else:
        S = _new_state()   # Missing save on first run is normal.
    S.setdefault("items", {}); S.setdefault("pending_chests", []); S.setdefault("seen_letters", {}); S.setdefault("local_dry", 0)
    S.setdefault("fever", 0); S.setdefault("free_bait", 0)
    S.setdefault("oxygen", 0); S.setdefault("oxygen_ever", False)
    S.setdefault("map_fragments", {})
    if S.get("location_id") not in LOCATIONS:
        old_loc = S.get("location_id", "(missing)")
        S["location_id"] = "colorado_headwaters"
        _IO_WARN = (_IO_WARN + "\n" if _IO_WARN else "") + "⚠️ Save referenced old-world location '%s'; moved you to Colorado Rocky Mountain Headwaters and kept compatible progress." % old_loc
    for starter in ("colorado_headwaters",):
        if starter not in S.setdefault("unlocked_locations", []):
            S["unlocked_locations"].append(starter)
    if "dive_unlocked" not in S:   # Underwater fish: dive-only catches, including capture feel text.
        unlocked = set()
        for fid in S.get("encyclopedia", {}):
            ff = FISH.get(fid)
            if ff and ff.get("dive"):
                for l in ff["locations"]:
                    if l != "all": unlocked.add(l)
        S["dive_unlocked"] = list(unlocked)
    S.setdefault("stats", {}).setdefault("total_chests", 0)
    S["stats"].setdefault("total_casts", 0); S["stats"].setdefault("total_caught", 0); S["stats"].setdefault("total_dives", 0)
    return S
def _save():
    global _IO_WARN
    try:
        with open(_SAVE, "w", encoding="utf-8") as f:
            json.dump(S, f, ensure_ascii=False)
    except Exception as e:
        # Surface save-write failures instead of pretending the game was saved.
        _IO_WARN = "⚠️ Save write failed (%s). This progress may not persist; check directory permissions or disk space." % e

def _eligible(f, loc_id, sea_id):
    lo = "all" in f["locations"] or loc_id in f["locations"]
    so = "all" in f["seasons"] or sea_id in f["seasons"]
    return lo and so
def _eff_weight(f, loc_id, sea_id, bait_id):
    loc, sea, bait = LOCATIONS[loc_id], SEASONS[sea_id], BAITS[bait_id]
    w = RARITY[f["rarity"]]["weight"] * f.get("individual_weight", 1.0)
    for tag in f.get("tags", []):
        w *= loc.get("tag_weight_mult", {}).get(tag, 1.0)
        w *= sea.get("tag_weight_mult", {}).get(tag, 1.0)
        w *= bait["effects"].get("tag_weight_mult", {}).get(tag, 1.0)
    w *= bait["effects"].get("rarity_weight_mult", {}).get(f["rarity"], 1.0)
    return w
def _wpick(rng, items, weights):
    total = sum(weights); r = rng.random() * total; up = 0.0
    for it, w in zip(items, weights):
        up += w
        if r <= up:
            return it
    return items[-1]
def _roll_size(rng, f):
    a, b = f["size_min"], f["size_max"]
    base = a + (b - a) * (rng.random() + rng.random()) / 2
    if rng.random() < 0.03:
        base = b - (b - base) * rng.random() * 0.3
    return round(base, 1)
def _value(f, size):
    mid = (f["size_min"] + f["size_max"]) / 2
    return max(1, round(f["base_value"] * (size / mid) ** 1.5))
def _upd_enc(f, size, value):
    first = f["id"] not in S["encyclopedia"]
    if first:
        S["encyclopedia"][f["id"]] = {"discovered": True, "first_caught_turn": S["turn"], "count": 0, "max_size": 0, "total_value_earned": 0,
                                          "identification": "pending" if f.get("quiz") else "verified", "misidentifications": 0}
    e = S["encyclopedia"][f["id"]]
    e["count"] += 1; e["max_size"] = max(e["max_size"], size); e["total_value_earned"] += value
    return first
def _adv_season():
    if S["turn"] - S["season_started_turn"] >= S["season_length"]:
        ordered = sorted(SEASONS.values(), key=lambda x: x["order"])
        cur = SEASONS[S["season_id"]]["order"]
        nxt = ordered[(cur + 1) % len(ordered)]
        old = SEASONS[S["season_id"]]["name"]
        S["season_id"] = nxt["id"]; S["season_started_turn"] = S["turn"]; S["local_dry"] = 0
        return "🍃 %s has ended; %s begins. Some schools move on, and new ones may appear.\n" % (old, nxt["name"])
    return ""

# Special events and items.
def _pick_by_weight(rng, arr):
    total = sum(x["weight"] for x in arr); r = rng.random() * total; up = 0.0
    for it in arr:
        up += it["weight"]
        if r <= up:
            return it
    return arr[-1]
def _grant_rewards(rng, rw):
    parts = []
    if not rw: return parts
    if rw.get("points_range"):
        p = rng.rint(rw["points_range"][0], rw["points_range"][1]); S["points"] += p; parts.append("+%d pts" % p)
    for b in rw.get("bait", []):
        S["bait_inventory"][b["id"]] = S["bait_inventory"].get(b["id"], 0) + b["qty"]; parts.append("%s×%d" % (BAITS.get(b["id"], {}).get("name", b["id"]), b["qty"]))
    for it in rw.get("items", []):
        S["items"][it["id"]] = S["items"].get(it["id"], 0) + it["qty"]; parts.append("%s×%d" % (ITEMS.get(it["id"], {}).get("name", it["id"]), it["qty"]))
    if rw.get("item_pool"):   # Weighted item-pool reward.
        iid = _pick_by_weight(rng, rw["item_pool"])["id"]
        S["items"][iid] = S["items"].get(iid, 0) + 1; parts.append("%s×1" % ITEMS.get(iid, {}).get("name", iid))
    if rw.get("fish"):   # Direct fish reward, including encyclopedia credit.
        gf = FISH.get(rw["fish"])
        if gf:
            gs = _roll_size(rng, gf); gv = _value(gf, gs); _gi, gfirst, _gb = _record_catch(gf, gs, gv)
            parts.append("%s%s %s%s%s" % (gf["name"], "★new" if gfirst else "", gs, gf["size_unit"], _milestone_line(gf, gfirst)))
    if rw.get("oxygen"):
        S["oxygen"] = S.get("oxygen", 0) + rw["oxygen"]; S["oxygen_ever"] = True; parts.append("Oxygen Tank×%d" % rw["oxygen"])
    if rw.get("chest"):   # Award a chest to be opened later.
        S["stats"]["total_chests"] = S["stats"].get("total_chests", 0) + 1
        cuid = "ch_%03d" % S["stats"]["total_chests"]
        S["pending_chests"].append({"chest_uid": cuid, "event_id": rw["chest"]})
        cname = (EVENTS.get(rw["chest"]) or DIVE_EVENTS.get(rw["chest"]) or {}).get("name", "Chest")
        parts.append("%s (pending, open %s)" % (cname, cuid))
    if rw.get("fragment") or rw.get("map"):   # Map fragments and rare full maps unlock dive sites.
        locked = [lid for lid in LOCATIONS if not _dive_unlocked(lid)]
        if not locked:                         # Convert excess map progress into points once all dive sites are unlocked.
            p = 180 if rw.get("map") else 60; S["points"] += p; parts.append("+%d pts" % p)
        elif rw.get("map"):
            lid = locked[rng.rint(0, len(locked) - 1)]
            S.setdefault("dive_unlocked", []).append(lid); S.get("map_fragments", {}).pop(lid, None)
            parts.append("🗺️✨ Complete treasure map -> dive site unlocked at %s" % LOCATIONS[lid]["name"])
        else:                                  # Prefer the current locked location for fragment progress.
            lid = S["location_id"] if S["location_id"] in locked else locked[rng.rint(0, len(locked) - 1)]
            fr = S.setdefault("map_fragments", {}); fr[lid] = fr.get(lid, 0) + rw["fragment"]
            need = _dive_frags_needed(LOCATIONS[lid]); nm = LOCATIONS[lid]["name"]
            if fr[lid] >= need:
                fr[lid] = 0
                if lid not in S.setdefault("dive_unlocked", []): S["dive_unlocked"].append(lid)
                parts.append("🗺️ Treasure map completed for %s -> dive site unlocked" % nm)
            else:
                parts.append("🧩 %s map fragment (%d/%d)" % (nm, fr[lid], need))
    return parts
def _letter_exhausted(e):
    return bool(e.get("unique")) and len(S["seen_letters"].get(e["id"], [])) >= len(e.get("messages", []))
def _resolve_event(rng):
    lst = [e for e in EVENTS.values() if e["type"] != "junk" and not _letter_exhausted(e)]
    if not lst: return "The surface trembles, then settles again.\n%s" % _footer()
    ev = _pick_by_weight(rng, lst)
    if ev["type"] == "chest":
        S["stats"]["total_chests"] += 1
        uid = "ch_%03d" % S["stats"]["total_chests"]
        S["pending_chests"].append({"chest_uid": uid, "event_id": ev["id"]})
        return "📦 %s! %s\n(Use open %s.)\n%s" % (ev["name"], ev["description"], uid, _footer())
    if ev["type"] == "bottle" and ev.get("unique") and ev.get("messages"):
        seen = S["seen_letters"].setdefault(ev["id"], [])
        avail = [i for i in range(len(ev["messages"])) if i not in seen]
        idx = avail[rng.rint(0, len(avail) - 1)]
        seen.append(idx)
        parts = _grant_rewards(rng, ev.get("rewards"))
        return "📜 %s! %s\n%s\n★ New letter collected (%d/%d; use encyclopedia to reread).%s\n%s" % (ev["name"], ev["description"], ev["messages"][idx], len(seen), len(ev["messages"]), ("\nGained " + ", ".join(parts)) if parts else "", _footer())
    msg = ""
    if ev["type"] == "bottle" and ev.get("messages"):
        msg = "\n" + ev["messages"][rng.rint(0, len(ev["messages"]) - 1)]
    parts = _grant_rewards(rng, ev.get("rewards"))
    icon = "📜" if ev["type"] == "bottle" else "✨"
    return "%s %s! %s%s%s\n%s" % (icon, ev["name"], ev["description"], msg, ("\nGained " + ", ".join(parts)) if parts else "", _footer())
def _c_open(uid):
    idx = next((i for i, c in enumerate(S["pending_chests"]) if c["chest_uid"] == uid), -1)
    if idx < 0: return "No pending chest named %s. Check inventory for chest ids." % uid
    eid = S["pending_chests"][idx]["event_id"]
    ev = EVENTS.get(eid) or DIVE_EVENTS.get(eid)   # Surface and underwater chests share the open lookup.
    if not ev:
        S["pending_chests"].pop(idx); return "Chest %s was missing its data and has been discarded." % uid
    rng = _Rng(S["rngState"], S["rngCalls"])
    lock = ev.get("lock")
    if lock:
        if lock.get("requires_item") and S["items"].get(lock["requires_item"], 0) > 0:
            S["items"][lock["requires_item"]] = S["items"].get(lock["requires_item"], 0) - 1
        elif lock.get("or_points") is not None and S["points"] >= lock["or_points"]:
            S["points"] -= lock["or_points"]
        else:
            need = " or ".join([x for x in [(ITEMS.get(lock["requires_item"], {}).get("name", lock["requires_item"]) if lock.get("requires_item") else ""), ("%d pts" % lock["or_points"]) if lock.get("or_points") is not None else ""] if x])
            return "%s will not open: needs %s. The chest stays in your inventory." % (uid, need)
    S["pending_chests"].pop(idx)
    parts = _grant_rewards(rng, _pick_by_weight(rng, ev["loot_table"])["reward"]) if ev.get("loot_table") else _grant_rewards(rng, ev.get("rewards"))
    S["rngState"] = rng.state; S["rngCalls"] = rng.calls
    return "🗝 Opened %s! %s\n%s" % (ev["name"], ("Gained " + ", ".join(parts)) if parts else "It was empty.", _footer())

_JUNK = ["一团废弃鱼线", "一只进水的旧靴", "一片水磨玻璃", "一截浮木", "一个褪色塑料瓶盖"]
def _rar(k): return RARITY[k]["label"] + " " + RARITY[k]["tag"]
def _sloc(): return LOCATIONS[S["location_id"]]["name"] + " · " + SEASONS[S["season_id"]]["name"]
def _footer(): return "Points %d | %s | Turn %d | Encyclopedia %d/%d" % (S["points"], _sloc(), S["turn"], len(S["encyclopedia"]), len(FISH))

# Compact machine-readable status bar appended to every command.
def _state_json():
    bait = {b: n for b, n in S["bait_inventory"].items() if n > 0}
    j = {"pts": S["points"], "loc": LOCATIONS[S["location_id"]]["name"], "sea": SEASONS[S["season_id"]]["name"],
         "turn": S["turn"], "enc": "%d/%d" % (len(S["encyclopedia"]), len(FISH)),
         "bait": bait, "hold": len(S["catch_inventory"])}   # hold means unsold catch instances.
    if S.get("pending_chests"): j["chest"] = len(S["pending_chests"])
    if S.get("oxygen", 0) > 0: j["oxygen"] = S["oxygen"]         # Oxygen tanks are dive consumables bought in the shop.
    if S.get("fever", 0) > 0: j["fever"] = S["fever"]            # Remaining doubled-catch casts.
    if S.get("free_bait", 0) > 0: j["free_bait"] = S["free_bait"]  # Remaining free-bait casts.
    lid = S["location_id"]   # Map fragments and rare full maps unlock dive sites.
    if not _dive_unlocked(lid):
        have = S.get("map_fragments", {}).get(lid, 0)
        if have > 0: j["map_frag"] = "%d/%d" % (have, _dive_frags_needed(LOCATIONS[lid]))
    return "📊 " + json.dumps(j, ensure_ascii=False)
# Count undiscovered in-season catches by normal and legendary bands.
# Global mythic fish are excluded from local completion walls.
def _undiscovered_here(loc_id, sea_id):
    normal = legend = 0
    for f in FISH.values():
        if f.get("dive") or not _eligible(f, loc_id, sea_id) or f["id"] in S["encyclopedia"]: continue
        if f["rarity"] in ("legendary", "mythic"):
            if "all" not in f["locations"]: legend += 1
        else:
            normal += 1
    return normal, legend
# Oxygen tanks are dive consumables bought in the shop.
def _undiscovered_dive(loc_id, sea_id):
    return sum(1 for f in FISH.values() if f.get("dive") and not f.get("branch_only") and _eligible(f, loc_id, sea_id) and f["id"] not in S["encyclopedia"])

def _c_status():
    baits = ", ".join("%s×%d" % (BAITS[b]["name"], n) for b, n in S["bait_inventory"].items() if n > 0) or "(no bait; buy more in shop)"
    extra = ""
    items = [(k, n) for k, n in S.get("items", {}).items() if n > 0]
    if items: extra += "\nItems: " + ", ".join("%s×%d" % (ITEMS.get(k, {}).get("name", k), n) for k, n in items)
    if S.get("pending_chests"): extra += "\n📦 Pending chests: %d (see inventory; open by id)" % len(S["pending_chests"])
    frags = [(k, v) for k, v in S.get("map_fragments", {}).items() if k in LOCATIONS and v > 0 and not _dive_unlocked(k)]
    if frags: extra += "\n🧩 Map fragments: " + ", ".join("%s %d/%d" % (LOCATIONS[k]["name"], v, _dive_frags_needed(LOCATIONS[k])) for k, v in frags)
    unlocked_dive_names = [LOCATIONS[l]["name"] for l in S.get("dive_unlocked", []) if l in LOCATIONS]
    if unlocked_dive_names: extra += "\n🗺️ Unlocked dive sites: " + ", ".join(unlocked_dive_names)
    air = ("\nOxygen tanks: %d (used by dive)" % S.get("oxygen", 0)) if (S.get("oxygen", 0) > 0 or S.get("oxygen_ever")) else ""
    return "[Status] %s\nBait: %s%s\nUnsold catches: %d | Total casts %d%s" % (_footer(), baits, air, len(S["catch_inventory"]), S["stats"]["total_casts"], extra)
def _c_shop():
    lines = ["%s  %s  %d pts  %s" % (b["id"], b["name"], b["cost"], ("has preference bonuses; use look" if (b["effects"].get("tag_weight_mult") or b["effects"].get("rarity_weight_mult")) else "no special effect")) for b in BAITS.values()]
    dive_open = bool(S.get("dive_unlocked"))   # Oxygen tanks are dive consumables bought in the shop.
    if dive_open:
        lines.append("%s  %s  %d pts  for diving; 5 tanks get 20%% off, 10 tanks get 30%% off" % (OXYGEN["id"], OXYGEN["name"], OXYGEN["cost"]))
    tail = "\nShopkeeper: Better bait helps fish already present bite more often, but it cannot create species. Change location or season to discover more."
    tail += "\nShopkeeper: Want underwater catches? Buy oxygen and use dive." if dive_open else "\nShopkeeper: Oxygen tanks unlock after your first completed treasure map reveals a dive site."
    return "[Shop] (buy <id> [qty])\n" + "\n".join(lines) + tail
def _c_buy(bait_id, qty):
    if bait_id in ("oxygen", "oxygen_tank", "oxygen_tank"):   # Oxygen tanks are dive consumables bought in the shop.
        if not S.get("dive_unlocked"):
            return "Oxygen tanks are not for sale yet. Collect treasure-map fragments from surface fishing to unlock your first dive site."
        qty = max(1, int(qty))
        disc = 0.7 if qty >= 10 else (0.8 if qty >= 5 else 1.0)   # Bulk oxygen discounts.
        base = OXYGEN["cost"] * qty; cost = int(round(base * disc))
        if S["points"] < cost: return "Not enough points: %s×%d costs %d pts%s; you have %d." % (OXYGEN["name"], qty, cost, " after bundle discount" if disc < 1.0 else "", S["points"])
        S["points"] -= cost; S["oxygen"] = S.get("oxygen", 0) + qty; S["oxygen_ever"] = True
        saved = ", saved %d pts" % (base - cost) if disc < 1.0 else ""
        return "Bought %s×%d for %d pts%s. Points left: %d. Oxygen tanks: %d. Use dive to explore underwater." % (OXYGEN["name"], qty, cost, saved, S["points"], S["oxygen"])
    b = BAITS.get(bait_id)
    if not b: return "No such bait: %s. Use shop to see the shelf." % bait_id
    qty = max(1, int(qty)); cost = b["cost"] * qty
    if S["points"] < cost: return "Not enough points: %s×%d costs %d pts; you have %d." % (b["name"], qty, cost, S["points"])
    S["points"] -= cost; S["bait_inventory"][bait_id] = S["bait_inventory"].get(bait_id, 0) + qty
    return "Bought %s×%d for %d pts. Points left: %d. You now have %s×%d." % (b["name"], qty, cost, S["points"], b["name"], S["bait_inventory"][bait_id])
def _goto_list():
    def rank(l):
        return 0 if l["id"] == S["location_id"] else (1 if l["id"] in S["unlocked_locations"] else 2)
    entries = sorted(LOCATIONS.values(), key=lambda l: (rank(l), l["unlock_cost"]))
    lines = []
    for l in entries:
        cur = l["id"] == S["location_id"]; unlocked = l["id"] in S["unlocked_locations"]
        mark = "✦" if cur else ("·" if unlocked else "🔒")
        st = "[current]" if cur else ("unlocked" if unlocked else "unlock %d pts" % l["unlock_cost"])
        season_ok = S["season_id"] in l["available_seasons"]
        normal, legend = _undiscovered_here(l["id"], S["season_id"]) if season_ok else (0, 0)
        leg = " (+%d legendary-tier)" % legend if legend > 0 else ""
        sea = "quiet this season" if not season_ok else ("%d undiscovered this season%s" % (normal, leg) if normal > 0 else ("regular catches complete%s" % leg if legend > 0 else "complete this season"))
        dive_seg = ""
        if _dive_aware() and season_ok:
            if _dive_unlocked(l["id"]):
                dn = _undiscovered_dive(l["id"], S["season_id"])
                if dn > 0: dive_seg = "  🤿 underwater undiscovered %d" % dn
            else:
                dive_seg = "  🔒 dive locked (map %d/%d)" % (S.get("map_fragments", {}).get(l["id"], 0), _dive_frags_needed(l))
        lines.append("  %s %s  %s -- %s | %s%s" % (mark, l["name"], l["id"], st, sea, dive_seg))
    return "[Locations] (goto <location_id>; locked sites cost points)\n%s\n(You have %d pts)" % ("\n".join(lines), S["points"])
def _c_goto(loc_id):
    if not loc_id: return _goto_list()   # No argument lists all fishing spots.
    loc = LOCATIONS.get(loc_id)
    if not loc: return "No such location: %s. Use goto without an argument to list locations." % loc_id
    if loc_id not in S["unlocked_locations"]:
        if S["points"] < loc["unlock_cost"]: return "%s is locked. It costs %d pts; you have %d." % (loc["name"], loc["unlock_cost"], S["points"])
        S["points"] -= loc["unlock_cost"]; S["unlocked_locations"].append(loc_id)
    S["location_id"] = loc_id; S["local_dry"] = 0
    season_ok = S["season_id"] in loc["available_seasons"]
    off = " (This location is quiet this season.)" if not season_ok else ""
    char = ("\n" + loc["character"]) if loc.get("character") else ""
    normal, legend = _undiscovered_here(loc_id, S["season_id"]) if season_ok else (0, 0)
    leg_hint = ", plus %d legendary-tier possibility" % legend if legend > 0 else ""
    hint = "" if not season_ok else ("\nThis season still has %d undiscovered regular catches%s here." % (normal, leg_hint) if normal > 0 else ("\nRegular catches are complete here this season, but %d legendary-tier possibility remains." % legend if legend > 0 else "\nYou have completed the regular catches here this season."))
    if _dive_aware() and season_ok:   # Underwater hint is shown only after the dive system is known.
        if _dive_unlocked(loc_id):
            dn = _undiscovered_dive(loc_id, S["season_id"])
            if dn > 0: hint += "\n🤿 Underwater has %d undiscovered catches. Use dive to explore." % dn
        else:
            have = S.get("map_fragments", {}).get(loc_id, 0)
            hint += "\n🔒 The dive site is locked. Surface fishing may find map fragments (%d/%d)." % (have, _dive_frags_needed(loc))
    return "Arrived at [%s]. %s%s%s%s" % (loc["name"], loc["description"], char, off, hint)
def _c_inv():
    out = []
    if S["catch_inventory"]:
        out.append("🐟 Catches:\n" + "\n".join("  %s  %s  %scm  %d pts" % (c["instance_id"], FISH.get(c["fish_id"], {}).get("name", c["fish_id"]), c["size"], c["value"]) for c in S["catch_inventory"]))
    items = [(k, n) for k, n in S.get("items", {}).items() if n > 0]
    if items:
        out.append("🎁 Items:\n" + "\n".join("  %s  %s×%d%s" % (k, ITEMS.get(k, {}).get("name", k), n, (" (sell item %s)" % k) if ITEMS.get(k, {}).get("sellable") else "") for k, n in items))
    if S.get("pending_chests"):
        out.append("📦 Pending chests:\n" + "\n".join("  %s (open %s)" % (c["chest_uid"], c["chest_uid"]) for c in S["pending_chests"]))
    frags = [(k, v) for k, v in S.get("map_fragments", {}).items() if k in LOCATIONS and v > 0 and not _dive_unlocked(k)]
    if frags:
        out.append("🧩 Map fragments (complete a map to unlock local diving):\n" + "\n".join("  %s %d/%d" % (LOCATIONS[k]["name"], v, _dive_frags_needed(LOCATIONS[k])) for k, v in frags))
    if not out: return "Your creel is empty. Use cast to fish."
    return "[Inventory] (sell <catch_id>/sell all/sell species <fish_id>/sell item <item_id>)\n" + "\n".join(out)
def _c_sell(target):
    target = (target or "").strip()
    m = re.match(r"^item[:\s]+(.+)$", target)
    if m:
        iid = m.group(1).strip(); it = ITEMS.get(iid)
        if not it: return "No such item: %s" % iid
        if not it.get("sellable"): return "%s cannot be sold." % it["name"]
        have = S["items"].get(iid, 0)
        if have <= 0: return "You do not have %s." % it["name"]
        gain = it["value"] * have; S["points"] += gain; S["items"][iid] = 0
        return "Sold %s×%d for %d pts. Current points: %d." % (it["name"], have, gain, S["points"])
    sm = re.match(r"^species[:\s]+(.+)$", target)
    if target == "all":
        sold = S["catch_inventory"]; S["catch_inventory"] = []
    elif sm:
        fid = sm.group(1).strip(); sold = [c for c in S["catch_inventory"] if c["fish_id"] == fid]; S["catch_inventory"] = [c for c in S["catch_inventory"] if c["fish_id"] != fid]
    else:
        c = next((x for x in S["catch_inventory"] if x["instance_id"] == target), None)
        if not c: return "No catch in your creel has id: %s" % target
        sold = [c]; S["catch_inventory"] = [x for x in S["catch_inventory"] if x["instance_id"] != target]
    if not sold: return "Nothing to sell for target: %s." % target
    gain = sum(c["value"] for c in sold); S["points"] += gain
    out = "Sold %d catch(es) for %d pts. Current points: %d. Encyclopedia records are kept." % (len(sold), gain, S["points"])
    if target == "all":   # sell all sells fish and reminds the player about sellable treasures.
        treas = [(k, n) for k, n in S.get("items", {}).items() if n > 0 and ITEMS.get(k, {}).get("sellable")]
        if treas: out += "\n💎 You still have sellable treasures: %s (use sell item <item_id>)." % ", ".join("%s×%d" % (ITEMS[k]["name"], n) for k, n in treas)
    return out
def _c_enc():
    total = len(FISH); got = len(S["encyclopedia"]); by = {}
    for f in FISH.values():
        cur = by.get(f["rarity"], [0, 0]); cur[1] += 1
        if f["id"] in S["encyclopedia"]: cur[0] += 1
        by[f["rarity"]] = cur
    rl = "  ".join("%s %d/%d" % (RARITY[k]["label"], by[k][0], by[k][1]) for k in RARITY if k in by)
    # Encyclopedia output stays compact and discovery-focused.
    lines = ["%s %s (%s) ×%d max %scm" % ("✔" if S["encyclopedia"][f["id"]].get("identification", "verified") == "verified" else "?", f["name"], _rar(f["rarity"]), S["encyclopedia"][f["id"]]["count"], S["encyclopedia"][f["id"]]["max_size"])
             for f in FISH.values() if f["id"] in S["encyclopedia"]]
    lb = ""
    for ev in EVENTS.values():
        if ev.get("unique") and ev.get("messages"):
            seen = sorted(S["seen_letters"].get(ev["id"], []))
            lb += "\n\n📜 %s %d/%d" % (ev["name"], len(seen), len(ev["messages"]))
            lb += ("\n" + "\n".join("  - %s" % ev["messages"][i] for i in seen)) if seen else "\n  (no letters collected yet)"
    body = "\n".join(lines) if lines else "(no fish recorded yet; use cast)"
    return "[Encyclopedia] %d/%d (discovered only)  %s\n%s%s" % (got, total, rl, body, lb)
def _by_id_or_name(table, q):
    if q in table: return table[q]
    for v in table.values():
        if v.get("name") == q: return v
    return None
def _c_look(oid):
    f = _by_id_or_name(FISH, oid)
    if f:
        if f["id"] not in S["encyclopedia"]:
            return "??? (%s) -- You have not caught it yet; land one to reveal the entry." % _rar(f["rarity"])
        locs = "any water" if "all" in f["locations"] else ", ".join(LOCATIONS.get(l, {}).get("name", l) for l in f["locations"])
        seas = "all year" if "all" in f["seasons"] else ", ".join(SEASONS.get(x, {}).get("name", x) for x in f["seasons"])
        latin = (" (%s)" % f["latin"]) if f.get("latin") else ""; rumor = ("\n📜 Rumor: %s" % f["rumor"]) if f.get("rumor") else ""
        cf = ("\n🫧 Feel: %s" % f["capture_feel"]) if f.get("capture_feel") else ""
        diveflag = " (🤿 dive-only; cannot be caught from the surface)" if f.get("dive") else ""
        origin = {"native": "原生", "introduced": "引入", "endemic": "特有"}.get(f.get("native_status"), f.get("native_status", "未记录"))
        release = " · 📷 仅观察放流" if f.get("release_only") else ""
        science = "\n🔬 科普：%s" % f.get("science_fact_zh", f["description"])
        identify = "\n🔎 辨认：%s" % f.get("identification_zh", "暂无辨认笔记")
        ecology = "\n🌿 身份：%s · 保护标记：%s%s" % (origin, f.get("conservation", "未评估"), release)
        return "%s%s (%s)%s\n%s%s%s%s%s%s\n体长 %s-%s%s | 观察价值 %s | 水域：%s · %s" % (f["name"], latin, _rar(f["rarity"]), diveflag, f["description"], rumor, cf, science, identify, ecology, f["size_min"], f["size_max"], f["size_unit"], f["base_value"], locs, seas)
    l = _by_id_or_name(LOCATIONS, oid)
    if l: return "%s\n%s\nOpen seasons: %s  Unlock cost: %d pts" % (l["name"], l["description"], ", ".join(SEASONS[x]["name"] for x in l["available_seasons"]), l["unlock_cost"])
    b = _by_id_or_name(BAITS, oid)
    if b: return "%s (%d pts)\n%s" % (b["name"], b["cost"], b["description"])
    it = _by_id_or_name(ITEMS, oid)
    if it: return "%s%s\n%s" % (it["name"], (" (treasure, sells for %d pts)" % it["value"]) if it.get("sellable") else " (key item, cannot be sold)", it["description"])
    x = _by_id_or_name(SEASONS, oid)
    if x: return "%s\n%s" % (x["name"], x["description"])
    return "No such object: %s" % oid

def _c_identify(fid, choice=None):
    f = FISH.get(fid)
    if not f: return "没有这个物种 id：%s" % fid
    e = S["encyclopedia"].get(fid)
    if not e: return "你还没有观察到这个物种，暂时无法进行鉴定。"
    quiz = f.get("quiz")
    if not quiz:
        e["identification"] = "verified"
        return "%s 的记录不需要额外纠错题，已经确认。" % f["name"]
    if choice is None:
        opts = "\n".join("  %d. %s" % (i + 1, text) for i, text in enumerate(quiz["choices_zh"]))
        state = "（已确认，可再次复习）" if e.get("identification") == "verified" else "（待鉴定）"
        return "[物种鉴定] %s %s\n%s\n%s\n回答：identify %s <编号>" % (f["name"], state, quiz["question_zh"], opts, fid)
    if not 1 <= choice <= len(quiz["choices_zh"]):
        return "选项应为 1-%d。" % len(quiz["choices_zh"])
    if choice == quiz["answer"]:
        first_verify = e.get("identification") != "verified"
        e["identification"] = "verified"
        if first_verify:
            S["points"] += 10
        return "✅ 鉴定确认：%s\n%s%s" % (f["name"], quiz["explanation_zh"], "\n观察奖励 +10 pts" if first_verify else "")
    e["misidentifications"] = e.get("misidentifications", 0) + 1
    e["identification"] = "pending"
    return "↺ 这次判断需要修正。%s\n误判已写入观察日志；可以重新检查特征后再答。" % quiz["wrong_zh"]
_BITE_SOFT = ["The float dips softly--", "The float vanishes with a plunk--", "The line tightens; something is moving--"]
_BITE_HARD = ["The line snaps tight, nearly out of your hand--!", "The rod bends hard and spray erupts--!", "A heavy force drags downward--!"]
def _bite_line(rng, rarity):
    pool = _BITE_HARD if rarity in ("rare", "epic", "legendary", "mythic") else _BITE_SOFT
    return pool[rng.rint(0, len(pool) - 1)]
# Catch narration scales by rarity and first discovery.
# Underwater fish: dive-only catches, including capture feel text.
def _format_catch(f, size, value, inst, first):
    u = f["size_unit"]; r = f["rarity"]; rl = RARITY[r]["label"]
    cf = ("\n🫧 " + f["capture_feel"]) if f.get("capture_feel") else ""   # Underwater fish: dive-only catches, including capture feel text.
    release_note = "\n📷 完成测量与辨认后原地放流；本记录不会进入鱼篓或出售。" if f.get("release_only") else ""
    flavor = f.get("description", "") + cf + release_note
    if r in ("legendary", "mythic"):   # Legendary and mythic catches receive full narration.
        top = "👑 --- LEGENDARY --- 👑" if r == "legendary" else "✧ ------ MYTHIC ------ ✧"
        nm = " (★first record +%d pts)" % RARITY[r]["discovery_bonus"] if first else ""
        body = "%s · %s%s · %d pts%s\n%s%s" % (f["name"], size, u, value, nm, flavor, ("\n📜 " + f["rumor"]) if f.get("rumor") else "")
        return "%s\n%s\n%s" % (top, body, top) if r == "mythic" else "%s\n%s" % (top, body)
    if first:   # First discoveries include compact detail and bonus text.
        quiz_note = "\n🔎 新观察仍待鉴定：identify %s" % f["id"] if f.get("quiz") else ""
        return "🆕 %s · %s · %s%s · %d pts\n%s\nFirst record +%d pts%s" % (f["name"], rl, size, u, value, flavor, RARITY[r]["discovery_bonus"], quiz_note)
    if r in ("rare", "epic"):
        return "%s %s · %s%s · %d pts\n%s" % ("✦✦ Epic" if r == "epic" else "✦ Rare", f["name"], size, u, value, flavor)
    return "· %s%s %s%s +%d" % (f["name"], " (uncommon)" if r == "uncommon" else "", size, u, value)
def _ambience(loc, rng):
    # Ambience appears once per location-season change.
    key = "%s|%s" % (S["location_id"], S["season_id"])
    if S.get("ambience_scene") == key: return ""
    S["ambience_scene"] = key
    amb = loc.get("ambience")
    if not amb: return ""
    return "\n(%s)" % amb[rng.rint(0, len(amb) - 1)]
# Completion walls ignore legendary and mythic catches.
def _local_practical_cleared():
    elig = [f for f in FISH.values() if _eligible(f, S["location_id"], S["season_id"]) and f["rarity"] not in ("legendary", "mythic")]
    return bool(elig) and all(f["id"] in S["encyclopedia"] for f in elig)
# In-world hinting is deterministic and RNG-free.
def _secret_hint():
    d = S.get("local_dry", 0)
    if d >= 8 and d % 8 == 0 and _local_practical_cleared():
        return "\n(You start to suspect this location has no more regular secrets this season. Try goto, or wait for seasons to turn.)"
    return ""
# Single-step cast/dive result helper.
# Record catch instance, inventory, encyclopedia, and discovery rewards.
def _record_catch(f, size, value):
    inst = "c_%03d" % (S["stats"]["total_caught"] + 1)
    if f.get("release_only"):
        inst = "obs_%03d" % (S["stats"]["total_caught"] + 1)
        S["stats"]["released"] = S["stats"].get("released", 0) + 1
    else:
        S["catch_inventory"].append({"instance_id": inst, "fish_id": f["id"], "size": size, "value": value})
    S["stats"]["total_caught"] += 1
    first = _upd_enc(f, size, value)
    bonus = RARITY[f["rarity"]]["discovery_bonus"] if first else 0
    if bonus: S["points"] += bonus
    return inst, first, bonus
# Encyclopedia milestone narration.
def _milestone_line(f, first):
    if not first: return ""
    got = len(S["encyclopedia"]); total = len(FISH)
    if got >= total: return "\n🎉🎉 Encyclopedia complete! All %d fish are recorded. You are a legend of these waters." % total
    tier = [x for x in FISH.values() if x["rarity"] == f["rarity"]]
    if tier and all(x["id"] in S["encyclopedia"] for x in tier):
        return "\n🎉 %s tier complete! (%d species recorded)" % (RARITY[f["rarity"]]["label"], len(tier))
    if got % 10 == 0: return "\n🎉 Encyclopedia milestone: %d/%d species!" % (got, total)
    return ""

def _c_journal():
    """Render ecological observations separately from sale inventory."""
    seen = [f for f in FISH.values() if f["id"] in S["encyclopedia"]]
    if not seen:
        return "[观察日志] 还没有物种记录。第一竿不一定有鱼，但每次观察都会让地图更清楚。"
    native = sum(f.get("native_status") == "native" for f in seen)
    introduced = sum(f.get("native_status") == "introduced" for f in seen)
    released = S.get("stats", {}).get("released", 0)
    lines = ["[观察日志] %d/%d 种 | 原生 %d · 引入 %d · 保护放流 %d 次" % (len(seen), len(FISH), native, introduced, released)]
    for f in seen:
        e = S["encyclopedia"][f["id"]]
        verified = e.get("identification", "verified") == "verified"
        mark = "📷" if f.get("release_only") else ("✓" if verified else "?")
        correction = " · 待鉴定" if not verified else (" · 曾纠正%d次" % e.get("misidentifications", 0) if e.get("misidentifications", 0) else "")
        lines.append("%s %s / %s — 观察%d次，最大%s cm%s" % (mark, f["name"], f.get("name_en", f["id"]), e["count"], e["max_size"], correction))
    lines.append("提示：用 identify <物种id> 学习鉴别；用 look <物种id> 查看完整科普笔记。")
    return "\n".join(lines)

# Map fragments and rare full maps unlock dive sites.
_FRAG_CHANCE = 0.15   # Extra local map-fragment chance on successful surface catches.
def _dive_unlocked(loc_id): return loc_id in S.get("dive_unlocked", [])
def _dive_aware(): return bool(S.get("oxygen_ever") or S.get("dive_unlocked") or S.get("map_fragments"))
def _dive_frags_needed(loc):   # Deeper or pricier waters require more map fragments.
    c = loc["unlock_cost"]
    return 3 if c <= 200 else (4 if c <= 480 else 5)
def _gain_fragment(loc_id):
    fr = S.setdefault("map_fragments", {}); fr[loc_id] = fr.get(loc_id, 0) + 1
    need = _dive_frags_needed(LOCATIONS[loc_id]); name = LOCATIONS[loc_id]["name"]
    if fr[loc_id] >= need:
        fr[loc_id] = 0
        if loc_id not in S.setdefault("dive_unlocked", []): S["dive_unlocked"].append(loc_id)
        return "\n🗺️ You assembled %d map fragments into the treasure map for [%s]. This dive site is unlocked! Buy oxygen and use dive." % (need, name)
    return "\n🧩 You also found a [%s] treasure-map fragment! (%d/%d to unlock this dive site)" % (name, fr[loc_id], need)

# Luck events can apply immediate rewards or short-lived buffs.
LUCK_CHANCE = 0.05          # Luck-event chance after a successful catch.
RUIN_CHANCE = 0.03          # Major ruin encounters pause the expedition for a choice.
FULL_DEX_RUIN_BOOST = 3     # Major ruin encounters pause the expedition for a choice.
_FEVER_CASTS = 3            # Fever duration in casts.
_FREE_BAIT_CASTS = 3       # Free-bait duration in casts.
_LUCK_EVENTS = [
    {"id": "split_hook", "weight": 28},
    {"id": "golden_touch", "weight": 24},
    {"id": "fever", "weight": 16},
    {"id": "river_blessing", "weight": 16},
    {"id": "tide_record", "weight": 8},
    {"id": "lucky_pearl", "weight": 8},
]
# Dive-only luck events.
_PEARL_TREASURES = ["coral_pearl", "gem_sapphire", "moonstone", "ambergris", "shipwreck_coin"]   # Fixed pearl treasure pool.
# Data-driven underwater encounter.
def _resolve_dive_encounter(rng, enc):
    parts = _grant_rewards(rng, enc.get("reward"))
    body = ("\n🎁 Gained " + ", ".join(parts)) if parts else ""
    return "%s ✨[%s] %s%s" % (enc.get("emoji", "🌊"), enc["name"], enc["text"], body)
def _roll_luck(rng, pool, bait_id, f, size, inst, mode="cast"):
    # Major ruin encounters pause the expedition for a choice.
    if mode == "dive":
        _full = len(S["encyclopedia"]) >= len(FISH)   # Major ruin encounters pause the expedition for a choice.
        if rng.random() < RUIN_CHANCE * (FULL_DEX_RUIN_BOOST if _full else 1):
            ruins = [{"id": e["id"], "weight": e["weight"]} for e in DIVE_ENCOUNTERS if e.get("branch")]
            return "", _pick_by_weight(rng, ruins)["id"]   # Major ruin encounters pause the expedition for a choice.
    if rng.random() >= LUCK_CHANCE: return "", None
    # Major ruin encounters pause the expedition for a choice.
    if mode == "dive":
        events = [{"id": e["id"], "weight": e["weight"]} for e in DIVE_ENCOUNTERS if not e.get("branch")]
    else:
        events = _LUCK_EVENTS
    eid = _pick_by_weight(rng, events)["id"]
    if eid == "split_hook":   # Split hook adds two extra catches.
        weights = [_eff_weight(g, S["location_id"], S["season_id"], bait_id) for g in pool]
        got = []
        for _ in range(2):
            g = _wpick(rng, pool, weights); gs = _roll_size(rng, g); gv = _value(g, gs)
            gi, gfirst, _b = _record_catch(g, gs, gv)
            got.append("%s%s %s%s[%s]" % (g["name"], "★new" if gfirst else "", gs, g["size_unit"], gi))
        return "🪝✨ Split Hook! The hook becomes three, pulling up two more catches: " + ", ".join(got), eid
    if eid == "golden_touch":   # This catch receives a value multiplier.
        c = next((x for x in S["catch_inventory"] if x["instance_id"] == inst), None)
        if not c: return "", None
        old = c["value"]; c["value"] = old * 3
        return "✨💰 Golden Touch! This catch value triples: %d -> %d pts" % (old, c["value"]), eid
    if eid == "fever":
        S["fever"] = S.get("fever", 0) + _FEVER_CASTS
        return "🔥 Catch Fever! The next %d successful catches are doubled." % _FEVER_CASTS, eid
    if eid == "river_blessing":
        if bait_id: S["bait_inventory"][bait_id] = S["bait_inventory"].get(bait_id, 0) + 1
        S["free_bait"] = S.get("free_bait", 0) + _FREE_BAIT_CASTS
        return "🌊🙏 River Blessing! This bait is refunded, and the next %d casts cost no bait." % _FREE_BAIT_CASTS, eid
    if eid == "tide_record":   # This catch is raised to its maximum size.
        c = next((x for x in S["catch_inventory"] if x["instance_id"] == inst), None)
        if not c: return "", None
        rs = f["size_max"]; rv = _value(f, rs)
        e = S["encyclopedia"].get(f["id"])
        if e: e["max_size"] = max(e["max_size"], rs); e["total_value_earned"] += max(0, rv - c["value"])
        c["size"] = rs; c["value"] = rv
        return "🌊📏 Once-in-a-Blue Tide! This catch surges to max size %s%s, worth %d pts." % (rs, f["size_unit"], rv), eid
    if eid == "lucky_pearl":   # Random treasure found inside the catch.
        tk = _PEARL_TREASURES[rng.rint(0, len(_PEARL_TREASURES) - 1)]
        S["items"][tk] = S["items"].get(tk, 0) + 1
        return "🦪✨ Hidden Pearl! A %s rolls out of the catch (sell item %s)." % (ITEMS[tk]["name"], tk), eid
    enc = _DIVE_ENC_BY_ID.get(eid)   # Data-driven underwater encounter.
    if enc:
        if enc.get("branch"): return "", eid   # Major ruin encounters pause the expedition for a choice.
        return _resolve_dive_encounter(rng, enc), eid
    return "", None

_DIVE_JUNK = ["a rope tangled with weeds", "a barnacled empty shell", "an awkward piece of reef rock", "an empty conch", "a slick clump of algae"]
_DIVE_BITE = ["You kick downward and a shape flashes past--", "Pressure wraps your ears as a shadow darts from the reef--", "You reach the bottom and touch a cold scale--"]
# Underwater fish: dive-only catches, including capture feel text.
# Underwater fish: dive-only catches, including capture feel text.
def _cast_step(rng, bait_id, mode="cast"):
    dive = mode == "dive"
    if dive:
        if S.get("oxygen", 0) <= 0:
            return {"text": "Out of oxygen tanks. Buy oxygen in shop before diving. No turn spent.", "consumed": False, "kind": "no_air", "season_changed": False}
        S["oxygen"] -= 1
        bait_id = "basic_worm"   # Dives borrow plain-worm zero-bonus weighting.
    else:
        inv = S["bait_inventory"]
        if not bait_id:
            avail = [b for b in inv if inv[b] > 0]
            if not avail: return {"text": "No bait left. Buy bait in shop. No turn spent.", "consumed": False, "kind": "no_bait", "season_changed": False}
            bait_id = sorted(avail, key=lambda b: BAITS[b]["cost"])[0]
        if bait_id not in BAITS: return {"text": "No such bait: %s" % bait_id, "consumed": False, "kind": "bad_bait", "season_changed": False}
        if inv.get(bait_id, 0) <= 0: return {"text": "%s is depleted. Switch bait or buy more in shop. No turn spent." % BAITS[bait_id]["name"], "consumed": False, "kind": "no_bait", "season_changed": False}
        if S.get("free_bait", 0) > 0: S["free_bait"] -= 1   # Active blessing prevents bait consumption for this cast.
        else: inv[bait_id] -= 1
    bait = BAITS[bait_id]
    S["turn"] += 1
    if dive: S["stats"]["total_dives"] = S["stats"].get("total_dives", 0) + 1
    else: S["stats"]["total_casts"] += 1
    season_msg = _adv_season(); season_changed = season_msg != ""
    loc = LOCATIONS[S["location_id"]]
    # Dives do not trigger surface bottle or chest events.
    event_chance = 0 if dive else ((loc.get("event_chance_base", 0.05) + bait["effects"].get("event_chance_add", 0)) if EVENTS else 0)
    if event_chance > 0 and rng.random() < event_chance:
        S["local_dry"] = S.get("local_dry", 0) + 1
        return {"text": season_msg + _resolve_event(rng) + _secret_hint(), "consumed": True, "kind": "event", "season_changed": season_changed}
    junk_chance = loc["junk_chance_base"] * (1.0 if dive else bait["effects"].get("junk_chance_mult", 1.0))
    if rng.random() < junk_chance:
        if not dive: S["local_dry"] = S.get("local_dry", 0) + 1
        if dive:
            return {"text": season_msg + "🪨 You find %s. Empty dive.%s" % (_DIVE_JUNK[rng.rint(0, len(_DIVE_JUNK) - 1)], _ambience(loc, rng)), "consumed": True, "kind": "junk", "season_changed": season_changed}
        local_junk = globals().get("_REAL_WORLD_JUNK", {}).get(S["location_id"], _JUNK)
        return {"text": season_msg + "🪣 你拉上来%s。这一竿没有鱼，但它也属于这片水域的记录。%s%s" % (local_junk[rng.rint(0, len(local_junk) - 1)], _ambience(loc, rng), _secret_hint()), "consumed": True, "kind": "junk", "season_changed": season_changed}
    pool = [f for f in FISH.values() if _eligible(f, S["location_id"], S["season_id"]) and bool(f.get("dive")) == dive and not (dive and f.get("branch_only"))]
    if not pool:
        if not dive: S["local_dry"] = S.get("local_dry", 0) + 1
        if dive:
            return {"text": season_msg + "You dive, but this underwater season is empty here.%s" % _ambience(loc, rng), "consumed": True, "kind": "empty", "season_changed": season_changed}
        return {"text": season_msg + "The float does not move. Nothing is biting here this season.%s%s" % (_ambience(loc, rng), _secret_hint()), "consumed": True, "kind": "empty", "season_changed": season_changed}
    weights = [_eff_weight(f, S["location_id"], S["season_id"], bait_id) for f in pool]
    f = _wpick(rng, pool, weights); size = _roll_size(rng, f); value = _value(f, size)
    inst, first, bonus = _record_catch(f, size, value)
    if first: S["local_dry"] = 0
    elif not dive: S["local_dry"] = S.get("local_dry", 0) + 1
    # Fever duplicates the main catch on this cast.
    fever_line = ""
    if S.get("fever", 0) > 0:
        S["fever"] -= 1
        di, dfirst, _b = _record_catch(f, size, value)
        fever_line = "\n🔥 Fever double: gained another %s%s (%s)" % (f["name"], "★new" if dfirst else "", di)
    _bite = (_DIVE_BITE[rng.rint(0, len(_DIVE_BITE) - 1)]) if dive else _bite_line(rng, f["rarity"])  # Keep the RNG draw while omitting repeated bite narration.
    luck_line, luck_id = _roll_luck(rng, pool, bait_id, f, size, inst, mode)   # English note for deterministic game behavior.
    luck_seg = ("\n" + luck_line) if luck_line else ""
    frag_line = ""   # Map fragments and rare full maps unlock dive sites.
    if not dive and not _dive_unlocked(S["location_id"]) and rng.random() < _FRAG_CHANCE:
        frag_line = _gain_fragment(S["location_id"])
    secret = "" if dive else _secret_hint()
    be = bait["effects"]   # Bait feedback explains whether the catch matched bait preferences.
    pref = bool(be) and (f["rarity"] in be.get("rarity_weight_mult", {}) or any(t in be.get("tag_weight_mult", {}) for t in f.get("tags", [])))
    return {"text": season_msg + "%s%s%s%s%s%s%s" % (_format_catch(f, size, value, inst, first), _milestone_line(f, first), fever_line, luck_seg, frag_line, _ambience(loc, rng), secret),
            "consumed": True, "kind": "fish", "fish_name": f["name"], "rarity": f["rarity"], "first": first, "season_changed": season_changed, "luck": luck_id, "fever_hit": fever_line != "", "frag": frag_line != "", "pref": pref}

def _c_cast(bait_id):
    rng = _Rng(S["rngState"], S["rngCalls"])
    out = _cast_step(rng, bait_id)["text"]
    S["rngState"] = rng.state; S["rngCalls"] = rng.calls
    return out

_RARITY_RANK = {"common": 0, "uncommon": 1, "rare": 2, "epic": 3, "legendary": 4, "mythic": 5}
_SOLO_HINT = "\n💡 One cast at a time is chatty. Try cast 10 for one compact summary; add stop=new or stop=rare to stop early."
_DIVE_SOLO_HINT = "\n💡 Bring several oxygen tanks for a longer dive: dive 5, optionally with stop=new."
def _cast_many(bait_id, times, stop_on):   # Multi-cast is surface-only; dives use the expedition system.
    times = max(1, min(20, int(times)))
    rng = _Rng(S["rngState"], S["rngCalls"])
    if times == 1 and not stop_on:
        r = _cast_step(rng, bait_id)
        S["rngState"] = rng.state; S["rngCalls"] = rng.calls
        return r["text"] + _SOLO_HINT if r["consumed"] else r["text"]
    stop = set(stop_on or [])
    highlights = []; caught = {}; caught_n = 0; junk_n = 0; empty_n = 0; done = 0; new_names = set(); pref_hits = 0
    stop_reason = None
    for _ in range(times):
        r = _cast_step(rng, bait_id)
        if not r["consumed"]:
            highlights.append(r["text"]); stop_reason = "out of bait"; break
        done += 1
        rank = _RARITY_RANK.get(r.get("rarity", ""), 0)
        if r.get("first") or rank >= 2 or r["kind"] == "event" or r["season_changed"] or r.get("luck") or r.get("fever_hit") or r.get("frag"):
            highlights.append(r["text"])
        if r["kind"] == "fish":
            caught[r["fish_name"]] = caught.get(r["fish_name"], 0) + 1; caught_n += 1
            if r["first"]: new_names.add(r["fish_name"])
            if r.get("pref"): pref_hits += 1
        elif r["kind"] == "junk": junk_n += 1
        elif r["kind"] == "empty": empty_n += 1
        new_hit = "new" in stop and r.get("first"); rare_hit = "rare" in stop and rank >= 2
        if new_hit or rare_hit or ("event" in stop and r["kind"] == "event"):
            stop_reason = "new species" if new_hit else ("rare catch" if rare_hit else "event"); break
    S["rngState"] = rng.state; S["rngCalls"] = rng.calls
    body = ("\n———\n".join(highlights) + "\n\n") if highlights else ""
    haul = ", ".join("%s%s×%d" % (n, "★" if n in new_names else "", c) for n, c in caught.items()) or "none"
    head = "🎣 Cast batch: %d cast(s)%s" % (done, (" · " + stop_reason) if stop_reason else "")
    tail = "🐟 Catches %d: %s" % (caught_n, haul)
    if junk_n or empty_n: tail += " (empty %d)" % (junk_n + empty_n)
    bf = BAITS.get(bait_id, {}).get("effects") if bait_id else None
    if bf and pref_hits: tail += " | 🎣 %s preference hit %d time(s)" % (BAITS[bait_id]["name"], pref_hits)
    return "%s\n%s%s" % (head, body, tail)

# Major ruin encounters pause the expedition for a choice.
def _exp_render_branch(bid):
    enc = _DIVE_ENC_BY_ID[bid]; ox = S.get("oxygen", 0)
    lines = ["%s ✨[%s] %s" % (enc.get("emoji", "🌊"), enc["name"], enc["intro"]),
             "[Choice] Oxygen remaining: %d tank(s). Use choose <number>:" % ox]
    for i, o in enumerate(enc["options"], 1):
        c = o.get("oxygen", 0); cost = "costs %d oxygen" % c if c > 0 else "free"
        lines.append("  %d. %s (%s)%s" % (i, o["label"], cost, "" if c <= ox else "  🔒 not enough oxygen"))
    return "\n".join(lines)
def _exp_run(rng):
    exp = S["expedition"]; stop = set(exp.get("stop", [])); seg = []; reason = None
    while exp["left"] > 0 and S.get("oxygen", 0) > 0:
        exp["left"] -= 1
        r = _cast_step(rng, None, "dive")
        if not r["consumed"]: break
        exp["done"] += 1
        rank = _RARITY_RANK.get(r.get("rarity", ""), 0); bid = r.get("luck")
        # Fever duplicates the main catch on this cast.
        if r["kind"] == "junk": exp["jn"] += 1
        elif r["kind"] == "empty": exp["en"] += 1
        if bid in _DIVE_BRANCH_IDS:   # Major ruin encounters pause the expedition for a choice.
            exp["pending"] = bid; seg.append(r["text"])
            S["rngState"] = rng.state; S["rngCalls"] = rng.calls
            return ("\n———\n".join(seg) + "\n\n" if seg else "") + _exp_render_branch(bid)
        if r.get("first") or rank >= 2 or r.get("luck") or r.get("fever_hit") or r.get("frag"):
            seg.append(r["text"])
        new_hit = "new" in stop and r.get("first"); rare_hit = "rare" in stop and rank >= 2
        if new_hit or rare_hit:
            reason = "new species" if new_hit else "rare catch"; break
    S["rngState"] = rng.state; S["rngCalls"] = rng.calls
    body = ("\n———\n".join(seg) + "\n\n") if seg else ""
    return body + _exp_settle(reason)
def _exp_settle(reason):   # This catch receives a value multiplier.
    exp = S.pop("expedition")
    trip = S["catch_inventory"][exp["inv0"]:]   # Fever duplicates the main catch on this cast.
    catch_value = sum(c["value"] for c in trip)
    enc0 = set(exp.get("enc0", []))
    new_names = {FISH.get(c["fish_id"], {}).get("name", c["fish_id"]) for c in trip if c["fish_id"] not in enc0}
    by = {}
    for c in trip:
        nm = FISH.get(c["fish_id"], {}).get("name", c["fish_id"]); by[nm] = by.get(nm, 0) + 1
    haul = ", ".join("%s%s×%d" % (n, "★" if n in new_names else "", ct) for n, ct in by.items()) or "none"
    treasure_value = sum(ITEMS.get(k, {}).get("value", 0) * (S["items"].get(k, 0) - exp["items0"].get(k, 0)) for k in S.get("items", {}))
    extra_in = treasure_value + (S["points"] - exp["pts0"])
    oxy_spent = exp["oxy0"] - S.get("oxygen", 0); cost = oxy_spent * OXYGEN["cost"]
    income = catch_value + extra_in; net = income - cost
    head = ("🤿 Expedition stopped: %s" % reason) if reason else ("🤿 Expedition complete · out of oxygen" if S.get("oxygen", 0) <= 0 else "🤿 Expedition complete")
    s = "%s | dives %d/%d | oxygen left %d" % (head, exp["done"], exp.get("budget", exp["done"]), S.get("oxygen", 0))
    s += "\n🐟 Catches %d: %s | estimated value %d pts" % (len(trip), haul, catch_value)
    if extra_in: s += " | 🎁 +%d pts" % extra_in
    if exp["jn"] + exp["en"]: s += " (empty %d)" % (exp["jn"] + exp["en"])
    s += "\n💰 Income %d - oxygen cost %d = trip net %+d pts" % (income, cost, net)
    return s
def _dive_start(n, stop_on):
    if S.get("expedition"): return "You are already on an underwater expedition. Use choose <number> for the current site, or surface to return."
    loc_id = S["location_id"]
    if not _dive_unlocked(loc_id):
        loc = LOCATIONS[loc_id]; need = _dive_frags_needed(loc); have = S.get("map_fragments", {}).get(loc_id, 0)
        return "🔒 The dive site at [%s] is locked. Surface fishing can find map fragments (%d/%d)." % (loc["name"], have, need)
    if S.get("oxygen", 0) <= 0: return "No oxygen tanks. Buy oxygen in shop, then dive."
    n = max(1, min(20, int(n)))
    rng = _Rng(S["rngState"], S["rngCalls"])
    S["expedition"] = {"left": n, "budget": n, "pending": None, "oxy0": S["oxygen"], "pts0": S["points"],
                       "inv0": len(S["catch_inventory"]), "items0": dict(S.get("items", {})), "enc0": list(S["encyclopedia"]),
                       "done": 0, "jn": 0, "en": 0, "stop": list(stop_on or [])}
    opts = LOCATIONS[loc_id].get("dive_ambience", {}).get(S["season_id"], [])
    scene = ("🤿 " + opts[rng.rint(0, len(opts) - 1)] + "\n\n") if opts else ""
    return scene + _exp_run(rng)   # _exp_run writes RNG state back itself.
def _c_choose(n):
    exp = S.get("expedition")
    if not exp or not exp.get("pending"): return "There is no pending major site to choose. Start an expedition with dive; use choose only when one pauses you."
    enc = _DIVE_ENC_BY_ID.get(exp["pending"])
    if not enc: exp["pending"] = None; rng = _Rng(S["rngState"], S["rngCalls"]); out = "That site has faded.\n\n" + _exp_run(rng); return out
    opts = enc["options"]
    if not (1 <= n <= len(opts)): return "Choose 1-%d with choose <number>." % len(opts)
    o = opts[n - 1]; c = o.get("oxygen", 0)
    if c > S.get("oxygen", 0): return "Not enough oxygen: '%s' needs %d tank(s), and you have %d. Pick another option or leave it." % (o["label"], c, S.get("oxygen", 0))
    rng = _Rng(S["rngState"], S["rngCalls"])
    if c: S["oxygen"] -= c
    parts = _grant_rewards(rng, o["outcome"].get("reward"))
    txt = "[%s] %s" % (o["label"], o["outcome"]["text"]) + (("\n🎁 Gained " + ", ".join(parts)) if parts else "")
    exp["pending"] = None
    return txt + "\n\n" + _exp_run(rng)   # Continue the expedition after resolving a choice.
def _c_surface():
    if not S.get("expedition"): return "You are not underwater. Use dive to start an expedition."
    S["expedition"]["pending"] = None
    return "You swim upward and end the expedition.\n" + _exp_settle("manual return")

_HELP = """World Waters Field Journal. Travel through real ecosystems, fish, identify species, release protected wildlife, and build a scientific observation journal.
Commands passed to cmd() are case-insensitive:
  cmd('status')                         Show points, location, season, bait, and progress.
  cmd('shop')                           Show bait and oxygen for sale.
  cmd('buy <bait_id> [qty]')             Buy bait, e.g. cmd('buy glow_bait 2').
  cmd('cast [bait_id]')                  Cast once. Omit bait to use the cheapest available bait.
  cmd('cast [bait_id] N')                Batch-cast N times (1-20) and return one compact summary.
  cmd('cast N stop=rare')                Stop a batch early on new species, rare-or-better catch, or event. Combine with stop=new,rare,event.
  cmd('buy oxygen [qty]')                Buy oxygen tanks for diving after a dive site is unlocked.
  cmd('dive [tanks] [stop=..]')          Start an underwater expedition using N oxygen tanks as the depth budget.
  cmd('choose <number>')                 Choose at a paused major underwater site. Without a number, show choices again.
  cmd('surface')                         End the current expedition and surface.
  cmd('goto')                            List locations, unlock costs, and seasonal undiscovered counts.
  cmd('goto <location_id>')              Travel to a location; locked locations cost points.
  cmd('inventory')                       Show catches, items, and pending chests.
  cmd('sell <catch_id>') | cmd('sell all') | cmd('sell species <fish_id>') | cmd('sell item <item_id>')
  cmd('open <chest_uid>')                Open a pending chest.
  cmd('encyclopedia')                    Show discovered fish and collected letters.
  cmd('journal')                         Show the ecological observation log, native status, and releases.
  cmd('identify <fish_id> [choice]')     Inspect field marks, answer an identification exercise, and correct mistakes.
  cmd('look <id_or_name>')               Inspect a fish, location, bait, season, or item. Unknown fish stay hidden as ???.
  cmd('A; B; C')                         Run up to 8 commands as a batch, e.g. cmd('buy basic_worm 10; cast 10').
Surface casts may find bottles, chests, treasures, and lucky moments. Diving finds underwater-only species and may pause at major sites for choose. Every result ends with a compact 📊 JSON status line, so you usually do not need a separate status call.
Goal: discover as many fish as possible with limited points. Some species depend on location and season; you start blind and learn by fishing."""

def _drain_warn(out):
    "Append any pending save I/O warning to the response once, then clear it."
    global _IO_WARN
    if _IO_WARN:
        out = out + "\n" + _IO_WARN
        _IO_WARN = ""
    return out

_BATCH_MAX = 8
def _run_one(line):
    "Run one command and return player-facing text without loading, saving, or appending the status bar."
    line = (line or "").strip()
    if not line: return _HELP
    parts = line.split()
    c = parts[0].lower(); a = parts[1:]
    # During an expedition, only choices, surfacing, and read-only commands are allowed.
    if S.get("expedition") and c not in ("choose", "ch", "surface", "up", "status", "s", "inventory", "inv", "i", "encyclopedia", "enc", "e", "journal", "j", "identify", "id", "look", "l", "help", "h"):
        return "You are still underwater. Use choose <number> for the current site, or surface to return."
    try:
        if c in ("help", "h"): return _HELP
        elif c in ("choose", "ch"):
            if a and a[0].lstrip("+").isdigit(): return _c_choose(int(a[0]))
            exp = S.get("expedition")
            return _exp_render_branch(exp["pending"]) if (exp and exp.get("pending")) else "There is no pending site to choose."
        elif c in ("surface", "up"): return _c_surface()
        elif c in ("status", "s"): return _c_status()
        elif c == "shop": return _c_shop()
        elif c == "buy":
            if len(a) > 1 and not a[1].lstrip("+").isdigit():
                return "Quantity must be a number, e.g. buy basic_worm 2."
            return _c_buy(a[0] if a else "", int(a[1]) if len(a) > 1 else 1)
        elif c in ("cast", "c"):
            cb = next((t for t in a if t in BAITS), None)
            ct = next((int(t) for t in a if t.isdigit()), 1)
            cs = next((t[5:].split(",") for t in a if t.startswith("stop=")), None)
            return _cast_many(cb, ct, cs)
        elif c == "dive":   # Major ruin encounters pause the expedition for a choice.
            dt = next((int(t) for t in a if t.isdigit()), 10)
            ds = next((t[5:].split(",") for t in a if t.startswith("stop=")), None)
            return _dive_start(dt, ds)
        elif c == "open": return _c_open(a[0] if a else "")
        elif c in ("goto", "go"): return _c_goto(a[0] if a else "")
        elif c in ("inventory", "inv", "i"): return _c_inv()
        elif c == "sell": return _c_sell(" ".join(a))
        elif c in ("encyclopedia", "enc", "e"): return _c_enc()
        elif c in ("journal", "j"): return _c_journal()
        elif c in ("identify", "id"):
            choice = int(a[1]) if len(a) > 1 and a[1].isdigit() else None
            return _c_identify(a[0] if a else "", choice)
        elif c in ("look", "l"): return _c_look(a[0] if a else "")
        else: return "Unknown command '%s'. Use cmd('help') for the command list." % c
    except Exception as e:
        # Public API catches unexpected errors and returns friendly text.
        return "I could not parse that command (%s). Use cmd('help'); examples: buy basic_worm 2 / cast 10 stop=rare." % e

def cmd(line=""):
    "Primary game entry point: pass one text command and get a string response; semicolons or newlines may batch commands."
    _load()
    raw = (line or "").strip()
    if not raw:
        return _drain_warn(_HELP + "\n" + _state_json())
    subs = [s.strip() for s in re.split(r"[;\n]+", raw) if s.strip()]   # Batch commands are split on semicolons or newlines.
    if len(subs) > 1:
        run = subs[:_BATCH_MAX]
        out = "\n\n".join("▶ %s\n%s" % (s, _run_one(s)) for s in run)
        if len(subs) > _BATCH_MAX: out += "\n\n(Only %d commands can run at once; %d extra command(s) were ignored.)" % (_BATCH_MAX, len(subs) - _BATCH_MAX)
    else:
        out = _run_one(subs[0])
    _save()
    return _drain_warn(out + "\n" + _state_json())   # Append the status JSON at the end of every command response.

def new_game(seed=_DEFAULT_SEED):
    "Start a new deterministic game, optionally with a seed."
    global S
    S = _new_state(seed); _save()
    return "New game started (seed %d). Use cmd('help') for rules, or cmd('cast') to fish." % S["seed"]
