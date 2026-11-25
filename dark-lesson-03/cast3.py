"""Cast for অন্ধকার পাঠ ০৩ — one rig, three sets of dials (design-lab doctrine, applied).

  AYAN   circle family — round head, narrow shoulders, ochre bag, 5.0 heads
  RAFIQ  square family — flat top, wide shoulders, thick forearms, boots, red wristband, 5.4 heads
  MIRA   hood family  — pointed hood, small shoulders, teal scarf, long skirt, 4.4 heads
  CROWD  muted midground figures — lower contrast, no face, no accent; they must not compete

Everything is a chain: a joint is a matrix, a limb is a capsule, so nothing can detach.
Units: 1.0 = 1 metre, +Y up, characters face +Z, feet at y = 0.
"""
import math
from cel3d import Part, Model, T, S, R


def lerp(a, b, k):
    return a + (b - a) * k


# ---- palette (daylight: nothing near black, one accent each)
INK = (0.11, 0.11, 0.13)
SKIN = (0.80, 0.60, 0.46)
SKIN_D = (0.60, 0.42, 0.33)
HAIR = (0.13, 0.11, 0.12)
EYE_W = (0.95, 0.94, 0.90)

PAPER = (0.93, 0.92, 0.86)
BOOKS = [(0.72, 0.30, 0.26), (0.28, 0.41, 0.61), (0.80, 0.66, 0.30), (0.32, 0.51, 0.37)]


def _part(kind, color, mat, emissive=0.0, subdiv=2, shade=1.0, rim=True):
    return Part(kind, mat, color, emissive=emissive, subdiv=subdiv, shade=shade, rim=rim)


def _ball(color, mat, r=None, subdiv=2, **kw):
    return _part("sphere", color, mat if r is None else mat @ S(r), subdiv=subdiv, **kw)


def _cap(color, mat, r, l, **kw):
    """A limb segment: a sphere stretched along -Y from `mat`, centred half a length down."""
    return _part("sphere", color, mat @ T(0, -l * 0.5, 0) @ S(r, l * 0.58, r), subdiv=2, **kw)


def _capsule(color, mat, rx, rz, length, **kw):
    """A vertical capsule from `mat`: `length` tall, elliptical in plan."""
    return _part("sphere", color, mat @ T(0, -length * 0.5, 0) @ S(rx, length * 0.62, rz), subdiv=2, **kw)


def _chain(root, links, out, cap_col=None, cap_r=0.0):
    """root @ [bend, length, radius, colour]* — each link starts where the last one ended."""
    m = root
    for i, (bend, length, radius, colour) in enumerate(links):
        m = m @ R("z", bend) if i == 0 else m @ R("z", bend)
        out.append(_cap(colour, m, radius, length * 1.12))
        if cap_col and cap_r:
            out.append(_ball(cap_col, m @ T(0, -length, 0) @ S(cap_r)))
        m = m @ T(0, -length * 1.0, 0)
    return m


def _face(p, hd, r, blink=0.0, look=0.0, brow=0.0):
    """Two eyes, two brows, a mouth. Small, close together — googly eyes kill a face."""
    for sx in (-1, 1):
        p.append(_part("sphere", EYE_W, hd @ T(sx * 0.050, 0.004, 0.118) @ S(0.032, 0.040 * (1 - 0.9 * blink), 0.020),
                       subdiv=2))
        if blink < 0.65:
            p.append(_part("sphere", INK, hd @ T(sx * 0.050 + look * 0.010, 0.0, 0.132)
                           @ S(0.016, 0.020, 0.012), subdiv=2))
        p.append(_part("box", HAIR, hd @ T(sx * 0.050, 0.052 + brow * 0.012, 0.124) @ R("y", -sx * 8)
                       @ S(0.042, 0.010, 0.012)))
    p.append(_part("box", SKIN_D, hd @ T(0, -0.058, 0.120) @ S(0.032, 0.009, 0.014)))


# ---------------------------------------------------------------- the shared rig
def _person(B, t=0.0, walk=0.0, arm=0.0, reach=0.0, look=0.0, head=0.0, slump=0.0,
            crouch=0.0, blink=0.0, brow=0.0, laugh=0.0):
    p = []
    sw = math.sin(walk * math.pi * 2.0) if walk else 0.0
    breathe = 1.0 + 0.014 * math.sin(t * 1.9)
    bend = 7.0 * slump + 30.0 * crouch
    drop = 0.30 * crouch
    hip_y = B["hip"] - drop

    # legs: hip -> knee -> ankle, with the knee bend solved so the foot stays on the ground
    Lt = B["hip"] - B["knee"]
    Ls = B["knee"] - B["ankle"]
    A = math.radians(54.0 * crouch + 15.0 * abs(sw))
    rem = (hip_y - B["ankle"]) - Lt * math.cos(A)
    Bk = math.acos(max(-1.0, min(1.0, rem / Ls))) if crouch > 0.02 else 0.0
    for sx in (-1, 1):
        swing = math.radians(15.0 * sw * sx) if walk else 0.0
        root = T(sx * B["leg_x"], hip_y, 0) @ R("x", -A + swing)
        kn = root @ T(0, -Lt, 0)
        kn_rot = kn @ R("x", math.degrees(A + Bk) - swing)
        an = kn_rot @ T(0, -Ls, 0)
        thigh_col = B["skin"] if B.get("shorts_len") else B["legs"]
        p.append(_cap(thigh_col, root, B["leg_r"], Lt))
        if B.get("shorts_len"):
            p.append(_cap(B["legs"], root @ T(0, 0.02, 0), B["leg_r"] * 1.16, B["shorts_len"]))
        p.append(_cap(B["skin"] if B.get("bare_shin") else B["legs"], kn_rot, B["leg_r"] * 0.90, Ls))
        p.append(_part("box", B["shoe"], an @ T(0, B["ankle"] * 0.42, 0.035)
                       @ S(B["shoe_w"], B["ankle"] * 0.9, B["shoe_l"])))

    # hips + torso: a waist capsule under a chest capsule — reads as one body, not a snowman
    p.append(_capsule(B["hipc"], T(0, hip_y + 0.115, 0), B["hip_w"], B["hip_d"], 0.16))
    chest_y = B["sh"] - drop + 0.015
    waist_y = hip_y + 0.075
    p.append(_capsule(B["shirt"], T(0, chest_y + 0.045, 0), B["chest_w"],
                      B["chest_d"], (chest_y - waist_y + 0.10) * breathe))
    if B.get("belt"):
        p.append(_part("box", B["belt"], T(0, waist_y + 0.03, 0)
                       @ S(B["chest_w"] * 1.03, 0.032, B["chest_d"] * 1.05)))

    # neck
    p.append(_part("box", SKIN_D, T(0, B["sh"] - drop + 0.045, 0) @ S(0.062, 0.075, 0.062)))

    # arms: shoulder -> elbow -> wrist. A sleeve covers the joint, then bare forearm.
    hands = {}
    for sx in (-1, 1):
        lift = arm if sx > 0 else 0.0
        fwd = reach if sx < 0 else 0.0
        root = (T(sx * (B["chest_w"] * 1.00), B["sh"] - drop + 0.035, 0.010)
                @ R("z", sx * (B["arm_out"] + 58.0 * lift))
                @ R("x", -sw * 22.0 - 62.0 * fwd + bend * 0.35))
        if B.get("sleeve") == "long":
            _chain(root, [(-sx * 5, B["up"], B["arm_r"], B["shirt"]),
                          (-sx * 7, B["fore"], B["arm_r"] * 0.88, B["shirt"])], p)
        else:
            # upper arm in cloth, forearm bare: a T-shirt, not a snowman with pads
            _chain(root, [(-sx * 5, B["up"], B["arm_r"] * 0.92, B["shirt"]),
                          (-sx * 7, B["fore"], B["arm_r"] * 0.80, B["skin"])], p)
        wrist = (root @ T(0, -B["up"], 0) @ R("z", -sx * 7) @ T(0, -B["fore"], 0))
        p.append(_ball(B["skin"], wrist @ S(B["arm_r"] * 0.94)))
        hands[sx] = wrist
        if B.get("band") and sx > 0:
            p.append(_part("box", B["band"], wrist @ T(0, 0.045, 0) @ S(B["arm_r"] * 1.02, 0.026, B["arm_r"] * 1.02)))

    # head
    hd = (T(0, B["head_y"] - drop, 0.006) @ R("y", look * 22) @ R("z", -head)
          @ R("x", -bend * 0.5 - 4 * laugh))
    r = B["head_r"]
    p.append(_part("sphere", SKIN, hd @ S(r, r * 1.08, r * 0.97), subdiv=3))
    if B["hair"] == "round":
        p.append(_part("sphere", HAIR, hd @ T(0, r * 0.34, -r * 0.36) @ S(r * 1.02, r * 0.96, r * 1.00), subdiv=3))
    elif B["hair"] == "flat":
        p.append(_part("sphere", HAIR, hd @ T(0, r * 0.40, -r * 0.30) @ S(r * 1.02, r * 0.92, r * 1.00), subdiv=3))
        p.append(_part("box", HAIR, hd @ T(0, r * 0.86, -r * 0.30) @ S(r * 1.80, r * 0.34, r * 1.50)))
    elif B["hair"] == "hood":
        p.append(_part("sphere", HAIR, hd @ T(0, r * 0.30, -r * 0.30) @ S(r * 1.02, r * 0.98, r * 1.0), subdiv=3))
        p.append(_part("cone", B["hood"], hd @ T(0, -r * 1.05, -r * 0.62) @ R("x", 34) @ R("z", 8)
                       @ S(r * 1.62, r * 2.35, r * 1.50)))
    _face(p, hd, r, blink=blink, look=look, brow=brow)

    if B.get("scarf"):
        p.append(_part("box", B["scarf"], T(0, B["sh"] - drop + 0.02, 0.012) @ S(B["chest_w"] * 1.06, 0.042, B["chest_d"] * 0.86)))
        p.append(_part("box", B["scarf"], T(B["chest_w"] * 0.55, B["sh"] - drop - 0.10, B["chest_d"] * 0.55)
                       @ R("z", 7) @ S(0.034, 0.13, 0.022)))
    return Model(p), hands, hd


# ---------------------------------------------------------------- the three
AYAN = dict(head_r=0.153, head_y=1.288, sh=1.10, chest_w=0.150, chest_d=0.118, hip_w=0.136,
            hip_d=0.112, hip=0.72, knee=0.37, ankle=0.075, leg_x=0.080, leg_r=0.049,
            up=0.225, fore=0.205, arm_r=0.045, arm_out=9.0, shorts_len=0.250,
            skin=SKIN, shirt=(0.87, 0.90, 0.94), legs=(0.24, 0.28, 0.44), hipc=(0.24, 0.28, 0.44),
            shoe=INK, shoe_w=0.088, shoe_l=0.215, hair="round", belt=None,
            scarf=None, bare_shin=True, sleeve="short", band=None)
AYAN["bag"] = (0.78, 0.56, 0.24)

RAFIQ = dict(head_r=0.152, head_y=1.505, sh=1.285, chest_w=0.215, chest_d=0.150, hip_w=0.185,
             hip_d=0.135, hip=0.845, knee=0.44, ankle=0.085, leg_x=0.098, leg_r=0.066,
             up=0.250, fore=0.230, arm_r=0.056, arm_out=11.0,
             skin=SKIN, shirt=(0.56, 0.25, 0.23), legs=(0.19, 0.20, 0.24),
             hipc=(0.19, 0.20, 0.24), shoe=INK, shoe_w=0.115, shoe_l=0.255, hair="flat",
             belt=(0.14, 0.14, 0.17), scarf=None, bare_shin=False, sleeve="short",
             band=(0.88, 0.26, 0.22))

MIRA = dict(head_r=0.135, head_y=1.185, sh=1.02, chest_w=0.122, chest_d=0.098, hip_w=0.116,
            hip_d=0.098, hip=0.665, knee=0.345, ankle=0.065, leg_x=0.068, leg_r=0.043,
            up=0.195, fore=0.175, arm_r=0.040, arm_out=10.0, shorts_len=0.310,
            skin=SKIN, shirt=(0.34, 0.52, 0.52), legs=(0.33, 0.31, 0.39), hipc=(0.33, 0.31, 0.39),
            shoe=INK, shoe_w=0.075, shoe_l=0.185, hair="hood", belt=None,
            scarf=(0.16, 0.50, 0.55), hood=(0.30, 0.47, 0.48), bare_shin=False, sleeve="long")


def ayan(t=0.0, walk=0.0, arm=0.0, look=0.0, head=0.0, slump=0.0, blink=0.0,
         crouch=0.0, reach=0.0, bag=1.0, brow=0.0):
    m, hands, hd = _person(AYAN, t=t, walk=walk, arm=arm, look=look, head=head, slump=slump,
                           crouch=crouch, blink=blink, reach=reach, brow=brow)
    if bag > 0.01:
        p = m.parts
        p.append(_part("box", (0.62, 0.44, 0.20), T(0, 1.03, 0.0) @ R("y", -20) @ S(0.030, 0.30, 0.016)))
        p.append(_part("box", (0.78, 0.56, 0.24), T(0.185, 0.735, -0.02) @ S(0.105, 0.135, 0.078)))
        p.append(_part("box", (0.62, 0.44, 0.20), T(0.185, 0.795, -0.02) @ S(0.108, 0.028, 0.081)))
    return m, hands, hd


def rafiq(t=0.0, walk=0.0, look=0.0, head=0.0, arm=0.0, help=0.0, laugh=0.0, slump=0.0):
    m, hands, hd = _person(RAFIQ, t=t, walk=walk, arm=arm, reach=help, look=look, head=head,
                           slump=slump, laugh=laugh, brow=1.0 - laugh)
    return m


def mira(t=0.0, walk=0.0, look=0.0, head=0.0, reach=0.0, arm=0.0, blink=0.0, slump=0.0,
         crouch=0.0):
    m, hands, hd = _person(MIRA, t=t, walk=walk, arm=arm, reach=reach, look=look, head=head,
                           blink=blink, slump=slump, crouch=crouch)
    # satchel on the far hip
    p = m.parts
    p.append(_part("box", (0.40, 0.30, 0.22), T(-0.04, 0.98, 0.0) @ R("y", 18) @ S(0.026, 0.26, 0.014)))
    p.append(_part("box", (0.46, 0.33, 0.22), T(-0.155, 0.735, -0.01) @ S(0.088, 0.105, 0.062)))
    return m, hands, hd


# ---------------------------------------------------------------- the crowd
CROWD_C = [(0.50, 0.53, 0.54), (0.45, 0.48, 0.51), (0.55, 0.53, 0.49),
           (0.48, 0.50, 0.53), (0.54, 0.51, 0.47), (0.47, 0.51, 0.50)]
CROWD_HAIR = (0.20, 0.19, 0.20)
CROWD_LEG = (0.26, 0.27, 0.30)


def crowd(i, t=0.0, tall=1.0, phone=0.0, turn=0.0, look=-0.15):
    """No face, muted colour, no accent: a person-shaped background element, not a character."""
    c = CROWD_C[i % len(CROWD_C)]
    B = dict(head_r=0.132 * tall, head_y=1.36 * tall, sh=1.18 * tall, chest_w=0.150 * tall,
             chest_d=0.110 * tall, hip_w=0.140 * tall, hip_d=0.108 * tall, hip=0.76 * tall,
             knee=0.39 * tall, ankle=0.08 * tall, leg_x=0.082 * tall, leg_r=0.070 * tall,
             up=0.215 * tall, fore=0.200 * tall, arm_r=0.058 * tall, arm_out=9.0,
             skin=(0.66, 0.51, 0.40), shirt=c, legs=CROWD_LEG, hipc=CROWD_LEG,
             shoe=(0.16, 0.16, 0.18), shoe_w=0.085 * tall, shoe_l=0.20 * tall,
             hair="round", belt=None, scarf=None, bare_shin=False, sleeve="short")
    m, hands, hd = _person(B, t=t, arm=0.62 * phone, look=look + turn * 0.4, head=0.0)
    # a phone held up: the small indictment
    if phone > 0.2:
        p = m.parts
        p.append(_part("box", (0.05, 0.05, 0.07), hands[1] @ T(0, 0.09, 0.05) @ R("x", -20)
                       @ S(0.048, 0.085, 0.012)))
    # hair, dark and flat — the crowd is a mass, not individuals
    m.parts.append(_part("sphere", CROWD_HAIR, hd @ T(0, 0.024 * tall, -0.012 * tall)
                         @ S(0.136 * tall, 0.130 * tall, 0.132 * tall), subdiv=2))
    return m


# ---------------------------------------------------------------- props
def book(color=(0.72, 0.30, 0.26)):
    return Model([_part("box", color, T(0, 0.014, 0) @ S(0.175, 0.028, 0.125)),
                  _part("box", (0.86, 0.83, 0.74), T(0, 0.030, 0) @ S(0.158, 0.020, 0.112))])


def bag_flat(t=0.0, spilled=1.0):
    p = [_part("box", (0.62, 0.44, 0.20), T(0, 0.050, 0) @ R("z", 5) @ S(0.145, 0.055, 0.105)),
         _part("box", (0.78, 0.56, 0.24), T(0, 0.090, 0) @ R("z", 5) @ S(0.135, 0.030, 0.098)),
         _part("box", (0.62, 0.44, 0.20), T(-0.05, 0.135, -0.01) @ R("z", 42) @ S(0.028, 0.075, 0.020))]
    if spilled > 0.5:
        for i, c in enumerate(BOOKS):
            ang = -42 + i * 30
            p.append(_part("box", c, T(-0.20 + 0.13 * i, 0.012, -0.05 + 0.05 * (i % 2))
                           @ R("y", ang) @ S(0.19, 0.024, 0.132)))
            p.append(_part("box", PAPER, T(-0.20 + 0.13 * i, 0.030, -0.05 + 0.05 * (i % 2))
                           @ R("y", ang) @ S(0.175, 0.020, 0.120)))
    return Model(p)
