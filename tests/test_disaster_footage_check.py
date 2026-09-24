"""Disaster footage coupling check (companion to GlyphAI dispatch GLYPH-C1).

Fixtures F1-F6 are implementation-authored REGRESSION checks on the scorer,
not validation of the checklist against any footage. Accuracy is UNMEASURED.

Run: python -m unittest discover -s tests -v   (standard library only)
"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import disaster_footage_check as dfc


def all_yes(event, **overrides):
    answers = {cue_id: dfc.ANSWER_YES for cue_id, _, _, _ in dfc.questions(event)}
    answers.update(overrides)
    return answers


class Fixtures(unittest.TestCase):
    def test_f1_flood_birds_calm_v_before_water_is_broken(self):
        result = dfc.evaluate("flood", all_yes("flood", **{"C-BIRD-1": "no"}))
        self.assertEqual(result["verdict"], dfc.COUPLING_BROKEN)
        self.assertEqual(result["cues"], ["C-BIRD-1"])

    def test_f2_flood_birds_flush_rest_ok_is_consistent(self):
        result = dfc.evaluate("flood", all_yes("flood"))
        self.assertEqual(result["verdict"], dfc.COUPLING_CONSISTENT)
        self.assertEqual(result["cues"], [])

    def test_f3_all_cannot_see_is_not_evaluable(self):
        answers = {cue_id: dfc.ANSWER_CANNOT_SEE for cue_id, _, _, _ in dfc.questions("flood")}
        result = dfc.evaluate("flood", answers)
        self.assertEqual(result["verdict"], dfc.NOT_EVALUABLE)
        self.assertEqual(result["reason"], dfc.REASON_TOO_FEW_VISIBLE)

    def test_f4_object_unflips_is_broken_on_c_obj_1(self):
        result = dfc.evaluate("earthquake", all_yes("earthquake", **{"C-OBJ-1": "no"}))
        self.assertEqual(result["verdict"], dfc.COUPLING_BROKEN)
        self.assertEqual(result["cues"], ["C-OBJ-1"])

    def test_f5_unknown_event_type_is_not_evaluable(self):
        result = dfc.evaluate("meteor", {})
        self.assertEqual(result["verdict"], dfc.NOT_EVALUABLE)
        self.assertEqual(result["reason"], dfc.REASON_EVENT_TYPE)

    def test_f6_share_before_they_delete_it_is_a_time_attack(self):
        flags = dfc.share_urgency_check("Nepal floods!! Share before they delete it")
        self.assertTrue(flags)
        self.assertEqual(flags[0]["type"], "FAKE_URGENCY")
        self.assertIn("TIME_ATTACK", flags[0]["mechanism"])


class AnswerSemantics(unittest.TestCase):
    def test_cannot_see_never_counts_against_the_clip(self):
        answers = all_yes("flood", **{"C-BIRD-1": "cannot_see", "C-ANIMAL-1": "cannot_see"})
        result = dfc.evaluate("flood", answers)
        self.assertEqual(result["verdict"], dfc.COUPLING_CONSISTENT)
        self.assertEqual(result["cannot_see"], 2)

    def test_one_answer_is_below_the_placeholder_minimum(self):
        result = dfc.evaluate("flood", {"C-BIRD-1": "yes"})
        self.assertEqual(result["verdict"], dfc.NOT_EVALUABLE)

    def test_single_contradiction_is_still_broken(self):
        result = dfc.evaluate("flood", {"C-BIRD-1": "no"})
        self.assertEqual(result["verdict"], dfc.COUPLING_BROKEN)

    def test_unknown_answer_and_foreign_cue_raise(self):
        with self.assertRaises(ValueError):
            dfc.evaluate("flood", {"C-BIRD-1": "maybe"})
        with self.assertRaises(ValueError):
            dfc.evaluate("flood", {"C-FIRE-1": "no"})


class OutputContract(unittest.TestCase):
    def test_no_real_fake_or_percentage_in_any_render(self):
        for event in dfc.event_types():
            for answers in (all_yes(event), {}, all_yes(event, **{"C-OBJ-1": "no"})):
                text = dfc.render(dfc.evaluate(event, answers, text="share now"))
                self.assertIsNone(re.search(r"\b(REAL|FAKE)\b", text), text)
                self.assertNotIn("%", text)

    def test_provenance_and_scope_ride_every_result(self):
        for result in (dfc.evaluate("flood", all_yes("flood")), dfc.evaluate("nope", {})):
            self.assertEqual(result["provenance_steps"], dfc.PROVENANCE_STEPS)
            self.assertEqual(result["scope_limits"], dfc.SCOPE_LIMITS)
            self.assertIn("UNMEASURED", dfc.render(result))


class ShareUrgency(unittest.TestCase):
    def test_word_boundary_not_substring(self):
        self.assertEqual(dfc.share_urgency_check("The hurrying river"), [])
        self.assertTrue(dfc.share_urgency_check("Hurry, share now"))

    def test_plain_and_empty_text_give_no_flags(self):
        self.assertEqual(dfc.share_urgency_check("Footage from the river this morning."), [])
        self.assertEqual(dfc.share_urgency_check(""), [])
        self.assertEqual(dfc.share_urgency_check(None), [])

    def test_flag_shape(self):
        flag = dfc.share_urgency_check("they're hiding this")[0]
        self.assertEqual(set(flag), {"type", "severity", "evidence", "mechanism"})
        self.assertIsInstance(flag["severity"], float)


class CueSet(unittest.TestCase):
    def test_every_row_carries_status_source_and_mechanism_status(self):
        for row in dfc.load_cues()["cues"]:
            self.assertIn(row["status"], dfc.STATUSES, row["id"])
            self.assertTrue(row["source"], row["id"])
            self.assertIn(row["mechanism"]["status"], dfc.STATUSES, row["id"])

    def test_every_event_type_has_enough_cues(self):
        data = dfc.load_cues()
        for event in data["event_types"]:
            self.assertGreaterEqual(len(dfc.cues_for(event, data)), dfc.MIN_ANSWERED_CUES, event)

    def test_validate_refuses_missing_status(self):
        data = dfc.load_cues()
        del data["cues"][0]["status"]
        with self.assertRaises(ValueError):
            dfc.validate_cues(data)

    def test_cue_set_matches_the_pinned_glyphai_copy(self):
        """A drift here means one copy moved and the other did not. Re-pin
        CUE_SET_SOURCE after copying the GlyphAI file, or copy this one back."""
        drift = dfc.cue_set_drift()
        self.assertTrue(drift["matches"], drift)


class PipelineHook(unittest.TestCase):
    def test_pipeline_source_calls_share_urgency_check(self):
        """The pipeline needs nltk/langdetect, absent here; check the wiring by source."""
        import ast
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "transcript_nlp_pipeline.py")
        with open(path, encoding="utf-8") as handle:
            tree = ast.parse(handle.read())
        calls = [n.func.id for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        self.assertIn("share_urgency_check", calls)


if __name__ == "__main__":
    unittest.main()
