# The HUD look, taken apart

The uploaded popup is a "cyber HUD": near-black panels, one electric accent (`#00f0ff`), a
magenta secondary (`#ff007b`), a green "success" (`#00e676`), monospace telemetry, and about ten
glows. It is not decoration for its own sake — every glow is doing one of four jobs. This is the
extracted system, plus where it hurts.

## 1. The one trick worth stealing: a gradient border on a pill

Borders cannot hold gradients. The fix is two background layers, one clipped to padding-box as
the fill and one clipped to border-box as the "border", with a transparent 2 px border:

```css
.btn {
  border: 2px solid transparent;
  border-radius: 30px;
  background-image:
    linear-gradient(135deg, #090d1a, #151b2e),                       /* fill  */
    linear-gradient(135deg, #00f0ff, #0051ff, #8a2be2, #ff007b);      /* rim   */
  background-clip: padding-box, border-box;
  background-origin: padding-box, border-box;
}
```

Hover swaps *both* gradients, which shifts the rim's hue without touching geometry. Works in
every Chromium version, no `mask`, no pseudo-element, no `@property`.

## 2. Four glow jobs

| Job | Recipe | Where |
|---|---|---|
| **Elevation** | `0 4px 18px rgba(0,0,0,.75)` | the pill sits on a dark page |
| **Identity** | `0 0 14px rgba(0,240,255,.55)` | accent = "this is ours" |
| **Bevelled material** | `inset 0 1.5px 1.5px rgba(255,255,255,.4), inset 0 -2px 6px rgba(0,0,0,.6)` | the 3D metal rim |
| **Aliveness** | `@keyframes beacon-glow` 6 px → 10 px on a status dot | "HUD ACTIVE" |

Stack them in one `box-shadow` list in that order: outer shadow, then identity halo, then the
two insets. Six shadows is the practical ceiling before the paint cost shows up on a laptop.

## 3. Depth without images

- **Pressed state** = `transform: translateY(1px) scale(.97)` **plus** removing the outer
  shadow and deepening the top inset. Only the shadow change reads as "pressed"; the transform
  alone reads as "shrunk".
- **Lift** = `translateY(-2px) scale(1.04)` + brighter halo. 2 px, not 6: a popup is 360 px
  wide, and a large lift clips against its own edge.
- **Type glow** = `text-shadow: 0 0 10px rgba(0,240,255,.5)` on numeric telemetry only. On body
  text it destroys legibility at 13 px.

## 4. Typography for "instrument panel"

- Numbers in monospace, letters in the system sans — the contrast is what reads as telemetry.
- Small caps + `letter-spacing: .06em` – `.12em` for labels; `tabular-nums` for anything that
  counts, or the row jitters as the badge ticks over.
- One accent per row. Two accent colours in a 360 px popup and nothing is emphasised.

## 5. `!important` everywhere — and its cost

Injected in-page CSS (`content.css`) must survive a hostile host page, so the reference build
marks every property `!important`. That works, and it is a maintenance trap: you can no longer
override your own rules, and a host page using `all: revert` or a CSS layer will still win.

Better, in order:

1. Attach to a **shadow root** you own (`attachShadow({mode:'open'})`) — full isolation, no
   `!important` at all. Best option in 2026.
2. Or raise specificity honestly with an ID you generate: `#mmdl-8f2a .btn { … }`.
3. Keep `!important` only for properties that layout-breaking hosts actually fight over
   (`position`, `z-index`, `display`, `transform`).

## 6. What I would change

| Reference | Problem | Fix |
|---|---|---|
| 490 lines of popup CSS, 10 keyframes | a 360 px popup repainting an animated radar | animate only `opacity` / `transform`; drop the rest |
| `backdrop-filter: blur(10px)` on an in-page button | forces a compositing layer on every video card | drop it; nobody sees the blur behind an opaque fill |
| accent `#00f0ff` on `#090d1a` | ~12:1, fine — but the *secondary* magenta on the same ground is ~4.4:1 | use magenta for focus rings only |
| 8 px 16 px padding, 13 px bold | the button is large enough to cover a video's own controls | 6 px 12 px, and offset it away from the player chrome |

Palette that survived the test: ground `#090d1a`, panel `#11172a`, accent `#00f0ff`, secondary
`#ff007b`, success `#00e676`, text `#ffffff`, muted `rgba(255,255,255,.55)`.
