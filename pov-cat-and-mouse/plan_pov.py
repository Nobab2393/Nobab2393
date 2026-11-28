"""Timeline for POV — a first-person slapstick chase through one house.

No narration, so nothing here is driven by a voice file: the picture is a fixed beat sheet and the
sound is built to it. Fourteen beats, 75 seconds, 24 fps.

    python3 plan_pov.py
"""

FPS = 24
SR = 48000
TOTAL = 75.0

# id, plate, seconds, move, note
BEATS = [
    ("b01", "hall",       7.5, "walk",     "walking down the hall towards the living room"),
    ("b02", "livingroom", 8.5, "handheld", "we are in — the room is quiet"),
    ("b03", "livingroom", 6.0, "tiltdown", "down to the coffee table, the biscuits"),
    ("b04", "livingroom", 1.2, "whip",     "a crash in the kitchen: snap left"),
    ("b05", "kitchen",    8.5, "walk",     "through the doorway, into the kitchen"),
    ("b06", "counter",    7.0, "tiltdown", "the counter: flour, a paw print"),
    ("b07", "paws",       6.5, "crouch",   "something moves at floor level — the paws"),
    ("b08", "undertable", 6.0, "handheld", "down flat behind the table"),
    ("b09", "mouse",      5.5, "track",    "the mouse breaks cover and runs"),
    ("b10", "lunge",      3.5, "shake",    "the cat comes over the top of the table"),
    ("b11", "lunge",      0.8, "white",    "impact"),
    ("b12", "chaos",      7.0, "handheld", "we get up: the room is already wrecked"),
    ("b13", "aftermath",  6.0, "pushin",   "the cat, sitting innocently, and the mouse on the sill"),
    ("b14", "black",      1.0, "still",    "black"),
]

PLATE = {
    "hall": "pov-hall",
    "livingroom": "pov-livingroom",
    "kitchen": "pov-kitchen",
    "counter": "pov-counter",
    "paws": "cat-paws",
    "undertable": "pov-under-table",
    "mouse": "mouse-floor",
    "lunge": "cat-lunge",
    "chaos": "chaos-table",
    "aftermath": "aftermath-wide",
    "black": None,
}


def build(verbose=True):
    shots, t = [], 0.0
    for sid, plate, dur, move, note in BEATS:
        shots.append(dict(id=sid, plate=PLATE.get(plate), move=move, note=note,
                          t0=t, t1=t + dur, dur=dur))
        t += dur
    for a, b in zip(shots, shots[1:]):
        b["t0"] = a["t1"]
    frames = int(round(t * FPS))
    for s in shots:
        s["f0"] = int(round(s["t0"] * FPS))
        s["f1"] = int(round(s["t1"] * FPS))
    shots[-1]["f1"] = frames
    plan = dict(fps=FPS, sr=SR, total=frames / FPS, frames=frames, shots=shots)
    if verbose:
        for s in shots:
            print("  %-4s %6.2f %6.2f  %-8s %s" % (s["id"], s["t0"], s["t1"], s["move"], s["note"]))
        print("  %.2f s · %d frames" % (plan["total"], frames))
    return plan


if __name__ == "__main__":
    build()
