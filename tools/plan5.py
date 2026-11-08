"""Plan n°5 : aperçu v2 en français, avec les nouveaux enregistrements (release V2).

Deux sources : clip="a" (13.21.54 : lobby, menus, passe de combat, caisses, vote de la map, rôle)
et clip="b" (13.43.25 : les parties). Même format que plan.py ; game = volume du son du jeu
pour ce plan (1 = discret, 3 = bien audible : tirs, sonar, victoire, caisse).
Sans voix : timing estimé. Avec la voix ElevenLabs, --voice cale tout sur ses syllabes.
"""

Y, R, P, C, G = "#FFE14D", "#FF3B3B", "#C77DFF", "#5CE1FF", "#5BE37A"

STYLE = dict(drift=0.035)

A, B = "a", "b"  # sources : a = lobby et menus (13.21.54), b = parties (13.43.25)


def sh(clip, src, **kw):
    return dict(clip=clip, src=src, game=kw.pop("game", 0.7), **kw)


SCRIPT = [
    # 1. accroche : la vraie vue du chasseur, dans le noir, puis un joueur repéré en rouge
    dict(
        text="Imagine devoir chasser des joueurs… sans rien voir !",
        hl={"chasser": R, "rien": Y, "voir": Y},
        shots=[
            sh(B, 371.6, w=1.0, cx=0.55),
            sh(B, 383.2, w=1.1, cx=0.5, fx=["punch"], game=1.6),
            sh(B, 375.0, w=1.0, cx=0.45, at="rien", fx=["flash"], game=2.2),
        ],
        sfx=[("^", "heartbeat", 0.6), ("voir", "boom", 0.8)],
        emoji=[("rien", "1f631")],
    ),
    # 2. le jeu : logo, ton avatar dans le lobby, les joueurs autour de la table
    dict(
        text="Bienvenue dans Blind Hunter, le jeu Roblox à faire avec tes potes !",
        hl={"blind": P, "hunter": P, "potes": Y},
        shots=[
            sh(A, 16.2, w=1.0, mode="fit", fz=1.15, fx=["flash"], game=0.4),
            sh(A, 22.6, w=1.0, cx=0.44, at="le", fx=["punch"]),
            sh(A, 212.0, w=1.0, cx=0.45, at="potes"),
        ],
        sfx=[("blind", "impact", 0.5), ("potes", "pop", 0.5)],
        emoji=[("potes", "1f3ae")],
    ),
    # 3. le vote de la map
    dict(
        text="Au début de la partie, tout le monde vote pour la map.",
        hl={"map": C},
        shots=[
            sh(B, 476.0, w=1.0, cx=0.45),
            sh(B, 486.0, w=1.4, mode="fit", fz=1.45, at="vote", game=1.2),
        ],
        sfx=[("vote", "click", 0.6), ("map", "pop", 0.5)],
        emoji=[("map", "1f5fa")],
    ),
    # 4. rôle Chasseur, puis le musée à mémoriser
    dict(
        text="Le chasseur a dix secondes pour mémoriser tous les recoins…",
        hl={"chasseur": R, "dix": Y, "secondes": Y},
        shots=[
            sh(B, 332.6, w=0.9, mode="fit", fz=1.6, fx=["punch"], game=1.5),
            sh(B, 337.6, w=1.0, cx=0.42, at="dix", speed=0.8),
            sh(B, 340.6, w=1.0, cx=0.5, at="recoins"),
        ],
        sfx=[("dix", "tick", 0.5), ("secondes", "tick", 0.5)],
        emoji=[("secondes", "23f3")],
    ),
    # 5. la vision rouge d'attente, puis le noir
    dict(
        text="et après, plus rien : le noir total !",
        hl={"rien": R, "noir": R},
        shots=[
            sh(B, 352.0, w=1.0, cx=0.5, fx=["glitch"], game=1.0),
            sh(B, 366.4, w=1.0, cx=0.55, at="noir", fx=["dark"], game=1.4),
        ],
        sfx=[("rien", "glitch", 0.45), ("noir", "whoosh_down", 0.5), ("total", "boom", 0.6)],
    ),
    # 6. les cacheurs : rôle, « Cache-toi ! », les joueurs qui courent se cacher
    dict(
        text="Pendant ce temps, les autres ont quinze secondes pour se cacher.",
        hl={"quinze": Y, "secondes": Y, "cacher": G},
        shots=[
            sh(B, 510.6, w=0.8, mode="fit", fz=1.6, game=1.2),
            sh(B, 527.0, w=1.0, cx=0.45, at="quinze", game=1.0),
            sh(B, 530.2, w=1.0, cx=0.82, at="cacher", game=1.2),
        ],
        sfx=[("quinze", "tick", 0.5), ("secondes", "tick", 0.5), ("cacher", "heartbeat", 0.5)],
        emoji=[("cacher", "1f92b")],
    ),
    # 7. « CHASSE ! », la vue aveugle, le sonar révèle les dinosaures
    dict(
        text="Puis la chasse commence : le chasseur ne voit qu'avec son sonar.",
        hl={"chasse": R, "commence": R, "sonar": P},
        shots=[
            sh(B, 369.2, w=1.0, cx=0.5, fx=["punch"], game=2.6),
            sh(B, 372.4, w=1.0, cx=0.55, at="le", game=1.6),
            sh(B, 391.4, w=1.3, cx=0.45, at="sonar", fx=["flash"], game=3.0),
        ],
        sfx=[("commence", "impact", 0.7), ("sonar", "sonar", 0.5)],
        emoji=[("sonar", "1f50a")],
    ),
    # 8. joueur repéré en rouge, puis l'élimination vue du cacheur
    dict(
        text="Au moindre bruit, il te voit en rouge… et c'est fini pour toi !",
        hl={"bruit": Y, "rouge": R, "fini": R},
        shots=[
            sh(B, 396.0, w=1.0, cx=0.45, game=2.0),
            sh(B, 404.0, w=1.0, cx=0.5, at="rouge", fx=["punch"], game=2.4),
            sh(B, 604.2, w=1.2, cx=0.5, at="fini", fx=["shake"], game=2.8),
        ],
        sfx=[("bruit", "tick", 0.5), ("fini", "boom", 0.8)],
        emoji=[("fini", "1f480")],
    ),
    # 9. les deux façons de gagner : survivre (vue du cacheur, le chasseur passe), ou victoire du chasseur
    dict(
        text="Caché ? Survis deux minutes. Chasseur ? Élimine tout le monde !",
        hl={"caché": G, "deux": Y, "minutes": Y, "chasseur": R, "tout": Y, "monde": Y},
        shots=[
            sh(B, 549.0, w=1.2, cx=0.48, game=1.0),
            sh(B, 413.4, w=1.0, cx=0.55, at="chasseur", game=2.6),
            sh(B, 420.2, w=1.1, mode="fit", fz=1.5, at="tout", fx=["flash"], game=3.0),
        ],
        sfx=[("deux", "tick", 0.5), ("minutes", "tick", 0.5), ("monde", "bling", 0.6)],
        emoji=[("monde", "1f3c6")],
    ),
    # 10. passe de combat, caisse Secret, revolver qui sort, l'Eclipse
    dict(
        text="Monte dans le passe de combat, ouvre des caisses et débloque des dizaines de revolvers, comme l'Eclipse !",
        hl={"passe": Y, "combat": Y, "caisses": P, "revolvers": C, "l'eclipse": P},
        shots=[
            sh(A, 33.0, w=1.0, mode="fit", fz=1.25, game=0.6),
            sh(A, 120.2, w=1.0, cx=0.5, at="caisses", fx=["punch"], game=2.4),
            sh(A, 126.2, w=0.9, cx=0.5, at="débloque", game=2.6),
            sh(A, 128.4, w=1.0, mode="fit", fz=1.3, at="revolvers", fx=["flash"], game=2.6),
            sh(A, 66.4, w=1.2, mode="fit", fz=1.55, cx=0.4, at="l'eclipse", fx=["punch"], game=0.6),
        ],
        sfx=[("passe", "pop", 0.45), ("caisses", "whoosh", 0.4), ("revolvers", "bling", 0.5)],
        emoji=[("caisses", "1f4e6"), ("l'eclipse", "1f48e")],
    ),
    # 11. le reroll de style, jusqu'au violet
    dict(
        text="Change de style… et avec beaucoup de chance, tombe sur un style secret !",
        hl={"style": C, "chance": G, "secret": P},
        shots=[
            sh(A, 96.0, w=1.0, cx=0.5, game=1.2),
            sh(A, 99.0, w=1.0, cx=0.5, at="chance", game=1.6),
            sh(A, 108.6, w=1.3, cx=0.5, at="secret", fx=["flash"], game=2.4),
        ],
        sfx=[("chance", "tick", 0.4), ("secret", "bling", 0.6)],
        emoji=[("secret", "2728")],
    ),
    # 12. la barre de recherche Roblox
    dict(
        text="Pour jouer, tape Blind Hunter dans la barre de recherche Roblox.",
        hl={"blind": P, "hunter": P, "roblox": Y},
        shots=[sh(A, 59.4, w=1.0, cx=0.44, game=0.4)],
        searchbar="tape",
        sfx=[("roblox", "pop", 0.5)],
        emoji=[("recherche", "1f50d")],
    ),
    # 13. carte du jeu
    dict(
        text="Et abonne-toi pour ne rien rater !",
        hl={"abonne-toi": R},
        shots=[
            sh(A, 23.0, w=1.0, cx=0.44, fx=["blur", "flash"], suby=0.8, game=0.3,
               gamecard=dict(title="Blind Hunter", clip=A, thumb=23.0, thumb_cx=0.44, y=0.44, scale=0.85)),
        ],
        sfx=[("^", "impact", 0.5), ("abonne-toi", "pop", 0.5)],
        emoji=[("abonne-toi", "1f514")],
    ),
]

SEARCH_TEXT = "Blind Hunter"

# début des phrases 2 à 13 dans la voix française (ElevenLabs 2026-11-08 13:55), posés sur ses pauses
VOICE_BREAKS = [3.2, 7.2, 9.75, 12.95, 15.9, 18.8, 22.4, 25.95, 30.05, 35.2, 38.9, 42.25]
TAIL = 2.2

# Texte à coller dans ElevenLabs (modèle Eleven v3, voix « Eric - Dynamic and Energetic ») :
# les balises entre crochets règlent le ton et ne sont pas lues ; les MAJUSCULES appuient le mot.
SCRIPT_ELEVENLABS = """\
[excited] Imagine devoir chasser des joueurs… sans RIEN voir !
[enthusiastic] Bienvenue dans BLIND HUNTER, le jeu Roblox à faire avec tes potes !
[energetic] Au début de la partie, tout le monde vote pour la map.
[excited] Le chasseur a DIX secondes pour mémoriser tous les recoins…
[energetic] et après, plus RIEN : le NOIR total !
[excited] Pendant ce temps, les autres ont QUINZE secondes pour se cacher.
[energetic] Puis la chasse COMMENCE : le chasseur ne voit qu'avec son SONAR.
[excited] Au moindre bruit, il te voit en ROUGE… et c'est FINI pour toi !
[energetic] Caché ? Survis DEUX minutes. Chasseur ? Élimine TOUT le monde !
[enthusiastic] Monte dans le PASSE DE COMBAT, ouvre des CAISSES et débloque des dizaines de revolvers, comme l'ECLIPSE !
[excited] Change de style… et avec beaucoup de chance, tombe sur un style SECRET !
[energetic] Pour jouer, tape BLIND HUNTER dans la barre de recherche Roblox.
[excited] Et abonne-toi pour ne rien rater !
"""
