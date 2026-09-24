"""Coupling check for disaster footage: a guided checklist, not a classifier.

Companion to GlyphAI's coupling_check.py (dispatch GLYPH-C1), applied where
YouTube Wisdom Lens sits: a video's title, description and transcript. It
does not look at pixels, calls no model, and touches no network. The viewer
watches the clip and answers a short set of questions about whether the
scene's LAYERS react to each other; the code counts the answers. The output
helps the viewer decide and never labels a clip REAL or FAKE.

PRINCIPLE
    Real events are COUPLED: every layer shares the same air and ground.
    Surge, quake or blast produce ground vibration and infrasound; animals
    and birds react FIRST, trees are driven from the base, people turn toward
    what they feel, shadows share one light. Generated scenes are often
    assembled from UNCOUPLED layers, each rendered from its own prototype
    (birds = a calm V formation) that never "hears" the event. A missing
    reaction BETWEEN layers is the durable tell; pixel artifacts get fixed
    first as generators improve.

CUE SET
    coupling_cues.json is a COPY of GlyphAI's file, pinned by sha256 in
    CUE_SET_SOURCE below. The two repositories cannot import each other, so a
    copy is the only form available; the pin is what makes drift visible.
    Every cue carries a status (OBSERVED | SECONDARY | DERIVED | PROPOSED), a
    source, and a mechanism column with its own status. Literature sources
    are carried from the dispatch and were not read here.

WHERE THIS DIFFERS FROM GLYPHAI
    GlyphAI runs the caption through its ManipulationDetector, a substring
    matcher. This repository has no such detector and its convention is
    word-boundary regex (sensitivity_check.py), so share_urgency_check() is a
    word-boundary scan over SHARE_URGENCY_PHRASES. Same mechanism tag
    (TIME_ATTACK: compresses deliberation below the cost of deciding), a
    different matcher. Neither has been rated against the other.

SCOPE
    Accuracy of the checklist is UNMEASURED. MIN_ANSWERED_CUES is a
    PLACEHOLDER. Fixtures in tests/ are implementation-authored regression
    checks, not validation.
"""

import hashlib
import json
import os
import re

DEFAULT_CUES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "coupling_cues.json")

# The file this cue set was copied from. Recompute with:
#   sha256sum coupling_cues.json
CUE_SET_SOURCE = {
    "repo": "JinnZ2/GlyphAI",
    "path": "coupling_cues.json",
    "sha256": "dafee87b746bf1b134780ddc23a4aff4011b741b6c7d9ce48d29551914f6c647",
}

COUPLING_BROKEN = "COUPLING_BROKEN"
COUPLING_CONSISTENT = "COUPLING_CONSISTENT"
NOT_EVALUABLE = "NOT_EVALUABLE"
VERDICTS = (COUPLING_BROKEN, COUPLING_CONSISTENT, NOT_EVALUABLE)

ANSWER_YES = "yes"
ANSWER_NO = "no"
ANSWER_CANNOT_SEE = "cannot_see"
ANSWERS = (ANSWER_YES, ANSWER_NO, ANSWER_CANNOT_SEE)

STATUSES = ("OBSERVED", "SECONDARY", "DERIVED", "PROPOSED")
TIMINGS = ("before", "during", "after")

# PLACEHOLDER: answered (yes/no) cues needed before COUPLING_CONSISTENT.
MIN_ANSWERED_CUES = 2

REASON_EVENT_TYPE = "event_type"
REASON_TOO_FEW_VISIBLE = "too_few_visible_layers"

# Share-step urgency in a title, description or transcript. Word-boundary
# regex, case-insensitive, per this repository's matching convention.
SHARE_URGENCY_PHRASES = [
    "share now", "share before", "share this before", "before they delete",
    "before it gets deleted", "before it's deleted", "before its deleted",
    "they're hiding this", "they are hiding this", "they don't want you to see",
    "they dont want you to see", "spread this", "share immediately",
    "share asap", "must share", "everyone needs to see this", "act now",
    "hurry", "limited time",
]

PROVENANCE_STEPS = [
    "1. Who posted it first? Find the earliest upload, not the loudest.",
    "2. Reverse-search a frame (screenshot one clear frame; search it).",
    "3. Check the date and place against the event: was there a flood / quake / fire there, then?",
    "4. Look for a published fact-check on this clip.",
    "5. Run a watermark / provenance check where a tool is available (C2PA, platform labels).",
]

SCOPE_LIMITS = [
    "Absence is not proof: real footage can lack animals (none present, frame too tight, audio stripped).",
    "Coupling cues depend on the viewer having seen real events; this checklist is a translation of a field baseline, not a replacement for one.",
    "Recycled real footage (wrong place, wrong date) passes every coupling check. The provenance steps catch that; coupling does not.",
    "Accuracy of this checklist: UNMEASURED. Rating it requires the four-arm test (untrained | artifact checklist | coupling checklist | field-baseline viewers) on watermark-confirmed fakes.",
]

REQUIRED_CUE_KEYS = ("id", "layer", "question", "expected_if_real",
                     "typical_if_generated", "timing", "applies_to",
                     "status", "source", "mechanism")


# ---------------------------------------------------------------- cue set

def validate_cues(data):
    """Raise ValueError on any cue row missing a field, status or source."""
    if not isinstance(data, dict) or "cues" not in data or "event_types" not in data:
        raise ValueError("cue file must carry 'cues' and 'event_types'")
    events = data["event_types"]
    seen = set()
    for row in data["cues"]:
        missing = [k for k in REQUIRED_CUE_KEYS if k not in row]
        if missing:
            raise ValueError(f"cue {row.get('id')} missing {missing}")
        if row["id"] in seen:
            raise ValueError(f"duplicate cue id {row['id']}")
        seen.add(row["id"])
        if row["status"] not in STATUSES:
            raise ValueError(f"cue {row['id']} has status {row['status']!r}")
        if row["timing"] not in TIMINGS:
            raise ValueError(f"cue {row['id']} has timing {row['timing']!r}")
        if not row["source"]:
            raise ValueError(f"cue {row['id']} has no source")
        mech = row["mechanism"]
        if (not isinstance(mech, dict) or mech.get("status") not in STATUSES
                or "claim" not in mech or "source" not in mech):
            raise ValueError(f"cue {row['id']} mechanism must state claim, status and source")
        unknown = [e for e in row["applies_to"] if e not in events]
        if unknown or not row["applies_to"]:
            raise ValueError(f"cue {row['id']} applies_to {row['applies_to']!r} outside event_types")
    return data


def load_cues(path=None):
    """Load and validate the cue set (default: coupling_cues.json beside this module)."""
    with open(path or DEFAULT_CUES, "r", encoding="utf-8") as handle:
        return validate_cues(json.load(handle))


def cue_set_drift(path=None):
    """Compare the local cue file against the pinned GlyphAI sha256.

    Returns a dict with local and pinned digests and a 'matches' bool. A
    mismatch is not an error: it means one copy moved and the other did not,
    which is the thing a reader needs to know before quoting either.
    """
    with open(path or DEFAULT_CUES, "rb") as handle:
        local = hashlib.sha256(handle.read()).hexdigest()
    pinned = CUE_SET_SOURCE["sha256"]
    return {"local_sha256": local, "pinned_sha256": pinned,
            "matches": local == pinned, "source": dict(CUE_SET_SOURCE)}


def event_types(cues=None):
    return list((cues or load_cues())["event_types"])


def cues_for(event_type, cues=None):
    """Cue rows that apply to one event type, in file order. Empty for an unknown type."""
    data = cues or load_cues()
    if event_type not in data["event_types"]:
        return []
    return [row for row in data["cues"] if event_type in row["applies_to"]]


def questions(event_type, cues=None):
    """The guided walk: (cue id, layer, timing, question) per applicable cue."""
    return [(row["id"], row["layer"], row["timing"], row["question"])
            for row in cues_for(event_type, cues)]


# ---------------------------------------------------------------- share step

def _phrase_in_text(phrase, text):
    pattern = re.compile(r"\b" + re.escape(phrase) + r"\b", re.IGNORECASE)
    return pattern.search(text) is not None


def share_urgency_check(text):
    """Flag time-attack language in a title, description or transcript.

    Returns a list of flags shaped like GlyphAI's detector output plus a
    mechanism tag: {type, severity, evidence, mechanism}. Empty when nothing
    fires. The pause before sharing is the countermeasure; this only names
    the pressure.
    """
    if not text:
        return []
    found = [p for p in SHARE_URGENCY_PHRASES if _phrase_in_text(p, text)]
    if not found:
        return []
    return [{
        "type": "FAKE_URGENCY",
        "severity": 0.7,
        "evidence": "Time-pressure language on the share decision: " + ", ".join(found),
        "mechanism": ["TIME_ATTACK"],
    }]


# ---------------------------------------------------------------- evaluate

def _base(verdict, reason, detail, broken, consistent, unseen, unanswered,
          event_type, text):
    return {
        "verdict": verdict,
        "reason": reason,
        "detail": detail,
        "cues": broken,
        "consistent": consistent,
        "cannot_see": len(unseen),
        "unanswered": unanswered,
        "answered": len(broken) + len(consistent),
        "event_type": event_type,
        "share_flags": share_urgency_check(text),
        "provenance_steps": list(PROVENANCE_STEPS),
        "scope_limits": list(SCOPE_LIMITS),
    }


def evaluate(event_type, answers, text=None, cues=None):
    """Evaluate a clip from the viewer's answers.

    answers: {cue_id: "yes" | "no" | "cannot_see"}. Unasked cues read as
    cannot_see. An answer outside the vocabulary or a cue outside the event's
    set raises ValueError rather than being ignored.  is the title,
    description or transcript to scan for share urgency.
    """
    data = cues or load_cues()
    answers = answers or {}
    if event_type not in data["event_types"]:
        detail = f"unknown event type {event_type!r}; known: {', '.join(data['event_types'])}"
        return _base(NOT_EVALUABLE, REASON_EVENT_TYPE, detail, [], [], [], [],
                     event_type, text)
    ids = [row["id"] for row in cues_for(event_type, data)]
    for cue_id, answer in answers.items():
        if cue_id not in ids:
            raise ValueError(f"cue {cue_id!r} does not apply to event {event_type!r}")
        if answer not in ANSWERS:
            raise ValueError(f"answer for {cue_id} must be one of {ANSWERS}, got {answer!r}")

    broken = [i for i in ids if answers.get(i) == ANSWER_NO]
    consistent = [i for i in ids if answers.get(i) == ANSWER_YES]
    unseen = [i for i in ids if answers.get(i, ANSWER_CANNOT_SEE) == ANSWER_CANNOT_SEE]
    unanswered = [i for i in ids if i not in answers]
    answered = len(broken) + len(consistent)

    if broken:
        # [CHOICE 1] one contradiction is already an observation about two
        # layers; it does not wait for the minimum.
        return _base(COUPLING_BROKEN, None, None, broken, consistent, unseen,
                     unanswered, event_type, text)
    if answered >= MIN_ANSWERED_CUES:
        return _base(COUPLING_CONSISTENT, None, None, broken, consistent, unseen,
                     unanswered, event_type, text)
    detail = f"{answered} cue(s) answered yes/no; {MIN_ANSWERED_CUES} needed (PLACEHOLDER minimum)"
    return _base(NOT_EVALUABLE, REASON_TOO_FEW_VISIBLE, detail, broken, consistent,
                 unseen, unanswered, event_type, text)


# ---------------------------------------------------------------- render

def render(result, cues=None):
    """Plain-text report carrying the scope limits and provenance steps every time."""
    data = cues or load_cues()
    by_id = {row["id"]: row for row in data["cues"]}
    lines = []
    verdict = result["verdict"]
    if verdict == COUPLING_BROKEN:
        lines.append("Coupling: BROKEN on " + ", ".join(result["cues"]))
        for cue_id in result["cues"]:
            row = by_id.get(cue_id)
            if row:
                lines.append(f"  {cue_id} ({row['layer']}): expected {row['expected_if_real']}; "
                             f"typical if generated: {row['typical_if_generated']}")
    elif verdict == COUPLING_CONSISTENT:
        lines.append(f"Coupling: CONSISTENT across {result['answered']} answered cue(s)")
    else:
        lines.append(f"Coupling: NOT EVALUABLE ({result['reason']}): {result['detail']}")
    lines.append(f"  answered: {result['answered']}   cannot_see: {result['cannot_see']}")
    if result.get("share_flags"):
        lines.append("")
        lines.append("Share-step flags:")
        for flag in result["share_flags"]:
            lines.append(f"  {flag['type']} severity {flag['severity']:.1f} "
                         f"mechanism {','.join(flag['mechanism'])}: {flag['evidence']}")
        lines.append("  The pause before sharing is the countermeasure.")
    lines.append("")
    lines.append("Before sharing, regardless of the result above:")
    lines.extend("  " + step for step in result["provenance_steps"])
    lines.append("")
    lines.append("Scope limits:")
    lines.extend("  - " + limit for limit in result["scope_limits"])
    return "\n".join(lines)
