#!/usr/bin/env python3
"""Template expander for lizles topics.

Reads topics/<slug>/wordlists.json (per-topic) and produces template-confidence
exercises into topics/<slug>/exercises.json, preserving verified + review items.

Each template encodes a slot grammar where the answer is determined by the rule,
not by free invention. Word lists are hand-vetted; the expander is mechanical.

To add a topic:
    1. Drop curated word lists in topics/<slug>/wordlists.json
    2. Add an `expand_<slug>(W) -> list[dict]` function below
    3. Register it in EXPANDERS

Usage:
    python3 tools/expand.py <slug> [per_template_cap]
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS_DIR = ROOT / "topics"

# ---- Shared helpers ---------------------------------------------------------

# Inflection for liggen-staan-zitten — only 3sg/3pl used in templates.
INFLECT = {
    "liggen": {"sg": "ligt",  "pl": "liggen"},
    "staan":  {"sg": "staat", "pl": "staan"},
    "zitten": {"sg": "zit",   "pl": "zitten"},
    "hangen": {"sg": "hangt", "pl": "hangen"},
}
CHOICES = {
    "sg": ["ligt", "staat", "zit", "hangt"],
    "pl": ["liggen", "staan", "zitten", "hangen"],
}


def make_id_factory(prefix: str):
    """Returns a function that emits dense ids like '<prefix>-T1-001'."""
    def make_id(template_id: str, counter: int) -> str:
        return f"{prefix}-{template_id}-{counter:03d}"
    return make_id


def neutralise_possessive(place: str) -> str:
    """'in mijn broekzak' → 'in een broekzak' (kills agent/owner clashes)."""
    out = place
    for poss in ("mijn ", "jouw ", "haar ", "zijn ", "onze ", "jullie ", "hun "):
        out = out.replace(f"in {poss}", "in een ")
    return out


# ---- Topic: liggen-staan-zitten --------------------------------------------

def expand_liggen_staan_zitten(W: dict) -> list[dict]:
    items: list[dict] = []
    mid = make_id_factory("lsz-tpl")

    # T1 — flat horizontal × flat surface → liggen
    for number, key in (("sg", "sg"), ("pl", "pl")):
        for obj in W["flat_horizontal"]:
            for place in W["flat_surface_pp"]:
                subj = obj[key]
                items.append({
                    "id": mid("T1" + ("s" if number == "sg" else "p"), len(items) + 1),
                    "type": "cloze",
                    "sentence": f"{subj} ___ {place}.",
                    "answer": INFLECT["liggen"][number],
                    "choices": CHOICES[number],
                    "explanation": f"{subj} is plat / horizontaal — dus gebruik je liggen.",
                    "tags": ["basic-rule", "liggen", "template"],
                    "source": "template:T1-flat-on-surface",
                    "confidence": "template",
                })

    # T2 — upright × flat surface → staan
    for number, key in (("sg", "sg"), ("pl", "pl")):
        for obj in W["upright_object"]:
            for place in W["flat_surface_pp"]:
                subj = obj[key]
                items.append({
                    "id": mid("T2" + ("s" if number == "sg" else "p"), len(items) + 1),
                    "type": "cloze",
                    "sentence": f"{subj} ___ {place}.",
                    "answer": INFLECT["staan"][number],
                    "choices": CHOICES[number],
                    "explanation": f"{subj} staat rechtop met een duidelijke onderkant — dus gebruik je staan.",
                    "tags": ["basic-rule", "staan", "template"],
                    "source": "template:T2-upright-on-surface",
                    "confidence": "template",
                })

    # T3 — vehicle × place → staan
    for number, key in (("sg", "sg"), ("pl", "pl")):
        for veh in W["vehicle"]:
            for place in W["vehicle_place_pp"]:
                items.append({
                    "id": mid("T3" + ("s" if number == "sg" else "p"), len(items) + 1),
                    "type": "cloze",
                    "sentence": f"{veh[key]} ___ {place}.",
                    "answer": INFLECT["staan"][number],
                    "choices": CHOICES[number],
                    "explanation": "Een voertuig heeft wielen (een duidelijke onderkant) — dus gebruik je staan.",
                    "tags": ["basic-rule", "staan", "voertuig", "template"],
                    "source": "template:T3-vehicle-in-place",
                    "confidence": "template",
                })

    # T4 — item in container → zitten (uses possessives, that's fine for intrans)
    for pair in W["container_pairs"]:
        for number, key in (("sg", "item_sg"), ("pl", "item_pl")):
            subj = pair.get(key)
            if not subj:
                continue
            items.append({
                "id": mid("T4" + ("s" if number == "sg" else "p"), len(items) + 1),
                "type": "cloze",
                "sentence": f"{subj} ___ {pair['place']}.",
                "answer": INFLECT["zitten"][number],
                "choices": CHOICES[number],
                "explanation": f"Iets is ergens IN ({pair['place']}) — dus gebruik je zitten.",
                "tags": ["basic-rule", "zitten", "template"],
                "source": "template:T4-in-container",
                "confidence": "template",
            })

    # T5 — hangable × hanger → hangen
    for pair in W["hangable_pairs"]:
        for number, key in (("sg", "obj_sg"), ("pl", "obj_pl")):
            subj = pair.get(key)
            if not subj:
                continue
            items.append({
                "id": mid("T5" + ("s" if number == "sg" else "p"), len(items) + 1),
                "type": "cloze",
                "sentence": f"{subj} ___ {pair['place']}.",
                "answer": INFLECT["hangen"][number],
                "choices": CHOICES[number],
                "explanation": f"Iets is los van de grond, vastgemaakt {pair['place']} — dus gebruik je hangen.",
                "tags": ["basic-rule", "hangen", "template"],
                "source": "template:T5-hanging",
                "confidence": "template",
            })

    # T6 — geography → ligt
    for pair in W["geography_pairs"]:
        items.append({
            "id": mid("T6", len(items) + 1),
            "type": "cloze",
            "sentence": f"{pair['place']} ___ {pair['loc']}.",
            "answer": "ligt",
            "choices": CHOICES["sg"],
            "explanation": "Bij plaatsen, steden en landen op een kaart gebruik je liggen.",
            "tags": ["collocation-liggen", "geography", "template"],
            "source": "template:T6-geography",
            "confidence": "template",
        })

    # T7a/b/c — trans-intrans pairs
    people = W["_trans_intrans_people"]
    flat_sg = [o["sg"] for o in W["flat_horizontal"]]
    upright_sg = [o["sg"] for o in W["upright_object"]]
    container_countable = [p for p in W["container_pairs"] if p.get("item_sg") and p.get("item_pl")]

    for person, obj in product(people, flat_sg):
        items.append({
            "id": mid("T7a", len(items) + 1),
            "type": "trans-intrans",
            "sentence": f"{person} ___ {obj.replace('De ', 'een ').replace('Het ', 'een ')} op tafel.",
            "answer": "legt",
            "options": ["legt", "ligt"],
            "explanation": "Iemand doet de actie (een plat voorwerp neerleggen) → leggen. 'Ligt' is voor waar het object daarna IS.",
            "tags": ["trans-intrans", "leggen-liggen", "template"],
            "source": "template:T7a-leggen-vs-liggen",
            "confidence": "template",
        })

    for person, obj in product(people, upright_sg):
        items.append({
            "id": mid("T7b", len(items) + 1),
            "type": "trans-intrans",
            "sentence": f"{person} ___ {obj.replace('De ', 'een ').replace('Het ', 'een ')} op tafel.",
            "answer": "zet",
            "options": ["zet", "staat"],
            "explanation": "Iemand doet de actie (een rechtop voorwerp plaatsen) → zetten. 'Staat' is voor waar het object daarna IS.",
            "tags": ["trans-intrans", "zetten-staan", "template"],
            "source": "template:T7b-zetten-vs-staan",
            "confidence": "template",
        })

    for person, pair in product(people, container_countable):
        items.append({
            "id": mid("T7c", len(items) + 1),
            "type": "trans-intrans",
            "sentence": f"{person} ___ {pair['item_sg'].replace('De ', 'een ').replace('Het ', 'een ')} {neutralise_possessive(pair['place'])}.",
            "answer": "stopt",
            "options": ["stopt", "zit"],
            "explanation": "Iemand doet de actie (iets ergens in plaatsen) → stoppen. 'Zit' is voor waar het object daarna IS.",
            "tags": ["trans-intrans", "stoppen-zitten", "template"],
            "source": "template:T7c-stoppen-vs-zitten",
            "confidence": "template",
        })

    # T8 — position verb + te + infinitief (Tweede ronde §21).
    # Note: 'lopen' replaces 'hangen' in the choice set because the construction needs an
    # ongoing-action verb; 'hangen + te + inf' doesn't form this pattern.
    te_inflect = {
        "liggen": {"sg": "ligt",  "pl": "liggen"},
        "staan":  {"sg": "staat", "pl": "staan"},
        "zitten": {"sg": "zit",   "pl": "zitten"},
        "lopen":  {"sg": "loopt", "pl": "lopen"},
    }
    te_choices_sg = ["ligt", "staat", "zit", "loopt"]
    te_choices_pl = ["liggen", "staan", "zitten", "lopen"]
    for pair in W.get("position_te_pairs", []):
        lemma = pair["lemma"]
        te_inf = pair["te_inf"]
        for subj in W.get("_te_subjects_3sg", []):
            items.append({
                "id": mid("T8s", len(items) + 1),
                "type": "cloze",
                "sentence": f"{subj} ___ {te_inf}.",
                "answer": te_inflect[lemma]["sg"],
                "choices": te_choices_sg,
                "explanation": f"Met positie-werkwoord + 'te' + infinitief beschrijf je een actie die je in die positie doet. Hier past '{lemma}' bij '{te_inf}'.",
                "tags": ["construction", "te-infinitief", "template"],
                "source": "template:T8-position-te-inf",
                "confidence": "template",
            })
        for subj in W.get("_te_subjects_3pl", []):
            items.append({
                "id": mid("T8p", len(items) + 1),
                "type": "cloze",
                "sentence": f"{subj} ___ {te_inf}.",
                "answer": te_inflect[lemma]["pl"],
                "choices": te_choices_pl,
                "explanation": f"Meervoud + 'te' + infinitief. Hier past '{lemma}' (meervoud) bij '{te_inf}'.",
                "tags": ["construction", "te-infinitief", "template"],
                "source": "template:T8-position-te-inf",
                "confidence": "template",
            })

    # T8b — voltooide tijd van het positie-werkwoord + infinitief (Tweede ronde §21).
    # In de voltooide tijd valt 'te' weg en krijg je een DUBBELE INFINITIEF:
    # 'Hij heeft de hele middag liggen slapen' (niet 'gelegen te slapen').
    # De locatie-bepaling komt vóór de werkwoordsgroep aan het eind.
    def split_te(te_inf: str) -> tuple[str, str]:
        rest = te_inf[3:] if te_inf.startswith("te ") else te_inf
        head, _, tail = rest.partition(" ")
        return head, tail  # 'te lezen op de bank' -> ('lezen', 'op de bank')

    perf_choices = ["liggen", "staan", "zitten", "lopen"]
    perf_subjects = [(s, "heeft") for s in W.get("_te_subjects_3sg", [])] + \
                    [(s, "hebben") for s in W.get("_te_subjects_3pl", [])]
    for pair in W.get("position_te_pairs", []):
        lemma = pair["lemma"]
        inf, pp = split_te(pair["te_inf"])
        for subj, aux in perf_subjects:
            mid_part = pp if pp else "de hele middag"
            items.append({
                "id": mid("T8b", len(items) + 1),
                "type": "cloze",
                "sentence": f"{subj} {aux} {mid_part} ___ {inf}.",
                "answer": lemma,
                "choices": perf_choices,
                "explanation": (
                    f"Voltooide tijd: 'te' valt weg en beide werkwoorden worden infinitief "
                    f"(dubbele infinitief). Dus '{aux} {lemma} {inf}', niet '… te {inf}'. "
                    f"Hier past '{lemma}' bij '{inf}'."
                ),
                "tags": ["construction", "te-infinitief", "voltooide-tijd", "template"],
                "source": "template:T8b-perfect-double-inf",
                "confidence": "template",
            })

    # T9 — existential 'er + position verb + onbepaald' (Tweede ronde §27).
    # Reuses the existing wordlists but reshapes them into the existential frame.
    def bare_pl(de_pl: str) -> str:
        return de_pl[3:] if de_pl.startswith("De ") else de_pl  # 'De kranten' → 'kranten'

    def indef_sg(form: str) -> str:
        return form.replace("De ", "een ").replace("Het ", "een ")

    # T9a — flat horizontal (liggen)
    for obj in W["flat_horizontal"]:
        items.append({
            "id": mid("T9a", len(items) + 1),
            "type": "cloze",
            "sentence": f"Er ___ {bare_pl(obj['pl'])} op tafel.",
            "answer": "liggen",
            "choices": CHOICES["pl"],
            "explanation": "Existentiële zin met 'er': de positie-werkwoord past nog steeds bij het object. Platte voorwerpen (meervoud) → liggen.",
            "tags": ["construction", "er-existentieel", "liggen", "template"],
            "source": "template:T9-er-existential",
            "confidence": "template",
        })
        items.append({
            "id": mid("T9a", len(items) + 1),
            "type": "cloze",
            "sentence": f"Er ___ {indef_sg(obj['sg'])} op tafel.",
            "answer": "ligt",
            "choices": CHOICES["sg"],
            "explanation": "Existentiële zin met 'er' (enkelvoud). Plat voorwerp → liggen.",
            "tags": ["construction", "er-existentieel", "liggen", "template"],
            "source": "template:T9-er-existential",
            "confidence": "template",
        })

    # T9b — upright objects (staan)
    for obj in W["upright_object"]:
        items.append({
            "id": mid("T9b", len(items) + 1),
            "type": "cloze",
            "sentence": f"Er ___ {bare_pl(obj['pl'])} op het dressoir.",
            "answer": "staan",
            "choices": CHOICES["pl"],
            "explanation": "Existentiële zin met 'er'. Voorwerpen met duidelijke onderkant (meervoud) → staan.",
            "tags": ["construction", "er-existentieel", "staan", "template"],
            "source": "template:T9-er-existential",
            "confidence": "template",
        })
        items.append({
            "id": mid("T9b", len(items) + 1),
            "type": "cloze",
            "sentence": f"Er ___ {indef_sg(obj['sg'])} op het dressoir.",
            "answer": "staat",
            "choices": CHOICES["sg"],
            "explanation": "Existentiële zin met 'er' (enkelvoud). Voorwerp met duidelijke onderkant → staan.",
            "tags": ["construction", "er-existentieel", "staan", "template"],
            "source": "template:T9-er-existential",
            "confidence": "template",
        })

    # T9c — vehicles (staan)
    for veh in W["vehicle"]:
        items.append({
            "id": mid("T9c", len(items) + 1),
            "type": "cloze",
            "sentence": f"Er ___ {bare_pl(veh['pl'])} op de parkeerplaats.",
            "answer": "staan",
            "choices": CHOICES["pl"],
            "explanation": "Existentiële zin. Voertuigen (wielen, duidelijke onderkant) → staan.",
            "tags": ["construction", "er-existentieel", "staan", "voertuig", "template"],
            "source": "template:T9-er-existential",
            "confidence": "template",
        })

    # T9d — items in containers (zitten)
    for pair in W["container_pairs"]:
        if pair.get("item_pl"):
            items.append({
                "id": mid("T9d", len(items) + 1),
                "type": "cloze",
                "sentence": f"Er ___ {bare_pl(pair['item_pl'])} {pair['place']}.",
                "answer": "zitten",
                "choices": CHOICES["pl"],
                "explanation": "Existentiële zin. Iets is ergens IN → zitten.",
                "tags": ["construction", "er-existentieel", "zitten", "template"],
                "source": "template:T9-er-existential",
                "confidence": "template",
            })

    # T9e — hangables (hangen)
    for pair in W["hangable_pairs"]:
        if pair.get("obj_pl"):
            items.append({
                "id": mid("T9e", len(items) + 1),
                "type": "cloze",
                "sentence": f"Er ___ {bare_pl(pair['obj_pl'])} {pair['place']}.",
                "answer": "hangen",
                "choices": CHOICES["pl"],
                "explanation": "Existentiële zin. Iets is los van de grond, vastgemaakt aan iets → hangen.",
                "tags": ["construction", "er-existentieel", "hangen", "template"],
                "source": "template:T9-er-existential",
                "confidence": "template",
            })

    return items


# ---- Topic: iets-leuks -----------------------------------------------------

def expand_iets_leuks(W: dict) -> list[dict]:
    """After iets/wat/niets/weinig + ADJ, the adjective takes -s.
    Exception: adjectives that already end in an /s/ sound take no extra -s."""
    items: list[dict] = []
    mid = make_id_factory("iel-tpl")

    regular_adj = W["regular_adjectives"]       # ["leuk", "mooi", ...]
    s_ending_adj = W["s_ending_adjectives"]      # ["fris", "vies", ...]
    frames = W["frames"]                          # each: {pattern, allowed_kinds, tag}

    for frame in frames:
        pattern = frame["pattern"]                # uses {adj} placeholder
        kinds = frame.get("allowed_kinds", ["regular", "s_ending"])
        tag = frame.get("tag", "iets-s")
        add_s = frame.get("add_s", True)          # default: rule-triggering frame

        if "regular" in kinds:
            for adj in regular_adj:
                if add_s:
                    correct, distractor = adj + "s", adj
                    explanation = f"Na 'iets/wat/niets/weinig/veel' krijgt het bijvoeglijk naamwoord een -s: '{correct}'."
                    source = "template:iel-regular-adj-plus-s"
                else:
                    correct, distractor = adj, adj + "s"
                    explanation = (f"In een predicaatzin (na 'is', 'vind ik', 'klinkt', ...) blijft het bijvoeglijk "
                                   f"naamwoord in de basisvorm: '{correct}'. Geen -s, want er staat geen iets/wat/niets voor.")
                    source = "template:iel-regular-adj-predicate"
                items.append({
                    "id": mid("R", len(items) + 1),
                    "type": "cloze",
                    "sentence": pattern.replace("{adj}", "___"),
                    "answer": correct,
                    "choices": [correct, distractor],
                    "explanation": explanation,
                    "tags": [tag, "regular-adj", "template"],
                    "source": source,
                    "confidence": "template",
                })

        if "s_ending" in kinds:
            for adj in s_ending_adj:
                # s-ending adj: bare form in both contexts. Distractor is the over-correction (+s).
                correct, distractor = adj, adj + "s"
                if add_s:
                    explanation = f"Uitzondering: '{adj}' eindigt al op een /s/-klank — geen extra -s."
                    source = "template:iel-s-ending-no-extra-s"
                else:
                    explanation = (f"In een predicaatzin blijft het bijvoeglijk naamwoord in de basisvorm: '{adj}'. "
                                   f"En geen extra -s, want '{adj}' eindigt al op een /s/-klank.")
                    source = "template:iel-s-ending-predicate"
                items.append({
                    "id": mid("S", len(items) + 1),
                    "type": "cloze",
                    "sentence": pattern.replace("{adj}", "___"),
                    "answer": correct,
                    "choices": [correct, distractor],
                    "explanation": explanation,
                    "tags": [tag, "s-ending-adj", "template"],
                    "source": source,
                    "confidence": "template",
                })

    return items


# ---- Topic: leren-kennen ---------------------------------------------------

def expand_leren_kennen(W: dict) -> list[dict]:
    """Semantic topic — distinguishing 5 verbs by *context*. Templates here are
    not slot-grammar; they are fixed scenario frames where the situation
    determines the answer. Lower volume than slot-grammar topics."""
    items: list[dict] = []
    mid = make_id_factory("lk-tpl")

    # Each scenario fixes one answer. Choices = all 5 verbs in the relevant form.
    # We provide scenarios in past-participle form (heb ... <pp>) since the book
    # uses past tense for "ontmoeten" / "tegenkomen" most, and present for "zien".
    PP_CHOICES = ["ontmoet", "gezien", "tegengekomen", "afgesproken", "leren kennen"]
    INF_CHOICES = ["ontmoeten", "zien", "tegenkomen", "afspreken", "leren kennen"]

    for scen in W.get("scenarios_pp", []):
        items.append({
            "id": mid("Spp", len(items) + 1),
            "type": "cloze",
            "sentence": scen["sentence"],
            "answer": scen["answer"],
            "choices": PP_CHOICES,
            "explanation": scen["explanation"],
            "tags": ["semantic", scen.get("tag", "context"), "template"],
            "source": "template:lk-scenarios-pp",
            "confidence": "template",
        })

    for scen in W.get("scenarios_inf", []):
        items.append({
            "id": mid("Sinf", len(items) + 1),
            "type": "cloze",
            "sentence": scen["sentence"],
            "answer": scen["answer"],
            "choices": INF_CHOICES,
            "explanation": scen["explanation"],
            "tags": ["semantic", scen.get("tag", "context"), "template"],
            "source": "template:lk-scenarios-inf",
            "confidence": "template",
        })

    for scen in W.get("scenarios_pres", []):
        items.append({
            "id": mid("Spres", len(items) + 1),
            "type": "cloze",
            "sentence": scen["sentence"],
            "answer": scen["answer"],
            "choices": scen.get("choices") or ["ontmoet", "ziet", "komt tegen", "spreekt af", "leert kennen"],
            "explanation": scen["explanation"],
            "tags": ["semantic", scen.get("tag", "context"), "template"],
            "source": "template:lk-scenarios-pres",
            "confidence": "template",
        })

    return items


# ---- Topic: koken-recepten -------------------------------------------------

def expand_koken_recepten(W: dict) -> list[dict]:
    """Thematic vocabulary topic — no grammar rule. The vetted wordlist IS the
    content. Each category produces:
      * match items: NL word ↔ English gloss, in chunks of MATCH_CHUNK.
      * cloze items: for entries that carry a `cloze` field, the answer is blanked
        and distractors are drawn from the SAME category (near-miss counter-examples
        so the item discriminates)."""
    items: list[dict] = []
    mid = make_id_factory("kok-tpl")
    MATCH_CHUNK = 5
    MAX_DISTRACTORS = 3

    # Categories are every list-valued key (skip the leading "_comment").
    categories = [(k, v) for k, v in W.items() if isinstance(v, list)]

    for cat, entries in categories:
        # --- match: chunk the category into small grids of NL ↔ EN pairs ---
        for start in range(0, len(entries), MATCH_CHUNK):
            chunk = entries[start:start + MATCH_CHUNK]
            if len(chunk) < 2:
                continue  # match needs >= 2 pairs to be valid
            items.append({
                "id": mid(f"M-{cat}", len(items) + 1),
                "type": "match",
                "prompt": "Match het Nederlandse woord met de Engelse vertaling.",
                "pairs": [{"left": e["nl"], "right": e["en"]} for e in chunk],
                "tags": ["vocab", cat, "match", "template"],
                "source": f"template:koken-match-{cat}",
                "confidence": "template",
            })

        # --- cloze: only for entries that supply a vetted sentence + answer ---
        cloze_entries = [e for e in entries if e.get("cloze")]
        answer_pool = [e["cloze"]["answer"] for e in cloze_entries]
        for i, e in enumerate(cloze_entries):
            c = e["cloze"]
            answer = c["answer"]
            distractors = [a for a in answer_pool if a != answer]
            rng = random.Random(len(items))
            rng.shuffle(distractors)
            choices = [answer] + distractors[:MAX_DISTRACTORS]
            rng.shuffle(choices)
            items.append({
                "id": mid(f"C-{cat}", len(items) + 1),
                "type": "cloze",
                "sentence": c["sentence"],
                "answer": answer,
                "choices": choices,
                "explanation": f"'{e['nl']}' — {e['en']}.",
                "tags": ["vocab", cat, "cloze", "template"],
                "source": f"template:koken-cloze-{cat}",
                "confidence": "template",
            })

    return items


# ---- Dispatch --------------------------------------------------------------

EXPANDERS = {
    "liggen-staan-zitten": expand_liggen_staan_zitten,
    "iets-leuks":          expand_iets_leuks,
    "leren-kennen":        expand_leren_kennen,
    "koken-recepten":      expand_koken_recepten,
}


def _dedup_key(it: dict):
    """Type-aware identity for dedup. Sentence-based items key on (sentence, answer);
    match items have neither, so key on the (left) words of their pairs instead —
    otherwise every match item collapses to (None, None) and all but one are lost."""
    if it.get("type") == "match":
        return ("match", tuple(p["left"] for p in it.get("pairs", [])))
    return (it.get("sentence"), it.get("answer"))


# Per-source cap overrides. The T7a/b/c trans-intrans templates are near-identical
# frames (T7a/b are literally "<person> ___ <object> op tafel" — only the name and
# noun change, and the answer is fixed per template), so a big sample just drills the
# same rule dozens of times and drowns out the hand-curated contrasts/idioms. Cap them
# hard; everything else keeps the global cap.
CAP_OVERRIDES = {
    "template:T7a-leggen-vs-liggen": 6,
    "template:T7b-zetten-vs-staan": 6,
    "template:T7c-stoppen-vs-zitten": 8,
    # Perfect double-infinitive: keep a focused set, one per distinct activity verb.
    "template:T8b-perfect-double-inf": 18,
}


def _variety_key(it: dict) -> str:
    """Pedagogically-relevant slot of a trans-intrans item: the object (and, for T7c,
    its container) — i.e. everything but the irrelevant person. Used to keep the small
    capped sample maximally varied instead of repeating the same noun."""
    m = re.search(r"___ (?:een |het |de )?(.+?)\.?$", it.get("sentence", ""))
    return m.group(1) if m else it.get("sentence", "")


def _diverse_sample(group: list[dict], cap: int, rng: random.Random) -> list[dict]:
    """Pick `cap` items maximizing distinct _variety_key (one per object first, then
    fill randomly if cap exceeds the number of distinct objects)."""
    buckets: dict[str, list[dict]] = {}
    for it in group:
        buckets.setdefault(_variety_key(it), []).append(it)
    keys = list(buckets.keys())
    rng.shuffle(keys)
    picked = [rng.choice(buckets[k]) for k in keys[:cap]]
    if len(picked) < cap:  # cap larger than distinct objects — top up from the rest
        rest = [it for it in group if it not in picked]
        rng.shuffle(rest)
        picked.extend(rest[: cap - len(picked)])
    return picked


def cap_per_template(items: list[dict], cap: int, seed: int = 1) -> list[dict]:
    """Sample down to `cap` (or its CAP_OVERRIDES value) per source/template; re-id
    densely within each source. Overridden templates sample for object variety."""
    by_src: dict[str, list[dict]] = {}
    for it in items:
        by_src.setdefault(it["source"], []).append(it)

    out: list[dict] = []
    for src, group in by_src.items():
        # Per-source rng so changing one template's cap never reshuffles the others.
        rng = random.Random(f"{seed}:{src}")
        c = CAP_OVERRIDES.get(src, cap)
        if len(group) <= c:
            sampled = group
        elif src in CAP_OVERRIDES:
            sampled = _diverse_sample(group, c, rng)
        else:
            sampled = rng.sample(group, c)
        # Preserve id prefix (everything before the last '-NNN'), renumber densely.
        for i, it in enumerate(sampled, start=1):
            prefix = it["id"].rsplit("-", 1)[0]
            it["id"] = f"{prefix}-{i:03d}"
        out.extend(sampled)
    return out


def main(argv: list[str]) -> int:
    slug = argv[1] if len(argv) > 1 else "liggen-staan-zitten"
    cap = int(argv[2]) if len(argv) > 2 else 25
    if slug not in EXPANDERS:
        raise SystemExit(f"No expander defined for topic '{slug}'. Known: {sorted(EXPANDERS)}")

    topic_dir = TOPICS_DIR / slug
    wl_path = topic_dir / "wordlists.json"
    ex_path = topic_dir / "exercises.json"

    W = json.loads(wl_path.read_text(encoding="utf-8")) if wl_path.exists() else {}
    existing = json.loads(ex_path.read_text(encoding="utf-8")) if ex_path.exists() else []
    preserved = [it for it in existing if it.get("confidence") != "template"]

    generated = EXPANDERS[slug](W)

    # Dedup against preserved AND within the generated batch. Key is (sentence, answer)
    # — for topics where the same sentence can have multiple correct answers depending
    # on the slot fill (e.g. 'Ik heb iets ___ gekocht.' → leuks / moois / lekkers …),
    # we want each (sentence, answer) pair to count as a distinct exercise.
    seen = {_dedup_key(it) for it in preserved}
    unique = []
    for it in generated:
        key = _dedup_key(it)
        if key in seen:
            continue
        seen.add(key)
        unique.append(it)
    capped = cap_per_template(unique, cap=cap)

    merged = preserved + capped
    ex_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    by_src = Counter(it["source"] for it in capped)
    print(f"[{slug}] generated {len(capped)} template items (cap={cap}). preserved {len(preserved)} non-template.")
    for src, n in sorted(by_src.items()):
        print(f"  {src}: {n}")
    print(f"  → wrote {len(merged)} total items to {ex_path}")

    _update_index_counts(slug, merged)
    return 0


def _update_index_counts(slug: str, items: list[dict]) -> None:
    index_path = TOPICS_DIR / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    counts = Counter(it["confidence"] for it in items)
    for t in index:
        if t["slug"] == slug:
            t["counts"] = {
                "verified": counts.get("verified", 0),
                "template": counts.get("template", 0),
                "review":   counts.get("review", 0),
            }
            break
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
