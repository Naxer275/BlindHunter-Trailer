"""Plan n°3 : version courte pensée pour percer (accroche immédiate, ~23 s, boucle).

La voix off est assemblée à partir des phrases des deux voix ElevenLabs déjà
générées : "voice": (clé, n° de phrase dans le plan source). Les clés sont
définies dans VOICES et les fichiers passés avec --voices v1=... v2=...
HEADERS : bandeaux de texte en haut de l'écran (de la phrase a à la phrase b).
"""
from plan import SCRIPT as S1
from plan2 import SCRIPT as S2

Y, R, P, C = "#FFE14D", "#FF3B3B", "#C77DFF", "#5CE1FF"

VOICES = {"v1": "plan", "v2": "plan2"}

STYLE = dict(whip=False, auto_whoosh=True, drift=0.04)


def line(src, key, idx, **kw):
    return dict(text=src[idx]["text"], voice=(key, idx), **kw)


SCRIPT = [
    # accroche : le joueur rouge surgit du noir, tir au ralenti
    line(S1, "v1", 0,
         hl={"chasser": R, "rien": Y, "voir": Y},
         shots=[
             dict(src=336.95, w=1.4, cx=0.45),
             dict(src=337.8, w=1.4, speed=0.5, at="sans", fx=["punch"], game=1.6),
         ],
         sfx=[("^", "heartbeat", 0.6), ("voir", "boom", 0.9)],
         emoji=[("voir", "1f631")]),
    line(S1, "v1", 3,
         hl={"chasseur": R, "dix": Y, "secondes": Y},
         shots=[dict(src=212.5, w=1.0, cx=0.52, fx=["punch"])],
         sfx=[("dix", "tick", 0.5), ("secondes", "tick", 0.5)],
         emoji=[("dix", "23f3")]),
    line(S1, "v1", 4,
         hl={"rien": Y, "noir": R},
         shots=[
             dict(src=225.6, w=1.0, cx=0.5, fx=["punch"]),
             dict(src=228.4, w=0.8, cx=0.6, at="plus", fx=["glitch"]),
             dict(src=249.2, w=1.0, at="noir", fx=["dark", "shake"]),
         ],
         sfx=[("plus", "glitch", 0.5), ("noir", "boom", 0.9)]),
    line(S1, "v1", 5,
         hl={"quinze": Y, "cacher": Y},
         shots=[
             dict(src=388.0, w=1.0, cx=0.5, fx=["punch"]),
             dict(src=412.0, w=1.0, cx=0.45, fx=["punch"]),
         ],
         sfx=[("quinze", "heartbeat", 0.6), ("cacher", "pop", 0.5)],
         emoji=[("cacher", "1f92b")]),
    line(S1, "v1", 7,
         hl={"sonar": P, "repérer": Y},
         shots=[dict(src=322.3, w=1.0, cx=0.5, fx=["punch"])],
         sfx=[("sonar", "sonar", 0.6)],
         emoji=[("repérer", "1f440")]),
    line(S1, "v1", 8,
         hl={"bruit": Y, "rouge": R, "fini": R},
         shots=[
             dict(src=257.9, w=1.0, cx=0.75, fx=["punch"]),
             dict(src=262.0, w=1.2, cx=0.55, at="rouge", fx=["punch"]),
             dict(src=263.2, w=1.0, speed=0.5, at="fini", fx=["flash", "shake"], game=1.6),
         ],
         sfx=[("bruit", "tick", 0.5), ("rouge", "heartbeat", 0.5), ("fini", "boom", 0.9)],
         emoji=[("fini", "1f480")]),
    line(S1, "v1", 11,
         hl={"toi": Y, "game": R, "over": R},
         shots=[
             dict(src=446.0, w=0.8, cx=0.5, fx=["punch"]),
             dict(src=473.0, w=1.0, cx=0.5, fx=["punch"]),
             dict(src=498.0, w=1.0, cx=0.5, at="game", fx=["flash"]),
         ],
         sfx=[("attraper", "scratch", 0.5), ("game", "boom", 0.8)],
         emoji=[("over", "1f62d")]),
    line(S2, "v2", 8,
         hl={"blind": P, "hunter": P},
         shots=[
             dict(src=128.5, w=1.0, cx=0.47, fx=["blur"], suby=0.8,
                  gamecard=dict(title="Blind Hunter", thumb=136.0, thumb_cx=0.47, y=0.44, scale=0.85)),
         ],
         sfx=[("blind", "pop", 0.5)]),
]

HEADERS = [
    (0, 6, "Le chasseur est AVEUGLE dans ce jeu Roblox", "1f631"),
    (7, 7, "Tu serais chasseur ou caché ?", "1f447"),
]

SEARCH_TEXT = ""
TAIL = 1.8
