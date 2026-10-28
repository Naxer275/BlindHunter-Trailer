"""Plan de montage du TikTok Blind Hunter.

Chaque phrase de la voix off a ses plans (timecodes dans BlindHunterGameplay.mp4),
ses mots surlignés, ses effets sonores et ses emojis. Les durées des plans sont
réparties automatiquement sur la durée réelle de la phrase dans la voix.

Plan :  src = début dans la vidéo source (s), w = poids de durée,
        mode = "crop" (plein écran vertical) ou "fit" (image entière sur fond flou),
        cx/cy = point visé (0..1), z = zoom, pan = (cx début, cx fin),
        speed = vitesse (0.5 = ralenti), at = mot où le plan doit commencer,
        fx = effets à l'entrée du plan : punch, flash, shake, glitch, dark, blur,
        card = (titre, sous-titre) affichés en grand (carton de fin),
        maxsrc = secondes de source utilisées avant de figer l'image,
        suby = hauteur des sous-titres pour ce plan (0..1, défaut 0.56).
Effets sonores / emojis : (mot, nom, gain) ; "^" = début de phrase.
"""

Y, R, P, C = "#FFE14D", "#FF3B3B", "#C77DFF", "#5CE1FF"

SCRIPT = [
    dict(
        text="Imagine devoir chasser des joueurs… sans rien voir.",
        hl={"chasser": R, "rien": Y, "voir": Y},
        shots=[
            dict(src=248.6, w=0.8),
            dict(src=336.4, w=1.3, cx=0.45, fx=["punch"]),
            dict(src=337.8, w=1.3, speed=0.5, fx=["punch"], game=1.6),
        ],
        sfx=[("^", "heartbeat", 0.7), ("rien", "whoosh", 0.4), ("voir", "boom", 0.8)],
        emoji=[("rien", "1f631")],
    ),
    dict(
        text="Bienvenue dans Blind Hunter.",
        hl={"blind": P, "hunter": P},
        shots=[
            dict(src=14.6, w=1.0, mode="fit", fz=1.25, fx=["flash"]),
            dict(src=136.0, w=1.0, cx=0.47, fx=["punch"]),
        ],
        sfx=[],
    ),
    dict(
        text="Au début de chaque partie, tout le monde vote pour la map.",
        hl={"vote": Y, "map": Y},
        shots=[
            dict(src=162.0, w=1.0, cx=0.5, fx=["punch"]),
            dict(src=169.0, w=1.6, pan=(0.28, 0.72), fx=["punch"]),
            dict(src=176.0, w=1.2, cx=0.5, cy=0.47, z=1.6, fx=["punch"]),
        ],
        sfx=[("^", "whoosh", 0.35), ("map", "pop", 0.6)],
    ),
    dict(
        text="Si tu es le chasseur, tu as dix secondes pour mémoriser les lieux.",
        hl={"chasseur": R, "dix": Y, "secondes": Y},
        shots=[
            dict(src=205.0, w=0.6, z=1.2, cy=0.45, suby=0.72, fx=["punch"]),
            dict(src=212.6, w=1.2, cx=0.5, fx=["punch"]),
            dict(src=214.4, w=1.1, cx=0.62, fx=["punch"]),
            dict(src=217.6, w=1.0, cx=0.45, fx=["punch"]),
        ],
        sfx=[("^", "whoosh", 0.35), ("dix", "tick", 0.5), ("secondes", "tick", 0.5)],
        emoji=[("dix", "23f3")],
    ),
    dict(
        text="Et après… plus rien. Tout devient noir.",
        hl={"rien": Y, "noir": R},
        shots=[
            dict(src=225.6, w=1.2, cx=0.5, fx=["punch"]),
            dict(src=228.4, w=0.8, cx=0.6, at="plus", fx=["glitch"]),
            dict(src=249.2, w=1.0, at="noir", fx=["dark", "shake"]),
        ],
        sfx=[("plus", "glitch", 0.5), ("noir", "boom", 0.9)],
        music_break="plus",
    ),
    dict(
        text="Les autres, eux, n'ont que quinze secondes pour se cacher.",
        hl={"quinze": Y, "cacher": Y},
        shots=[
            dict(src=399.0, w=0.6, z=1.2, cy=0.45, suby=0.72, fx=["punch"]),
            dict(src=388.0, w=1.2, cx=0.5, fx=["punch"]),
            dict(src=412.0, w=1.3, cx=0.45, fx=["punch"]),
        ],
        sfx=[("^", "whoosh", 0.35), ("quinze", "heartbeat", 0.6), ("cacher", "pop", 0.6)],
        emoji=[("cacher", "1f92b")],
    ),
    dict(
        text="Ensuite, la chasse commence.",
        hl={"chasse": R, "commence": R},
        shots=[
            dict(src=244.3, w=1.0, speed=1.8, z=1.2, cy=0.45, suby=0.72, fx=["punch"]),
            dict(src=248.8, w=0.6, at="commence", fx=["flash", "shake"]),
        ],
        sfx=[("commence", "impact", 0.8)],
        music_drop="commence",
    ),
    dict(
        text="Le chasseur n'a que son sonar pour repérer les autres.",
        hl={"sonar": P, "repérer": Y},
        shots=[
            dict(src=322.3, w=1.5, cx=0.5, fx=["punch"]),
            dict(src=266.6, w=1.0, cx=0.5, fx=["punch"]),
            dict(src=250.4, w=1.2, cx=0.62, fx=["punch"]),
        ],
        sfx=[("sonar", "sonar", 0.6)],
        emoji=[("repérer", "1f440")],
    ),
    dict(
        text="Au moindre bruit, il te voit en rouge… et là, c'est fini.",
        hl={"bruit": Y, "rouge": R, "fini": R},
        shots=[
            dict(src=257.9, w=1.0, cx=0.78, fx=["punch"]),
            dict(src=262.0, w=1.2, cx=0.55, fx=["punch"]),
            dict(src=263.2, w=1.0, speed=0.5, at="fini", fx=["flash", "shake"], game=1.6),
        ],
        sfx=[("bruit", "tick", 0.5), ("rouge", "heartbeat", 0.5), ("fini", "boom", 0.9)],
        emoji=[("fini", "1f480")],
    ),
    dict(
        text="Il a deux minutes pour éliminer tout le monde.",
        hl={"deux": Y, "minutes": Y, "éliminer": R},
        shots=[
            dict(src=426.0, w=1.0, cx=0.56, z=1.1, maxsrc=1.3, fx=["punch"]),
            dict(src=267.0, w=1.2, cx=0.5, fx=["punch"]),
            dict(src=270.6, w=1.1, cx=0.45, fx=["punch"]),
        ],
        sfx=[("minutes", "tick", 0.5), ("éliminer", "whoosh", 0.4)],
        emoji=[("éliminer", "1f3af")],
    ),
    dict(
        text="S'il réussit, c'est la victoire.",
        hl={"victoire": Y},
        shots=[
            dict(src=338.0, w=0.8, speed=0.5, fx=["punch"], game=1.4),
            dict(src=343.2, w=1.4, cx=0.5, at="victoire", fx=["flash"]),
        ],
        sfx=[("victoire", "bling", 0.7)],
        emoji=[("victoire", "1f3c6")],
    ),
    dict(
        text="Et si c'est toi qui te fais attraper… game over.",
        hl={"toi": Y, "game": R, "over": R},
        shots=[
            dict(src=446.0, w=0.9, cx=0.5, fx=["punch"]),
            dict(src=473.0, w=1.0, cx=0.5, fx=["punch"]),
            dict(src=476.4, w=0.6, fx=["shake"]),
            dict(src=498.0, w=1.0, cx=0.5, at="game", fx=["flash"]),
        ],
        sfx=[("attraper", "scratch", 0.5), ("game", "boom", 0.8)],
        emoji=[("over", "1f62d")],
    ),
    dict(
        text="Chaque partie te rapporte des Shards pour ouvrir des caisses…",
        hl={"shards": C, "caisses": Y},
        shots=[
            dict(src=343.4, w=1.1, cx=0.15, cy=0.7, z=1.4, fx=["punch"]),
            dict(src=69.6, w=0.9, cx=0.5, fx=["punch"]),
            dict(src=73.2, w=1.0, speed=2.0, fx=["punch"]),
            dict(src=78.0, w=1.0, cx=0.5, fx=["flash"]),
        ],
        sfx=[("shards", "ding", 0.4), ("caisses", "whoosh", 0.4)],
        emoji=[("shards", "1f48e")],
    ),
    dict(
        text="et débloquer des revolvers de malade, comme le Prism ou l'Eclipse.",
        hl={"revolvers": Y, "prism": Y, "l'eclipse": P},
        shots=[
            dict(src=80.4, w=1.2, cx=0.45, fx=["punch"]),
            dict(src=37.6, w=0.5, cx=0.22, fx=["punch"]),
            dict(src=39.1, w=0.5, cx=0.22, fx=["punch"]),
            dict(src=43.6, w=0.8, cx=0.24, at="prism", fx=["punch"]),
            dict(src=90.5, w=0.9, cx=0.22, at="l'eclipse", fx=["punch"]),
        ],
        sfx=[("revolvers", "whoosh", 0.4), ("prism", "pop", 0.6), ("l'eclipse", "bling", 0.6)],
        emoji=[("malade", "1f525")],
    ),
    dict(
        text="Et avec un peu de chance, tu peux même tomber sur un style secret.",
        hl={"chance": Y, "secret": P},
        shots=[
            dict(src=55.0, w=1.0, cx=0.5, fx=["punch"]),
            dict(src=58.1, w=0.7, z=1.1, suby=0.66),
            dict(src=59.0, w=1.2, cx=0.5, fx=["punch"]),
            dict(src=63.0, w=1.3, cx=0.5, at="secret", fx=["flash"]),
        ],
        sfx=[("chance", "whoosh", 0.35), ("secret", "impact", 0.7), ("secret", "bling", 0.5)],
        emoji=[("secret", "2728")],
    ),
    dict(
        text="Alors si toi aussi tu veux tester, tape Blind Hunter dans la barre de recherche Roblox.",
        hl={"blind": P, "hunter": P, "roblox": Y},
        shots=[
            dict(src=0.5, w=1.3, cx=0.42, fx=["punch"]),
            dict(src=145.0, w=1.6, cx=0.47, at="tape", fx=["punch"]),
            dict(src=5.0, w=1.0, mode="fit", fz=1.6, at="recherche", fx=["flash"]),
        ],
        sfx=[("tape", "click", 0.5), ("roblox", "pop", 0.6)],
        emoji=[("recherche", "1f50d")],
        searchbar="tape",
    ),
    dict(
        text="Et abonne-toi pour plus de jeux comme ça.",
        hl={"abonne-toi": R},
        shots=[
            dict(src=343.6, w=1.0, cx=0.5, fx=["punch"]),
            dict(src=128.5, w=1.6, cx=0.47, card=("BLIND HUNTER", "DISPONIBLE SUR ROBLOX"), fx=["flash", "blur"]),
        ],
        sfx=[("abonne-toi", "pop", 0.6)],
        emoji=[("abonne-toi", "1f447")],
    ),
]

SEARCH_TEXT = "Blind Hunter"
TAIL = 1.4  # secondes d'image après la dernière phrase
