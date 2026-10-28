"""Plan n°2 : présentation claire du jeu, inspirée du 2e TikTok exemple.

Plans longs et larges pour bien voir le jeu à chaque étape, sous-titres sobres
(police condensée blanche), coupes franches, carte de jeu Roblox à la fin.
Même format que plan.py (voir sa documentation).
"""

STYLE = dict(
    font="Anton-Regular.ttf", weight=None, size=112, stroke=7, sub_y=0.66,
    pop="soft", whip=False, auto_whoosh=False, drift=0.03,
)

SCRIPT = [
    dict(
        text="Voici un jeu Roblox à faire absolument avec tes potes.",
        shots=[
            dict(src=267.0, w=1.0, cx=0.5),
            dict(src=388.0, w=1.0, cx=0.5),
        ],
    ),
    dict(
        text="Dans Blind Hunter, un joueur devient le chasseur… mais il est complètement aveugle.",
        shots=[
            dict(src=162.0, w=1.0, cx=0.5),
            dict(src=248.8, w=1.0, at="mais"),
        ],
    ),
    dict(
        text="Au début de la partie, il a dix secondes pour mémoriser la map.",
        shots=[dict(src=212.5, w=1.0, cx=0.52)],
    ),
    dict(
        text="Pendant ce temps, les autres ont quinze secondes pour se cacher.",
        shots=[dict(src=411.6, w=1.0, cx=0.45)],
    ),
    dict(
        text="Ensuite, la chasse commence : le chasseur ne voit plus rien, à part avec son sonar.",
        shots=[
            dict(src=244.4, w=1.0, speed=2.0, z=1.2, cy=0.45, suby=0.74),
            dict(src=249.0, w=1.0, at="le"),
            dict(src=322.3, w=1.4, at="sonar"),
        ],
    ),
    dict(
        text="Au moindre bruit, il te voit en rouge et peut t'éliminer.",
        shots=[
            dict(src=257.9, w=1.0, cx=0.72),
            dict(src=262.0, w=1.6, cx=0.55, at="rouge"),
        ],
    ),
    dict(
        text="Si tu es caché, le but est de survivre deux minutes sans te faire attraper.",
        shots=[dict(src=429.7, w=1.0, cx=0.55)],
    ),
    dict(
        text="Et si tu es le chasseur, tu dois trouver tout le monde pour gagner.",
        shots=[
            dict(src=336.5, w=1.6, cx=0.45),
            dict(src=343.2, w=1.0, cx=0.5, at="gagner"),
        ],
    ),
    dict(
        text="Le jeu s'appelle Blind Hunter.",
        shots=[
            dict(src=128.5, w=1.0, cx=0.47, fx=["blur"],
                 gamecard=dict(title="Blind Hunter", thumb=136.0, thumb_cx=0.47)),
        ],
        sfx=[("blind", "pop", 0.5)],
    ),
]

SEARCH_TEXT = ""
TAIL = 2.2
MUSIC_GAIN = 0.2
