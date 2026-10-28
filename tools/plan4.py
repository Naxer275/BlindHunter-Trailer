"""Plan n°4 : « la vidéo aveugle ».

La vidéo voit comme le chasseur : écran noir, chaque son envoie une onde de sonar
qui révèle le décor un instant, les joueurs repérés brillent en rouge. Passage
muet où les pings accélèrent, climax en pleine lumière, puis retournement en vue
du cacheur. Voix assemblée depuis les deux voix ElevenLabs (voir plan3.py).

Clés propres à ce plan :
  blind=True (plan)         vision aveugle, pc = centre des ondes (0..1)
  pulses="words" | [s, …]   ondes sur chaque mot, ou aux instants donnés (avec ping)
  silent=durée (phrase)     passage sans voix ; texts=[(début, durée, texte, couleur)]
  fx "redpulse"             battement de cœur rouge au bord de l'écran
"""
from plan import SCRIPT as S1
from plan2 import SCRIPT as S2

Y, R, P = "#FFE14D", "#FF3B3B", "#C77DFF"

VOICES = {"v1": "plan", "v2": "plan2"}
STYLE = dict(whip=False, auto_whoosh=False, drift=0.035)


def line(src, key, idx, **kw):
    return dict(text=src[idx]["text"], voice=(key, idx), **kw)


ACCEL = [0.05, 1.0, 1.8, 2.45, 3.0, 3.45, 3.8, 4.1, 4.35, 4.57, 4.77, 4.95, 5.1, 5.24]

SCRIPT = [
    # 1. noir total, le joueur rouge brille, chaque mot envoie une onde
    line(S1, "v1", 0,
         hl={"chasser": R, "rien": Y, "voir": Y},
         shots=[
             dict(src=336.95, w=1.4, cx=0.45, speed=0.5, blind=True),
             dict(src=337.9, w=1.4, speed=0.5, at="sans", blind=True, game=1.6),
         ],
         pulses="words",
         sfx=[("^", "drone", 0.5), ("voir", "boom", 0.8)]),
    # 2. le sonar
    line(S1, "v1", 7,
         hl={"sonar": P, "repérer": Y},
         shots=[dict(src=266.6, w=1.0, cx=0.5, blind=True)],
         pulses="words",
         sfx=[("sonar", "sonar", 0.5)]),
    # 3. silence : les pings accélèrent, le joueur rouge se rapproche
    dict(text="", silent=5.5,
         shots=[
             dict(src=254.8, w=1.2, cx=0.6, blind=True),
             dict(src=257.6, w=1.4, cx=0.72, blind=True),
         ],
         pulses=ACCEL, ping_gain=0.5,
         texts=[(0.3, 2.2, "Écoute.", "#FFFFFF"), (3.0, 2.5, "Il est tout près.", R)],
         sfx=[(o, "heartbeat", 0.55) for o in (0.0, 1.1, 2.0, 2.7, 3.3, 3.8, 4.2, 4.6, 4.95, 5.25)]),
    # 4. climax : pleine lumière pour la première fois
    line(S1, "v1", 8,
         hl={"bruit": Y, "rouge": R, "fini": R},
         shots=[
             dict(src=261.9, w=1.0, cx=0.55, speed=0.6, blind=True),
             dict(src=263.2, w=1.0, speed=0.5, at="fini", fx=["flash", "shake"], game=1.8),
         ],
         pulses="words",
         sfx=[("fini", "boom", 1.0), ("fini", "impact", 0.6)],
         emoji=[("fini", "1f480")]),
    # 5. retournement : vue du cacheur, battement rouge
    dict(text="", silent=3.4,
         shots=[
             dict(src=430.0, w=1.6, cx=0.55, fx=["redpulse"]),
             dict(src=473.0, w=1.0, cx=0.5, fx=["redpulse", "punch"]),
         ],
         texts=[(0.15, 3.2, "Maintenant, c'est TOI qui te caches.", Y)],
         sfx=[(o, "heartbeat", 0.7) for o in (0.0, 0.62, 1.25, 1.87, 2.5, 3.0)] + [(3.2, "glitch", 0.5)]),
    # 6. révélation du jeu
    line(S2, "v2", 8,
         hl={"blind": P, "hunter": P},
         shots=[
             dict(src=128.5, w=1.0, cx=0.47, fx=["blur", "flash"], suby=0.8,
                  gamecard=dict(title="Blind Hunter", thumb=136.0, thumb_cx=0.47, y=0.44, scale=0.85)),
         ],
         sfx=[("blind", "pop", 0.5), ("^", "impact", 0.5)]),
]

HEADERS = [
    (0, 1, "Monte le son : cette vidéo est aveugle", "1f50a"),
    (5, 5, "T'as vu combien de joueurs en rouge ?", "1f447"),
]

SEARCH_TEXT = ""
TAIL = 2.0
