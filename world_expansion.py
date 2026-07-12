"""Second field edition: eight habitats and seventy-four researched species."""

ALL = ["spring", "summer", "autumn", "winter"]


def location(id, en, zh, en_desc, zh_desc, tags, cost, junk, biome):
    return {"id": id, "name": zh, "name_en": en, "name_zh": zh,
            "description": zh_desc, "description_en": en_desc, "description_zh": zh_desc,
            "biome": biome, "junk_chance_base": junk, "event_chance_base": 0.06,
            "tag_weight_mult": tags, "unlock_cost": cost, "available_seasons": ALL,
            "ambience": ["你记录水色、风和岸边结构，再等待下一条证据。"],
            "character": "真实水域不会保证收获，但每次结果都能留下记录。"}


LOCATIONS = {
    "colorado_river_canyon": location("colorado_river_canyon", "Colorado River Canyon", "科罗拉多河峡谷",
        "A warm, sediment-shaped desert river reach holding highly specialized native big-river fishes.",
        "受泥沙、洪水与峡谷塑造的温暖荒漠河段，保存着高度特化的大河原生鱼类。",
        {"large_river": 1.5, "native_colorado": 1.7, "warmwater": 1.25}, 700, 0.18, "desert canyon river"),
    "florida_mangrove_estuary": location("florida_mangrove_estuary", "Florida Mangrove Estuary", "佛罗里达红树林河口",
        "Tidal creeks where Everglades freshwater mixes with the sea among mangrove roots and seagrass.",
        "大沼泽地淡水与海水在潮沟、红树林根系和海草床之间混合。",
        {"marine": 1.3, "brackish": 1.6, "mangrove": 1.7, "estuary": 1.5}, 900, 0.24, "subtropical mangrove estuary"),
    "norway_fjord": location("norway_fjord", "Norwegian Fjord", "挪威峡湾",
        "A steep cold-water fjord linking kelp shallows, rocky slopes, deep basins, and the North Atlantic.",
        "陡峭的冷水峡湾连接海藻浅滩、岩质坡面、深盆地与北大西洋。",
        {"marine": 1.4, "coldwater": 1.5, "fjord": 1.7, "deep": 1.25}, 1150, 0.18, "cold marine fjord"),
    "lake_superior_shore": location("lake_superior_shore", "Lake Superior Shore", "苏必利尔湖岸",
        "A vast cold glacial lake with rocky reefs, river mouths, deep water, and native plus introduced fishes.",
        "巨大的寒冷冰川湖，包含岩礁、河口和深水，也并存原生与引入鱼类。",
        {"lake": 1.6, "coldwater": 1.45, "great_lakes": 1.7}, 1250, 0.16, "large cold glacial lake"),
    "murray_darling_river": location("murray_darling_river", "Murray–Darling River", "墨累—达令河",
        "A variable inland river system where flow pulses reconnect channels, benches, floodplains, and billabongs.",
        "流量高度变化的内陆河系，洪水脉冲连接河槽、河床台地、泛滥平原与死水潭。",
        {"large_river": 1.5, "warmwater": 1.3, "australian_native": 1.6}, 1350, 0.23, "dryland flood-pulse river"),
    "new_zealand_south_island": location("new_zealand_south_island", "Aotearoa South Island River", "新西兰南岛河流",
        "Braided and forested waterways connecting alpine headwaters, lowland wetlands, lakes, and the Pacific.",
        "辫状河与森林河流连接高山源头、低地湿地、湖泊和太平洋。",
        {"stream": 1.4, "migratory": 1.5, "nz_native": 1.7, "coldwater": 1.2}, 1450, 0.17, "temperate braided and forest river"),
    "chesapeake_bay": location("chesapeake_bay", "Chesapeake Bay", "切萨皮克湾",
        "A large estuary of marsh creeks, seagrass, oyster structure, tidal rivers, and seasonal marine migrants.",
        "由盐沼潮沟、海草、牡蛎礁、潮汐河流和季节性海洋洄游鱼组成的大型河口湾。",
        {"estuary": 1.7, "brackish": 1.5, "marine": 1.25, "migratory": 1.35}, 1550, 0.25, "temperate estuary"),
    "monterey_kelp_forest": location("monterey_kelp_forest", "Monterey Bay Kelp Forest", "蒙特雷湾海藻林",
        "Central California rocky reef and giant-kelp habitat spanning canopy, understory, sand edge, and deeper groundfish water.",
        "加州中部的岩礁与巨藻生境，包含冠层、林下、沙地边缘和更深的底栖鱼水层。",
        {"marine": 1.4, "kelp": 1.8, "rocky": 1.4, "california_current": 1.5}, 1700, 0.21, "temperate giant-kelp forest"),
}


def fish(id, en, zh, latin, rarity, size, value, loc, tags, fact_en, fact_zh,
         identify_en, identify_zh, status="least_concern", origin="native", release=False, seasons=None):
    return {"id": id, "name": zh, "name_en": en, "name_zh": zh, "latin": latin,
            "rarity": rarity, "size_min": size[0], "size_max": size[1], "size_unit": "cm",
            "base_value": value, "locations": [loc], "seasons": seasons or ALL, "tags": tags,
            "description": fact_zh, "science_fact_en": fact_en, "science_fact_zh": fact_zh,
            "identification_en": identify_en, "identification_zh": identify_zh,
            "conservation": status, "native_status": origin, "release_only": release}


FISH = {}


def add(*args, **kwargs):
    record = fish(*args, **kwargs); FISH[record["id"]] = record


# Colorado River canyon — four imperiled native big-river fishes.
add("colorado_pikeminnow", "Colorado Pikeminnow", "科罗拉多拟鲤", "Ptychocheilus lucius", "rare", (35, 180), 90, "colorado_river_canyon", ["large_river", "native_colorado", "predator"],
    "North America's largest minnow is a long-distance native predator requiring connected warm river habitat.", "北美最大的鲤科鱼类之一，是需要连通温暖大河生境的长距离移动原生捕食者。",
    "An elongated body, large terminal mouth, and long cylindrical caudal peduncle separate adults from suckers.", "修长身体、大端位口和圆筒状尾柄可与吸口鱼类区别。", "endangered", release=True)
add("humpback_chub", "Humpback Chub", "驼背雅罗鱼", "Gila cypha", "rare", (20, 50), 75, "colorado_river_canyon", ["large_river", "native_colorado", "canyon"],
    "The pronounced hump and streamlined tail region suit turbulent canyon hydraulics.", "突出的背部隆起与流线型尾部适应峡谷湍急水力环境。",
    "Adults combine a steep forehead and dorsal hump with a narrow caudal peduncle.", "成鱼具有陡峭前额、明显背峰和狭窄尾柄。", "endangered", release=True)
add("razorback_sucker", "Razorback Sucker", "剃刀背胭脂鱼", "Xyrauchen texanus", "rare", (35, 90), 78, "colorado_river_canyon", ["large_river", "native_colorado", "bottom"],
    "A bony dorsal keel gives this long-lived Colorado River sucker its name.", "背部刀片状骨质隆脊赋予这种长寿科罗拉多河吸口鱼名称。",
    "The sharp dorsal keel behind the head is unmistakable in adults.", "成鱼头后锐利的背部隆脊极具辨识度。", "endangered", release=True)
add("bonytail", "Bonytail", "骨尾雅罗鱼", "Gila elegans", "rare", (25, 60), 80, "colorado_river_canyon", ["large_river", "native_colorado"],
    "A thin caudal peduncle and large fins reflect specialization for the historic Colorado River flow regime.", "细尾柄和较大鱼鳍反映其对历史科罗拉多河流态的特化。",
    "Look for a smoothly humped back, very narrow caudal peduncle, and relatively large fins.", "辨认组合是平滑隆背、极窄尾柄和相对较大的鳍。", "endangered", release=True)

# Florida mangrove estuary.
add("common_snook", "Common Snook", "锯盖鱼", "Centropomus undecimalis", "uncommon", (30, 120), 40, "florida_mangrove_estuary", ["estuary", "mangrove", "predator"], "Snook use mangrove shorelines and tidal creeks as feeding and nursery habitat.", "锯盖鱼利用红树林岸线和潮沟觅食并度过幼鱼期。", "A bold black lateral line runs onto the tail; the lower jaw projects beyond the upper.", "粗黑侧线延伸到尾部，下颌明显前突。")
add("atlantic_tarpon", "Atlantic Tarpon", "大西洋大海鲢", "Megalops atlanticus", "rare", (60, 240), 85, "florida_mangrove_estuary", ["estuary", "migratory", "air_breathing"], "Tarpon can gulp air using a vascularized swim bladder, helping them use low-oxygen water.", "大海鲢能用富血管鳔吞咽空气，因此可利用低氧水域。", "Huge silver scales, an upturned mouth, and an elongated final dorsal-fin ray are diagnostic.", "巨大银鳞、上翘口和延长的最后一根背鳍条是关键特征。", "regulated", release=True)
add("red_drum", "Red Drum", "红鼓鱼", "Sciaenops ocellatus", "common", (25, 120), 32, "florida_mangrove_estuary", ["estuary", "brackish", "bottom"], "Juvenile red drum use estuaries while adults can move into coastal water.", "幼年红鼓鱼利用河口湾，成鱼可进入沿岸海域。", "One or more black spots near the tail base contrast with a copper-red body.", "铜红体色配尾基附近一个或多个黑斑。")
add("spotted_seatrout", "Spotted Seatrout", "斑点犬牙石首鱼", "Cynoscion nebulosus", "common", (25, 80), 25, "florida_mangrove_estuary", ["estuary", "seagrass", "predator"], "Spotted seatrout often hunt around seagrass and shallow estuarine structure.", "斑点犬牙石首鱼常在海草与浅河口结构附近捕食。", "Round black spots cover the upper body and both dorsal and tail fins.", "圆形黑斑分布于上体、背鳍和尾鳍。")
add("gray_snapper", "Gray Snapper", "灰笛鲷", "Lutjanus griseus", "common", (20, 75), 24, "florida_mangrove_estuary", ["mangrove", "estuary", "reef"], "Young gray snapper shelter among mangrove roots before many shift toward reef habitat.", "幼年灰笛鲷在红树林根系间躲藏，许多个体长大后转向礁区。", "A dark eye stripe, reddish fins, and prominent canine teeth help identification.", "深色眼纹、偏红鱼鳍和明显犬齿有助辨认。")
add("sheepshead", "Sheepshead", "羊头鲷", "Archosargus probatocephalus", "common", (20, 75), 22, "florida_mangrove_estuary", ["estuary", "structure", "shell_crusher"], "Incisor-like front teeth and crushing rear teeth let sheepshead graze hard-shelled prey from structure.", "门齿状前牙与压碎型后牙使羊头鲷能从硬结构上取食带壳猎物。", "Five to seven dark vertical bars cross a deep silver body; the human-like incisors are distinctive.", "银色高体有五至七条深色竖纹，类似人类门齿的前牙非常醒目。")
add("crevalle_jack", "Crevalle Jack", "马鲹", "Caranx hippos", "uncommon", (30, 120), 33, "florida_mangrove_estuary", ["estuary", "pelagic", "schooling"], "Crevalle jacks are fast schooling predators that move between estuaries and coastal water.", "马鲹是快速群游捕食者，会在河口与沿岸水域之间移动。", "A black spot on the gill cover and another at the pectoral-fin base mark the silver-yellow body.", "鳃盖黑斑与胸鳍基部黑斑标记银黄身体。")
add("ladyfish", "Ladyfish", "北美海鲢", "Elops saurus", "common", (25, 90), 18, "florida_mangrove_estuary", ["estuary", "pelagic", "schooling"], "Ladyfish chase small prey through shallow bays and often leap when hooked.", "北美海鲢在浅湾追逐小型猎物，受惊或中钩时常跃出水面。", "The slender silver body has a deeply forked tail and a small terminal mouth without tarpon's huge scales.", "细长银色身体配深叉尾，鳞片不像大海鲢那样巨大。")
add("hardhead_catfish", "Hardhead Catfish", "硬头海鲶", "Ariopsis felis", "common", (20, 70), 15, "florida_mangrove_estuary", ["estuary", "bottom", "barbel"], "Hardhead catfish use barbels to search turbid estuarine bottoms.", "硬头海鲶用触须搜索浑浊河口底部。", "Six barbels, a deeply forked tail, and stiff venomous fin spines require careful handling.", "六根触须、深叉尾和坚硬有毒鳍棘要求避免徒手接触。")
add("gafftopsail_catfish", "Gafftopsail Catfish", "帆鳍海鲶", "Bagre marinus", "uncommon", (25, 100), 24, "florida_mangrove_estuary", ["estuary", "bottom", "barbel"], "The enlarged dorsal and pectoral rays form long streamers but also carry defensive spines.", "延长的背鳍与胸鳍条形成丝状结构，同时也是防御鳍棘。", "Long ribbon-like fin rays and only two chin barbels separate it from hardhead catfish.", "长丝状鳍条与仅两根下颌触须可和硬头海鲶区别。")

# Norwegian fjord.
add("atlantic_cod", "Atlantic Cod", "大西洋鳕", "Gadus morhua", "common", (30, 150), 32, "norway_fjord", ["fjord", "coldwater", "bottom"], "Cod connect benthic and pelagic prey across fjord and shelf food webs.", "大西洋鳕在峡湾与陆架食物网中连接底栖和中上层猎物。", "Three dorsal fins, two anal fins, a pale lateral line, and one chin barbel form the classic combination.", "三背鳍、两臀鳍、浅色侧线和一根下颌触须是经典组合。")
add("haddock", "Haddock", "黑线鳕", "Melanogrammus aeglefinus", "common", (25, 110), 28, "norway_fjord", ["fjord", "coldwater", "bottom"], "Haddock feed heavily on benthic invertebrates and fish eggs in Norwegian waters.", "黑线鳕在挪威水域大量取食底栖无脊椎动物与鱼卵。", "A black shoulder blotch below the first dorsal fin and a dark lateral line are diagnostic.", "第一背鳍下方黑色肩斑与深色侧线是关键特征。")
add("saithe", "Saithe", "青鳕", "Pollachius virens", "common", (30, 130), 27, "norway_fjord", ["fjord", "pelagic", "schooling"], "Saithe often form mobile schools along the coast and within fjords.", "青鳕常在沿岸与峡湾内形成移动鱼群。", "The nearly straight pale lateral line contrasts with a dark back and deeply forked tail.", "近乎笔直的浅色侧线与深色背部、深叉尾形成对比。")
add("atlantic_mackerel", "Atlantic Mackerel", "大西洋鲭", "Scomber scombrus", "common", (20, 55), 20, "norway_fjord", ["fjord", "pelagic", "schooling", "migratory"], "Mackerel schools follow seasonal temperature and food across coastal water.", "大西洋鲭鱼群随季节温度和食物在沿岸水域移动。", "Dark wavy bars cross the blue-green back; the belly lacks spots.", "蓝绿色背部有深色波纹，腹部通常无斑。")
add("atlantic_halibut", "Atlantic Halibut", "大西洋庸鲽", "Hippoglossus hippoglossus", "rare", (50, 350), 85, "norway_fjord", ["fjord", "deep", "bottom"], "A slow-growing late-maturing giant flatfish can be vulnerable where spawning groups concentrate.", "这种生长缓慢、成熟较晚的巨型鲽鱼在繁殖群聚时尤其脆弱。", "Both eyes lie on the right; the eyed side is gray-brown and the blind side white.", "双眼位于右侧，有眼侧灰褐、盲侧白色。", "regulated", release=True)
add("atlantic_wolffish", "Atlantic Wolffish", "大西洋狼鱼", "Anarhichas lupus", "uncommon", (35, 150), 42, "norway_fjord", ["fjord", "rocky", "shell_crusher"], "Powerful teeth crush sea urchins, mollusks, and crustaceans on cold rocky bottoms.", "强壮牙齿能压碎寒冷岩底的海胆、软体动物和甲壳类。", "Large canine teeth, a long continuous dorsal fin, and dark vertical bars are conspicuous.", "大型犬齿、连续长背鳍和深色竖纹十分醒目。")
add("ling", "Ling", "欧洲鼬鳚", "Molva molva", "uncommon", (50, 200), 45, "norway_fjord", ["fjord", "deep", "rocky"], "Ling shelter along steep rocky slopes and deep wreck-like structure.", "欧洲鼬鳚利用陡峭岩坡和深水复杂结构。", "An elongated body, two dorsal fins, and a single chin barbel distinguish ling from true eels.", "修长身体、两背鳍和一根下颌触须可与真正鳗类区别。")
add("pollack", "Pollack", "绿青鳕", "Pollachius pollachius", "uncommon", (30, 120), 34, "norway_fjord", ["fjord", "kelp", "predator"], "Pollack hunt around kelp edges and rocky coastal structure.", "绿青鳕常在海藻边缘与岩质沿岸结构附近捕食。", "Its lateral line curves strongly above the pectoral fin, unlike the straighter line of saithe.", "侧线在胸鳍上方明显弯曲，可与侧线较直的青鳕区别。")
add("atlantic_herring", "Atlantic Herring", "大西洋鲱", "Clupea harengus", "common", (15, 45), 15, "norway_fjord", ["fjord", "pelagic", "schooling", "migratory"], "Herring convert plankton production into prey for cod, saithe, seabirds, and whales.", "大西洋鲱把浮游生物生产转化为鳕鱼、青鳕、海鸟和鲸类的猎物。", "A compressed silver body lacks an adipose fin; the belly edge is mildly keeled.", "侧扁银色身体无脂鳍，腹缘略呈棱状。")
add("anglerfish", "Anglerfish", "鮟鱇", "Lophius piscatorius", "rare", (35, 200), 62, "norway_fjord", ["fjord", "bottom", "ambush"], "Anglerfish wait on the seabed and use a modified first dorsal ray as a lure.", "鮟鱇伏在海底，用改造的第一背鳍棘充当诱饵。", "The enormous flattened head, wide mouth, and fishing-rod-like lure are unmistakable.", "巨大扁平头部、宽口和钓竿状诱饵结构极易辨认。")

# Lake Superior and connected Great Lakes water.
add("walleye", "Walleye", "玻璃梭鲈", "Sander vitreus", "common", (25, 90), 30, "lake_superior_shore", ["great_lakes", "lake", "low_light"], "Reflective eyes aid feeding in low light and turbid water.", "反光眼结构帮助玻璃梭鲈在弱光和浑水中觅食。", "A white lower tip on the tail and opaque-looking eyes separate walleye from sauger.", "尾鳍下叶白尖与乳白反光眼可和近似种区别。")
add("yellow_perch", "Yellow Perch", "黄鲈", "Perca flavescens", "common", (12, 40), 14, "lake_superior_shore", ["great_lakes", "lake", "schooling"], "Yellow perch form schools and feed on plankton, insects, and small fish.", "黄鲈群游并取食浮游生物、昆虫和小鱼。", "Six to nine dark vertical bars cross a yellow-gold body with orange lower fins.", "黄金额身体有六至九条深色竖纹，下部鱼鳍偏橙。")
add("lake_whitefish", "Lake Whitefish", "湖白鲑", "Coregonus clupeaformis", "common", (25, 75), 27, "lake_superior_shore", ["great_lakes", "lake", "coldwater", "bottom"], "A small subterminal mouth picks benthic invertebrates from cold lake bottoms.", "较小的亚下位口适合从寒冷湖底摄取底栖无脊椎动物。", "The body is silver with a small head, deeply forked tail, and adipose fin.", "银色身体配小头、深叉尾和脂鳍。")
add("burbot", "Burbot", "江鳕", "Lota lota", "uncommon", (30, 110), 32, "lake_superior_shore", ["great_lakes", "lake", "coldwater", "bottom"], "Burbot are the only freshwater cod and are especially active in cold seasons.", "江鳕是唯一完全淡水生活的鳕形鱼，寒冷季节尤其活跃。", "An eel-like mottled body, two dorsal fins, and one chin barbel identify it.", "鳗状斑驳身体、两背鳍和一根下颌触须是辨认组合。")
add("lake_sturgeon", "Lake Sturgeon", "湖鲟", "Acipenser fulvescens", "rare", (60, 220), 80, "lake_superior_shore", ["great_lakes", "lake", "bottom", "migratory"], "Late maturity and long life make lake sturgeon recovery slow even after protection.", "成熟晚且寿命长使湖鲟即便受保护后也恢复缓慢。", "Five rows of bony scutes, four barbels, and a protrusible underslung mouth mark a sturgeon.", "五列骨板、四根触须与可伸缩腹位口标志鲟鱼。", "protected", release=True)
add("freshwater_drum", "Freshwater Drum", "淡水石首鱼", "Aplodinotus grunniens", "common", (20, 90), 20, "lake_superior_shore", ["great_lakes", "lake", "shell_crusher"], "Freshwater drum can produce sound and crush mollusks with throat teeth.", "淡水石首鱼能发声，并用咽齿压碎软体动物。", "A deep silver body, long dorsal fin, and rounded tail differ from perch and bass.", "银色高体、长背鳍与圆尾可区别于鲈类。")
add("northern_pike", "Northern Pike", "白斑狗鱼", "Esox lucius", "common", (35, 130), 30, "lake_superior_shore", ["great_lakes", "lake", "ambush"], "Pike ambush prey from vegetation and shallow structure.", "白斑狗鱼从水草和浅水结构中伏击猎物。", "A duckbill snout and pale bean-shaped spots cover the green body.", "鸭嘴状吻部与绿色身体上的浅色豆形斑点。")
add("muskellunge", "Muskellunge", "大狗鱼", "Esox masquinongy", "rare", (60, 150), 65, "lake_superior_shore", ["great_lakes", "lake", "ambush"], "Large muskellunge are low-density apex predators requiring extensive habitat.", "大型大狗鱼是低密度顶级捕食者，需要广阔生境。", "Dark bars or spots lie on a pale body; sensory pores under each jaw help separate it from pike.", "浅色体底配深色条斑，下颌感觉孔数量可辅助区别白斑狗鱼。", "regulated", release=True)
add("round_goby", "Round Goby", "圆吻鰕虎鱼", "Neogobius melanostomus", "common", (6, 25), 8, "lake_superior_shore", ["great_lakes", "bottom", "invasive"], "This invasive bottom fish spreads through connected waters and competes for food and shelter.", "这种入侵底栖鱼沿连通水域扩散，并竞争食物与庇护。", "Fused pelvic fins form a suction disk; the first dorsal fin bears a dark spot.", "腹鳍融合成吸盘，第一背鳍有黑斑。", "invasive", "introduced")
add("coho_salmon", "Coho Salmon", "银鲑", "Oncorhynchus kisutch", "uncommon", (35, 90), 38, "lake_superior_shore", ["great_lakes", "lake", "migratory", "introduced"], "Introduced coho support a fishery but are not native to the Great Lakes basin.", "引入银鲑支持渔业，但并非五大湖流域原生物种。", "Black spots usually cover the upper tail lobe; the lower gums are pale rather than black.", "黑斑多在尾鳍上叶，下牙龈较浅而非黑色。", origin="introduced")

# Murray–Darling Basin.
add("murray_cod", "Murray Cod", "墨累鳕鲈", "Maccullochella peelii", "rare", (35, 180), 72, "murray_darling_river", ["large_river", "australian_native", "ambush"], "Murray cod use woody structure and can complete a lifecycle within a relatively short river reach.", "墨累鳕鲈利用沉木结构，并可能在相对较短的河段内完成生活史。", "A broad head and mottled olive reticulation cover a heavy-bodied perch-like fish.", "宽头、粗壮身体与橄榄色网状斑纹。", "vulnerable", release=True)
add("golden_perch", "Golden Perch", "金鲈", "Macquaria ambigua", "common", (25, 75), 30, "murray_darling_river", ["large_river", "australian_native", "migratory"], "Flow pulses can trigger movement and spawning across long river distances.", "流量脉冲能触发金鲈长距离移动与繁殖。", "A deep bronze-gold body has a concave forehead and rounded tail.", "高而铜金色身体配凹额线和圆尾。")
add("silver_perch", "Silver Perch", "银鲈", "Bidyanus bidyanus", "uncommon", (20, 60), 34, "murray_darling_river", ["large_river", "australian_native", "schooling"], "Silver perch are native schooling fish affected by barriers, altered flow, and invasive species.", "银鲈是原生群游鱼，受到阻隔、流态改变和入侵物种影响。", "Small scales, a relatively small head, and silver-gray body distinguish it from golden perch.", "小鳞、较小头部与银灰体色可和金鲈区别。", "vulnerable", release=True)
add("trout_cod", "Trout Cod", "鳟鳕鲈", "Maccullochella macquariensis", "rare", (25, 85), 60, "murray_darling_river", ["large_river", "australian_native", "rocky"], "Trout cod are a threatened native predator associated with flowing rocky and woody habitat.", "鳟鳕鲈是受威胁原生捕食者，与流动的岩石和沉木生境相关。", "A pointed snout and dark stripe through the eye help separate it from Murray cod.", "尖吻和穿眼深色条纹有助与墨累鳕鲈区别。", "endangered", release=True)
add("macquarie_perch", "Macquarie Perch", "麦夸里鲈", "Macquaria australasica", "rare", (20, 60), 55, "murray_darling_river", ["stream", "australian_native", "rocky"], "This threatened native perch depends on suitable flowing-water and spawning habitat.", "这种受威胁原生鲈依赖适合的流水与繁殖生境。", "A rounded tail, large eye, and dark gray body differ from the golden perch's bronze profile.", "圆尾、大眼和深灰身体可区别于铜金色金鲈。", "endangered", release=True)
add("freshwater_catfish_au", "Freshwater Catfish", "澳洲鳗尾鲶", "Tandanus tandanus", "uncommon", (25, 90), 32, "murray_darling_river", ["large_river", "australian_native", "bottom"], "Unlike fork-tailed catfish, this native species has a continuous eel-like tail fin.", "与叉尾鲶不同，这种原生鱼具有连续鳗状尾鳍。", "Four pairs of barbels and a continuous second dorsal, caudal, and anal fin form an eel tail.", "四对触须，第二背鳍、尾鳍和臀鳍连续成鳗尾。")
add("australian_smelt", "Australian Smelt", "澳洲胡瓜鱼", "Retropinna semoni", "common", (4, 12), 8, "murray_darling_river", ["australian_native", "schooling", "small_fish"], "Small smelt transfer plankton and insect energy to larger native predators.", "小型澳洲胡瓜鱼把浮游生物和昆虫能量传递给更大的原生捕食者。", "A translucent silver body, forked tail, and small adipose fin identify this tiny schooling fish.", "半透明银色身体、叉尾和小脂鳍。")
add("bony_herring", "Bony Herring", "骨鲱", "Nematalosa erebi", "common", (10, 45), 12, "murray_darling_river", ["australian_native", "schooling", "floodplain"], "Bony herring can become abundant after floodplain productivity pulses.", "骨鲱在泛滥平原生产力脉冲后可能大量增加。", "A deep compressed body has a sharp saw-like belly keel and a trailing dorsal filament.", "高侧扁身体有锯状腹棱和延长背鳍丝。")
add("murray_darling_rainbowfish", "Murray–Darling Rainbowfish", "墨累—达令彩虹鱼", "Melanotaenia fluviatilis", "common", (4, 11), 9, "murray_darling_river", ["australian_native", "small_fish", "vegetation"], "Small rainbowfish use vegetated margins and are important prey within floodplain food webs.", "小型彩虹鱼利用植被岸缘，也是泛滥平原食物网的重要猎物。", "Two separate dorsal fins and a laterally compressed iridescent body identify rainbowfishes.", "两枚分离背鳍与侧扁虹彩身体标志彩虹鱼类。")
add("common_carp", "Common Carp", "鲤", "Cyprinus carpio", "common", (25, 110), 14, "murray_darling_river", ["large_river", "bottom", "invasive"], "Introduced carp can dominate biomass and disturb sediment while feeding.", "引入鲤在取食时扰动沉积物，并可能占据很高生物量。", "Two barbels on each side of the mouth and a long-based dorsal fin distinguish carp.", "口角每侧两根触须与长基底背鳍。", "invasive", "introduced")

# Aotearoa New Zealand South Island waterways.
add("longfin_eel", "Longfin Eel / Tuna", "新西兰长鳍鳗", "Anguilla dieffenbachii", "rare", (30, 200), 58, "new_zealand_south_island", ["nz_native", "migratory", "nocturnal"], "Endemic longfin eels grow slowly for decades before a one-way ocean spawning migration.", "特有长鳍鳗在淡水中缓慢生长数十年，最终单程洄游到海洋繁殖。", "The dorsal fin extends much farther forward than the anal fin and the skin forms broad wrinkles when bent.", "背鳍起点远早于臀鳍，身体弯曲时皮肤形成宽大皱褶。", "at_risk_declining", "endemic", True)
add("shortfin_eel", "Shortfin Eel", "短鳍鳗", "Anguilla australis", "uncommon", (25, 110), 32, "new_zealand_south_island", ["nz_native", "migratory", "nocturnal"], "Shortfin eels often occupy lowland water nearer the sea before migrating to the Pacific to spawn.", "短鳍鳗常利用更靠海的低地水域，成熟后洄游太平洋繁殖。", "Dorsal and anal fins begin at nearly the same level; skin wrinkles are finer than in longfin eel.", "背鳍与臀鳍起点接近，皮肤皱褶比长鳍鳗细。")
add("giant_kokopu", "Giant Kōkopu", "巨型科科普鱼", "Galaxias argenteus", "rare", (15, 58), 48, "new_zealand_south_island", ["nz_native", "migratory", "low_light"], "The world's largest galaxiid uses shaded lowland streams, wetlands, and cover near the sea.", "世界最大的银河鱼类利用近海阴蔽低地溪流、湿地与遮蔽物。", "Large adults show gold galaxy-like markings on a dark scaleless body.", "大型成鱼深色无鳞身体上有金色星系状斑纹。", "declining", "endemic", True)
add("koaro", "Kōaro", "科阿罗鱼", "Galaxias brevipinnis", "uncommon", (8, 30), 28, "new_zealand_south_island", ["nz_native", "migratory", "stream", "climber"], "Kōaro can climb wet barriers and penetrate far into fast bouldery forest streams.", "科阿罗鱼能攀爬湿润障碍，深入急流、多巨石的森林溪流。", "An elongated tubular body with large pectoral fins carries irregular pale and dark bands.", "细长筒状身体配大胸鳍和不规则明暗条斑。", "at_risk_declining", "native", True)
add("inanga", "Īnanga", "伊南加鱼", "Galaxias maculatus", "common", (4, 12), 10, "new_zealand_south_island", ["nz_native", "migratory", "estuary", "small_fish"], "Īnanga form most of the whitebait run and connect estuaries, wetlands, and rivers.", "伊南加鱼构成白饵洄游主体，连接河口、湿地与河流。", "A small scaleless silver fish has a mildly forked tail and no adipose fin.", "小型无鳞银鱼，尾鳍略叉且无脂鳍。", "at_risk_declining", "native", True)
add("torrentfish", "Torrentfish / Panoko", "激流鱼", "Cheimarrichthys fosteri", "uncommon", (8, 22), 24, "new_zealand_south_island", ["nz_native", "stream", "rocky"], "Torrentfish hold position in fast open braided-river channels over coarse stones.", "激流鱼在开阔辫状河的快速粗石河道中保持位置。", "A flattened head, large pectoral fins, and downward-facing mouth suit life in current.", "扁头、大胸鳍和向下的嘴适应急流。", "at_risk_declining", "endemic", True)
add("common_bully", "Common Bully", "普通塘鳢", "Gobiomorphus cotidianus", "common", (4, 15), 9, "new_zealand_south_island", ["nz_native", "bottom", "lake"], "Common bullies are small benthic fish using lakes and slow river margins.", "普通塘鳢是利用湖泊和缓流岸缘的小型底栖鱼。", "Two dorsal fins, a broad head, and mottled body identify this small sleeper goby relative.", "两背鳍、宽头与斑驳身体。")
add("redfin_bully", "Redfin Bully", "红鳍塘鳢", "Gobiomorphus huttoni", "uncommon", (5, 14), 14, "new_zealand_south_island", ["nz_native", "stream", "bottom"], "Redfin bullies use clear flowing water and males develop vivid fin color.", "红鳍塘鳢利用清澈流水，雄鱼会出现鲜艳鳍色。", "Orange-red fin margins and diagonal cheek stripes distinguish breeding males.", "繁殖雄鱼具橙红鳍缘和斜向颊纹。", "at_risk_declining", "endemic", True)
add("new_zealand_lamprey", "Piharau / New Zealand Lamprey", "澳新七鳃鳗", "Geotria australis", "rare", (30, 75), 40, "new_zealand_south_island", ["nz_native", "migratory", "jawless"], "This jawless migratory fish returns from the sea to freshwater to spawn.", "这种无颌洄游鱼从海洋返回淡水繁殖。", "A round oral disc replaces jaws; seven gill openings appear behind each eye.", "圆形口吸盘取代上下颌，每只眼后有七个鳃孔。", "nationally_vulnerable", "native", True)
add("chinook_salmon_nz", "Chinook Salmon", "帝王鲑", "Oncorhynchus tshawytscha", "uncommon", (40, 130), 42, "new_zealand_south_island", ["coldwater", "migratory", "introduced"], "Introduced Chinook established sea-run and landlocked populations in parts of South Island waterways.", "引入帝王鲑在南岛部分水域建立了降海型与陆封种群。", "Black spots cover both tail lobes and the gums inside the lower jaw are black.", "尾鳍上下叶均有黑斑，下颌内侧牙龈黑色。", origin="introduced")

# Chesapeake Bay.
add("striped_bass", "Striped Bass", "条纹鲈", "Morone saxatilis", "uncommon", (30, 150), 40, "chesapeake_bay", ["estuary", "migratory", "schooling"], "Striped bass migrate between ocean, bay, and spawning rivers.", "条纹鲈在海洋、海湾与繁殖河流之间洄游。", "Seven or eight dark horizontal stripes run along a silver body.", "银色身体有七至八条深色横纹。", "regulated", release=True)
add("bluefish", "Bluefish", "扁鲹蓝鱼", "Pomatomus saltatrix", "common", (25, 100), 26, "chesapeake_bay", ["estuary", "pelagic", "schooling", "predator"], "Fast bluefish schools follow small prey into coastal bays.", "快速蓝鱼鱼群追随小型猎物进入沿岸海湾。", "A powerful jaw with triangular teeth, blue-green back, and forked tail are distinctive.", "强壮颌部配三角牙、蓝绿背和叉尾。")
add("atlantic_croaker", "Atlantic Croaker", "大西洋黄姑鱼", "Micropogonias undulatus", "common", (15, 55), 16, "chesapeake_bay", ["estuary", "bottom", "sound_producer"], "Croaker use muscles against the swim bladder to produce courtship and disturbance sounds.", "大西洋黄姑鱼用肌肉振动鳔发出求偶与受扰声音。", "Small chin barbels and oblique wavy bars mark the bronze-silver body.", "下颌小触须与斜向波纹标记铜银身体。")
add("spot", "Spot", "黄尾短须石首鱼", "Leiostomus xanthurus", "common", (10, 35), 11, "chesapeake_bay", ["estuary", "bottom", "schooling"], "Spot are abundant small estuarine fish transferring benthic production to larger predators.", "Spot是数量丰富的小型河口鱼，把底栖生产传递给更大捕食者。", "A single black shoulder spot and yellowish tail identify this small drum.", "单个黑色肩斑与偏黄尾鳍。")
add("summer_flounder", "Summer Flounder", "夏鲆", "Paralichthys dentatus", "uncommon", (25, 95), 32, "chesapeake_bay", ["estuary", "bottom", "ambush"], "Juveniles use marsh creeks, seagrass, mud flats, and open bays before seasonal offshore movement.", "幼鱼利用盐沼潮沟、海草、泥滩与开阔海湾，之后季节性向外海移动。", "Both eyes lie on the left; five prominent ocellated spots appear on the eyed side.", "双眼在左侧，有眼侧通常有五个醒目眼状斑。")
add("black_drum", "Black Drum", "黑鼓鱼", "Pogonias cromis", "uncommon", (30, 160), 38, "chesapeake_bay", ["estuary", "bottom", "shell_crusher"], "Black drum use throat teeth to crush oysters and other hard prey.", "黑鼓鱼用咽齿压碎牡蛎等硬壳猎物。", "Numerous chin barbels mark adults; juveniles have dark vertical bars.", "成鱼下颌有许多触须，幼鱼体侧有深色竖纹。")
add("weakfish", "Weakfish", "弱鱼", "Cynoscion regalis", "uncommon", (25, 90), 28, "chesapeake_bay", ["estuary", "migratory", "predator"], "Weakfish move seasonally through Mid-Atlantic estuaries with temperature and prey.", "弱鱼随温度和猎物季节性进出中大西洋河口。", "Small dark spots form diagonal rows on a bronze back; the mouth has canine teeth.", "铜色背部有斜列小黑斑，口中具犬齿。")
add("tautog", "Tautog", "美洲隆头鱼", "Tautoga onitis", "uncommon", (25, 90), 30, "chesapeake_bay", ["estuary", "structure", "shell_crusher"], "Tautog remain close to oyster, rock, and wreck structure while crushing hard prey.", "美洲隆头鱼贴近牡蛎礁、岩石和沉船结构并压碎硬壳猎物。", "Thick lips, stout front teeth, and a mottled dark body are characteristic.", "厚唇、粗壮前牙与深色斑驳身体。")
add("oyster_toadfish", "Oyster Toadfish", "蚝蟾鱼", "Opsanus tau", "common", (15, 45), 12, "chesapeake_bay", ["estuary", "structure", "ambush", "sound_producer"], "Oyster toadfish shelter in reef and debris cavities and males produce boat-whistle calls.", "蚝蟾鱼躲在礁体与碎屑洞穴中，雄鱼能发出船笛般叫声。", "A broad flattened head, fleshy flaps, and large mouth create a toad-like profile.", "宽扁头、肉质突起和大口形成蟾蜍般外形。")
add("black_sea_bass", "Black Sea Bass", "黑海鲈", "Centropristis striata", "uncommon", (20, 65), 27, "chesapeake_bay", ["estuary", "reef", "structure"], "Black sea bass use reefs, wrecks, and structured bottom and can change sex during life.", "黑海鲈利用礁石、沉船与复杂底质，并可在一生中发生性别转换。", "A dark body carries pale spots and a blue-edged dorsal fin; large males develop a nuchal hump.", "深色身体有浅斑与蓝缘背鳍，大型雄鱼出现颈背隆起。")

# Monterey Bay kelp forest and adjacent sand/reef habitat.
add("california_halibut", "California Halibut", "加州牙鲆", "Paralichthys californicus", "uncommon", (30, 150), 42, "monterey_kelp_forest", ["california_current", "bottom", "ambush"], "California halibut bury in sand beside bays, eelgrass, and kelp edges to ambush prey.", "加州牙鲆埋伏在海湾、鳗草和海藻林边缘沙底捕食。", "Most have both eyes on the left, but some are right-eyed; a large toothed mouth is diagnostic.", "多数双眼在左侧但也有右眼型，大而具牙的嘴是关键。")
add("lingcod", "Lingcod", "长蛇齿单线鱼", "Ophiodon elongatus", "uncommon", (35, 150), 38, "monterey_kelp_forest", ["california_current", "rocky", "predator"], "Lingcod hold near rocky reefs and kelp structure; males guard egg masses.", "长蛇齿单线鱼守在岩礁和海藻结构附近，雄鱼会守护卵块。", "A huge toothed mouth and elongated mottled body distinguish it from true cod.", "巨大齿口与修长斑驳身体可区别于真正鳕鱼。")
add("cabezon", "Cabezon", "花斑杜父鱼", "Scorpaenichthys marmoratus", "common", (20, 100), 28, "monterey_kelp_forest", ["california_current", "rocky", "kelp", "bottom"], "Cabezon attach adhesive egg masses to reef or macroalgae and remain close to structure.", "花斑杜父鱼把黏性卵块附着在礁石或大型藻类上，并贴近结构活动。", "Broad cirri above the eyes and a scaleless mottled body with a huge head are distinctive.", "眼上有宽大皮瓣，无鳞斑驳身体配巨大头部。")
add("blue_rockfish", "Blue Rockfish", "蓝岩鱼", "Sebastes mystinus", "common", (15, 55), 20, "monterey_kelp_forest", ["california_current", "kelp", "rocky", "schooling"], "Blue rockfish often school in the midwater of kelp forests and rocky reefs.", "蓝岩鱼常在海藻林和岩礁中层水域群游。", "A blue-gray body has dark vertical bars and a small mouth without the vermilion rockfish's red color.", "蓝灰身体有深色竖纹，小口且不具朱红岩鱼的红色。")
add("vermilion_rockfish", "Vermilion Rockfish", "朱红岩鱼", "Sebastes miniatus", "uncommon", (25, 75), 34, "monterey_kelp_forest", ["california_current", "rocky", "deep"], "Vermilion rockfish occupy rocky habitat and are vulnerable to barotrauma when brought rapidly from depth.", "朱红岩鱼生活在岩质深水，快速拉离深处时易受气压伤。", "Bright red-orange color with gray mottling and a deeply notched dorsal fin are useful clues.", "鲜红橙体色配灰斑与深缺刻背鳍。", "regulated", release=True)
add("white_seabass", "White Seabass", "白犬牙石首鱼", "Atractoscion nobilis", "uncommon", (40, 150), 45, "monterey_kelp_forest", ["california_current", "kelp", "migratory", "predator"], "White seabass move along the coast and feed around kelp, reef, and schooling prey.", "白犬牙石首鱼沿岸移动，在海藻、礁石和群游猎物附近觅食。", "A raised ridge runs along the belly and the body lacks the horizontal stripes of striped bass.", "腹部有明显棱脊，身体没有条纹鲈的横纹。")
add("leopard_shark", "Leopard Shark", "豹纹鲨", "Triakis semifasciata", "uncommon", (40, 180), 38, "monterey_kelp_forest", ["california_current", "bottom", "estuary"], "Leopard sharks use shallow bays and sandy reef edges and give birth to live young.", "豹纹鲨利用浅湾和礁石沙地边缘，并产下活体幼鲨。", "Dark saddles and spots form a leopard pattern across a slender gray body.", "深色鞍斑与斑点在细长灰体上组成豹纹。", "regulated", release=True)
add("california_sheephead", "California Sheephead", "加州羊头鱼", "Bodianus pulcher", "uncommon", (20, 90), 35, "monterey_kelp_forest", ["california_current", "kelp", "shell_crusher"], "This wrasse changes sex; large terminal-phase males develop black head and tail with a red middle.", "这种隆头鱼会性别转换，大型终末期雄鱼黑头黑尾、中段红色。", "Adult males are tricolored with a prominent forehead; females are uniformly pink-red.", "成雄三色且额部隆起，雌鱼整体粉红。")
add("kelp_greenling", "Kelp Greenling", "花斑六线鱼", "Hexagrammos decagrammus", "common", (20, 60), 22, "monterey_kelp_forest", ["california_current", "kelp", "rocky"], "Kelp greenling occupy rocky kelp habitat and show strong sex-related color differences.", "花斑六线鱼利用岩质海藻生境，雌雄体色差异明显。", "Five lateral lines characterize greenlings; males show blue spots while females carry reddish spots.", "六线鱼类具多条侧线，雄鱼有蓝斑、雌鱼有红褐斑。")
add("giant_sea_bass", "Giant Sea Bass", "巨坚鳞鲈", "Stereolepis gigas", "rare", (80, 250), 95, "monterey_kelp_forest", ["california_current", "kelp", "reef", "predator"], "A very large slow-growing reef predator is protected and should only be observed at distance.", "这种巨大、缓慢生长的礁区捕食者受到保护，只应远距离观察。", "Adults are massive and dark with pale spots; juveniles are orange with black spots.", "成鱼巨大深色配浅斑，幼鱼橙色配黑斑。", "protected", release=True)


def quiz(fish_id, question_en, question_zh, choices_en, choices_zh, answer, explanation_en, explanation_zh, wrong_en, wrong_zh):
    FISH[fish_id]["quiz"] = {"question_en": question_en, "question_zh": question_zh,
        "choices_en": choices_en, "choices_zh": choices_zh, "answer": answer,
        "explanation_en": explanation_en, "explanation_zh": explanation_zh,
        "wrong_en": wrong_en, "wrong_zh": wrong_zh}


quiz("hardhead_catfish", "Which feature best separates hardhead from gafftopsail catfish?", "怎样可靠区分硬头海鲶和帆鳍海鲶？",
    ["Hardhead has long ribbon-like dorsal and pectoral rays", "Hardhead lacks the long fin streamers and has more chin barbels", "Body color alone"],
    ["硬头海鲶有很长的丝状背鳍和胸鳍", "硬头海鲶没有长鳍丝，且下颌触须更多", "只看体色"], 2,
    "Correct. Fin streamers and barbel arrangement are more stable than color.", "正确。鳍丝与触须排列比体色更稳定。", "Recheck the fin rays and chin barbels rather than color.", "请重新检查鳍条与下颌触须，不要只看颜色。")
quiz("saithe", "What field mark separates saithe from pollack?", "青鳕和绿青鳕最实用的区别是什么？",
    ["Saithe has a nearly straight pale lateral line", "Saithe always has red fins", "Pollack has no tail"],
    ["青鳕的浅色侧线近乎笔直", "青鳕总有红鳍", "绿青鳕没有尾鳍"], 1,
    "Correct. Pollack's lateral line curves strongly above the pectoral fin.", "正确。绿青鳕侧线在胸鳍上方明显弯曲。", "Use lateral-line shape, not invented color or fin rules.", "应看侧线形状，不要使用虚构的颜色或鱼鳍规则。")
quiz("northern_pike", "How should pike and muskellunge be separated in the field?", "野外如何区分白斑狗鱼和大狗鱼？",
    ["Pike usually has pale spots on a darker body; muskie often has dark marks on a paler body", "Every long fish is a pike", "Only by weight"],
    ["白斑狗鱼常为深底浅斑，大狗鱼多为浅底深纹", "所有长鱼都是白斑狗鱼", "只看重量"], 1,
    "Correct. Pattern direction plus jaw pores is stronger evidence than size alone.", "正确。斑纹底色关系配合下颌感觉孔，比体型更可靠。", "Length overlaps; inspect pattern direction and jaw pores.", "两者体长重叠，应检查斑纹底色关系与下颌感觉孔。")
quiz("longfin_eel", "What is the strongest longfin-versus-shortfin eel clue?", "长鳍鳗与短鳍鳗最可靠的区别是什么？",
    ["Longfin dorsal fin begins much farther forward than the anal fin", "Longfin is always exactly two metres", "Shortfin has no dorsal fin"],
    ["长鳍鳗背鳍起点远早于臀鳍", "长鳍鳗总是正好两米", "短鳍鳗没有背鳍"], 1,
    "Correct. Fin origin and skin wrinkling outperform size and color alone.", "正确。鳍起点与皮肤皱褶比单看体型和颜色更可靠。", "Size and color vary; compare dorsal and anal fin origins.", "体型和颜色会变化，请比较背鳍与臀鳍起点。")
quiz("atlantic_cod", "Which combination separates Atlantic cod from haddock?", "大西洋鳕和黑线鳕如何组合辨认？",
    ["Cod has a pale lateral line and lacks haddock's black shoulder blotch", "Cod has no chin barbel", "Haddock has one dorsal fin"],
    ["大西洋鳕侧线较浅，且没有黑线鳕的黑色肩斑", "大西洋鳕没有下颌触须", "黑线鳕只有一枚背鳍"], 1,
    "Correct. Both are gadoids, so use lateral-line color and the haddock shoulder mark.", "正确。两者都属鳕科，应看侧线颜色和黑线鳕肩斑。", "Both have multiple dorsal fins and a barbel; inspect the shoulder blotch.", "两者都有多枚背鳍和触须，请检查肩斑。")
quiz("red_drum", "What separates red drum from juvenile black drum?", "红鼓鱼与幼年黑鼓鱼如何区分？",
    ["Red drum has tail-base spot(s); juvenile black drum has vertical bars and chin barbels", "Only red drum makes sound", "Black drum has no fins"],
    ["红鼓鱼尾基有黑斑；幼黑鼓鱼有竖纹和下颌触须", "只有红鼓鱼会发声", "黑鼓鱼没有鳍"], 1,
    "Correct. Tail spots versus bars and barbels provide a useful combination.", "正确。尾基斑与竖纹、触须的组合很实用。", "Both are drums; use tail spots, vertical bars, and chin barbels.", "两者都属石首鱼，应结合尾基斑、竖纹和下颌触须。")
quiz("summer_flounder", "Which side carries both eyes in summer flounder?", "夏鲆的双眼位于哪一侧？",
    ["Usually the left side, with five prominent ocellated spots", "Always one eye on each side", "The side changes every season"],
    ["通常在左侧，并有五个醒目眼状斑", "永远一侧一只眼", "每个季节换一侧"], 1,
    "Correct. Eye side and ocellated spot pattern are useful flatfish clues.", "正确。眼侧与眼状斑组合是实用鲽鱼特征。", "Flatfish eye migration is developmental, not seasonal.", "鲽鱼眼睛迁移发生在发育期，并非季节性换侧。")
quiz("california_halibut", "Why can eye side alone fail for California halibut?", "为什么只看眼侧可能误判加州牙鲆？",
    ["Most are left-eyed but a minority are right-eyed", "It has no eyes", "Both eyes migrate daily"],
    ["多数为左眼型，但少数个体为右眼型", "它没有眼睛", "双眼每天迁移"], 1,
    "Correct. Combine eye side with the large toothed mouth and local morphology.", "正确。还应结合大齿口和当地形态特征。", "Eye side is variable in this species; use multiple characters.", "本种眼侧存在变异，应组合多个特征。")


CONDITIONS = {}
EPISODES = {}
JUNK = {}
WILDLIFE = {}
RELATIONSHIPS = []

for lid, loc in LOCATIONS.items():
    CONDITIONS[lid] = [
        {"name_zh": "结构边缘活跃", "name_en": "Active habitat edge", "fact_zh": "不同底质或水团交界提高生境异质性，但不保证咬口。", "fact_en": "A boundary between substrates or water masses increases habitat variety without guaranteeing a bite.", "tag_weight_mult": {next(iter(loc["tag_weight_mult"])): 1.2}},
        {"name_zh": "水体混合阶段", "name_en": "Mixed-water phase", "fact_zh": "风、流量或潮汐正在重新分配温度、氧气与漂流食物。", "fact_en": "Wind, flow, or tide is redistributing temperature, oxygen, and drifting food.", "tag_weight_mult": {}}]
    EPISODES[lid] = [
        {"id": lid + "_productive", "name_zh": "生产力脉冲", "name_en": "Productivity pulse", "fact_zh": "食物供应短期增加会沿食物网传递，但各物种响应并不同步。", "fact_en": "A short food-supply increase propagates through the web, but species do not respond in lockstep.", "tag_weight_mult": {next(iter(loc["tag_weight_mult"])): 1.25}, "wildlife_mult": 1.15},
        {"id": lid + "_stress", "name_zh": "生境压力阶段", "name_en": "Habitat stress episode", "fact_zh": "温度、流量或浪况偏离常态，空杆增加也是有效证据。", "fact_en": "Temperature, flow, or sea state departs from usual conditions, making more empty casts valid evidence.", "tag_weight_mult": {}, "empty_mult": 1.25}]
    JUNK[lid] = ["一段废弃鱼线", "一块水磨天然材料", "一只旧拟饵", "一片当地植物碎屑"]
    WILDLIFE[lid + "_indicator"] = {"id": lid + "_indicator", "name_en": "Local Indicator Wildlife", "name_zh": "当地指示生物", "group": "field_sign", "locations": [lid], "seasons": ALL, "fact_en": "A non-fish observation adds evidence about habitat use beyond the catch record.", "fact_zh": "非鱼类观察为渔获记录之外的生境利用提供证据。", "status": "observe_only"}

for lid in LOCATIONS:
    local_fish = [f["id"] for f in FISH.values() if lid in f["locations"]]
    RELATIONSHIPS.append({"id": lid + "_community", "location_id": lid, "type": "community_structure",
        "requires": local_fish[:2], "min_count": 2,
        "title_zh": LOCATIONS[lid]["name_zh"] + "群落线索", "title_en": LOCATIONS[lid]["name_en"] + " community clue",
        "fact_zh": "两个重复观察的物种共享同一水域，却可能利用不同水层、底质或食物；地点名并不是生态位。",
        "fact_en": "Two repeatedly observed species share a waterbody while using different depth, substrate, or food; a place name is not an ecological niche."})
