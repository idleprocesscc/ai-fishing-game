"""Canonical real-world content pack for World Waters Field Journal.

English is the source language used for ids, scientific names, and research.
Chinese fields are the default player-facing localization.
"""

ALL_SEASONS = ["spring", "summer", "autumn", "winter"]


def _loc(id, en, zh, description_en, description_zh, tags, cost, junk=0.16,
         seasons=None, biome=""):
    return {
        "id": id, "name": zh, "name_en": en, "name_zh": zh,
        "description": description_zh,
        "description_en": description_en, "description_zh": description_zh,
        "biome": biome, "junk_chance_base": junk,
        "event_chance_base": 0.06, "tag_weight_mult": tags,
        "unlock_cost": cost, "available_seasons": seasons or ALL_SEASONS,
        "ambience": [
            "水面记录着风、温度和光线；在这里，等待也是调查的一部分。",
            "浮漂轻轻一侧，远处的水鸟随即安静下来。",
            "你检查水色和岸边植被，再把这一笔写进观察日志。",
        ],
        "character": "每一次抛竿都可能成为一条生态记录，不只有鱼才算收获。",
    }


LOCATIONS = {
    "colorado_headwaters": _loc(
        "colorado_headwaters", "Colorado Rocky Mountain Headwaters", "科罗拉多落基山源流",
        "Cold, clear mountain streams shaped by snowmelt, riffles, and native cutthroat trout habitat.",
        "由融雪、浅滩和砾石河床塑造的寒冷山溪，也是原生割喉鳟的重要栖息地。",
        {"coldwater": 1.5, "stream": 1.4, "native_colorado": 1.5}, 0, 0.13,
        biome="cold mountain stream"),
    "colorado_reservoir": _loc(
        "colorado_reservoir", "Colorado Foothills Reservoir", "科罗拉多山麓水库",
        "A layered reservoir where cold deep water and warmer coves support very different fish communities.",
        "一座具有明显水层差异的山麓水库：冷凉深水与温暖湾汊孕育着不同鱼群。",
        {"reservoir": 1.5, "coldwater": 1.15, "warmwater": 1.15}, 180, 0.18,
        biome="temperate reservoir"),
    "hokkaido_river": _loc(
        "hokkaido_river", "Hokkaido Forest River", "北海道森林河川",
        "A cool forest river connecting mountain habitat to the sea through migration corridors.",
        "连接山地与海洋的冷凉森林河川，洄游鱼沿着这条生态走廊往返。",
        {"coldwater": 1.4, "stream": 1.3, "migratory": 1.6}, 260, 0.14,
        biome="northern forest river"),
    "hokkaido_rocky_coast": _loc(
        "hokkaido_rocky_coast", "Hokkaido Rocky Coast", "北海道岩礁海岸",
        "Cold coastal water, kelp edges, rock crevices, and seasonal currents around northern Japan.",
        "北海道近岸的冷水、海藻边缘与岩缝共同组成多层次栖息地。",
        {"marine": 1.5, "coldwater": 1.3, "rocky": 1.4}, 420, 0.21,
        biome="cold rocky coast"),
    "cape_kelp_forest": _loc(
        "cape_kelp_forest", "Cape Peninsula Kelp Forest", "开普半岛海藻林",
        "A wave-driven temperate reef where kelp creates shelter, feeding grounds, and shifting underwater corridors.",
        "受海浪驱动的温带礁区；巨藻形成庇护所、觅食场和不断变化的水下廊道。",
        {"marine": 1.5, "kelp": 1.7, "rocky": 1.3}, 600, 0.24,
        biome="temperate kelp forest"),
    "cape_open_water": _loc(
        "cape_open_water", "Cape Offshore Water", "好望角外海",
        "Exposed offshore water influenced by powerful currents, wind, and productive food webs.",
        "受强劲洋流、海风与高生产力食物网影响的开阔外海。",
        {"marine": 1.6, "pelagic": 1.7, "migratory": 1.3}, 850, 0.17,
        biome="exposed temperate ocean"),
}


def _fish(id, en, zh, latin, rarity, size, value, locations, seasons, tags,
          fact_en, fact_zh, identify_en, identify_zh, status="least_concern",
          origin="native", release_only=False):
    return {
        "id": id, "name": zh, "name_en": en, "name_zh": zh,
        "latin": latin, "rarity": rarity, "size_min": size[0],
        "size_max": size[1], "size_unit": "cm", "base_value": value,
        "locations": locations, "seasons": seasons, "tags": tags,
        "description": fact_zh, "science_fact_en": fact_en,
        "science_fact_zh": fact_zh, "identification_en": identify_en,
        "identification_zh": identify_zh, "conservation": status,
        "native_status": origin, "release_only": release_only,
    }


FISH = {
    "colorado_river_cutthroat": _fish(
        "colorado_river_cutthroat", "Colorado River Cutthroat Trout", "科罗拉多河割喉鳟",
        "Oncorhynchus clarkii pleuriticus", "rare", (18, 55), 55,
        ["colorado_headwaters"], ["spring", "summer", "autumn"],
        ["coldwater", "stream", "native_colorado"],
        "A native cutthroat lineage adapted to cold headwater streams in the Colorado River basin.",
        "科罗拉多河流域的原生割喉鳟谱系，适应寒冷的高海拔源流。",
        "Look for the orange-red slash below the jaw and spotting concentrated toward the tail.",
        "辨认重点是下颌橙红色的“割喉”斑，以及较集中在尾部的黑色斑点。",
        "conservation_concern", "native", True),
    "rainbow_trout": _fish(
        "rainbow_trout", "Rainbow Trout", "虹鳟", "Oncorhynchus mykiss", "common", (18, 65), 18,
        ["colorado_headwaters", "colorado_reservoir"], ALL_SEASONS,
        ["coldwater", "stream", "reservoir"],
        "The pink lateral band is famous, but its intensity changes with age, sex, and spawning condition.",
        "虹鳟以粉红色侧带闻名，但颜色会随年龄、性别和繁殖状态明显变化。",
        "Many small black spots cover the back, dorsal fin, and usually the tail.",
        "背部、背鳍以及通常连尾鳍上都有许多细小黑斑。", origin="introduced"),
    "brown_trout": _fish(
        "brown_trout", "Brown Trout", "褐鳟", "Salmo trutta", "uncommon", (20, 80), 28,
        ["colorado_headwaters", "colorado_reservoir"], ALL_SEASONS,
        ["coldwater", "stream", "reservoir"],
        "Introduced brown trout can become strongly territorial and often feed most actively in low light.",
        "作为引入种，褐鳟领地性较强，常在弱光环境中更加活跃。",
        "Red and black spots often have pale halos; the tail usually has fewer spots than a rainbow trout.",
        "红黑斑点常带浅色晕圈，尾鳍斑点通常少于虹鳟。", origin="introduced"),
    "smallmouth_bass": _fish(
        "smallmouth_bass", "Smallmouth Bass", "小口黑鲈", "Micropterus dolomieu", "common", (18, 55), 16,
        ["colorado_reservoir"], ["spring", "summer", "autumn"],
        ["warmwater", "reservoir", "rocky"],
        "Smallmouth bass favor rocky structure and generally tolerate cooler water than largemouth bass.",
        "小口黑鲈偏爱岩石结构，通常比大口黑鲈更能适应凉水。",
        "The closed jaw ends near the middle of the eye, and dark vertical bars often cross the body.",
        "闭合嘴的后缘大致到眼睛中部，体侧常有深色纵向条纹。", origin="introduced"),
    "lake_trout": _fish(
        "lake_trout", "Lake Trout", "湖红点鲑", "Salvelinus namaycush", "rare", (35, 110), 58,
        ["colorado_reservoir"], ALL_SEASONS, ["coldwater", "reservoir", "deep"],
        "Despite its common name, lake trout is a char and depends on cold, oxygen-rich water.",
        "湖红点鲑虽然英文名叫 trout，分类上其实属于红点鲑类，依赖寒冷且富氧的水层。",
        "Pale spots lie on a dark body; trout in the genus Oncorhynchus usually show dark spots on a paler body.",
        "它是深色身体配浅色斑点；这能与许多浅底色配深斑点的鳟鱼区分。"),
    "cherry_salmon": _fish(
        "cherry_salmon", "Cherry Salmon", "樱鳟", "Oncorhynchus masou", "rare", (20, 70), 52,
        ["hokkaido_river"], ["spring", "summer", "autumn"], ["coldwater", "stream", "migratory"],
        "Some individuals migrate to sea while others remain in rivers; the life-history forms differ greatly in size.",
        "樱鳟有些个体降海洄游，有些终生留在河川，两种生活史会造成明显体型差异。",
        "Juveniles and stream-resident fish show oval parr marks; spawning adults may develop a pink cast.",
        "幼鱼和河川残留型体侧有椭圆幼鱼斑，繁殖期成鱼可能呈现樱粉色调。",
        "regulated", "native", True),
    "white_spotted_char": _fish(
        "white_spotted_char", "White-spotted Char", "远东红点鲑", "Salvelinus leucomaenis", "uncommon", (18, 65), 30,
        ["hokkaido_river"], ALL_SEASONS, ["coldwater", "stream"],
        "White-spotted char use cold streams, lakes, and in some populations coastal marine habitat.",
        "远东红点鲑利用冷水溪流、湖泊，部分种群也会进入沿岸海域。",
        "Pale round spots stand out on a darker body, especially along the flanks.",
        "深色体侧分布明显的浅色圆斑，是很实用的辨认特征。"),
    "arabesque_greenling": _fish(
        "arabesque_greenling", "Arabesque Greenling", "花斑六线鱼", "Pleurogrammus azonus", "common", (20, 55), 19,
        ["hokkaido_rocky_coast"], ALL_SEASONS, ["marine", "coldwater", "rocky"],
        "This northern Pacific fish is associated with coastal waters and is important in Hokkaido fisheries.",
        "这种北太平洋鱼类常见于沿岸水域，也是北海道具有代表性的渔业资源。",
        "Its mottled, maze-like markings inspired the English name 'arabesque'.",
        "体表曲折交错的花纹正是英文名“arabesque”的来源。"),
    "japanese_flounder": _fish(
        "japanese_flounder", "Japanese Flounder", "褐牙鲆", "Paralichthys olivaceus", "uncommon", (25, 90), 34,
        ["hokkaido_rocky_coast"], ["spring", "summer", "autumn"], ["marine", "bottom", "ambush"],
        "A flatfish begins life upright; during development one eye migrates as the body becomes bottom-adapted.",
        "牙鲆幼体最初像普通鱼一样直立游泳，发育时一只眼会迁移，身体逐渐适应海底生活。",
        "Both eyes are on the left side in this species; the large toothed mouth distinguishes it from many soles.",
        "本种双眼位于左侧，具明显大口和牙齿，可与许多鳎类区别。"),
    "pacific_cod": _fish(
        "pacific_cod", "Pacific Cod", "太平洋鳕", "Gadus macrocephalus", "rare", (35, 100), 48,
        ["hokkaido_rocky_coast"], ["autumn", "winter", "spring"], ["marine", "coldwater", "bottom"],
        "A chin barbel helps Pacific cod investigate prey near the seabed.",
        "太平洋鳕下颌的触须能帮助它在海底附近探查猎物。",
        "Three dorsal fins, two anal fins, and a single chin barbel form a useful identification set.",
        "三枚背鳍、两枚臀鳍和一根下颌触须是一组可靠的辨认特征。"),
    "galjoen": _fish(
        "galjoen", "Galjoen", "南非黑鲷", "Dichistius capensis", "rare", (25, 65), 55,
        ["cape_kelp_forest"], ALL_SEASONS, ["marine", "kelp", "rocky"],
        "Galjoen is endemic to southern African coastal waters and is closely associated with turbulent rocky shores.",
        "南非黑鲷是南部非洲沿岸特有鱼类，与浪涌强烈的岩岸环境关系密切。",
        "The deep, compressed body can look nearly black in kelp habitat, with strong fin rays for rough water.",
        "身体高而侧扁，在海藻林中可显得近乎黑色，强健鳍条适应剧烈浪涌。",
        "regulated", "native", True),
    "hottentot_seabream": _fish(
        "hottentot_seabream", "Hottentot Seabream", "霍屯督海鲷", "Pachymetopon blochii", "common", (18, 50), 18,
        ["cape_kelp_forest"], ALL_SEASONS, ["marine", "kelp", "rocky"],
        "This seabream commonly feeds around reefs and kelp-associated habitat of the Cape region.",
        "这种海鲷常在开普地区的礁石与海藻生境附近觅食。",
        "A compact grey-brown body and small mouth suit grazing and picking food from reef surfaces.",
        "灰褐色紧凑体型与较小的嘴，适合从礁石表面啄食。"),
    "snoek": _fish(
        "snoek", "Snoek", "蛇鲭", "Thyrsites atun", "uncommon", (55, 130), 38,
        ["cape_open_water"], ["autumn", "winter", "spring"], ["marine", "pelagic", "schooling"],
        "Snoek is a fast pelagic predator whose seasonal schools have long supported Cape fishing culture.",
        "蛇鲭是迅捷的中上层捕食者，其季节性鱼群长期影响着开普地区的渔业文化。",
        "The body is long and metallic with a large toothed mouth and a single lateral line.",
        "身体细长呈金属色，嘴大而具牙，体侧只有一条侧线。"),
    "yellowtail_amberjack": _fish(
        "yellowtail_amberjack", "Yellowtail Amberjack", "黄尾鰤", "Seriola lalandi", "rare", (45, 150), 65,
        ["cape_open_water", "cape_kelp_forest"], ["spring", "summer", "autumn"],
        ["marine", "pelagic", "migratory"],
        "A powerful open-water predator, yellowtail can move between offshore schools and structure near reefs.",
        "黄尾鰤是力量强劲的开放水域捕食者，也会在外海鱼群与近礁结构之间活动。",
        "A yellow tail and yellowish side stripe contrast with the streamlined blue-grey body.",
        "黄色尾鳍和淡黄色体侧带与流线型蓝灰身体形成鲜明对比。"),
}

# Identification exercises are observations, not trivia detached from the fish.
# Each asks the player to use a visible field mark that separates a commonly
# confused species or corrects a misleading common name.
FISH["colorado_river_cutthroat"]["quiz"] = {
    "question_zh": "这条鱼下颌有橙红色斑，黑斑集中于尾柄附近。哪项判断最可靠？",
    "choices_zh": ["这是虹鳟，因为所有鳟鱼都有粉色侧带", "这是割喉鳟；下颌色斑和尾部斑点分布是关键", "仅凭体型就能确定"],
    "answer": 2,
    "explanation_zh": "正确。割喉鳟的下颌橙红斑是核心线索；体色会变化，不能只凭整体颜色或体型。",
    "wrong_zh": "先别急着定种。整体颜色和体型都容易随环境与年龄变化，应优先检查下颌色斑与斑点分布。",
}
FISH["rainbow_trout"]["quiz"] = {
    "question_zh": "怎样把虹鳟与常被混淆的褐鳟区分开？",
    "choices_zh": ["看背部、背鳍和尾鳍是否普遍有细小黑斑", "只看鱼是不是银色", "只看长度是否超过30厘米"],
    "answer": 1,
    "explanation_zh": "正确。虹鳟通常在背部、背鳍和尾鳍都有密集细黑斑；银亮程度和体长都不是稳定鉴别点。",
    "wrong_zh": "银亮程度和体长会随个体与环境变化。请把注意力移到鳍和斑点分布上。",
}
FISH["lake_trout"]["quiz"] = {
    "question_zh": "“Lake Trout”这个英文俗名最容易造成什么误解？",
    "choices_zh": ["它只能生活在湖边", "它分类上其实是红点鲑属的 char，并非典型 trout", "它没有斑点"],
    "answer": 2,
    "explanation_zh": "正确。俗名不等于严格分类；湖红点鲑属于 Salvelinus（红点鲑属）。",
    "wrong_zh": "这是一次名称陷阱。查学名属名 Salvelinus，再判断它与 trout 的关系。",
}
FISH["cherry_salmon"]["quiz"] = {
    "question_zh": "观察到体侧椭圆幼鱼斑的小型个体时，为什么不能断言它永远不会入海？",
    "choices_zh": ["所有小鱼都会入海", "樱鳟具有降海型与河川残留型，幼年外观不能单独决定未来生活史", "斑纹与生活史完全无关"],
    "answer": 2,
    "explanation_zh": "正确。同一物种可表现不同生活史；需要结合年龄、地点和长期观察。",
    "wrong_zh": "关键不是把所有个体归为同一种命运，而是认识樱鳟存在降海型与河川残留型。",
}
FISH["galjoen"]["quiz"] = {
    "question_zh": "海藻林里鱼体看起来很黑，为什么不能仅凭颜色鉴定南非黑鲷？",
    "choices_zh": ["水下光线与背景会改变视觉颜色，还要结合高侧扁体型和鳍条", "黑色鱼一定都是南非黑鲷", "只需看捕获地点"],
    "answer": 1,
    "explanation_zh": "正确。光线、深度和应激都会改变观感；鉴定必须组合多个形态与生境线索。",
    "wrong_zh": "单一颜色和单一地点都可能误导。尝试组合体型、鳍条、花纹与生境。",
}


BAITS = {
    "earthworm": {"id": "earthworm", "name": "蚯蚓", "name_en": "Earthworm", "cost": 8,
                  "description": "适合溪流和水库的通用天然饵。", "effects": {"tag_weight_mult": {"stream": 1.25}, "junk_chance_mult": 1.0}},
    "spoon_lure": {"id": "spoon_lure", "name": "亮片拟饵", "name_en": "Spoon Lure", "cost": 26,
                   "description": "闪光模拟受伤小鱼，偏向主动捕食者。", "effects": {"rarity_weight_mult": {"rare": 1.25}, "tag_weight_mult": {"pelagic": 1.3}, "junk_chance_mult": 0.8}},
    "soft_plastic": {"id": "soft_plastic", "name": "软虫拟饵", "name_en": "Soft Plastic", "cost": 18,
                     "description": "可慢速搜索岩缝和底层，但也更容易挂底。", "effects": {"tag_weight_mult": {"bottom": 1.4, "rocky": 1.15}, "junk_chance_mult": 1.15}},
}

SURFACE_JUNK = {
    "colorado_headwaters": ["一截被水獭啃过的树枝", "一团废弃尼龙鱼线", "一枚无倒刺旧鱼钩", "一片被磨圆的花岗岩"],
    "colorado_reservoir": ["一副进水的太阳镜", "一只褪色网球", "一段水库测深线", "半个铝罐拉环"],
    "hokkaido_river": ["一片桦树皮", "一只空的昆虫羽化壳", "一截缠着水草的旧线", "一枚被水磨亮的玻璃碎片"],
    "hokkaido_rocky_coast": ["一个旧玻璃浮球碎片", "一团海带", "一只空贝壳", "一段幽灵渔网"],
    "cape_kelp_forest": ["一根脱落的巨藻固着器", "一只空鲍壳", "一段缠在海藻上的鱼线", "一块被浪磨圆的海玻璃"],
    "cape_open_water": ["一只漂流瓶", "一块风化浮木", "一段旧船绳", "一只被咬过的拟饵"],
}


def install(namespace):
    """Replace fantasy content while preserving the mature engine mechanics."""
    namespace["LOCATIONS"].clear(); namespace["LOCATIONS"].update(LOCATIONS)
    namespace["FISH"].clear(); namespace["FISH"].update(FISH)
    namespace["BAITS"].clear(); namespace["BAITS"].update(BAITS)
    namespace["EVENTS"].clear()
    namespace["ITEMS"].clear()
    namespace["DIVE_EVENTS"].clear()
    namespace["DIVE_ENCOUNTERS"][:] = []
    namespace["_REAL_WORLD_JUNK"] = SURFACE_JUNK
