"""Walking + gesture motion library for the rig."""
import math

from char import Pose
from rig import clamp01, lerp, smoothstep, vlerp

TAU = math.pi * 2


def idle(t, amp=1.0):
    """Breathing offset + micro sway (returns hip dx, dy, torso ang, head ang)."""
    b = math.sin(t * TAU * 0.28)
    s = math.sin(t * TAU * 0.17 + 0.8)
    return s * 0.004 * amp, -abs(b) * 0.010 * amp, b * 0.012 * amp, s * 0.020 * amp


def walk_phase(phase, P, stride=0.20, lift=0.055, bob=0.022):
    """Feet positions + hip bob for a normalised walk phase (0..1)."""
    fn = _step(phase, P, stride, lift)
    ff = _step((phase + 0.5) % 1.0, P, stride, lift)
    # hip rises mid-stance, dips at double support
    hy = -abs(math.sin(phase * TAU)) * bob + bob * 0.5
    return fn, ff, hy


def _step(ph, P, stride, lift):
    """Foot position for one leg over a gait cycle. Contact at ph=0 (front)."""
    if ph < 0.5:  # stance: foot slides back on the ground
        u = ph / 0.5
        x = lerp(stride * 0.5, -stride * 0.5, u)
        y = P * 0.462
    else:  # swing: lifts, travels forward
        u = (ph - 0.5) / 0.5
        e = smoothstep(0, 1, u)
        x = lerp(-stride * 0.5, stride * 0.5, e)
        y = P * 0.462 - math.sin(u * math.pi) * lift * P
    return (x * P, y)


def hand_swing(base, phase, P, amp=0.085):
    a = math.sin(phase * TAU) * amp * P
    return (base[0] - a * 0.55, base[1] - abs(a) * 0.18)


class Performer:
    """Holds the current pose and lets a shot stack gestures on top of it."""

    def __init__(self, ch):
        self.ch = ch
        self.P = ch.height
        self.hip = (0.0, 0.0)
        self.torso = 0.0
        self.head = 0.0
        self.foot_n = (0.105 * self.P, 0.462 * self.P)
        self.foot_f = (-0.115 * self.P, 0.462 * self.P)
        self.hand_n = (0.175 * self.P, 0.215 * self.P)
        self.hand_f = (-0.195 * self.P, 0.225 * self.P)
        self.coat = 0.0
        self.blink = 1.0
        self.mouth = 0.0
        self.smile = 0.5
        self.brow = 0.0
        self.look = 0.0
        self.flip = False

    # ---------- transitions
    def to(self, pose_fn, k):
        """Blend the performer towards pose_fn(t=1) by factor k."""
        target = pose_fn(1.0)
        self.hip = vlerp(self.hip, target.hip, k)
        self.torso = lerp(self.torso, target.torso, k)
        self.head = lerp(self.head, target.head, k)
        self.foot_n = vlerp(self.foot_n, target.foot_n, k)
        self.foot_f = vlerp(self.foot_f, target.foot_f, k)
        self.hand_n = vlerp(self.hand_n, target.hand_n, k)
        self.hand_f = vlerp(self.hand_f, target.hand_f, k)
        self.coat = lerp(self.coat, target.coat, k)
        self.smile = lerp(self.smile, target.smile, k)
        self.brow = lerp(self.brow, target.brow, k)
        self.look = lerp(self.look, target.look, k)

    def pose(self):
        return Pose(hip=self.hip, torso=self.torso, head=self.head,
                    foot_n=self.foot_n, foot_f=self.foot_f,
                    hand_n=self.hand_n, hand_f=self.hand_f,
                    coat=self.coat, blink=self.blink, mouth=self.mouth,
                    smile=self.smile, brow=self.brow, look=self.look, flip=self.flip)


# ---------------------------------------------------------------- gesture builders
def stand(look_at_camera=True):
    def f(t):
        P = 700.0
        p = Pose()
        return p
    return f


def gesture_point(P, base_hand=(0.175, 0.215), up=(0.34, -0.16)):
    """Arm raised, index pointing — used for 'declare' beats."""
    b = (base_hand[0] * P, base_hand[1] * P)
    u = (up[0] * P, up[1] * P)
    return b, u


def talk_hand(t, P, base, amp=1.0, speed=1.0):
    a = math.sin(t * TAU * 1.6 * speed)
    b = math.cos(t * TAU * 1.1 * speed)
    return (base[0] + a * 0.030 * P * amp, base[1] - (0.5 + 0.5 * b) * 0.035 * P * amp)


def walk_cycle(t, P, base_hip=(0.0, 0.0), speed=1.0, phase0=0.0, stride=0.20, arm_amp=0.075):
    ph = (t * speed + phase0) % 1.0
    fn, ff, hy = walk_phase(ph, P, stride=stride)
    hip = (base_hip[0], base_hip[1] + hy)
    hn = hand_swing((0.175 * P, 0.215 * P), ph, P, arm_amp)
    hf = hand_swing((-0.195 * P, 0.225 * P), (ph + 0.5) % 1.0, P, arm_amp)
    return hip, fn, ff, hn, hf, ph
