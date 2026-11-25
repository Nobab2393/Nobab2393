# Camera vocabulary — the names the platform actually knows

From upstream `vocab.md` (v3.42.0). **Use these exact names**; do not paraphrase a preset into
"the camera moves in a nice way". If a move you want is not on this list, describe it physically
(`a slow 30° arc around the subject, lens 35 mm`) rather than inventing a preset.

## Linear

- **Dolly In / Out** — smooth track toward / away from the subject
- **Dolly Left / Right** — lateral track
- **Dolly Zoom In / Out** — dolly + counter-zoom (the Vertigo effect)
- **Super Dolly In / Out** — exaggerated, fast dolly
- **Truck** — lateral dolly, same family

## Vertical

- **Crane Up / Down**, **Crane Over The Head**, **Levitation** (dreamlike float), **Tilt Up / Down**

## Orbit / arc

- **360 Orbit**, **Arc** (semi-circular sweep), **Lazy Susan** (slow turntable), **Robo Arm**
  (precision mechanical arc)

## Zoom

- **Crash Zoom In / Out**, **Rack Focus** (refocus near→far)

## Follow / immersive

- **Action Run** (low chase behind a runner), **FPV Drone** (fast weaving aerial),
  **Handheld**, **Head Tracking**, **Snorricam** (mounted on the actor)

## Techniques and angles

- **Bullet Time**, **Dutch Angle**, **Fisheye**, **Whip Pan**, **Overhead**, **Flying**
- **Low Angle** (power), **High Angle** (vulnerability), **Eye Level**, **Bird's-Eye View**

## Shot sizes

extreme wide · wide · full · medium full · medium · medium close · close-up · extreme close-up ·
insert · two-shot · over-the-shoulder

## How to write a camera line

Name the move **and** the amount, because the model needs the scale:

```
Camera: Dolly In — slow, from wide to medium close.
Camera: Arc — 40° right, eye level, subject centred.
Camera: Handheld — locked to his shoulders, 1 m behind, walking pace.
```

## The camera contract

A move is a promise about what stays constant. Three rules keep generations stable:

1. **One move per shot.** Two moves in one prompt is how you get a camera that does neither.
2. **Say what holds.** "The subject stays the same size as the background rushes forward"
   (dolly zoom) reads far better than "dramatic zoom".
3. **Anchor the physics.** If the camera moves, say what it moves *through* or *around*
   ("weaving between the hanging sheets"), so the model has a parallax cue.

## Still-camera moves that are not moves

Slow push-in would otherwise read as "nothing happens". For dialogue and quiet beats, pick:

- **Dolly In** at 5–10 % of frame across the shot (the classic "the shot breathes")
- **Tilt Up** a few degrees on a reveal line
- **Rack Focus** from foreground object to face
- **static locked-off** — say it explicitly; it is a legitimate choice, and models otherwise
  invent drift.
