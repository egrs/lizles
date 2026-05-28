#!/usr/bin/env python3
"""Seed `confidence: review` items for a topic.

These are freeform sentences that go *beyond* the textbook — common idioms,
dialogue snippets, modal-verb variants. They are flagged `review` so the drill
UI hides them by default until a human approves them via review.html.

To add review items for a topic, write a `seed_<slug>() -> list[dict]` function
and register it in SEEDERS.

Usage:
    python3 tools/seed_review.py <slug>
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS_DIR = ROOT / "topics"


# ---- Shared shorthand -------------------------------------------------------

# liggen-staan-zitten choice sets
LSZ_SG_3 = ["ligt", "staat", "zit", "hangt"]
LSZ_PL_3 = ["liggen", "staan", "zitten", "hangen"]
LSZ_SG_1 = ["lig", "sta", "zit", "hang"]
LSZ_INF  = ["liggen", "staan", "zitten", "hangen"]
LEGT_LIGT = ["legt", "ligt"]
ZET_STAAT = ["zet", "staat"]
STOPT_ZIT = ["stopt", "zit"]


def _cloze(sentence, answer, choices, explanation, tag, source):
    return {
        "id": "",
        "type": "cloze",
        "sentence": sentence,
        "answer": answer,
        "choices": choices,
        "explanation": explanation,
        "tags": [tag, "review"],
        "source": source,
        "confidence": "review",
    }


def _mcq(sentence, answer, options, explanation, tag, source):
    return {
        "id": "",
        "type": "mcq",
        "sentence": sentence,
        "answer": answer,
        "options": options,
        "explanation": explanation,
        "tags": [tag, "review"],
        "source": source,
        "confidence": "review",
    }


def _trans(sentence, answer, options, explanation, tag, source):
    return {
        "id": "",
        "type": "trans-intrans",
        "sentence": sentence,
        "answer": answer,
        "options": options,
        "explanation": explanation,
        "tags": [tag, "review"],
        "source": source,
        "confidence": "review",
    }


# ---- Topic: liggen-staan-zitten --------------------------------------------

def seed_liggen_staan_zitten() -> list[dict]:
    items: list[dict] = []
    A = items.append

    # liggen idioms / extensions
    A(_cloze("Het ___ voor de hand dat we morgen vroeg moeten beginnen.", "ligt", LSZ_SG_3,
             "'Voor de hand liggen' = 'duidelijk / vanzelfsprekend zijn'.", "idiom-liggen", "freeform:voor-de-hand-liggen"))
    A(_cloze("Aan mij ___ het niet, hoor.", "ligt", LSZ_SG_3,
             "'Aan iemand liggen' = 'iemands schuld zijn'. Hier: 'Het is mijn schuld niet.'", "idiom-liggen", "freeform:aan-iemand-liggen"))
    A(_cloze("Mijn opa ___ al twee weken in het ziekenhuis.", "ligt", LSZ_SG_3,
             "'In het ziekenhuis liggen' = 'opgenomen zijn in het ziekenhuis'.", "idiom-liggen", "freeform:in-het-ziekenhuis-liggen"))
    A(_cloze("Waar ___ de afstandsbediening?", "ligt", LSZ_SG_3,
             "Bij voorwerpen die plat / horizontaal kunnen liggen, gebruik je liggen.", "basic-rule", "freeform:locatie-liggen"))
    A(_cloze("Het hotel ___ aan zee.", "ligt", LSZ_SG_3,
             "Bij gebouwen op een locatie (vooral met aan/bij/tegen) gebruik je liggen.", "collocation-liggen", "freeform:hotel-aan-zee"))
    A(_cloze("De brug ___ over de rivier.", "ligt", LSZ_SG_3,
             "Bruggen 'liggen' over een rivier (vaste combinatie).", "collocation-liggen", "freeform:brug-over-rivier"))
    A(_cloze("Sinds zijn ontslag ___ hij maar wat op de bank.", "ligt", LSZ_SG_3,
             "Hier 'liggen' in de letterlijke zin: hij ligt op de bank (een platte positie op een bank).", "basic-rule", "freeform:op-de-bank-liggen"))
    A(_cloze("Het kind ___ al een uur te slapen.", "ligt", LSZ_SG_3,
             "'Liggen te + infinitief' beschrijft iets wat iemand doet terwijl hij/zij ligt.", "construction", "freeform:liggen-te-slapen"))

    # staan idioms / extensions
    A(_cloze("Het ___ vandaag in de krant.", "staat", LSZ_SG_3,
             "'In de krant staan' = 'in de krant gepubliceerd zijn' (vaste combinatie).", "collocation-staan", "freeform:in-de-krant-staan"))
    A(_cloze("Daar ___ ik volledig achter.", "sta", LSZ_SG_1,
             "'Achter iets/iemand staan' = 'iets/iemand steunen'.", "idiom-staan", "freeform:achter-iets-staan"))
    A(_cloze("Het eten ___ klaar op tafel.", "staat", LSZ_SG_3,
             "'Klaarstaan' = 'gereed zijn'. Eten op tafel → staat (duidelijke onderkant).", "collocation-staan", "freeform:klaar-staan"))
    A(_cloze("Wij ___ voor een belangrijke keuze.", "staan", LSZ_PL_3,
             "'Voor een keuze staan' = 'met een keuze geconfronteerd worden'.", "idiom-staan", "freeform:voor-keuze-staan"))
    A(_cloze("Hij ___ op het punt te vertrekken.", "staat", LSZ_SG_3,
             "'Op het punt staan om te + infinitief' = 'bijna op het punt te doen'.", "idiom-staan", "freeform:op-het-punt-staan"))
    A(_cloze("Ik ___ versteld van haar talent.", "sta", LSZ_SG_1,
             "'Versteld staan van' = 'verbaasd zijn over'.", "idiom-staan", "freeform:versteld-staan"))
    A(_cloze("Het bedrijf ___ er financieel goed voor.", "staat", LSZ_SG_3,
             "'Ergens goed voor staan' = 'in een goede positie verkeren'.", "idiom-staan", "freeform:er-goed-voor-staan"))
    A(_cloze("Het standbeeld ___ midden op het plein.", "staat", LSZ_SG_3,
             "Een standbeeld is rechtop met een duidelijke onderkant → staan.", "basic-rule", "freeform:standbeeld-staan"))
    A(_cloze("Mijn collega ___ er goed voor met zijn nieuwe baan.", "staat", LSZ_SG_3,
             "'Ergens goed voor staan' = 'er goed bijstaan / het goed doen'.", "idiom-staan", "freeform:er-goed-voor-staan-2"))

    # zitten idioms / extensions
    A(_cloze("Daar ___ een addertje onder het gras.", "zit", LSZ_SG_3,
             "'Een addertje onder het gras' = 'een verborgen probleem / haakje'.", "idiom-zitten", "freeform:addertje-onder-het-gras"))
    A(_cloze("We ___ vast in het verkeer.", "zitten", LSZ_PL_3,
             "'Vastzitten in het verkeer' = 'in een file staan / niet vooruit komen'.", "idiom-zitten", "freeform:vastzitten-verkeer"))
    A(_cloze("Ik ___ er helemaal doorheen.", "zit", LSZ_SG_1,
             "'Erdoorheen zitten' = 'uitgeput, op'.", "idiom-zitten", "freeform:er-doorheen-zitten"))
    A(_cloze("Hij ___ in de problemen.", "zit", LSZ_SG_3,
             "'In de problemen zitten' = 'in moeilijkheden verkeren'.", "idiom-zitten", "freeform:in-de-problemen-zitten"))
    A(_cloze("Ze ___ goed in haar vel.", "zit", LSZ_SG_3,
             "'Goed in je vel zitten' = 'je goed voelen, in balans zijn'.", "idiom-zitten", "freeform:in-je-vel-zitten"))
    A(_cloze("Daar ___ niets anders op dan accepteren.", "zit", LSZ_SG_3,
             "'Er zit niets anders op (dan …)' = 'er is geen andere optie dan …'.", "idiom-zitten", "freeform:niets-anders-op"))
    A(_cloze("Het ___ er niet in dat we vandaag nog klaar zijn.", "zit", LSZ_SG_3,
             "'Het zit er (niet) in dat …' = 'het is (on)waarschijnlijk dat …'.", "idiom-zitten", "freeform:het-zit-er-niet-in"))
    A(_cloze("Hij ___ goed bij kas.", "zit", LSZ_SG_3,
             "'Goed bij kas zitten' = 'genoeg geld hebben' (informeel/ouderwets).", "idiom-zitten", "freeform:bij-kas-zitten"))
    A(_cloze("De sleutels ___ in mijn jaszak.", "zitten", LSZ_PL_3,
             "Iets in een zak / container → zitten.", "basic-rule", "freeform:sleutels-in-jaszak"))
    A(_cloze("Er ___ pennen en potloden in de la.", "zitten", LSZ_PL_3,
             "Spullen in een lade → zitten (meervoud → zitten).", "basic-rule", "freeform:pennen-in-de-la"))

    # hangen idioms / extensions
    A(_cloze("Onze toekomst ___ aan een zijden draadje.", "hangt", LSZ_SG_3,
             "'Aan een zijden draadje hangen' = 'op het punt staan mis te lopen; zeer onzeker zijn'.", "idiom-hangen", "freeform:zijden-draadje"))
    A(_cloze("Het ___ van het weer af of we gaan.", "hangt", LSZ_SG_3,
             "'Afhangen van' = 'gebaseerd zijn op / bepaald worden door'.", "idiom-hangen", "freeform:afhangen-van"))
    A(_cloze("Hij ___ de hele dag rond in de stad.", "hangt", LSZ_SG_3,
             "'Rondhangen' = 'doelloos ergens verblijven'.", "idiom-hangen", "freeform:rondhangen"))
    A(_cloze("Er ___ een onheilspellende sfeer in de lucht.", "hangt", LSZ_SG_3,
             "'Iets hangt in de lucht' = 'iets is voelbaar maar nog niet gebeurd'.", "idiom-hangen", "freeform:in-de-lucht-hangen"))
    A(_cloze("Op die muur ___ allemaal foto's van de kinderen.", "hangen", LSZ_PL_3,
             "Foto's aan een muur zijn los van de grond, vastgemaakt aan de muur → hangen (meervoud).", "basic-rule", "freeform:fotos-aan-muur"))
    A(_cloze("De jas ___ aan de kapstok.", "hangt", LSZ_SG_3,
             "Een jas aan een kapstok is los van de grond → hangt.", "basic-rule", "freeform:jas-kapstok"))

    # dialogue
    A(_cloze("— Waar ___ mijn jas? — Aan de kapstok in de hal.", "hangt", LSZ_SG_3,
             "Locatievraag bij kleding aan een haak → hangen.", "dialogue", "freeform:dialogue-jas"))
    A(_cloze("— Waar ___ de auto? — In de garage.", "staat", LSZ_SG_3,
             "Locatievraag bij een voertuig → staan (wielen, duidelijke onderkant).", "dialogue", "freeform:dialogue-auto"))
    A(_cloze("— Waar ___ mijn telefoon? — Op de keukentafel.", "ligt", LSZ_SG_3,
             "Telefoon plat op tafel → liggen (in tegenstelling tot 'in je broekzak zitten').", "dialogue", "freeform:dialogue-telefoon-tafel"))
    A(_cloze("— ___ het eten al op tafel? — Bijna, nog vijf minuten.", "Staat", ["Ligt", "Staat", "Zit", "Hangt"],
             "Eten op tafel staat klaar — vaste combinatie 'klaarstaan'.", "dialogue", "freeform:dialogue-eten"))
    A(_cloze("— ___ jullie hier al lang? — Een halfuurtje.", "Zitten", ["Liggen", "Staan", "Zitten", "Hangen"],
             "Op een stoel of bank zitten → zitten (meervoud: 'jullie zitten').", "dialogue", "freeform:dialogue-jullie"))

    # modal verbs
    A(_cloze("Het moet hier ergens ___.", "liggen", LSZ_INF,
             "Na modaal werkwoord (moeten/mogen/kunnen) volgt het werkwoord in de infinitief aan het eind van de zin.", "construction", "freeform:modal-liggen"))
    A(_cloze("Die fiets mag daar niet ___.", "staan", LSZ_INF,
             "Modaal + infinitief. Fiets met wielen → staan.", "construction", "freeform:modal-staan"))
    A(_cloze("De jas moet aan de kapstok ___.", "hangen", LSZ_INF,
             "Modaal + infinitief. Jas aan kapstok → hangen.", "construction", "freeform:modal-hangen"))
    A(_cloze("Je portemonnee kan in je tas ___.", "zitten", LSZ_INF,
             "Modaal + infinitief. In tas → zitten.", "construction", "freeform:modal-zitten"))
    A(_cloze("Laat die papieren maar ___.", "liggen", LSZ_INF,
             "'Laten + infinitief' — papieren plat → liggen.", "construction", "freeform:laat-liggen"))

    # trans-intrans freeform
    A(_trans("De ober ___ het glas water op tafel.", "zet", ZET_STAAT,
             "Iemand doet de actie (een rechtop voorwerp neerzetten) → zetten. 'Staat' is voor waar het glas daarna IS.",
             "trans-intrans", "freeform:ober-zet-glas"))
    A(_trans("De receptioniste ___ de map met documenten op de balie.", "legt", LEGT_LIGT,
             "Iemand legt een plat voorwerp (map) ergens neer → leggen. 'Ligt' is voor waar de map IS.",
             "trans-intrans", "freeform:receptioniste-legt-map"))
    A(_trans("Mijn zus ___ haar paspoort in de kluis.", "stopt", STOPT_ZIT,
             "Iemand stopt iets in een container → stoppen. 'Zit' is voor waar het paspoort daarna IS.",
             "trans-intrans", "freeform:zus-stopt-paspoort"))

    # MCQ variants
    A(_mcq("Mijn opa ___ in het ziekenhuis met een gebroken heup.", "ligt", LSZ_SG_3,
           "'In het ziekenhuis liggen' = opgenomen zijn. Modale context.", "idiom-liggen", "freeform:mcq-opa-ziekenhuis"))
    A(_mcq("De situatie ___ ons niet aan.", "staat", LSZ_SG_3,
           "'Iets staat iemand aan' = 'iemand vindt het prettig / acceptabel'.", "idiom-staan", "freeform:mcq-staat-aan"))

    return items


# ---- Topic: iets-leuks -----------------------------------------------------

def seed_iets_leuks() -> list[dict]:
    items: list[dict] = []
    A = items.append

    # Dialogue / contextual
    A(_cloze("— Wat heb je gegeten? — Iets ___, een Italiaans gerecht.",
             "lekkers", ["lekker", "lekkers"],
             "Na 'iets' krijgt het bijvoeglijk naamwoord een -s.", "dialogue", "freeform:iets-lekkers-dialoog"))
    A(_cloze("— Heb je nieuws? — Nee, niets ___.",
             "nieuws", ["nieuw", "nieuws"],
             "Na 'niets' krijgt het bijvoeglijk naamwoord een -s.", "dialogue", "freeform:niets-nieuws"))
    A(_cloze("— Heb je een leuke film gezien? — Ja, iets ___ over de natuur.",
             "moois", ["mooi", "moois"],
             "Na 'iets' + bijvoeglijk naamwoord → -s.", "dialogue", "freeform:iets-moois-film"))
    A(_cloze("— Vond je het romantisch? — Nee, niets ___.",
             "romantisch", ["romantisch", "romantischs"],
             "'Romantisch' eindigt al op /s/-klank — geen extra -s.", "s-ending", "freeform:niets-romantisch"))

    # Idioms / common combinations
    A(_cloze("Ik heb zin in iets ___.", "lekkers", ["lekker", "lekkers"],
             "'Zin in iets lekkers' = vaste combinatie. -s na 'iets'.", "idiom", "freeform:zin-in-iets-lekkers"))
    A(_cloze("Op vakantie wil je toch iets ___ doen?", "leuks", ["leuk", "leuks"],
             "Na 'iets' + bijvoeglijk naamwoord → -s.", "context", "freeform:vakantie-iets-leuks"))
    A(_cloze("Ze heeft mij iets ___ verteld dat ik nog niet wist.",
             "interessants", ["interessant", "interessants"],
             "Na 'iets' + bijvoeglijk naamwoord → -s.", "context", "freeform:iets-interessants-verteld"))
    A(_cloze("Heb je iets ___ tegen kou? Ik vroor toen ik in Amsterdam was.",
             "warms", ["warm", "warms"],
             "'iets warms' = 'something warm' (bv. kleding). -s na 'iets'.", "context", "freeform:iets-warms"))

    # Variation across pronouns
    A(_cloze("Hij heeft me weinig ___ verteld over zijn reis.",
             "spannends", ["spannend", "spannends"],
             "Ook na 'weinig' krijgt het bijvoeglijk naamwoord een -s.", "extension", "freeform:weinig-spannends"))
    A(_cloze("Op zijn verjaardag was er veel ___ te eten.",
             "lekkers", ["lekker", "lekkers"],
             "Ook na 'veel' krijgt het bijvoeglijk naamwoord een -s.", "extension", "freeform:veel-lekkers"))
    A(_cloze("Heb je iets ___ tegen hoofdpijn?", "goeds", ["goed", "goeds"],
             "Na 'iets' + bijvoeglijk naamwoord → -s. 'goed' → 'goeds'.", "idiom", "freeform:iets-goeds"))

    # S-ending variety
    A(_cloze("Ik heb iets ___ uit te leggen.", "vies", ["vies", "viess"],
             "'Vies' eindigt al op /s/-klank — geen extra -s.", "s-ending", "freeform:iets-vies"))
    A(_cloze("Wat hij zegt, is niets ___ dan een grap.",
             "anders", ["anders", "anderss"],
             "'Anders' eindigt al op -s; geen extra -s nodig.", "s-ending", "freeform:niets-anders"))
    A(_cloze("Er is iets ___ aan zijn gedrag.", "vreemds", ["vreemd", "vreemds"],
             "Na 'iets' + bijvoeglijk naamwoord → -s. 'vreemd' → 'vreemds'.", "context", "freeform:iets-vreemds"))

    # Questions
    A(_cloze("Heb je iets ___ gepland voor het weekend?", "leuks", ["leuk", "leuks"],
             "Na 'iets' + bijvoeglijk naamwoord → -s.", "question", "freeform:vraag-iets-leuks"))
    A(_cloze("Wil je nog iets ___ drinken?", "fris", ["fris", "friss"],
             "'Fris' eindigt al op /s/-klank — geen extra -s.", "s-ending", "freeform:iets-fris-drinken"))
    A(_cloze("Heb je niets ___ tegen de hitte?", "koeler", ["koeler", "koelers"],
             "Let op: comparatief 'koeler' krijgt geen -s. Het is een regelmatige uitzondering.", "comparative", "freeform:comparatief-geen-s"))
    A(_cloze("Heb je iets ___ te lezen?", "kleins", ["klein", "kleins"],
             "Na 'iets' + bijvoeglijk naamwoord → -s. 'klein' → 'kleins'.", "context", "freeform:iets-kleins-lezen"))

    # Negation
    A(_cloze("Hij wil niets ___ aan zijn computer veranderen.", "groots", ["groot", "groots"],
             "Na 'niets' + bijvoeglijk naamwoord → -s. 'groot' → 'groots'.", "context", "freeform:niets-groots"))
    A(_cloze("Er is helemaal niets ___ aan deze kamer.",
             "bijzonders", ["bijzonder", "bijzonders"],
             "Na 'niets' + bijvoeglijk naamwoord → -s. 'bijzonder' → 'bijzonders'.", "context", "freeform:niets-bijzonders"))

    # Variations
    A(_cloze("Mijn moeder maakt altijd iets ___ klaar als ik op bezoek kom.",
             "lekkers", ["lekker", "lekkers"],
             "Na 'iets' + bijvoeglijk naamwoord → -s.", "context", "freeform:iets-lekkers-moeder"))
    A(_cloze("Vind je het feest leuk? — Ja, er is iets ___ over.",
             "speciaals", ["speciaal", "speciaals"],
             "Na 'iets' + bijvoeglijk naamwoord → -s. 'speciaal' → 'speciaals'.", "context", "freeform:iets-speciaals"))

    return items


# ---- Topic: leren-kennen ---------------------------------------------------

def seed_leren_kennen() -> list[dict]:
    items: list[dict] = []
    A = items.append

    # Choice sets
    PP    = ["ontmoet", "gezien", "tegengekomen", "afgesproken", "leren kennen"]
    INF   = ["ontmoeten", "zien", "tegenkomen", "afspreken", "leren kennen"]
    PRES3 = ["ontmoet", "ziet", "komt tegen", "spreekt af", "leert kennen"]

    # Dialogue snippets
    A(_cloze("— Heb je Lisa al ___? — Ja, op het feestje van Anna.",
             "ontmoet", PP,
             "'Ontmoeten' = iemand voor het eerst leren kennen (vaak gepland of bij een gelegenheid).",
             "context", "freeform:lisa-ontmoet"))
    A(_cloze("Vandaag heb ik mijn oude collega in de supermarkt ___.",
             "tegengekomen", PP,
             "'Tegenkomen' = iemand bij toeval tegenkomen (niet gepland).",
             "context", "freeform:tegengekomen-supermarkt"))
    A(_cloze("Zullen we volgende week iets ___ om te gaan eten?",
             "afspreken", INF,
             "'Afspreken' = een afspraak / plan maken om elkaar te zien.",
             "context", "freeform:afspreken-eten"))
    A(_cloze("We hebben elkaar nu drie maanden, maar ik moet hem nog beter ___.",
             "leren kennen", INF,
             "'Leren kennen' = iemand geleidelijk (beter) leren kennen, over tijd.",
             "context", "freeform:beter-leren-kennen"))
    A(_cloze("Ik kijk ernaar uit om je morgen weer te ___.",
             "zien", INF,
             "'Zien' = iemand opnieuw zien (mensen die je al kent).",
             "context", "freeform:weer-zien"))

    # More past tense
    A(_cloze("Op de cursus Nederlands heb ik veel nieuwe mensen ___.",
             "ontmoet", PP,
             "Bij een georganiseerde gelegenheid → ontmoeten.",
             "context", "freeform:cursus-ontmoet"))
    A(_cloze("Gisteren kwam ik bij toeval een oude vriend ___ in de tram.",
             "tegen", ["aan", "uit", "tegen", "over", "weg"],
             "Let op: 'tegenkomen' is een scheidbaar werkwoord. De prefix 'tegen' staat hier achteraan.",
             "separable-verb", "freeform:tegenkomen-separable"))
    A(_cloze("We hebben ___ om vanavond samen naar de bioscoop te gaan.",
             "afgesproken", PP,
             "'Afspreken' (in perfectum: hebben + afgesproken).",
             "context", "freeform:bioscoop-afgesproken"))
    A(_cloze("Mijn man en ik hebben elkaar op een cursus Nederlands ___.",
             "leren kennen", PP,
             "'Leren kennen' in perfectum: 'hebben + leren kennen' (geen 'ge-' op kennen).",
             "context", "freeform:cursus-leren-kennen"))
    A(_cloze("Ik heb haar al een tijdje niet meer ___.",
             "gezien", PP,
             "'Zien' in perfectum: 'hebben + gezien'. (Geen contact in langere tijd.)",
             "context", "freeform:niet-meer-gezien"))

    # Present tense
    A(_cloze("Mijn baas ___ me elke ochtend bij de koffieautomaat.",
             "ontmoet", PRES3,
             "Hier 'ontmoeten' in een routinematige context — 3e persoon enkelvoud.",
             "present-tense", "freeform:baas-ontmoet"))
    A(_cloze("Mijn moeder ___ haar oude buurvrouw bijna elke week toevallig in de winkel.",
             "komt tegen", PRES3,
             "'Tegenkomen' = bij toeval ergens tegen iemand aanlopen.",
             "present-tense", "freeform:moeder-komt-tegen"))

    # Distinction tests — focus on the difference between two confusable verbs
    A(_cloze("Ik kende hem al van vroeger, maar ik wilde hem beter ___.",
             "leren kennen", INF,
             "'Iemand al kennen' vs. 'iemand (beter) leren kennen' = het proces van iemand (meer) leren kennen.",
             "distinction", "freeform:al-kennen-beter-leren-kennen"))
    A(_cloze("We ___ elkaar al jaren niet gezien. Wat een verrassing om jou hier te zien!",
             "hebben", ["hebben", "zijn", "kunnen", "moeten"],
             "Perfectum met 'zien' gebruikt 'hebben' als hulpwerkwoord. (Sommige bewegingswerkwoorden gebruiken 'zijn'.)",
             "auxiliary", "freeform:zien-hebben-auxiliary"))

    # Match exercise — a freeform variation on the textbook one
    items.append({
        "id": "",
        "type": "match",
        "prompt": "Match de zin met de reactie waarin een passend werkwoord wordt gebruikt.",
        "pairs": [
            {"left": "Heb je collega's al goed leren kennen?",
             "right": "Een beetje, maar ik werk hier nog maar twee weken."},
            {"left": "Waar hebben jullie elkaar ontmoet?",
             "right": "Op een muziekfestival in 2018."},
            {"left": "Zullen we morgen afspreken?",
             "right": "Goed idee, hoe laat schikt het jou?"},
            {"left": "Kom je hem vaak tegen?",
             "right": "Ja, hij woont in mijn straat."},
            {"left": "Wanneer zie je je zus weer?",
             "right": "Volgend weekend, ze komt naar Amsterdam."},
        ],
        "explanation": "Elk werkwoord past bij een specifiek soort ontmoeting: ontmoeten (vaak eerste keer), zien (vervolgmoment), tegenkomen (toevallig), afspreken (plannen), leren kennen (geleidelijk).",
        "tags": ["distinction", "review"],
        "source": "freeform:match-distinction",
        "confidence": "review",
    })

    # Reverse — given context, pick infinitive
    A(_cloze("Hij wilde haar bij een lunch ___.",
             "ontmoeten", INF,
             "Gepland eerste contact → ontmoeten.",
             "context", "freeform:lunch-ontmoeten"))
    A(_cloze("Het kostte tijd voor ze haar collega's echt konden ___.",
             "leren kennen", INF,
             "Proces van iemand beter leren kennen → leren kennen.",
             "context", "freeform:collegas-leren-kennen"))
    A(_cloze("Het is een kleine stad, dus je kunt hem zomaar ___.",
             "tegenkomen", INF,
             "Mogelijkheid op toevallig zien → tegenkomen.",
             "context", "freeform:kleine-stad-tegenkomen"))

    # Common error pitfalls
    A(_cloze("Ik wil je graag mijn ouders ___. Kom jij volgende week eten?",
             "voorstellen aan", ["voorstellen aan", "leren kennen", "ontmoeten met", "tegenkomen aan"],
             "Let op: 'jou voorstellen aan' is hier de natuurlijke uitdrukking. 'Leren kennen' kan ook maar minder vloeiend; 'ontmoeten met' bestaat niet in deze betekenis.",
             "pitfall", "freeform:voorstellen-aan-pitfall"))
    A(_cloze("Heb je in Amsterdam veel oude bekenden ___?",
             "ontmoet", PP,
             "Bij 'oude bekenden' is 'ontmoet' het normale werkwoord, ook al ken je ze al — het gaat om de gelegenheid.",
             "subtle", "freeform:oude-bekenden-ontmoet"))

    return items


# ---- Dispatch --------------------------------------------------------------

SEEDERS = {
    "liggen-staan-zitten": seed_liggen_staan_zitten,
    "iets-leuks":          seed_iets_leuks,
    "leren-kennen":        seed_leren_kennen,
}

ID_PREFIXES = {
    "liggen-staan-zitten": "lsz-rev",
    "iets-leuks":          "iel-rev",
    "leren-kennen":        "lk-rev",
}


def main(argv: list[str]) -> int:
    slug = argv[1] if len(argv) > 1 else "liggen-staan-zitten"
    if slug not in SEEDERS:
        raise SystemExit(f"No review seeds defined for topic '{slug}'. Known: {sorted(SEEDERS)}")

    topic_dir = TOPICS_DIR / slug
    ex_path = topic_dir / "exercises.json"
    data = json.loads(ex_path.read_text(encoding="utf-8")) if ex_path.exists() else []
    data = [it for it in data if it.get("confidence") != "review"]

    review = SEEDERS[slug]()
    prefix = ID_PREFIXES[slug]
    for n, it in enumerate(review, start=1):
        it["id"] = f"{prefix}-{n:03d}"
    data.extend(review)
    ex_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts = Counter(it["confidence"] for it in data)
    print(f"[{slug}] wrote {len(review)} review items. Total: {len(data)}.")
    print(f"  verified={counts.get('verified',0)}  template={counts.get('template',0)}  review={counts.get('review',0)}")

    # Update topics/index.json counts.
    index_path = TOPICS_DIR / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    for t in index:
        if t["slug"] == slug:
            t["counts"] = {k: counts.get(k, 0) for k in ("verified", "template", "review")}
            break
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
