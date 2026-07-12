"""Regression tests for the real-world field-journal content and rules."""
import os
import json
import tempfile
import unittest

import engine


class RealWorldDataTests(unittest.TestCase):
    def setUp(self):
        engine._SAVE = os.path.join(tempfile.mkdtemp(), "save.json")
        engine.S = None
        engine._IO_WARN = ""
        engine.new_game(20260711)

    def test_world_has_three_distinct_expansion_regions(self):
        required = {"amazon_flooded_forest", "baikal_littoral", "mekong_mainstem"}
        self.assertTrue(required.issubset(engine.LOCATIONS))
        for location_id in required:
            self.assertTrue(any(location_id in fish["locations"] for fish in engine.FISH.values()))

    def test_every_species_has_canonical_science_fields(self):
        for fish_id, fish in engine.FISH.items():
            with self.subTest(fish=fish_id):
                self.assertTrue(fish["name_en"])
                self.assertTrue(fish["name_zh"])
                self.assertRegex(fish["latin"], r"^[A-Z][a-z]+ ")
                self.assertTrue(fish["science_fact_en"])
                self.assertTrue(fish["science_fact_zh"])
                self.assertTrue(fish["identification_en"])
                self.assertTrue(fish["identification_zh"])
                self.assertIn(fish["rarity"], engine.RARITY)
                self.assertTrue(set(fish["locations"]).issubset(engine.LOCATIONS))
                self.assertTrue(set(fish["seasons"]).issubset(engine.SEASONS))

    def test_ecology_relationships_reference_real_species_and_places(self):
        for relationship in engine.RELATIONSHIPS:
            with self.subTest(relationship=relationship["id"]):
                self.assertIn(relationship["location_id"], engine.LOCATIONS)
                self.assertTrue(set(relationship["requires"]).issubset(engine.FISH))
                self.assertTrue(relationship["fact_zh"])

    def test_wildlife_records_reference_real_places(self):
        for wildlife_id, record in engine.WILDLIFE.items():
            with self.subTest(wildlife=wildlife_id):
                self.assertTrue(set(record["locations"]).issubset(engine.LOCATIONS))
                self.assertTrue(set(record["seasons"]).issubset(engine.SEASONS))
                self.assertTrue(record["fact_en"])
                self.assertTrue(record["fact_zh"])

    def test_every_location_has_junk_and_conditions(self):
        for location_id in engine.LOCATIONS:
            with self.subTest(location=location_id):
                self.assertGreaterEqual(len(engine._REAL_WORLD_JUNK[location_id]), 4)
                self.assertGreaterEqual(len(engine._REAL_WORLD_CONDITIONS[location_id]), 2)

    def test_release_only_species_never_enters_creel(self):
        protected = engine.FISH["mekong_giant_catfish"]
        instance, first, _ = engine._record_catch(protected, 210.0, 100)
        self.assertTrue(first)
        self.assertTrue(instance.startswith("obs_"))
        self.assertEqual(engine.S["catch_inventory"], [])
        self.assertEqual(engine.S["stats"]["released"], 1)

    def test_identification_error_is_recorded_then_corrected(self):
        fish = engine.FISH["rainbow_trout"]
        engine._record_catch(fish, 40.0, 20)
        engine._c_identify(fish["id"], 2)
        entry = engine.S["encyclopedia"][fish["id"]]
        self.assertEqual(entry["identification"], "pending")
        self.assertEqual(entry["misidentifications"], 1)
        engine._c_identify(fish["id"], 1)
        self.assertEqual(entry["identification"], "verified")

    def test_conditions_are_deterministic_and_rng_free(self):
        before = engine.S["rngCalls"]
        first = engine._current_condition()
        second = engine._current_condition()
        self.assertEqual(first, second)
        self.assertEqual(engine.S["rngCalls"], before)
        time_first = engine._current_time()
        time_second = engine._current_time()
        self.assertEqual(time_first, time_second)
        self.assertEqual(engine.S["rngCalls"], before)

    def test_day_cycle_advances_every_two_actions(self):
        engine.S["turn"] = 0
        self.assertEqual(engine._current_time()["id"], "dawn")
        engine.S["turn"] = 2
        self.assertEqual(engine._current_time()["id"], "day")
        engine.S["turn"] = 4
        self.assertEqual(engine._current_time()["id"], "dusk")
        engine.S["turn"] = 6
        self.assertEqual(engine._current_time()["id"], "night")
        engine.S["turn"] = 8
        self.assertEqual(engine._current_time()["id"], "dawn")

    def test_repeated_observation_unlocks_ecology_relationship(self):
        fish = engine.FISH["tambaqui"]
        self.assertNotIn("森林结果，鱼群进食", engine._c_ecosystem())
        for size in (40.0, 42.0, 44.0):
            engine._record_catch(fish, size, 20)
        entry = engine.S["encyclopedia"][fish["id"]]
        self.assertEqual(engine._observation_level(entry)[0], "深入观察")
        ecosystem = engine._c_ecosystem()
        self.assertIn("森林结果，鱼群进食", ecosystem)
        self.assertIn("Forest fruit becomes fish food", ecosystem)

    def test_nonfish_find_is_persisted_in_field_journal(self):
        location_id = engine.S["location_id"]
        found = engine._REAL_WORLD_JUNK[location_id][0]
        key = "%s|%s" % (location_id, found)
        engine.S["field_observations"][key] = {
            "location_id": location_id, "name": found, "count": 2, "human_debris": False}
        journal = engine._c_journal()
        self.assertIn("[非鱼类发现]", journal)
        self.assertIn(found, journal)
        self.assertIn("×2", journal)

    def test_wildlife_outcome_is_observation_not_inventory(self):
        class FixedRng:
            def __init__(self):
                self.values = iter((0.5, 0.01, 0.0))
            def random(self):
                return next(self.values)
            def rint(self, low, high):
                return low + int(self.random() * (high - low + 1))
        before = len(engine.S["catch_inventory"])
        result = engine._cast_step(FixedRng(), "earthworm")
        self.assertEqual(result["kind"], "wildlife")
        self.assertIn("只记录，不接近、不投喂、不捕捉", result["text"])
        self.assertEqual(len(engine.S["catch_inventory"]), before)
        self.assertEqual(engine.S["stats"]["wildlife_observations"], 1)
        self.assertTrue(any(key.startswith("wildlife|") for key in engine.S["field_observations"]))

    def test_public_command_surface_smoke(self):
        commands = ["help", "status", "conditions", "shop", "goto", "inventory",
                    "encyclopedia", "journal", "ecosystem", "look colorado_headwaters",
                    "buy earthworm 1", "cast 3", "sell all"]
        for command in commands:
            with self.subTest(command=command):
                output = engine.cmd(command)
                self.assertIn("📊 ", output)
                self.assertNotIn("Traceback", output)

    def test_seed_and_command_sequence_are_reproducible(self):
        def replay():
            engine._SAVE = os.path.join(tempfile.mkdtemp(), "save.json")
            engine.S = None
            engine._IO_WARN = ""
            transcript = [engine.new_game(424242)]
            transcript.extend(engine.cmd(command) for command in (
                "conditions", "cast 6", "journal", "inventory", "sell all", "status"))
            return transcript
        self.assertEqual(replay(), replay())

    def test_fantasy_save_is_archived_without_stale_ids(self):
        legacy = engine._new_state(5)
        legacy["location_id"] = "moonlit_pond"
        legacy["unlocked_locations"] = ["moonlit_pond", "reed_river"]
        legacy["bait_inventory"] = {"basic_worm": 3}
        legacy["encyclopedia"] = {"mud_carp": {"count": 1, "max_size": 20}}
        legacy["catch_inventory"] = [{"instance_id": "c_001", "fish_id": "mud_carp", "size": 20, "value": 5}]
        engine.S = None
        with open(engine._SAVE, "w", encoding="utf-8") as f:
            json.dump(legacy, f)
        loaded = engine._load()
        self.assertEqual(loaded["location_id"], "colorado_headwaters")
        self.assertEqual(loaded["bait_inventory"], {"earthworm": 8})
        self.assertEqual(loaded["encyclopedia"], {})
        self.assertEqual(loaded["catch_inventory"], [])
        self.assertEqual(loaded["legacy_archive_count"], 5)
        self.assertIn("Archived 5", engine.cmd("status"))


if __name__ == "__main__":
    unittest.main()
