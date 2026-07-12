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

LOCATIONS.update({
    "amazon_flooded_forest": _loc(
        "amazon_flooded_forest", "Amazon Flooded Forest", "亚马孙泛滥森林",
        "Seasonally flooded forest where fish move among submerged trunks and feed on fruits, seeds, insects, and other fish.",
        "季节性洪水淹没森林，鱼类穿行于树干之间，利用果实、种子、昆虫和其他鱼类形成的食物网。",
        {"tropical": 1.4, "floodplain": 1.7, "fruit_eater": 1.35}, 1050, 0.22,
        biome="tropical flooded forest"),
    "baikal_littoral": _loc(
        "baikal_littoral", "Lake Baikal Littoral", "贝加尔湖沿岸带",
        "Cold, oxygen-rich lake margins connected to tributaries, rocky slopes, and an exceptionally endemic food web.",
        "寒冷富氧的湖岸与支流、岩质湖坡相连，承载高度特有的食物网。",
        {"coldwater": 1.5, "baikal_endemic": 1.6, "lake": 1.35}, 1250, 0.16,
        biome="ancient cold lake"),
    "mekong_mainstem": _loc(
        "mekong_mainstem", "Mekong Mainstem", "湄公河主河道",
        "A vast tropical river whose flood pulse and long migration routes connect channels, floodplains, and tributaries.",
        "巨大的热带河流以洪水脉动和长距离洄游路线连接主河道、泛滥平原与支流。",
        {"tropical": 1.4, "large_river": 1.7, "migratory": 1.5}, 1450, 0.26,
        biome="tropical large river"),
})


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

FISH.update({
    "arapaima": _fish(
        "arapaima", "Arapaima", "巨骨舌鱼", "Arapaima gigas", "rare", (80, 300), 90,
        ["amazon_flooded_forest"], ALL_SEASONS, ["tropical", "floodplain", "air_breathing"],
        "Arapaima must surface to breathe air; community counts of surfacing adults help support managed conservation harvests.",
        "巨骨舌鱼必须浮到水面呼吸空气；社区可利用成鱼换气行为进行计数，支撑保护性管理。",
        "Large plate-like scales, a long body, and reddish color toward the tail distinguish adults.",
        "成鱼具有大型板状鳞片、修长身体，尾部常带红色。", "managed", "native", True),
    "tambaqui": _fish(
        "tambaqui", "Tambaqui", "大盖巨脂鲤", "Colossoma macropomum", "common", (25, 100), 28,
        ["amazon_flooded_forest"], ALL_SEASONS, ["tropical", "floodplain", "fruit_eater"],
        "During floods, tambaqui enter inundated forest and consume fruits and seeds, linking fish movement with forest ecology.",
        "洪水期大盖巨脂鲤进入淹水森林取食果实和种子，把鱼类迁移与森林生态连接起来。",
        "A deep body and strong molar-like teeth suit crushing hard fruits and seeds.",
        "高而侧扁的身体与强壮的臼齿状牙齿适合压碎坚硬果实和种子。"),
    "matrinxa": _fish(
        "matrinxa", "Matrinxã", "亚马孙布氏脂鲤", "Brycon amazonicus", "uncommon", (25, 75), 34,
        ["amazon_flooded_forest"], ["spring", "summer", "autumn"], ["tropical", "floodplain", "migratory"],
        "Matrinxã move through river and floodplain habitat and eat a flexible mix of plant and animal food.",
        "亚马孙布氏脂鲤在河道与泛滥平原之间移动，食物包含多种植物和动物来源。",
        "The streamlined silver body has a darker back and a distinct dark mark near the tail base.",
        "流线型银色身体背部较深，尾柄附近有明显深色标记。"),
    "electric_eel": _fish(
        "electric_eel", "Electric Eel", "电鳗", "Electrophorus electricus", "rare", (50, 200), 62,
        ["amazon_flooded_forest"], ALL_SEASONS, ["tropical", "floodplain", "electric", "air_breathing"],
        "Despite its name, an electric eel is a knifefish, not a true eel; it also breathes air at the surface.",
        "电鳗并不是真正的鳗鲡，而属于裸背电鳗类；它也需要到水面呼吸空气。",
        "The long cylindrical body lacks the continuous dorsal fin expected on many true eels.",
        "身体细长近圆筒状，没有许多真正鳗类那种连续而明显的背鳍。", "observe_only", "native", True),
    "baikal_omul": _fish(
        "baikal_omul", "Baikal Omul", "贝加尔欧姆白鲑", "Coregonus migratorius", "uncommon", (25, 60), 36,
        ["baikal_littoral"], ["spring", "summer", "autumn"], ["coldwater", "lake", "migratory", "baikal_endemic"],
        "Omul feed in the lake and migrate into tributaries to spawn, with several ecological populations using the basin differently.",
        "贝加尔欧姆白鲑在湖中摄食并进入支流繁殖，不同生态种群以不同方式利用湖盆。",
        "A terminal mouth, relatively large eyes, small scales, and many long gill rakers fit plankton feeding.",
        "端位口、较大的眼、小鳞片与细长而数量较多的鳃耙适合滤食浮游生物。", "regulated", "native", True),
    "small_golomyanka": _fish(
        "small_golomyanka", "Small Golomyanka", "小胎生贝湖鱼", "Comephorus dybowskii", "rare", (8, 16), 48,
        ["baikal_littoral"], ALL_SEASONS, ["coldwater", "deep", "pelagic", "baikal_endemic"],
        "This translucent endemic gives birth to live larvae and makes daily vertical migrations through the cold water column.",
        "这种半透明特有鱼会产下活体仔鱼，并在寒冷水柱中进行昼夜垂直迁移。",
        "A translucent scaleless-looking body, large pectoral fins, and reduced pelvic fins suit open deep water.",
        "半透明且近乎无鳞的身体、较大胸鳍和退化腹鳍适应深层开放水域。", "research_observation", "endemic", True),
    "baikal_sturgeon": _fish(
        "baikal_sturgeon", "Baikal Sturgeon", "贝加尔鲟", "Acipenser baerii baicalensis", "rare", (70, 180), 95,
        ["baikal_littoral"], ["spring", "summer", "autumn"], ["coldwater", "bottom", "migratory"],
        "Baikal sturgeon mature slowly and spawn in major tributaries, making loss of young or spawning adults especially costly.",
        "贝加尔鲟成熟缓慢并进入大型支流繁殖，因此幼鱼或繁殖成鱼的损失尤其难以恢复。",
        "Five rows of bony scutes, an underslung mouth, and four barbels identify a sturgeon.",
        "五列骨板、腹面的嘴和四根触须是鲟鱼的典型组合特征。", "endangered", "native", True),
    "baikal_grayling": _fish(
        "baikal_grayling", "Baikal Grayling", "贝加尔茴鱼", "Thymallus baicalensis", "common", (20, 55), 24,
        ["baikal_littoral"], ["spring", "summer", "autumn"], ["coldwater", "lake", "stream"],
        "Grayling move between lake margins and flowing tributary habitat and use a tall dorsal fin for stability and display.",
        "贝加尔茴鱼利用湖岸和流动支流水域，高大的背鳍兼有稳定身体与展示作用。",
        "The sail-like dorsal fin is the clearest field mark, but local forms still require careful context.",
        "帆状高背鳍是最醒目的特征，但鉴定地方类型仍需结合具体环境。"),
    "mekong_giant_catfish": _fish(
        "mekong_giant_catfish", "Mekong Giant Catfish", "湄公河巨鲶", "Pangasianodon gigas", "rare", (100, 300), 110,
        ["mekong_mainstem"], ["spring", "summer"], ["tropical", "large_river", "migratory"],
        "One of the world's largest freshwater fishes, this highly threatened migratory catfish depends on connected river habitat.",
        "湄公河巨鲶是世界最大的淡水鱼之一；这种高度受威胁的洄游鱼依赖连通的河流生境。",
        "Adults are massive, largely toothless, and lack the long barbels seen on many other catfish.",
        "成鱼体型巨大、牙齿退化，也缺少许多其他鲶鱼常见的长触须。", "critically_endangered", "native", True),
    "giant_barb": _fish(
        "giant_barb", "Giant Barb", "暹罗巨鲤", "Catlocarpio siamensis", "rare", (80, 250), 100,
        ["mekong_mainstem"], ["summer", "autumn"], ["tropical", "large_river", "migratory"],
        "Giant barb are large native cyprinids whose decline makes them ambassadors for protecting Mekong migration routes.",
        "暹罗巨鲤是大型原生鲤科鱼，其衰退使它成为保护湄公河洄游通道的旗舰物种。",
        "The huge deep body, large scales, and lack of catfish barbels separate it from the river's giant pangasiids.",
        "巨大的高体型与大鳞片、且没有鲶鱼触须，可与大型巨鲶类区分。", "critically_endangered", "native", True),
    "striped_catfish": _fish(
        "striped_catfish", "Striped Catfish", "低眼巨鲶", "Pangasianodon hypophthalmus", "common", (30, 130), 28,
        ["mekong_mainstem"], ALL_SEASONS, ["tropical", "large_river", "migratory"],
        "Wild striped catfish migrate through the Mekong system; the species is also widely raised in aquaculture.",
        "野生低眼巨鲶在湄公河水系中迁移，同时也是广泛养殖的鱼类。",
        "Juveniles show dark horizontal stripes; the eyes sit low on the head relative to many similar catfish.",
        "幼鱼体侧有深色横纹，眼睛在头部的位置比许多近似鲶鱼更低。"),
    "siamese_mud_carp": _fish(
        "siamese_mud_carp", "Siamese Mud Carp", "暹罗泥鲤", "Henicorhynchus siamensis", "common", (10, 25), 14,
        ["mekong_mainstem"], ALL_SEASONS, ["tropical", "large_river", "schooling", "migratory"],
        "Small migratory fishes can move biomass and nutrients through the river on a scale that individual size hides.",
        "小型洄游鱼能以巨大鱼群在河流中搬运营养与生物量，单个个体的尺寸掩盖了这种尺度。",
        "A small silvery cyprinid is best identified with fin position, scale counts, and local keys rather than color alone.",
        "这种小型银色鲤科鱼不能只凭颜色，应结合鳍位、鳞片计数和当地检索表。"),
})

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

_QUIZ_EN = {
    "colorado_river_cutthroat": {
        "question_en": "The fish has an orange-red slash below the jaw and spots concentrated near the tail. Which conclusion is best supported?",
        "choices_en": ["Rainbow trout, because every trout has a pink stripe", "Cutthroat trout; the jaw slash and spot distribution are key", "Body size alone is enough"],
        "explanation_en": "Correct. The jaw slash is a key clue; overall color and size vary with age and environment.",
        "wrong_en": "Do not rely on overall color or size. Recheck the jaw slash and the distribution of spots."},
    "rainbow_trout": {
        "question_en": "Which feature best separates a rainbow trout from a commonly confused brown trout?",
        "choices_en": ["Numerous small dark spots across the back, dorsal fin, and usually the tail", "Whether the fish looks silver", "Whether it is longer than 30 cm"],
        "explanation_en": "Correct. Fine dark spotting on the back and fins is more useful than variable color or length.",
        "wrong_en": "Silver color and length vary. Focus on fin and spot distribution."},
    "lake_trout": {
        "question_en": "What misconception is encouraged by the common name 'lake trout'?",
        "choices_en": ["It can only live beside a lake", "It is a char in genus Salvelinus, not a typical trout", "It has no spots"],
        "explanation_en": "Correct. Common names are not strict taxonomy; lake trout belongs to Salvelinus.",
        "wrong_en": "This is a common-name trap. Check the genus Salvelinus before classifying it."},
    "cherry_salmon": {
        "question_en": "Why can juvenile parr marks not prove that a small cherry salmon will never enter the sea?",
        "choices_en": ["Every small fish goes to sea", "The species has sea-run and stream-resident life histories; juvenile appearance alone cannot predict the outcome", "Marks have no relationship to life history"],
        "explanation_en": "Correct. One species can express different life histories, so age, place, and repeated observation matter.",
        "wrong_en": "Cherry salmon can be sea-run or stream-resident; do not assign every juvenile the same future."},
    "galjoen": {
        "question_en": "Why is a nearly black appearance in kelp habitat insufficient to identify galjoen?",
        "choices_en": ["Underwater light and background alter apparent color; body shape and fin rays also matter", "Every black fish is a galjoen", "Location alone is enough"],
        "explanation_en": "Correct. Light, depth, and stress alter appearance; combine multiple form and habitat clues.",
        "wrong_en": "One color and one location can mislead. Combine body shape, fins, pattern, and habitat."},
}
for _fish_id, _translations in _QUIZ_EN.items():
    FISH[_fish_id]["quiz"].update(_translations)

# Behavior tags used by the deterministic day-cycle layer. These are modest
# probability nudges, never guarantees: habitat, season, water, and bait still
# combine with time of day.
FISH["brown_trout"]["tags"].append("low_light")
FISH["electric_eel"]["tags"].extend(["low_light", "nocturnal"])
FISH["japanese_flounder"]["tags"].append("low_light")
FISH["small_golomyanka"]["tags"].append("vertical_migrant")
FISH["snoek"]["tags"].append("daylight")
FISH["yellowtail_amberjack"]["tags"].append("daylight")

CONDITIONS = {
    "colorado_headwaters": [
        {"name_zh": "融雪高水", "name_en": "Snowmelt high water", "fact_zh": "融雪使水温降低、流速升高，鱼会寻找缓流带节省能量。", "tag_weight_mult": {"coldwater": 1.25, "stream": 0.85}},
        {"name_zh": "清澈低水", "name_en": "Clear low water", "fact_zh": "低水位提高能见度，也让鱼更容易察觉岸上的移动。", "tag_weight_mult": {"stream": 1.15, "native_colorado": 1.1}}],
    "colorado_reservoir": [
        {"name_zh": "背风湾平水", "name_en": "Calm sheltered cove", "fact_zh": "背风湾升温较快，暖水鱼可能靠近浅层结构。", "tag_weight_mult": {"warmwater": 1.35}},
        {"name_zh": "深层冷水稳定", "name_en": "Stable cold depth", "fact_zh": "深水保留更低温度，但鱼仍需要足够的溶解氧。", "tag_weight_mult": {"coldwater": 1.3, "deep": 1.35}}],
    "hokkaido_river": [
        {"name_zh": "林荫清流", "name_en": "Clear shaded flow", "fact_zh": "河岸林遮阴能减缓水温上升，并向食物网输入昆虫。", "tag_weight_mult": {"coldwater": 1.25, "stream": 1.15}},
        {"name_zh": "降雨涨水", "name_en": "Rain-swollen flow", "fact_zh": "涨水会重排浅滩与深潭的可用栖息地，也影响洄游通道。", "tag_weight_mult": {"migratory": 1.35}}],
    "hokkaido_rocky_coast": [
        {"name_zh": "海藻边缘缓流", "name_en": "Slack water at a kelp edge", "fact_zh": "海藻边缘兼有隐蔽与开阔觅食面，是生物密集的过渡带。", "tag_weight_mult": {"rocky": 1.25, "bottom": 1.15}},
        {"name_zh": "港外浑水", "name_en": "Turbid harbor edge", "fact_zh": "浑浊降低视觉范围，依靠侧线或伏击的物种可能更占优势。", "tag_weight_mult": {"ambush": 1.35, "bottom": 1.15}}],
    "cape_kelp_forest": [
        {"name_zh": "海藻林浪涌", "name_en": "Kelp-forest surge", "fact_zh": "浪涌让巨藻廊道不断开合，礁栖鱼必须在水流中保持位置。", "tag_weight_mult": {"kelp": 1.35, "rocky": 1.2}},
        {"name_zh": "冷水上升流", "name_en": "Cold upwelling", "fact_zh": "上升流把深层冷水和营养盐带到表层，支撑高生产力食物网。", "tag_weight_mult": {"coldwater": 1.35, "kelp": 1.15}}],
    "cape_open_water": [
        {"name_zh": "风成流线", "name_en": "Wind-current line", "fact_zh": "流线会聚集浮游生物和小鱼，从而吸引中上层捕食者。", "tag_weight_mult": {"pelagic": 1.4}},
        {"name_zh": "洋流混合带", "name_en": "Current-mixing zone", "fact_zh": "水团交界并非固定边界，而是随风与海况移动的动态区域。", "tag_weight_mult": {"migratory": 1.3, "marine": 1.15}}],
    "amazon_flooded_forest": [
        {"name_zh": "洪水进入森林", "name_en": "Floodwater enters the forest", "fact_zh": "上涨的河水打开通往果实、种子和林下庇护所的新通道。", "tag_weight_mult": {"floodplain": 1.4, "fruit_eater": 1.5}},
        {"name_zh": "退水汇入湖洼", "name_en": "Falling water concentrates in lakes", "fact_zh": "退水缩小可用水域，捕食与缺氧压力可能同时上升。", "tag_weight_mult": {"air_breathing": 1.45, "tropical": 1.1}}],
    "baikal_littoral": [
        {"name_zh": "沿岸冷水清澈", "name_en": "Clear cold littoral water", "fact_zh": "低温高透明度有利于观察，但湖中生物适应的温度范围可能很窄。", "tag_weight_mult": {"coldwater": 1.35, "lake": 1.15}},
        {"name_zh": "支流羽状水团", "name_en": "Tributary plume", "fact_zh": "支流入湖形成温度、沉积物和化学条件不同的过渡水团。", "tag_weight_mult": {"migratory": 1.4, "stream": 1.2}}],
    "mekong_mainstem": [
        {"name_zh": "洪水脉动上涨", "name_en": "Rising flood pulse", "fact_zh": "洪水把主河道与泛滥平原重新连通，扩大觅食和育幼空间。", "tag_weight_mult": {"migratory": 1.4, "large_river": 1.15}},
        {"name_zh": "旱季主槽收缩", "name_en": "Dry-season channel contraction", "fact_zh": "水位下降使深槽和支流汇口成为关键避难空间。", "tag_weight_mult": {"large_river": 1.3, "schooling": 1.2}}],
}

EPISODES = {
    "colorado_headwaters": [
        {"id": "insect_emergence", "name_zh": "水生昆虫集中羽化", "name_en": "Aquatic insect emergence", "fact_zh": "若虫集中羽化会短期改变水面食物供应，也吸引河乌等捕食者。", "fact_en": "A concentrated insect emergence briefly changes surface food supply and attracts predators such as dippers.", "tag_weight_mult": {"stream": 1.3}, "wildlife_mult": 1.35},
        {"id": "warm_low_flow", "name_zh": "偏暖低流阶段", "name_en": "Warm low-flow episode", "fact_zh": "低流量和升温会压缩冷水避难空间；更少的水不等于更容易钓。", "fact_en": "Low flow and warming compress cold-water refuges; less water does not mean easier fishing.", "tag_weight_mult": {"coldwater": 0.75}, "empty_mult": 1.35}],
    "colorado_reservoir": [
        {"id": "turnover_mix", "name_zh": "水库翻转混合", "name_en": "Reservoir turnover mixing", "fact_zh": "水层混合会重新分配温度和氧气，鱼群位置可能随之变化。", "fact_en": "Water-column mixing redistributes temperature and oxygen, shifting where fish can remain active.", "tag_weight_mult": {"reservoir": 1.25}},
        {"id": "shoreline_cleanup", "name_zh": "退水岸线暴露", "name_en": "Exposed drawdown shoreline", "fact_zh": "水位回落暴露遗留物，也创造一次清理岸线的机会。", "fact_en": "Drawdown exposes stranded debris and creates a shoreline-cleanup opportunity.", "tag_weight_mult": {}, "junk_mult": 1.5}],
    "hokkaido_river": [
        {"id": "migration_window", "name_zh": "洄游窗口", "name_en": "Migration window", "fact_zh": "适宜流量打开河海通道，但抵达不等于每条鱼都会进食。", "fact_en": "Suitable flow opens a river-sea corridor, but arrival never means every fish will feed.", "tag_weight_mult": {"migratory": 1.5}},
        {"id": "storm_runoff", "name_zh": "暴雨径流阶段", "name_en": "Storm-runoff episode", "fact_zh": "浑水和漂流物增加，鱼会重新选择缓流区与遮蔽物。", "fact_en": "Turbidity and drifting material increase while fish redistribute among slack water and cover.", "tag_weight_mult": {"stream": 0.85}, "junk_mult": 1.35}],
    "hokkaido_rocky_coast": [
        {"id": "cold_productivity_pulse", "name_zh": "冷水生产力脉冲", "name_en": "Cold-water productivity pulse", "fact_zh": "营养与浮游生物变化会沿食物网向上影响沿岸鱼和海鸟。", "fact_en": "Changes in nutrients and plankton can propagate upward to coastal fish and seabirds.", "tag_weight_mult": {"coldwater": 1.25, "marine": 1.15}, "wildlife_mult": 1.2},
        {"id": "rough_coast", "name_zh": "持续风浪", "name_en": "Persistent coastal swell", "fact_zh": "风浪首先限制安全观察，并增加挂到漂流物的机会。", "fact_en": "Swell first limits safe observation and increases encounters with drifting material.", "tag_weight_mult": {"rocky": 0.9}, "junk_mult": 1.25, "empty_mult": 1.2}],
    "cape_kelp_forest": [
        {"id": "upwelling_pulse", "name_zh": "上升流脉冲", "name_en": "Upwelling pulse", "fact_zh": "冷而富营养的水进入表层，效应会从初级生产逐步传到更高营养级。", "fact_en": "Cold nutrient-rich water reaches the surface, with effects propagating from primary production upward.", "tag_weight_mult": {"kelp": 1.3, "coldwater": 1.25}, "wildlife_mult": 1.2},
        {"id": "kelp_wrack", "name_zh": "风暴后巨藻漂积", "name_en": "Post-storm kelp wrack", "fact_zh": "脱落巨藻把有机物与附着生物搬到新的岸段，也会缠住人造垃圾。", "fact_en": "Detached kelp moves organic matter and attached organisms while also trapping human debris.", "tag_weight_mult": {"kelp": 0.85}, "junk_mult": 1.45}],
    "cape_open_water": [
        {"id": "baitfish_aggregation", "name_zh": "小型鱼群聚集", "name_en": "Baitfish aggregation", "fact_zh": "流线聚集小型猎物时，海鸟和中上层捕食者可能同时响应。", "fact_en": "When current lines aggregate small prey, seabirds and pelagic predators may respond together.", "tag_weight_mult": {"pelagic": 1.45}, "wildlife_mult": 1.35},
        {"id": "marine_heat_anomaly", "name_zh": "偏暖海水阶段", "name_en": "Warm-water anomaly", "fact_zh": "异常升温会重排活动范围；它不是简单的‘鱼更多’或‘鱼更少’。", "fact_en": "Unusual warming redistributes activity rather than producing a simple more-fish or fewer-fish outcome.", "tag_weight_mult": {"coldwater": 0.75, "migratory": 1.1}, "empty_mult": 1.15}],
    "amazon_flooded_forest": [
        {"id": "forest_connection", "name_zh": "泛滥森林连通", "name_en": "Flooded-forest connection", "fact_zh": "水进入林下后，鱼获得新的食物、庇护与移动路线。", "fact_en": "When water enters the forest, fish gain new food, shelter, and movement routes.", "tag_weight_mult": {"floodplain": 1.45, "fruit_eater": 1.4}, "wildlife_mult": 1.15},
        {"id": "drought_refuge", "name_zh": "干旱湖洼避难", "name_en": "Drought-refuge isolation", "fact_zh": "水体隔离提高拥挤、缺氧和捕食压力，能呼吸空气也不代表不受影响。", "fact_en": "Isolation raises crowding, low-oxygen, and predation pressure; air breathing does not remove every risk.", "tag_weight_mult": {"air_breathing": 1.35, "floodplain": 0.7}, "empty_mult": 1.3}],
    "baikal_littoral": [
        {"id": "ice_edge_bloom", "name_zh": "冰缘浮游生物增长", "name_en": "Ice-edge plankton growth", "fact_zh": "冰下与冰缘的初级生产能为寒冷水柱食物网提供季节性能量。", "fact_en": "Primary production beneath and beside ice can supply seasonal energy to the cold-water food web.", "tag_weight_mult": {"lake": 1.25, "pelagic": 1.2}, "wildlife_mult": 1.15},
        {"id": "littoral_warming", "name_zh": "沿岸偏暖阶段", "name_en": "Littoral warming episode", "fact_zh": "适应窄温度范围的特有生物可能在岸带升温时受到额外压力。", "fact_en": "Endemic organisms adapted to narrow temperatures may face added stress during littoral warming.", "tag_weight_mult": {"coldwater": 0.72, "baikal_endemic": 0.85}, "empty_mult": 1.25}],
    "mekong_mainstem": [
        {"id": "floodplain_reconnection", "name_zh": "洪泛区重新连通", "name_en": "Floodplain reconnection", "fact_zh": "上涨水位把主槽、支流和泛滥平原重新接成一张移动网络。", "fact_en": "Rising water reconnects channel, tributary, and floodplain into one movement network.", "tag_weight_mult": {"migratory": 1.45, "schooling": 1.2}, "wildlife_mult": 1.1},
        {"id": "dry_pool_fragmentation", "name_zh": "旱季深潭分隔", "name_en": "Dry-season pool fragmentation", "fact_zh": "深潭成为避难所，但通道缩窄会同时影响鱼群和淡水豚的移动。", "fact_en": "Deep pools become refuges while narrowed connections constrain both fish and dolphin movement.", "tag_weight_mult": {"large_river": 0.8, "migratory": 0.7}, "empty_mult": 1.35}],
}

_CONDITION_FACT_EN = {
    "Snowmelt high water": "Snowmelt lowers water temperature and raises velocity, pushing fish toward slower refuges.",
    "Clear low water": "Low water improves visibility but also makes movement on the bank easier for fish to detect.",
    "Calm sheltered cove": "Sheltered coves warm quickly, so warm-water fish may approach shallow structure.",
    "Stable cold depth": "Deep water can remain cold, but fish still require enough dissolved oxygen.",
    "Clear shaded flow": "Riparian shade limits warming and supplies terrestrial insects to the river food web.",
    "Rain-swollen flow": "Rising flow rearranges riffle and pool habitat and can alter migration routes.",
    "Slack water at a kelp edge": "Kelp edges combine cover with open feeding surfaces in a dense transition zone.",
    "Turbid harbor edge": "Turbidity reduces visual range and can favor lateral-line sensing or ambush behavior.",
    "Kelp-forest surge": "Surge repeatedly opens and closes kelp corridors, challenging reef fish to hold position.",
    "Cold upwelling": "Upwelling brings cold, nutrient-rich deep water toward the productive surface food web.",
    "Wind-current line": "Current lines concentrate plankton and small fish, attracting pelagic predators.",
    "Current-mixing zone": "A water-mass boundary is dynamic, shifting with wind and sea state rather than forming a fixed line.",
    "Floodwater enters the forest": "Rising water opens routes to fruit, seeds, and shelter beneath the forest canopy.",
    "Falling water concentrates in lakes": "Falling water shrinks habitat while predation and low-oxygen pressure may rise together.",
    "Clear cold littoral water": "Cold transparency aids observation, but endemic organisms may tolerate only a narrow temperature range.",
    "Tributary plume": "River inflow creates a transition zone with distinct temperature, sediment, and chemistry.",
    "Rising flood pulse": "Floodwater reconnects the main channel and floodplain, expanding feeding and nursery habitat.",
    "Dry-season channel contraction": "Falling water makes deep channels and tributary junctions critical refuges."}
for _condition_pool in CONDITIONS.values():
    for _condition in _condition_pool:
        _condition["fact_en"] = _CONDITION_FACT_EN[_condition["name_en"]]


BAITS = {
    "earthworm": {"id": "earthworm", "name": "蚯蚓", "name_en": "Earthworm", "cost": 8,
                  "description": "适合溪流和水库的通用天然饵。", "effects": {"tag_weight_mult": {"stream": 1.25}, "junk_chance_mult": 1.0}},
    "spoon_lure": {"id": "spoon_lure", "name": "亮片拟饵", "name_en": "Spoon Lure", "cost": 26,
                   "description": "闪光模拟受伤小鱼，偏向主动捕食者。", "effects": {"rarity_weight_mult": {"rare": 1.25}, "tag_weight_mult": {"pelagic": 1.3}, "junk_chance_mult": 0.8}},
    "soft_plastic": {"id": "soft_plastic", "name": "软虫拟饵", "name_en": "Soft Plastic", "cost": 18,
                     "description": "可慢速搜索岩缝和底层，但也更容易挂底。", "effects": {"tag_weight_mult": {"bottom": 1.4, "rocky": 1.15}, "junk_chance_mult": 1.15}},
}
BAITS["earthworm"]["description_en"] = "General natural bait suited to streams and reservoirs."
BAITS["spoon_lure"]["description_en"] = "Flash imitates a struggling small fish and favors active predators."
BAITS["soft_plastic"]["description_en"] = "Can search rock gaps and bottom habitat slowly, with a higher snag risk."

SURFACE_JUNK = {
    "colorado_headwaters": ["一截被水獭啃过的树枝", "一团废弃尼龙鱼线", "一枚无倒刺旧鱼钩", "一片被磨圆的花岗岩"],
    "colorado_reservoir": ["一副进水的太阳镜", "一只褪色网球", "一段水库测深线", "半个铝罐拉环"],
    "hokkaido_river": ["一片桦树皮", "一只空的昆虫羽化壳", "一截缠着水草的旧线", "一枚被水磨亮的玻璃碎片"],
    "hokkaido_rocky_coast": ["一个旧玻璃浮球碎片", "一团海带", "一只空贝壳", "一段幽灵渔网"],
    "cape_kelp_forest": ["一根脱落的巨藻固着器", "一只空鲍壳", "一段缠在海藻上的鱼线", "一块被浪磨圆的海玻璃"],
    "cape_open_water": ["一只漂流瓶", "一块风化浮木", "一段旧船绳", "一只被咬过的拟饵"],
    "amazon_flooded_forest": ["一枚被鱼啃过的硬果核", "一段长满附生物的树枝", "一只空棕榈种壳", "一团需要清理的尼龙线"],
    "baikal_littoral": ["一块圆润的湖岸卵石", "一小片脱落绿海绵组织", "一只空端足类蜕壳", "一段废弃透明鱼线"],
    "mekong_mainstem": ["一枚漂流植物种子", "一截被水磨亮的竹片", "一只旧塑料凉鞋", "一团废弃刺网线"],
}

RELATIONSHIPS = [
    {"id": "colorado_native_refuge", "location_id": "colorado_headwaters", "type": "competition_and_refuge",
     "requires": ["colorado_river_cutthroat", "brown_trout"], "min_count": 1,
     "title_zh": "原生源流与引入种", "title_en": "Native headwaters and introduced trout",
     "fact_zh": "寒冷且连通性受控的源流可成为原生割喉鳟的避难所；引入鳟类会带来竞争、捕食或杂交等不同压力，具体影响取决于物种与水系。"},
    {"id": "hokkaido_migration_corridor", "location_id": "hokkaido_river", "type": "migration",
     "requires": ["cherry_salmon", "white_spotted_char"], "min_count": 1,
     "title_zh": "森林河川的海陆通道", "title_en": "Forest river as a sea-land corridor",
     "fact_zh": "河岸林、深潭、浅滩和河口不是孤立地点；它们共同决定洄游型与河川残留型鱼类能否完成不同生活史。"},
    {"id": "hokkaido_kelp_edge", "location_id": "hokkaido_rocky_coast", "type": "habitat_structure",
     "requires": ["arabesque_greenling", "japanese_flounder"], "min_count": 2,
     "title_zh": "岩缝、海藻边缘与海底伏击", "title_en": "Rock crevices, kelp edges, and benthic ambush",
     "fact_zh": "结构复杂的岩礁海岸把藏身、产卵、伏击和开放觅食面压缩在很短的距离内，因此底质变化会重组整个小型群落。"},
    {"id": "cape_kelp_architecture", "location_id": "cape_kelp_forest", "type": "habitat_structure",
     "requires": ["galjoen", "hottentot_seabream"], "min_count": 2,
     "title_zh": "巨藻不是背景", "title_en": "Kelp is architecture, not scenery",
     "fact_zh": "巨藻林改变水流、遮蔽和附着表面；鱼类利用的是一座会随浪涌移动的立体栖息地，而不是一片静止的植物布景。"},
    {"id": "amazon_fruit_link", "location_id": "amazon_flooded_forest", "type": "cross_ecosystem_food",
     "requires": ["tambaqui"], "min_count": 3,
     "title_zh": "森林结果，鱼群进食", "title_en": "Forest fruit becomes fish food",
     "fact_zh": "洪水把树冠下的果实和种子带入水中；取食它们的鱼又移动种子与营养，使森林和河流成为同一个季节性系统。"},
    {"id": "amazon_managed_arapaima", "location_id": "amazon_flooded_forest", "type": "community_conservation",
     "requires": ["arapaima"], "min_count": 2,
     "title_zh": "从浮头换气到社区计数", "title_en": "From air breathing to community counts",
     "fact_zh": "巨骨舌鱼必须浮头换气，使有经验的社区观察者能够计数；监测、分区与守护湖泊共同构成管理，而不是把“可捕”简化为无限资源。"},
    {"id": "baikal_pelagic_chain", "location_id": "baikal_littoral", "type": "food_web",
     "requires": ["baikal_omul", "small_golomyanka"], "min_count": 2,
     "title_zh": "寒冷水柱中的能量通道", "title_en": "Energy pathways in a cold water column",
     "fact_zh": "浮游甲壳动物支撑欧姆白鲑和胎生贝湖鱼等水柱消费者，后者又是贝加尔海豹食物网的重要环节。"},
    {"id": "baikal_slow_recovery", "location_id": "baikal_littoral", "type": "life_history",
     "requires": ["baikal_sturgeon"], "min_count": 2,
     "title_zh": "长寿不等于恢复快", "title_en": "Long-lived does not mean fast recovery",
     "fact_zh": "贝加尔鲟成熟缓慢且依赖支流繁殖；当繁殖成鱼或幼鱼持续损失时，种群无法用短期高繁殖迅速补回。"},
    {"id": "mekong_connected_river", "location_id": "mekong_mainstem", "type": "migration_conservation",
     "requires": ["mekong_giant_catfish", "giant_barb"], "min_count": 2,
     "title_zh": "巨鱼需要一条完整的河", "title_en": "Giant fish need a connected river",
     "fact_zh": "大型洄游鱼把深槽、主河道、支流与繁殖地连成一条生命史路线；保护单个点位无法替代整条通道的连通性。"},
    {"id": "mekong_small_fish_scale", "location_id": "mekong_mainstem", "type": "biomass_flow",
     "requires": ["siamese_mud_carp", "striped_catfish"], "min_count": 3,
     "title_zh": "小鱼也能移动巨量生物量", "title_en": "Small fish can move enormous biomass",
     "fact_zh": "个体尺寸很小的洄游鱼能以庞大鱼群移动营养与能量；生态重要性不能只按单条鱼的重量排序。"},
]

_RELATION_FACT_EN = {
    "colorado_native_refuge": "Cold headwaters with managed connectivity can shelter native cutthroat trout. Introduced trout may add competition, predation, or hybridization pressure depending on species and watershed.",
    "hokkaido_migration_corridor": "Riparian forest, pools, riffles, and estuary are not isolated sites; together they determine whether sea-run and stream-resident life histories can be completed.",
    "hokkaido_kelp_edge": "Complex rocky coasts place shelter, spawning sites, ambush cover, and open feeding surfaces close together, so bottom structure can reorganize the community.",
    "cape_kelp_architecture": "Kelp changes flow, cover, and attachment surfaces. Fish use a three-dimensional habitat moving with surge, not a static plant backdrop.",
    "amazon_fruit_link": "Floodwater carries fruit and seeds below the canopy. Fish consume and redistribute them, linking forest and river into one seasonal system.",
    "amazon_managed_arapaima": "Arapaima must surface for air, enabling skilled community counts. Monitoring, zoning, and lake protection make management more than unlimited permission to harvest.",
    "baikal_pelagic_chain": "Planktonic crustaceans support water-column consumers such as omul and golomyanka, which in turn are important within the Baikal seal food web.",
    "baikal_slow_recovery": "Baikal sturgeon mature slowly and depend on tributaries to spawn; sustained loss of adults or young cannot be replaced by rapid reproduction.",
    "mekong_connected_river": "Large migratory fish link deep pools, main channel, tributaries, and spawning grounds into one life-history route; protecting one site cannot replace corridor connectivity.",
    "mekong_small_fish_scale": "Small migratory fish can move nutrients and energy in enormous schools; ecological importance cannot be ranked by individual body mass alone."}
for _relationship in RELATIONSHIPS:
    _relationship["fact_en"] = _RELATION_FACT_EN[_relationship["id"]]


def _wild(id, en, zh, group, locations, fact_en, fact_zh, seasons=None, status="observe_only"):
    return {"id": id, "name_en": en, "name_zh": zh, "group": group,
            "locations": locations, "seasons": seasons or ALL_SEASONS,
            "fact_en": fact_en, "fact_zh": fact_zh, "status": status}


WILDLIFE = {
    "american_dipper": _wild("american_dipper", "American Dipper", "美洲河乌", "bird", ["colorado_headwaters"],
        "A dipper walks and swims in fast streams, using aquatic insects as a bridge between river and bird food webs.",
        "美洲河乌会在急流中步行、潜游并取食水生昆虫，把河流底栖食物网与鸟类连接起来。"),
    "mayfly_nymph": _wild("mayfly_nymph", "Mayfly Nymph", "蜉蝣若虫", "aquatic_insect", ["colorado_headwaters"],
        "Mayfly nymphs live underwater before a brief winged adult stage and are widely used in stream assessment.",
        "蜉蝣的大部分生活史以水下若虫度过，成虫期短；若虫群落常用于评估溪流环境。"),
    "osprey": _wild("osprey", "Osprey", "鹗", "bird", ["colorado_reservoir"],
        "Ospreys hunt fish near the surface, making their flight and plunge a visible sign of predator-prey activity.",
        "鹗从空中观察并俯冲捕捉近表层鱼类，它的飞行与入水能提示捕食活动正在发生。"),
    "dragonfly_exuvia": _wild("dragonfly_exuvia", "Dragonfly Exuvia", "蜻蜓羽化壳", "aquatic_insect", ["colorado_reservoir"],
        "An empty exuvia marks where an aquatic dragonfly nymph left the water and became a flying adult.",
        "空羽化壳记录了一只水生蜻蜓若虫离开水体、变成飞行成虫的位置。"),
    "brown_bear_track": _wild("brown_bear_track", "Brown Bear Track", "棕熊足迹", "mammal_sign", ["hokkaido_river"],
        "Bear signs near salmon rivers reveal a land-water food-web connection; observers should keep distance and follow local safety guidance.",
        "鲑鱼河附近的熊迹揭示陆地与水域食物网的联系；观察者必须保持距离并遵循当地安全指引。"),
    "caddisfly_case": _wild("caddisfly_case", "Caddisfly Larval Case", "石蛾幼虫巢", "aquatic_insect", ["hokkaido_river"],
        "Many caddisfly larvae build portable cases from sand, leaf, or twig fragments available in their stream.",
        "许多石蛾幼虫会用溪流中现成的砂粒、叶片或细枝搭建可移动的巢。"),
    "stellers_sea_eagle": _wild("stellers_sea_eagle", "Steller's Sea Eagle", "虎头海雕", "bird", ["hokkaido_rocky_coast"],
        "This large raptor is part of the Shiretoko sea-land food web supported by migratory fish and productive cold water.",
        "虎头海雕属于知床海陆相连的食物网，洄游鱼类与高生产力冷水生态共同支撑它。", ["autumn", "winter", "spring"], "protected_observation"),
    "kombu_kelp": _wild("kombu_kelp", "Kombu Kelp", "昆布", "algae", ["hokkaido_rocky_coast"],
        "Kelp is a primary producer and three-dimensional habitat, not merely an object washed onto shore.",
        "昆布既是初级生产者，也是三维栖息地，并不只是被冲上岸的一团海藻。"),
    "cape_fur_seal": _wild("cape_fur_seal", "Cape Fur Seal", "南非毛皮海狮", "mammal", ["cape_kelp_forest", "cape_open_water"],
        "Cape fur seals forage across reef and open-water habitats and should be watched without feeding or approaching.",
        "南非毛皮海狮会跨越礁区与开放水域觅食；观察时不应投喂或主动靠近。", status="protected_observation"),
    "kelp_holdfast_community": _wild("kelp_holdfast_community", "Kelp Holdfast Community", "巨藻固着器微群落", "invertebrate_community", ["cape_kelp_forest"],
        "A kelp holdfast anchors the alga and creates small spaces used by many invertebrates.",
        "巨藻固着器不仅固定藻体，其复杂缝隙也为多种无脊椎动物提供微型栖息地。"),
    "cape_cormorant": _wild("cape_cormorant", "Cape Cormorant", "南非鸬鹚", "bird", ["cape_open_water"],
        "A flock of diving cormorants can reveal where schooling prey is concentrated near the surface.",
        "成群潜水的南非鸬鹚有时能提示近表层的小型群游猎物正在哪里聚集。", status="protected_observation"),
    "southern_right_whale": _wild("southern_right_whale", "Southern Right Whale", "南露脊鲸", "mammal", ["cape_open_water"],
        "A whale sighting is a distant observation event, never a fishing target; vessel distance matters.",
        "鲸类出现只能作为远距离观察事件，绝不是垂钓目标；船只与鲸的距离十分重要。", ["winter", "spring"], "protected_observation"),
    "hoatzin": _wild("hoatzin", "Hoatzin", "麝雉", "bird", ["amazon_flooded_forest"],
        "Hoatzins feed largely on leaves and live around floodplain vegetation, adding a herbivorous bird pathway to the wetland web.",
        "麝雉主要取食叶片并生活在泛滥平原植被附近，为湿地食物网加入一条植食鸟类通道。"),
    "giant_water_lily": _wild("giant_water_lily", "Giant Water Lily", "王莲", "plant", ["amazon_flooded_forest"],
        "Floating leaves change shade and surface structure while flowers and submerged stems interact with insects and aquatic life.",
        "王莲浮叶改变水面遮阴与结构，花朵和水下茎叶又与昆虫及水生生物发生联系。"),
    "baikal_seal": _wild("baikal_seal", "Baikal Seal", "贝加尔海豹", "mammal", ["baikal_littoral"],
        "The world's only exclusively freshwater seal feeds within a food web that includes golomyanka, sculpins, and omul.",
        "贝加尔海豹是独特的纯淡水海豹，其食物网包含胎生贝湖鱼、杜父鱼和欧姆白鲑等。", status="protected_observation"),
    "baikal_green_sponge": _wild("baikal_green_sponge", "Baikal Green Sponge", "贝加尔绿海绵", "sponge", ["baikal_littoral"],
        "Green Baikal sponges are animals whose color comes from symbiotic algae living in their tissues.",
        "贝加尔绿海绵是动物；它们的绿色来自生活在组织中的共生藻类。"),
    "irrawaddy_dolphin": _wild("irrawaddy_dolphin", "Irrawaddy Dolphin", "伊洛瓦底江豚", "mammal", ["mekong_mainstem"],
        "The isolated Mekong freshwater subpopulation is critically endangered and depends on deep pools, prey, and safe connected habitat.",
        "湄公河的伊洛瓦底江豚淡水亚种群高度孤立且极危，依赖深潭、猎物与安全连通的河流环境。", status="critically_endangered_observation"),
    "mekong_freshwater_prawn": _wild("mekong_freshwater_prawn", "Freshwater Prawn", "湄公河淡水长臂虾", "crustacean", ["mekong_mainstem"],
        "Freshwater prawns connect detritus, small prey, fish, and people across river and floodplain food webs.",
        "淡水长臂虾把碎屑、小型猎物、鱼类与人类利用连接进河流和泛滥平原食物网。"),
}


# Original fiction is structurally separate from species and science data.
# These are not claims about local traditional knowledge and never affect odds.
STORIES = [
    {"id": "colorado_returned_line", "location_id": "colorado_headwaters", "casts_required": 5,
     "title_zh": "自己回来的鱼线", "title_en": "The Line That Returned",
     "text_zh": "营火旁有人说，源流会把遗失的鱼线一圈圈推回岸边，直到失主学会不用它们缠住河底。第二天，靴旁果然多了一团旧线——也可能只是昨夜涨水。",
     "text_en": "Around the fire, someone says the headwater returns lost line coil by coil until its owner learns not to leave it below. By morning an old tangle lies beside the boots—or perhaps the water simply rose overnight."},
    {"id": "hokkaido_second_splash", "location_id": "hokkaido_river", "casts_required": 5,
     "title_zh": "第二声水响", "title_en": "The Second Splash",
     "text_zh": "故事里，森林河每次鱼跃后都会晚半拍响起第二声，像山在练习模仿河流。调查员写道：若只听声音，永远别把回声当成第二条鱼。",
     "text_en": "In the story, every leap in the forest river is followed by a second splash, as if the mountain were practicing the river's voice. The observer writes: never turn an echo into a second fish merely by listening."},
    {"id": "cape_kelp_knock", "location_id": "cape_kelp_forest", "casts_required": 5,
     "title_zh": "巨藻门外的敲击", "title_en": "The Knock Beyond the Kelp Door",
     "text_zh": "浪涌合上巨藻走廊时，潜水员听见三次敲击；浪退后只有固着器里的小石块互相碰撞。故事坚持那是海藻林在询问来客有没有保持距离。",
     "text_en": "When surge closes the kelp corridor, a diver hears three knocks. After the water falls away, only small stones click inside a holdfast. The story insists the forest was asking whether its visitor kept a respectful distance."},
    {"id": "amazon_lake_counts", "location_id": "amazon_flooded_forest", "casts_required": 5,
     "title_zh": "会数数的湖", "title_en": "The Lake That Counts Back",
     "text_zh": "管理者数浮头换气的巨骨舌鱼，传说湖也在数岸上的人。若有人多报一条鱼，夜里就会少听见一次换气声。真正的记录表当然不会接受传说作证据。",
     "text_en": "Managers count arapaima surfacing for air; the tale says the lake counts people on shore. Add a fish that was not there, and one breath goes missing at night. The real survey sheet, of course, accepts no tale as evidence."},
    {"id": "baikal_light_under_ice", "location_id": "baikal_littoral", "casts_required": 5,
     "title_zh": "冰下那盏灯", "title_en": "The Lamp Beneath the Ice",
     "text_zh": "有人看见冰下有一盏灯缓慢升降，便说是湖在读夜间观察日志。科学笔记只写：透明水体、移动生物与折射足以制造许多灯。两种文字被并排保留。",
     "text_en": "A lamp seems to rise and fall beneath the ice, and someone says the lake is reading the night journal. The science note records only that clear water, moving organisms, and refraction can manufacture many lamps. Both texts are kept side by side."},
    {"id": "mekong_deep_pool_echo", "location_id": "mekong_mainstem", "casts_required": 5,
     "title_zh": "深潭归还的名字", "title_en": "The Name Returned by the Deep Pool",
     "text_zh": "船经过深潭时，故事要求每个人只说一次自己的名字；第二次若从水面传来，就当作水流与船壳的回声，不回答，也不靠近。",
     "text_en": "Passing a deep pool, the story permits each traveler to say their name once. If it returns from the water, treat it as current and hull echo: do not answer, and do not approach."},
]
