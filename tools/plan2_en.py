"""Plan n°2 en anglais : même montage que plan2.py (mêmes plans, même style), texte et effets
sonores calés sur la voix anglaise. Les phrases doivent rester mot pour mot celles lues par
ElevenLabs (voir SCRIPT_ELEVENLABS en bas) : les sous-titres sont calés sur les syllabes."""

from plan2 import STYLE, TAIL, MUSIC_GAIN  # noqa: F401

SCRIPT = [
    dict(
        text="Here's a Roblox game you have to play with your friends.",
        shots=[
            dict(src=267.0, w=1.0, cx=0.5),
            dict(src=388.0, w=1.0, cx=0.5),
        ],
        sfx=[("^", "heartbeat", 0.5), ("friends", "pop", 0.5)],
    ),
    dict(
        text="In Blind Hunter, one player becomes the hunter… but they can't see a thing.",
        shots=[
            dict(src=162.0, w=1.0, cx=0.5),
            dict(src=248.8, w=1.0, at="but"),
        ],
        sfx=[("but", "whoosh_down", 0.4), ("thing", "boom", 0.8)],
    ),
    dict(
        text="At the start, the hunter gets ten seconds to memorize the map.",
        shots=[dict(src=212.5, w=1.0, cx=0.52)],
        sfx=[("ten", "tick", 0.5), ("seconds", "tick", 0.5), ("map", "pop", 0.4)],
    ),
    dict(
        text="Meanwhile, everyone else has fifteen seconds to hide.",
        shots=[dict(src=411.6, w=1.0, cx=0.45)],
        sfx=[("fifteen", "tick", 0.5), ("seconds", "tick", 0.5), ("hide", "heartbeat", 0.5)],
    ),
    dict(
        text="Then the hunt begins: the hunter sees nothing, except with their sonar.",
        shots=[
            dict(src=244.4, w=1.0, speed=2.0, z=1.2, cy=0.45, suby=0.74),
            dict(src=249.0, w=1.0, at="sees"),
            dict(src=322.3, w=1.4, at="sonar"),
        ],
        sfx=[("begins", "impact", 0.7), ("nothing", "glitch", 0.4), ("sonar", "sonar", 0.6)],
    ),
    dict(
        text="One tiny sound, and they see you in red… and they can eliminate you.",
        shots=[
            dict(src=257.9, w=1.0, cx=0.72),
            dict(src=262.0, w=1.6, cx=0.55, at="red"),
        ],
        sfx=[("sound", "tick", 0.5), ("red", "heartbeat", 0.5), ("eliminate", "boom", 0.8)],
    ),
    dict(
        text="If you're hiding, your goal is to survive two minutes without getting caught.",
        shots=[dict(src=429.7, w=1.0, cx=0.55)],
        sfx=[("two", "tick", 0.5), ("minutes", "tick", 0.5), ("caught", "scratch", 0.4)],
    ),
    dict(
        text="And if you're the hunter, you have to find everyone to win.",
        shots=[
            dict(src=336.5, w=1.6, cx=0.45),
            dict(src=343.2, w=1.0, cx=0.5, at="everyone"),
        ],
        sfx=[("find", "whoosh", 0.35), ("win", "bling", 0.7)],
    ),
    dict(
        text="The game is called Blind Hunter.",
        shots=[
            dict(src=128.5, w=1.0, cx=0.47, fx=["blur"],
                 gamecard=dict(title="Blind Hunter", thumb=136.0, thumb_cx=0.47)),
        ],
        sfx=[("blind", "pop", 0.5)],
    ),
]

SEARCH_TEXT = ""

# Script à coller dans ElevenLabs (modèle Eleven v3, voix « Eric - Dynamic and Energetic ») :
# les balises entre crochets règlent le ton et ne sont pas lues ; les MAJUSCULES appuient le mot.
SCRIPT_ELEVENLABS = """\
[excited] Here's a Roblox game you HAVE to play with your friends.
[enthusiastic] In Blind Hunter, one player becomes the hunter… [excited] but they can't see a THING!
[enthusiastic] At the start, the hunter gets TEN seconds to memorize the map.
[energetic] Meanwhile, everyone else has FIFTEEN seconds to hide.
[excited] Then the hunt BEGINS: the hunter sees NOTHING, except with their sonar.
[energetic] One tiny sound, and they see you in RED… and they can ELIMINATE you.
[energetic] If you're hiding, your goal is to survive TWO minutes without getting caught.
[confident] And if you're the hunter, you have to find EVERYONE to win.
[excited] The game is called… BLIND HUNTER!
"""
