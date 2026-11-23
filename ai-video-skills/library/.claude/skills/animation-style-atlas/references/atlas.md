# The Atlas — 119 animation styles, by category

Auto-extracted from four open skill libraries, then grouped. Every line below comes from a
real `STYLE.md` / `SKILL.md`; nothing is paraphrased into generic advice. Palettes are the
hexes that file actually prints (the first few, in order of appearance).

## Code-drawn style skill — 13 styles

### breakdown
> A 3D exploded view. A phone comes apart layer by layer, and every part gets a leader line and a label.
- **Palette:** #F08A5D
- **Source:** `artemnovitckii/claude-animation-skills` → `breakdown`

### dan-koe
> Black-and-white line art. One dot grows into a hairline tree that splits in two at every step, and the tips light up.
- **Motion:** - depth: 6 to 10 levels of branching. 9 makes 256 tips and a 4 s video; each level adds or removes 0.25 s.
- **Source:** `artemnovitckii/claude-animation-skills` → `dan-koe`

### graph
> A minimal line graph. A smooth line draws itself, and one big number counts up with its tip. Black on white, or white on black.
- **Source:** `artemnovitckii/claude-animation-skills` → `graph`

### kinetic-reel
> >-
- **Source:** `tuzhechen2005/opus-video-skills` → `kinetic-reel`

### kurzgesagt
> Flat-vector space. Glowing planets with a dark crescent, twinkling stars and bright label tags. The built-in scene stacks every planet, to scale, between Earth and the Moon.
- **Palette:** #140C3F #0C0830
- **Motion:** - lines: 1 to 3 captions. They show at 0.15 s, 1.3 s and 2.5 s (the payoff).
- **Source:** `artemnovitckii/claude-animation-skills` → `kurzgesagt`

### low-poly
> PS1-era low-poly 3D. Chunky pixels, wobbly vertices, dithering and small yellow captions. The built-in scene: a dog waits on a station platform, a train comes and goes, and he is still there in the snow.
- **Motion:** - lines: line one shows from 0.3 s, line two from 2.6 s, just before the train clears.
- **Source:** `artemnovitckii/claude-animation-skills` → `low-poly`

### map-route
> A 3D map route. A white city, a route that draws itself while the camera follows, a pin drop, an ETA that counts down and a destination card.
- **Palette:** #2F7CF6
- **Source:** `artemnovitckii/claude-animation-skills` → `map-route`

### minecraft
> A blocky voxel build. A cottage builds itself block by block on a grassy hill, the chimney slams in and the windows light up. Every texture is drawn in code.
- **Motion:** - lines: line one drops in letter by letter at 0.3 s and fades at 2.6 s. Line two slams in with the chimney at 2.7 s. Keep line one under ~17 characters and line two under ~9.
- **Source:** `artemnovitckii/claude-animation-skills` → `minecraft`

### minimalistic-graphics
> Black-and-white line art. Hairline steps rise, one white dot hops up them and gets an orbit at the top, with one quiet line of text.
- **Source:** `artemnovitckii/claude-animation-skills` → `minimalistic-graphics`

### painted-animation
> Make hand-painted watercolour-and-ink cartoon videos (MP4) with code — p5.js + p5.brush rendered frame by frame in headless Chrome, encoded with ffmpeg — starring Clawd or any character. Use when the user asks to make an animation, animated short, cartoon, music video, lyric video, animated GIF/loop or "a video of Clawd…", or mentions the PDoomVideo / ClaudeAnimationBase approach. Covers storyboarding, the engine API, the render-and-look review loop, music/lyric sync and…
- **Motion:** How it works: every frame is a pure function of time t. studio.html loads p5.js + p5.brush and your scene files; each shot paints the whole 1920×1080 frame with watercolour fills and boiling ink lines. render.mj
- **Source:** `tuzhechen2005/opus-video-skills` → `painted-animation`

### stick-figure
> A stick-figure explainer reel. A bright cartoon world, stick people with big faces, whip transitions, 1 to 2 word captions, and music and sound effects made in code. Comes with a finished 37 s example.
- **Palette:** #221C22
- **Source:** `artemnovitckii/claude-animation-skills` → `stick-figure`

### zach-3d-films
> The 3D cartoon explainer. The same engine as /zach-d-films, under the name from the reel.
- **Source:** `artemnovitckii/claude-animation-skills` → `zach-3d-films`

### zach-d-films
> A 3D cartoon "what if" explainer. Cartoon people, props and effects built in three.js, slow-motion impacts, a red force ripple and captions timed to your voiceover. Comes with a finished 29 s example to build from.
- **Motion:** 5. Shots. Plan a shot every 2 to 4 s (8 to 10 for 30 s, 3 for 10 s), cutting on caption beats, the mechanism shot longest. Write one function per shot by copying the closest example, change the props, poses and camer
- **Source:** `artemnovitckii/claude-animation-skills` → `zach-d-films`

## 3D & Miniature — 8 styles

### Brick Toy · 积木玩具
> Stop-motion toy-brick films shot like macro photography on a real desk: a world built from interlocking plastic bricks with round studs, animated a pose at a time. References (grammar only): brick-film stop-motion on a tabletop and the "brick movie" approach of stepping characters while the camera moves smoothly; macro toy photography (softboxes on glossy plastic, shallow focus, real objects as landscape). Copy none of their characters, sets or music, and never use a brand…
- **Palette:** #C91A09 #0055BF #F2CD37 #237841 #F2F2EE #1B2A34
- **Not:** Not a low-poly isometric island (no flat-shaded facets, no floating diorama), not a clay or felt stop-motion (no deformation: bricks are rigid), not a clean product render of a toy (this world is played with, handled, knocked over).
- **Motion:** - Subtitles live on a toy element: a dark rounded pill low in the frame with a small brick icon beside the text, or a printed tile, or a sign built into the set. White on dark, ≤ 2 lines. A second speaker type (radio
- **Use for:** Toys & kids, Product builds, Space
- **Source:** `lemomo-ai/lemo-opuscar` → `brick-toy`

### Crayon World 3D · 蜡笔立体世界
> A whole world built in 3D and redrawn in wax crayon, by a child's hand, twelve times a second, while a camera moves through it: real depth and parallax, a flight or a walk in first person, and every frame still a crayon drawing on the same sheet of paper. References (grammar only): first-person walking films and long takes (the camera is someone, their gaze is the cut); children's drawings of a village (houses with a gable front and a slanted side, lollipop trees,…
- **Palette:** #6CB24A #C8452F
- A real 3D place, drawn. The world is modelled in simple primitives and seen through a perspective camera; the 3D render never reaches the screen. Each frame its shapes are traced and drawn again in crayon: outlines, scribbled hatching, colour that spills past the line.
- The paper never moves. The sheet is the screen: tooth, emboss and vignette stay put while the world turns behind them. Depth comes from overlap, size and parallax, never from shading gradients or fog.
- 12 drawings a second. The camera moves smoothly, but the drawing is replaced 12 times a second, so motion has the faint stepping of hand animation.
- **Not:** Not Crayon Picture Book: that style is a flat page drawn while you watch, the camera moving over the paper, a watercolour wash, narration printed as the book's words. Here the camera moves *inside* a world, the page is only the surface it is drawn on, and there is no wash. Not a toon shader or cel…
- **Tech:** - Bilingual: the Chinese line, then the English line a size smaller underneath, written in after it. Example faces (OFL): Long Cang for Chinese at 110–140 px, Patrick Hand for Latin at 50–64 px.
- **Use for:** Short stories, Tributes, Journeys
- **Source:** `lemomo-ai/lemo-opuscar` → `crayon-world`

### Glass Product Render · 玻璃质感产品
> Launch-film product rendering in transparent and frosted glass: a dark-field studio, strip-light sweeps, dispersion, caustics, light travelling inside the object, slow exploded views that snap shut on a downbeat. References (grammar only): premium launch films (a sweep drawing a contour in the dark, slow orbits, macro rack focus, cuts on the beat, ultra-thin wide type); transparent-hardware adverts (internals as ornament, exploded views, black and white plus one accent);…
- **Not:** Not a white-cyclorama catalogue shot, not a wireframe HUD, not a keynote slide: material and light are the subject.
- **Motion:** - Subtitles are a slab of frosted glass: a centred rounded bar filled with the live frame blurred (filter: blur() brightness() on the WebGL canvas, preserveDrawingBuffer: true), a little cool white, a thin highli
- **Use for:** Product launches, Consumer tech, Beauty
- **Source:** `lemomo-ai/lemo-opuscar` → `glass-product`

### Isometric People Scene · 等距小人场景
> A calm explainer of an everyday rule, set in one real place drawn in true isometric with flat colour: small faceless people seen from behind do the thing in order, while serif type lands on the ground, character by character, as if painted there. Whatever hides the action (a roof, a wall) is cut away or lifts off like a paper flap. The order of movement is the explanation. References (grammar only): isometric explainers about public manners (queues, platforms, crossings)…
- **Palette:** #F1E8D8 #EAE2D3 #F2E5CE #2A2E29 #D0573A #3D6B59
- One real place, full bleed. A platform, a gate, a cabin, a crossing, a counter: the ground runs off every edge of the frame. No floating board, no frame line, no vignette. A topic that travels (a parcel, a route, a production line) can still be one place: one continuous ground at one scale, with…
- People are the diagram. Slim figures seen from behind, no faces and no hands, move only when the rule says so. Who moves first, who waits, who sits is the information.
- Type lies on the ground. Each idea is one key word or number painted on the floor, big and small sizes, one accent character, landing one character at a time.
- **Not:** Not Isometric Infographic: that style builds a model on a floating board over a dot lattice and labels it with sans-serif pins, icon statistics and inset bubbles to trace a process; here there is no board edge, no pins and no icons: the place is real and full bleed, the labels are serif words…
- **Tech:** When the film tells something, a narrator says it and the picture shows it at the same moment: one line per action or shot, each line starting as its action starts. A calm, quick reader in the film's language; the floor
- **Use for:** Everyday rules, Queues, Comparisons
- **Source:** `lemomo-ai/lemo-opuscar` → `isometric-picture-book`

### Low-poly Isometric Island · 低多边形等距
> A tiny faceted world seen through an orthographic isometric lens: everything is a geometric block, and everything that appears arrives with a bounce and a note. References (grammar only): *Townscaper* (building is the performance; every piece lands with a springy bounce and a sound; pieces sprout small details by themselves); *Monument Valley* (isometric geometry, soft pastel palettes, gradient skies, calm pacing, lots of empty space). Never copy their grids, buildings,…
- **Not:** Not a voxel game (no cubes-of-cubes, no pixel texture), not a tilt-shift photograph of a real place (no perspective, no photo detail), not a smooth-shaded 3D cartoon (no rounded normals, no subsurface).
- **Motion:** - Subtitles: no box; warm white with a soft dark-blue drop shadow, centred low; a small flat-shaded tile icon beside them whose top colour follows the time of day. Hold ≥ max(1.8 s, speech + 0.6 s), never overlapping
- **Use for:** Game trailers, World building, Calm content
- **Source:** `lemomo-ai/lemo-opuscar` → `lowpoly-island`

### Memphis Diorama · 孟菲斯微缩景观
> A place built as a tabletop model: on warm white paper an organic, grainy frame grows open, and inside it a small world in flat Memphis colours, ink outlines, hard purple shadows and tiny patterns, full of small motions under a slow camera. Calm, bright and warm; a place you watch, not a story you follow. References (grammar only): the Memphis Group, Ettore Sottsass, Nathalie Du Pasquier (saturated primaries next to pastels, dots, zigzags and terrazzo flecks on every…
- **Palette:** #FFFCF6 #25214A #FFD36E #FF9E7A #FFD234 #FF7EB3
- Paper and a grainy frame. A warm white ground; the picture lives in a rounded, organic frame whose edge dissolves into grain. It grows open from the centre at the start and draws back in at the end.
- Memphis flat colour. Saturated primaries plus pastels, flat fills, no gradients; a deep-indigo ink outline; small patterns tiled on surfaces (dots, stripes, zigzags, terrazzo flecks, halftone).
- The eye of a model-maker. High three-quarter, top-down or cutaway views. The film always looks at a *place*, never at a person.
- **Not:** Not character animation: nobody acts. Code-made faces, gestures, getting in and out of cars always look stiff, so this style never shows them. Not an isometric infographic (that one is cool and diagrammatic; this one has weather, seasons and sound). Not tilt-shift (no photograph, no depth of…
- **Motion:** - Three centred lines under the frame: line 1, the title, Chinese and English, weight 600, about 25 px, dark; line 2, one sentence, weight 400, about 18 px, grey; line 3, small data (time, solar term, place, coordina
- **Use for:** Web heroes, Ambient loops, Seasons
- **Source:** `lemomo-ai/lemo-opuscar` → `memphis-diorama`

### Paper Pop-up Book · 纸片立体书
> A pop-up book on a real desk becomes a stage: flat cut-paper actors with white borders perform in front of paper sets that spring up from the page, under real lamp light and a real macro lens. References (grammar only): the *Paper Mario* series (flat cut-paper actors with a white border in a 3D diorama, bubbles that type on with blips, action ratings); Robert Sabuda / Matthew Reinhart pop-up books (layered V-folds, pieces rising back to front, pull-tabs); macro "tiny world…
- **Not:** Not a papercut silhouette film (no one-colour lace, no backlight), not a 3D cartoon (nothing modelled round), not claymation (paper hinges, folds, curls and slides; it never squishes).
- **Motion:** - Narration subtitles: bottom centre, ~40 px, cream with a thick dark-brown outline and soft shadow, second language smaller below. Hold ≥ max(1.8 s, speech + 0.6 s).
- **Use for:** Children's books, Game trailers, Story films
- **Source:** `lemomo-ai/lemo-opuscar` → `paper-popup`

### Tilt-Shift Miniature · 移轴微缩
> A real-looking place photographed from high above with a tilted lens and a time-lapse camera, so the whole world reads as a tabletop model. References (grammar only): Sam O'Hare's *The Sandpit* (2010) and tilt-shift time-lapse photography in general: high vantage points, the blur band, time-lapse rhythm, cloud shadows sweeping over streets. Copy none of its places or music; show no real landmarks, brands or logos.
- **Not:** Not a toy or clay render (the world is photoreal, only the lens and the clock make it small), not a game's top-down view (no UI, no clean flat shading), not drone footage (the band, the saturation and the stutter are mandatory).
- **Tech:** - Subtitles belong to the world's own signage: a panel in the graphic language of the place's signs (road sign, platform board, harbour notice…), an open sign-revival font (Overpass, OFL, is a Highway-Gothic revival), si
- **Use for:** City promos, Real estate, Transport
- **Source:** `lemomo-ai/lemo-opuscar` → `tilt-shift`

## Edit & Documentary — 8 styles

### 1920s Newsreel · 1920s 新闻影片
> A sound newsreel of the late 1920s, cut from real archive material: a searchlight-and-globe ident with a brass fanfare, a newspaper that spins into the lens, a fast and cheerful announcer on an optical soundtrack, place-and-date cards, maps, magazine pages and documents, wipes, flips and irises, and a hot band that can stop dead for the punchline. References (grammar only): Fox Movietone News and Universal Newspaper Newsreel (1927–1930s) — the ident ritual, the announcer's…
- **Palette:** #F3EEE4 #D6CFC0 #D9D4CA #9E978A #EFEBE2
- Archive in a projected gate: 1.37:1 picture, full height, rounded corners, black outside; everything inside it shares one silver grade, gate weave, flicker, scratches and dust.
- News objects do the explaining: newspapers, magazine pages, books, telegrams, maps, records. They are filmed (spun, slammed, panned, turned, underlined), never typeset as slides.
- A voice talks over everything: short exclamations, half joking, never a lecture.
- **Not:** Not silent-film (1920s Silent Film, in this library): that style is a drawn, inked comedy projected between velvet curtains, with intertitles instead of voices, a cinema pianist and no foley. Here nothing is drawn but the packaging; the footage and print are real; somebody always speaks; the…
- **Tech:** - Base grade for every source, before anything else (tools/prep.py, grade()): greyscale → percentile stretch (0.6 % → black, 99.6 % → white; print: 0.2–0.3 % / 99.0–99.7 % with the black lifted to 26–30, like new
- **Use for:** History stories, Fads & eras, Anniversaries
- **Source:** `lemomo-ai/lemo-opuscar` → `newsreel`

### Broadcast News Package · 电视新闻包装
> A television newsroom's on-air package, built entirely in code: a sting that becomes the channel bug, a rundown of today's stories that opens and closes the bulletin, a lower-third strap that never leaves the bottom of the frame, and full-frame graphics (split-flap price boards, a line breaking a threshold, explainer maps, documents flying out of a city, quote cards, spec cards with proportion bars, stamps) that carry the facts. The style is the package system plus its…
- **Palette:** #121417 #1B1E23 #22262C #F2CF1D #F8DE4A #D8B30C
- **Not:** Not Caption News (that is captions-first social video: huge slammed captions are the lead, no rundown, no strap; here type is small and orderly and the graphics lead). Not Data Storytelling (one chart per beat, never a dashboard; the chart is an insert in a bulletin). Not a keynote: no centred…
- **Tech:** - One grade for every plate: greyscale → auto black/white points (0.5 / 99.6 percentile) → γ 1.05 → 35 % S-curve → black 8, white 232 → duotone #0E1013 → #ECE7D8 (tools/prep.py: grade()), plus a left-dark ink gradi
- **Use for:** News round-ups, Bulletins, Market updates
- **Source:** `lemomo-ai/lemo-opuscar` → `news-package`

### Caption News · 字幕新闻
> Social-video news that reads with the sound off. Real footage, photos and the source document are the ground; huge captions are the lead actor, slammed in a chunk at a time with one keyword on a yellow block. Hard cuts on a music grid, numbers that roll, a source tag that slides in whenever a figure appears, and the original document highlighted on screen before its number is believed. 16:9, built for a feed. References (grammar only): the captions-first social news of the…
- **Palette:** #F7F5EF #FFC21A #0E0E0C #151512 #FF4A3D #8D8B83
- **Not:** Not Data Storytelling (charts are short inserts between footage, never the whole film, never a dashboard). Not a TV news package (no anchor, no lower-third ticker, no studio, no scrolling crawl). Not a keynote: no headers, no centred title-and-bullets, no page turns.
- **Tech:** Under the caption: a bottom gradient (0 → 84 % from y 560) plus a soft dark radial from the bottom-left corner; a top gradient (55 % → 0 over 200 px) under the bug and the credit. Data cards use a lighter gradient that s
- **Use for:** Social news, Report explainers, Data shorts
- **Source:** `lemomo-ai/lemo-opuscar` → `caption-news`

### City Symphony · 城市交响曲
> A city film cut like a piece of minimalist music: time-lapse turns traffic, crowds and clouds into rivers of light, the cuts get denser with the score's subdivisions, one thing is slowed almost to a stop, and the film ends on a hard cut to black on a downbeat. No narrator. The music carries it. Grammar learned from the city-symphony tradition and the "Qatsi" films (Reggio / Fricke, scores in the Philip Glass manner). Nothing is taken from those films: no footage, no melody,…
- **Palette:** #EDE8DF #B0AAA0 #D9772F #000000
- An edit style. The picture is real footage of a place (time-lapse, hyperlapse, aerials, slow motion, archive film, photographs). The style lives in *how time is bent* and *where the cuts fall*, not in a drawn look.
- The score is the script. It is written first, with a clear arc: minimal repetition → acceleration → climax → a sudden stop → acceleration again → hard stop → a quiet coda. Every cut sits on a beat or a subdivision of it.
- Machines fast, people slow. Cars, trains, clouds and light are sped up until they become lines; the one slowed moment is something fragile (a soap bubble, steam, a flag, a flock), and people appear as crowds, tracks or long-exposure ghosts.
- **Motion:** - Everything is unified into one 35 mm release-print look: 1.85:1 matte (21 px bars on 1920×1080), warm highlights, lifted blacks, highlight bloom, clumped mid-tone grain, ±0.5 px gate weave, soft vignette.
- **Use for:** City films, Music montages, Openers
- **Source:** `lemomo-ai/lemo-opuscar` → `city-symphony`

### Constructivist Montage · 构成主义蒙太奇
> Real archive footage, photographs and documents, printed as one ink-and-paper poster with a single red, and cut on a machine beat. Diagonal bands carry the type; windows cut along the axis hold the film; people are scissored out of photographs and stacked into structures; numbers count, documents are marked in red, and two images collide to make a third idea. References (grammar only): Soviet montage cinema of the 1920s (city symphonies with split screens, counting and…
- **Palette:** #D52B1E #141210 #EDE4D0
- **Not:** Not Data Storytelling or a keynote: no centred headline with bullets, no slide transitions, no header bars; data appears as marked documents, counters and measured bars inside the composition. Not Swiss Motion Graphics: asymmetric, diagonal, no grid of white space, no thin rules as decoration. Not…
- **Motion:** - Subtitles stay bottom-left in a 960–1056 px strip; key type keeps above y 930 while narration runs. Subtitles hold ≥ max(1.8 s, speech + 0.6 s). On-screen text follows readcheck.mjs (CJK ÷ 4.5 + other ÷ 15 + 1.5
- **Use for:** Industry histories, Milestones, Collective effort
- **Source:** `lemomo-ai/lemo-opuscar` → `kino-montage`

### Live Countdown Split-screen · 实时倒计时分屏
> An edit style, not a look. Real footage of one event with a known zero (a launch, a verdict, a final whistle, polls closing), shown in real time: screen time equals event time, a clock ticks every second, and the screen splits into more and more cells as the moment nears, every cell showing the same second. At zero the cells merge into one picture and the clock flips. References (grammar only): the real-time clock and splitting screens of the TV series *24*; the…
- **Palette:** #06080A #0B0E11 #F2F5F7 #7C878D #FF5B1F #FF3B30
- **Not:** Not a montage (time jumps), not a security wall (the layout never moves), not a flashback structure (real time cannot go back), not a slide deck (cells that don't follow events, text filling the cells, centred titles with page turns).
- **Tech:** - Cells: hard rectangles on near-black #06080A, 24 px outer margin, 8–9 px gutters, 1 px border rgba(222,232,238,.16), a light radial vignette (to 36 % black) on video cells. No rounded corners, no drop shadows,
- **Use for:** Launches, Countdowns, Live events
- **Source:** `lemomo-ai/lemo-opuscar` → `countdown`

### Sports Telestrator · 体育战术板
> The TV football analysis segment: play the clip at full speed, rewind, freeze it, and draw on the broadcast picture — rings under players' feet, marker arrows for the ball, a red patch for the space nobody covered — then play on, switch angles, count the frames, and flatten the pitch into a board. Real match footage is the ground; every line is drawn on top of it and moves with it. A studio show's packaging (sting, corner bug, score bar, a yellow wipe) holds it together.…
- **Palette:** #FFD400 #3FD8FF #FF3B30 #F4F1E8 #0C1411 #080C0E
- **Not:** Not Visual Investigation (that is restrained, synchronised multi-camera evidence where the timeline is the protagonist; this is a pundit's show with packaging and enthusiasm). Not a highlight reel (no montage of goals to music; each clip is analysed). Not Data Storytelling or an infographic:…
- **Motion:** - Split screen: two 960×1080 vertical windows, each a 960-px-wide slice of a 1920 frame at 1:1 (no extra scaling), a 6 px yellow divider between them, a camera label at each window's top left (A MAIN CAMERA / B HIGH
- **Use for:** Sports analysis, Match recaps, Coaching
- **Source:** `lemomo-ai/lemo-opuscar` → `telestrator`

### Visual Investigation · 视觉调查
> A cold investigation desk: footage, photographs, documents, sound and maps from one real event, laid out on one shared clock so they check each other. The clock lives inside the picture — timestamps on the evidence, a playhead on a data chart, a stopwatch over the decisive seconds; frozen frames are circled and magnified; quotes are highlighted on the page they come from; a plan shows where cameras stood and where they looked; what is known and what is not are kept apart;…
- **Palette:** #0B0C0E #141619 #2E3238 #ECEAE4 #8B9097 #4A4F57
- **Not:** Not Satellite Briefing (no orbital imagery, no zoom from space). Not Archive Light Table (no paper on glass, loupes or hands: documents are flat evidence frames). Not Halftone Dossier (no print texture, stamps or collage). Not a newsreel package (no channel bug, ticker or anchor voice). Not a…
- **Motion:** - Subtitles (bilingual films): at the bottom of the frame (Chinese baseline y ≈ 984, English y ≈ 1022): Chinese 34 px bold over English 23 px, centred, 10 px black shadow; one line per language, measured in the p
- **Use for:** Reconstructions, Fact-checks, Incident reports
- **Source:** `lemomo-ai/lemo-opuscar` → `visual-investigation`

## Graphic & Type — 8 styles

### 60s Spy Title Sequence · 60s 间谍片头
> A cut-paper, four-ink opening title sequence for a film that never existed: silhouettes move through sets built out of the credits themselves, every brass stab is a cut, and a title is assembled from the pieces. References (grammar only): Saul Bass's titles for *North by Northwest*, *Anatomy of a Murder* and *Vertigo* (flat opaque inks, abstraction down to silhouettes, type as structure); the 2002 homage by Kuntzel + Deygas for *Catch Me If You Can* (a cut-paper chase…
- **Palette:** #1B1714 #EFE4C9 #D23A22 #E2A52A #161A22 #ECE6D6
- Flat, opaque inks on paper: four colours, no gradients.
- Hand-cut edges on every shape; pieces layered with cut gaps and small paper shadows.
- Abstraction down to silhouettes: figures in profile, all acting in outline and timing.
- **Not:** Not flat vector motion graphics (the edges are cut, the paper is physical), not a halftone print style (no dots), not a Swiss grid (diagonals, jaunty type, playful), not a spy parody with gadgets and gun barrels.
- **Tech:** - Scissor-cut edges: every polygon resampled every ~9–10 px and displaced along its normal by low-frequency noise (amp ~1.2–2.2 px, larger for bigger shapes) plus a rare 1–2 px notch. **Cut the edge once in the piece
- **Use for:** Title sequences, Event openers, Trailers
- **Source:** `lemomo-ai/lemo-opuscar` → `spy-titles`

### Art Deco · 装饰艺术
> Black lacquer, engraved gold line and airbrushed geometry: a 1930s poster that moves. Every composition has a centre axis, transitions open or close along it, and light arrives as bulbs switching on one by one. References (grammar only): A. M. Cassandre posters (giant geometry, steep perspective, airbrush inside hard edges); Chrysler Building / Rockefeller Center ornament (setbacks, sunbursts, chevrons); Busby Berkeley overhead numbers overheads (human kaleidoscopes); The…
- **Not:** Not a gold-foil slideshow (things move and have volume), not Art Nouveau (no whiplash curves, no flowers), not a flat vector poster (volumes are airbrushed and rimmed), not a 60s spy title (no silhouettes on flat colour).
- **Tech:** - Subtitle card (subtitleCard): a lacquer bar (~88 % black) with stepped ends like the title bar, double gold keyline, Josefin Sans SemiBold ~40–42 px ivory, an optional small speaker icon per voice. It **unfolds f
- **Use for:** Luxury & hospitality, Galas, Invitations
- **Source:** `lemomo-ai/lemo-opuscar` → `art-deco`

### Bauhaus Shapes · 包豪斯几何
> An explainer told only with circles, squares, triangles, arcs and straight lines, set in opaque colour on a light, matte paper. Every shape is a quantity drawn to scale (area is the amount), the shapes are the characters, and type only names them. A thin construction grid lays out each scene before anything lands, and folds away when it is done. References (grammar only): the Bauhaus preliminary course (Itten, Albers, Kandinsky's point–line–plane), Bayer's and Moholy-Nagy's…
- **Palette:** #F8F7F3 #0E9F7A #2138C8 #F4E04D #D5DCEE #161C3A
- Shapes are amounts. A disc that doubles doubles its *area* (radius × √2); a weight three times heavier is a square of three times the area; a share of a whole is a ring of that share of the area. If the numbers would make a shape unreadably small, change the framing, never the proportions.
- Shapes have roles. Circle = what grows or moves; square = what stays or weighs; triangle = slope, time, pivot. One shape keeps one meaning through a film.
- Point → line → plane. The protagonist starts as a dot, draws a line by moving (its path stays on screen), and becomes a plane (a field, a disc that runs out of frame). Use this progression as the spine of an explanation.
- **Not:** Not Swiss Motion Graphics (there type is the material; here type is a label and the shapes carry the meaning), not Mid-century Cartoon (no characters, no faces), not Data Storytelling (no axes, ticks and legends as chrome: a ruler appears only when it measures something), not a slide deck (no…
- **Motion:** - Lines: one weight for paths (5 px), one for construction and leaders (2–3 px), butt caps. Lines only draw a path, a tangent, a leader or the grid; never a decorative frame.
- **Use for:** Finance and economics explainers, Mechanisms and principles, Titles and chapter cards
- **Source:** `lemomo-ai/lemo-opuscar` → `bauhaus-shapes`

### Pictogram Motion · 象形运动图形
> A beat-locked film built from three things only: a square-grid "core graphic" of circles, half-discs and tiny patterned cells whose rows slide past each other; geometric pictograms (objects, vehicles, weather, signs, and a disc-headed figure when one is needed) made of round-capped bars, discs and capsules; and bold bilingual type that slides up out of masks. Every cut lands on a drum hit. References (grammar only): Otl Aicher's 1972 Munich pictograms (geometric athletes);…
- **Not:** Not an isometric infographic (no depth, no 3D), not Swiss motion graphics (the pictograms and the pattern carry as much as the type), not a cartoon (pictograms never emote, figures have no faces), not a data film (numbers are labels, not charts).
- **Tech:** - Figure model (optional): unit = body height, origin at the hip; draw far limbs (mixed ~40 % toward the background), torso, near limbs, head. A second person sits behind, mixed further (~60 %). People can also appea
- **Use for:** Public services and city stories, Brand and event identity films, Explainers told through signs and objects
- **Source:** `lemomo-ai/lemo-opuscar` → `pictogram-motion`

### Scale Zoom Explainer · 扁平尺度漫游
> Solid flat shapes on a deep night-blue ground, each with one shade step and hard-edged ring "glows", drawn to true scale inside each frame, guided by a small character who is the camera's own lens. A continuous change of scale carries the viewer through orders of magnitude while a scale ribbon in the corner reads the field of view. References (grammar only): mid-century educational posters and flat vector science illustration (solid fills, two values per object, geometric…
- **Palette:** #1D2052 #252A63 #30367C #4D7CFE #3A5FD9 #3FD8AE
- Flat and opaque: every object is a solid colour plus at most one shade step. No gradients, blur, transparency, outlines or drop shadows.
- Glow is two hard rings: anything bright sits on two concentric solid discs one and two steps lighter than the night ground, like a screen print.
- True scale inside each frame, a readout for the camera: things in one frame are drawn to one scale; a corner ribbon (a log track with a few stop icons) and a field-of-view number come from the same camera.
- **Not:** Not Isometric Infographic (no isometric projection, no dioramas), not Data Storytelling (no charts on paper), not a 3D soft-body render (no rim light, bloom or depth of field), not Sci-fi Hologram HUD (no glowing wireframes), not a keynote (no header bars, centred stacks or page turns).
- **Tech:** - Roles: a geometric sans (e.g. Jost, OFL): titles 96–132 px weight 700 with tight tracking; labels 26–34 px weight 600; small caps tags 16–18 px weight 600 with letter-spacing 3 in mist or sun. One short Chinese lin
- **Use for:** Science explainers, Scale and size, Classroom
- **Source:** `lemomo-ai/lemo-opuscar` → `flat-space-explainer`

### Silhouette Rhythm · 剪影律动
> Pure black silhouettes against a saturated sunset, changing pose on every beat; on the key beat everything freezes and only the sky keeps moving. The water is the second canvas: reflections, ripples and back-lit droplets. References (grammar only): beat-locked silhouette commercials of the 2000s (flat black figures, every pose and cut on the beat); Lotte Reiniger's silhouette films (acting in profile, the outline carries everything); telephoto wildlife cinematography at…
- **Palette:** #090307 #FFF6DC #FFB347 #FC4D2B #E0245C #380A52
- The figure is one black shape. No detail inside it, no gradient, no outline, no shadow. Everything the viewer reads is in the contour.
- There is always light behind it: the sun disc, the bright band of the horizon, the glitter on the water. A silhouette sits on light, never on dark.
- Poses land on the beat and hold between beats. A group moves in unison; anything off the beat is a deliberate choice of the story.
- **Not:** Not Shadow Puppetry (no visible rods, no paper texture, no lamp behind a screen), not Paper-cut Lightbox (no layered paper, no inner light), not Red Paper-cut (no ornament inside the shape), not a sunset stock photo (the figures act, on a grid).
- **Tech:** - Roles: a heavy condensed sans for the title (120–150 px, e.g. Anton), a condensed sans for small lines (30–40 px, e.g. Barlow Condensed), a bold CJK sans for Chinese (≥ 34 px, e.g. Noto Sans SC). OFL, self-hosted,
- **Use for:** Music videos, Sports and team films, Nature and festival openers
- **Source:** `lemomo-ai/lemo-opuscar` → `silhouette-rhythm`

### Swiss Motion Graphics · 瑞士动态排版
> International Typographic Style in motion: a modular grid, one typeface, one signal colour, and movement as exact as a printing press. References (grammar only): 1950s–70s Zurich posters (Müller-Brockmann, Hofmann, Gerstner, Crouwel) for the grid, flush-left type, scale contrast and "designing programmes"; modern identity systems in motion (Experimental Jetset, Pentagram) for snaps on the beat. Never copy a specific historical poster's composition (no concentric-circle or…
- **Palette:** #EAE9E5 #FFFFFF #111111 #E30613 #F2F0EA #141414
- Pure 2D graphic design animated on a grid: flat paper, black type and bars, a very light grey and one saturated signal colour.
- Every element snaps to the grid, every move lands on a beat, nothing bounces.
- Rigor with one exception: the whole frame obeys a system, so the one element that doesn't becomes a character.
- **Not:** Not a keynote (no gradients, no glow, no device renders), not kinetic typography for a lyric video (words don't fly, spin or bounce), not data visualisation (bars have mass as graphic form, not as charted quantities, unless the grid gives them that meaning), not a Bauhaus pastiche of primary shapes.
- **Motion:** - Frame grid: 1920×1080, 12 columns, ~96 px side margins, 24 px gutters, 24 px baseline. The frame can act as a spread: a left page (the programme: numeral, rule text, notes) and a right page (the artifact).
- **Use for:** Brand identity, Events, Design education
- **Source:** `lemomo-ai/lemo-opuscar` → `swiss-motion`

### Text Flash Cuts · 文字闪切
> Avant-garde TV anime in the manner of the early-2000s "text frame" school: full-screen heavy Mincho title cards cut in for two to nine frames, architecture reduced to symbolic geometry, a red-black-white palette, characters as silhouettes or extreme close-ups, and the signature over-the-shoulder head tilt. Painted characters come from image generation; everything else (cards, buildings, rain, cuts, inversions) is code. References (grammar only): the early-2000s TV-anime…
- **Palette:** #D4162B #0A0A0C #F2EFE8 #8D8A84 #D8D4CC #26262A
- Type as picture. A word fills the frame, bleeds off an edge, or stands in a vertical column. Cards are dialogue, chapter titles and punctuation of the cut.
- Symbolic architecture. Stairs that never end, window grids, lockers, a one-point street: flat polygons, no props, no sky, no texture.
- Flat characters in three states only: black silhouette (far), flat cel colour (mid), fragment (an eye, a hand, a mouth corner) filling the frame.
- **Motion:** - Cards and titles: Noto Serif SC 900 (heavy Mincho feel, OFL). Single glyphs 700–1100 px, allowed to bleed off the frame on flash cards; dialogue columns 120–170 px, never bleeding.
- **Use for:** Suspense & drama trailers, Title sequences, Manifesto films
- **Source:** `lemomo-ai/lemo-opuscar` → `text-flash-cuts`

## Instruments & Evidence — 8 styles

### Archive Light Table · 档案看片台
> Real archive objects (glass negatives, slides, letters, telegrams, clippings, drawings) lie on a cool, backlit light table. A loupe comes down on one of them, and inside the glass the object comes alive: a negative turns positive, a line of type lights up, a number lifts off the page, a photograph opens into depth. Precise catalogue numbers, dates and readings are pinned to the objects. Clean, modern and quiet, with no vintage filter. References (grammar only): archive…
- **Palette:** #F7F9FB #15171A #FF5A1F
- The objects are real: scans of public-domain or licensed archive items, at their true proportions, with their real damage (broken corners, emulsion edges, folds, pencil marks). Nothing in them is drawn or generated.
- Light comes from below: the table glows a near-white cool grey; film and glass transmit it, paper glows warm at its edges, opaque things read darker than the table.
- The loupe is the camera's door: every dive into an object goes through a loupe that lands on it. The inside of the lens is where the object changes state.
- **Not:** Not Halftone Dossier (no newsprint dots, no aged-paper grade), not Satellite Briefing (objects on a table, not the ground from orbit), not Data Storytelling (no charts; the numbers live on the objects), not a keynote (no slides or header bars).
- **Tech:** - Roles: a monospace for identifiers, dates and readings (e.g. IBM Plex Mono, 17–34 px; readings 74–120 px); a sans for labels in the film's language (e.g. Noto Sans SC or Inter, 21–36 px); a serif only for titles an
- **Use for:** Brand history, Archive stories, Museums
- **Source:** `lemomo-ai/lemo-opuscar` → `archive-lighttable`

### Engineering Briefing Board · 工程简报板
> One real whiteboard wall, filmed: window light on enamel, ghosts of erased marker, frame and tray. Cut-out photographs of real things land on it with weight; tags, magnets, a ruler and stamps are pinned to it; marker ink draws itself in three colours with fixed meanings. The camera rides the lines from fact to fact and only at the end pulls back to show the whole briefing. References (grammar only): explainers filmed on a map wall; the long pull-back over a wall covered in…
- **Not:** Not Whiteboard Explainer (a hand drawing line art on a flat page): the board is a filmed object, subjects are photographs. Not Data Storytelling: comparisons are dimension lines in real units beside real objects. Not a keynote: no headers, centred bullets, page turns.
- **Tech:** - Ink (multiply): flat colour at about 90 %, lighter core, round caps, a wet-tip glint on the stroke being drawn. Lettering: a marker font revealed glyph by glyph with seeded tilt and baseline jitter. Erasing leaves
- **Use for:** Engineering, Option comparisons, Briefings
- **Source:** `lemomo-ai/lemo-opuscar` → `briefing-board`

### LiDAR Survey · 点云测绘
> Real airborne laser points of a real place, floating in the dark as a measured cloud; a scan line or a cutting plane passes through them and the points condense into a solid, raking-lit surface, which is then measured with hairline instruments. One designed camera move carries the whole film: the cloud is something you fly through, not a picture you look at. References (grammar only): survey and archaeology lidar visualisations (colour as height, the canopy removed);…
- **Palette:** #05080A #1F3F35 #5C9A7A #E2F3DC #C8B38C #BDB5A6
- The cloud is the data: every point is a real return at its measured position; points appear, glow, lift away or give way to a surface, but are never moved into a shape.
- Points become a surface: a front (scan line, cutting plane) behind which the cloud condenses into a solid model of the same place.
- Classification is a lever: ground, vegetation, buildings, water are layers to peel, isolate and recolour.
- **Not:** Not Sci-fi Hologram HUD (no invented interface: the points are real, sparse where the survey was), not Satellite Briefing (photographs from above; here a 3D cloud flown through), not Blueprint, not Low-poly Isometric, not Glass Product Render.
- **Tech:** - Roles: light condensed numerals for readings (110–130 px, e.g. Barlow Condensed 300); a monospace for instruments, coordinates, counts and source lines (19–22 px, e.g. IBM Plex Mono); a sans for labels in the film'
- **Use for:** Heritage, Environment, Site surveys
- **Source:** `lemomo-ai/lemo-opuscar` → `lidar-survey`

### Radar Sweep Documentary · 雷达扫描纪录片
> The world is black until a scan passes. A plane of light sweeps across terrain, machines and rooms; what it has touched lights up, then settles into echoes (contour lines, range rings, wireframe edges) that slowly fade. Facts arrive as instrument readings: thin titles, small monospaced type, gauges and timelines written on by the same scan, placed beside the thing they describe. References (grammar only): radar and sonar displays (sweep, return, decay); LiDAR and survey…
- **Palette:** #B3DBFF #F2C48D #FF8C78 #EEF2F6 #C4CED8 #96A2B0
- Existence is scanned. Nothing is lit by ambient light. A subject appears only when a scan reaches it: a bright front line, a short glow, then echoes that persist and decay. Black means "not yet seen", not "shadow".
- Echoes are the material. Surfaces resolve into contour lines, range rings around the subject, a survey grid and ghost copies of the scan front, each fading at its own rate. A moving subject leaves wireframe after-images: the echo records time.
- The subject keeps a cold rim. Once scanned, the hero object carries a thin cold rim light so its silhouette never sinks into the ground or the sky.
- **Not:** Not LiDAR Survey (no point clouds, no measured scan data; the scan is a light, the echoes are line geometry), not Sci-fi Hologram HUD (no glowing chrome, no floating panels, no invented interfaces), not Satellite Briefing (not a map or overhead imagery), not a keynote (no slides, no centred title…
- **Tech:** - Readings and labels: a light monospace (JetBrains Mono 300), 14–17 px, all caps, tracked +1.2 to +2.4 px; big numbers (a time, an angle, a ratio) in the thin sans at 50–150 px.
- **Use for:** History of science and engineering, Archaeology, sites and reconstructions, Astronomy, deep space and survey
- **Source:** `lemomo-ai/lemo-opuscar` → `dark-documentary`

### Satellite Briefing · 卫星简报
> Real satellite imagery of a real place, graded down to an analyst's grey, with thin white measurement lines drawn on the ground: a lock-on reticle, outlines, a range line, one reading. One continuous zoom built from stacked imagery plates carries the viewer from orbit to the ground and back, and time can run inside one locked frame. References (grammar only): open-source investigation films that annotate satellite pictures (thin lines on imagery, one claim per screen,…
- **Palette:** #070B0E #A1A7A9 #F2F5F6 #FFBE55
- The ground is a photograph: real, licence-clean, georeferenced satellite or aerial imagery of the actual place. Nothing on the ground is drawn, stylised or generated.
- Two layers, two truths: the imagery is what the satellite saw; the hairlines are what the analyst measured. Marks are thin, white, sparse, and sit on real coordinates.
- The grade moves with the story: orbit in true colour, the analysis layer in grey, colour back only where the story turns.
- **Not:** Not Data Storytelling (a chart on paper), not Sci-fi Hologram HUD (no glowing wireframes or invented chrome), not Blueprint, not Isometric Infographic (real nadir or oblique views, no diorama), not a keynote (no slides, header bars or chapter numbers).
- **Tech:** - Roles: a light condensed grotesk for the reading (96–130 px, e.g. Barlow Condensed); a monospace for instruments and dates (20–34 px, e.g. IBM Plex Mono); a sans for labels in the film's language (24–42 px); a seri
- **Use for:** Climate, News explainers, Geography
- **Source:** `lemomo-ai/lemo-opuscar` → `satellite-briefing`

### Security X-ray · 安检 X 光
> The film is seen through a baggage-screening console: objects are never shown, only their dual-energy X-ray image, where every material has its colour (organic orange, mixed green, metal blue, impenetrable black) and every outline comes from thickness, not from a drawing. The operator exists only as actions on the screen: a box dragged around an object, a zoom, a measurement, a material filter, a verdict. References (grammar only): real checkpoint and cargo screening…
- **Palette:** #080F1A
- Transmission, not rendering. Every pixel is the path length of the X-ray through matter, split by material class. Overlaps change the colour (a cable over clothes turns green), walls glow at their edges, solid metal goes dark.
- The colour code is the language. Orange = organic (Zeff < 10), green = mixed or light inorganic (Zeff 10–18), blue = metal (Zeff > 18), black = nothing got through. The legend sits on screen; the audience learns it within seconds.
- A machine with a person behind it. The console chrome (lane, belt speed, clock, bag counter, material legend, function keys, status) is always readable; decisions arrive as operator actions on the screen. If there is a voice, it is that operator in the first person: few words, flat, saying only…
- **Not:** Not Sci-fi Hologram HUD (no invented glowing chrome: the console is plain, functional, dark), not Exploded Teardown (objects are never taken apart or lit as solids), not Under the Microscope, not a medical scan film (luggage, belts, trays, a checkpoint), not a keynote (no slides, no centred title…
- **Tech:** - Machine voice: a monospace (e.g. IBM Plex Mono, OFL), 15–22 px for chrome, 56–64 px for the clock and counter, about 32 px for the status word. English only, upper case for states and keys, as a real console wo
- **Use for:** Airport and customs screening, Parcel and cargo inspection, Product internals
- **Source:** `lemomo-ai/lemo-opuscar` → `security-xray`

### Thermal Camera · 热成像
> The film is seen through a radiometric thermal camera: a low-resolution, slightly noisy picture in an iron palette where brightness means temperature, with the camera's own instruments on screen (colour scale, spot meters, area boxes, isotherm, hot-spot tracker). A scan line or a split turns the ordinary night picture into heat, and every number on screen is read off the temperature image itself. References (grammar only): building-envelope thermography reports (spot, box…
- **Palette:** #000008 #120554 #4D0894 #991294 #DB3352 #FA7812
- Temperature is the picture. Every pixel is an apparent temperature mapped through one palette and one scale; brighter means warmer, always. Nothing is coloured for drama.
- It looks like a sensor. A coarse grid (320×240 or 640×480 class, cropped to 16:9) blown up to the frame, optical softness, temporal noise, column stripes, lens shading. Never a clean gradient.
- Physics decides what glows. Surfaces get temperatures from heat flow (indoor vs outdoor, thermal bridges, leaks, bodies, engines), then emissivity and reflection decide what the camera reads: glass and bare metal look cold because they mirror the sky.
- **Not:** Not Sci-fi Hologram HUD (no glowing wireframes, no invented sci-fi chrome), not Data Storytelling (no charts on paper), not a neon colour grade (no false colour without a scale), not Under the Microscope (no lab optics).
- **Tech:** - Roles: a monospace for readings, scale ends, time stamp and measurement names (IBM Plex Mono, 22–40 px); a sans for labels (Noto Sans SC for Chinese 24–40 px, Inter for English 20–32 px). OFL, self-hosted, CJK subs
- **Use for:** Building and energy inspection, Wildlife at night, Machines and electrics
- **Source:** `lemomo-ai/lemo-opuscar` → `thermal-camera`

### Under the Microscope · 显微镜下
> Real, licence-clean microscopy of a real specimen, seen as it is, and one continuous change of scale that carries the viewer from the glass slide in the hand to a single cell. Focus breathes when the magnification changes, a focal plane sweeps when the camera lands, and every scale bar, field of view and reading comes from the image's own metadata. References (grammar only): Charles and Ray Eames' *Powers of Ten* (one continuous change of scale with a readout riding along);…
- **Palette:** #F4F1EC #0B0D0F #2A3036 #181B1F
- The specimen is a photograph: a real micrograph or whole-slide scan of the actual sample, CC0, public domain or CC BY. Nothing on the specimen is drawn, retouched or generated. A whole-slide image (WSI) is the ideal source: one sample, one registered pyramid from millimetres to microns, with the…
- Scale is the camera: one log-space dive (and, when the story wants it, the climb back) through nested plates of the same sample. The scale bar shortens and jumps in a 1-2-5 sequence, the field-of-view readout rolls, the magnification steps.
- Focus has a grammar: a rack-in from soft at the start, a short breath (blur + a hint of field change) each time the magnification changes, a focal-plane sweep across the frame when the camera lands.
- **Not:** Not Satellite Briefing (no grey grade; the stain keeps its colour), not Sci-fi HUD (no glowing wireframes or crosshairs), not Data Storytelling (no chart paper), not a keynote (no slides or header bars).
- **Tech:** - Roles: a light condensed grotesk for readings and the scale bar (40–72 px, e.g. Barlow Condensed); a monospace for instruments and pixel counts (20 px, e.g. IBM Plex Mono); a sans in the film's language for labels
- **Use for:** Biomedicine, Materials science, Skincare science
- **Source:** `lemomo-ai/lemo-opuscar` → `microscope`

## Line Diagrams — 8 styles

### Assembly-Line Diagram · 流水线图解
> A process explained as a factory cut open in elevation: a silhouette (a body, a machine, a building, a city) is sliced like a doll's house into rooms on floors, each room a work station with a machine, a numbered plaque and tiny workers; coloured pipes carry the goods between them, and the colour of a pipe is the legend. The camera rides one piece of cargo through the whole line, and every station starts working the moment it arrives. References (grammar only): Fritz Kahn,…
- **Palette:** #F2ECE0 #1D2030 #24345A #FBF7EE #EE9F87 #E04A2F
- One line, one direction. The subject is a process that turns one thing into another in steps. The film is a single continuous production line the cargo travels; every shot is a station on it, in order.
- Metaphor per station, said straight. Each step is one machine everyone can read (a press, a sieve, a weighing scale, a crane, a loading dock, a paint booth). The plaque gives both names: the machine's in English, the real thing's in Chinese (SIEVE | 沉砂池). The humour comes from the metaphor being…
- Colour is the legend. Each kind of output gets one spot colour; its pipe, its parts and its legend tag carry that colour for the rest of the film, so the viewer follows a colour instead of reading a label twice.
- **Not:** Not Isometric Infographic (no isometric or perspective view: everything is a flat front elevation), not Whiteboard Explainer (no hand, no drawing-on), not Exploded Teardown (no 3D parts flying apart), not Blueprint (full colour on paper, not white lines on blue), not a keynote (no slides, no…
- **Tech:** - Flat shadows. A Holmes shadow is the same shape offset down-right in one pale flat colour (plaques 5–6 px, large shapes 14–18 px). No soft shadows, no blur except motion blur on whip moves.
- **Use for:** How a process works, Biology and medicine, Supply chains and pipelines
- **Source:** `lemomo-ai/lemo-opuscar` → `assembly-line-diagram`

### Blueprint · 工程蓝图
> Engineering drawings that come alive on a sheet of cyanotype paper: white technical line work on Prussian blue, drawn in drafting order, with annotations that move. References (grammar only, never copy): the moving technical drawings in Prologue Films' *Iron Man* (2008) end credits, Leonardo's *Codex Atlanticus* pages, 19th-century US patent drawings (Fig. 1 / Fig. 2, part balloons, fine-line shading), the automaton drawings in *Hugo* (2011). No Marvel elements, no real…
- **Palette:** #18336B #2A58A6 #E7F0F9 #0D1116 #3A6DA8 #5B8CC4
- The whole film happens on one sheet of blueprint paper lying on a dark drafting table. The camera moves over it like an eye reading a drawing.
- White line work on uneven Prussian blue: centre lines, outlines, hatching, dimension lines, leader lines with numbered balloons, a title block, a notes column.
- A 2D line-drawing language: orthographic and oblique/isometric projection are allowed, 3D rendering never.
- **Not:** Not Hologram HUD (no glowing wireframe, no 3D orbit), not Whiteboard (no marker on white), not Copperplate Engraving (no burin tonal hatching as the whole look).
- **Motion:** - Subtitles are drawing notes: a light translucent box with double white rules, a "NOTE / n" cell, the text lettered on in ~0.35 s, a small leader tick. Placed per shot in empty sky, never fixed to the bottom (th
- **Use for:** Engineering, Hardware launches, Tech explainers
- **Source:** `lemomo-ai/lemo-opuscar` → `blueprint`

### Color-Coded Mechanism · 分色机械图解
> A real mechanism built in 3D and coloured like an anatomy plate: a pale ground, one flat colour per subsystem, the part being explained in a single accent. The machine runs truthfully (true ratios, true rates, true physics), and the camera cuts it open, explodes it by system and follows the force through it. References (grammar only): anatomical atlas plates (one colour per system, colour as the legend); technical drawings and section views (hatched cut faces, title blocks,…
- **Palette:** #F3F0EA #DDD8CF #25282D #E6B94F #79B09F #8A97D4
- Colour is the structure. Every part takes the colour of the system it belongs to (energy source, transmission, control), everything else is one light neutral. A viewer reads the machine's organisation from the colours before reading a word.
- Soft cel, own-colour outlines. Two-tone flat shading with no reflections; every part is ringed in a darker shade of its own colour, never in black.
- The machine is true. Wheels turn by their tooth ratios, the oscillator swings at its real rate, numbers on screen are computed from the model. Slow motion is stated on screen.
- **Not:** Not Exploded Teardown (no product photography, no materials, no real-brand object), not Blueprint (light ground, filled solids, not line-only), not Isometric Infographic (a perspective camera that moves through the object, not a fixed diorama), not Glass Product Render (opaque, matte, no…
- **Motion:** - Outlines (demo/film-outline.js): a second pass of view normals and depth; an edge on the near side of a depth step or on a crease is drawn in the part's own colour × 0.52 mixed with 28 % ink. 2× supersampling; li
- **Use for:** How machines work, Product and engineering explainers, Science teaching
- **Source:** `lemomo-ai/lemo-opuscar` → `precise-mechanism`

### Exploded Teardown · 产品拆解
> A real product, built from its own engineering files (CAD, PCB layout, bill of materials), lit like a studio packshot and taken apart in front of the camera: the layers lift on one axis, the camera travels between them, every part is named with the numbers its files contain, and it closes again into one object. References (grammar only): hardware-launch exploded films (layer stagger, orbit timing), repair-guide teardowns (opening order, the macro on the part that matters),…
- **Palette:** #34363A #0D0E10 #F1EFE9 #FF6B3D
- the object is real and exact: geometry, positions and counts come from the product's own files (STEP, KiCad, BOM, assembly guide). Nothing is eyeballed that a file can give;
- it is shown apart: layers float on one axis with even, readable gaps, each still oriented as it sits in the product;
- it is photographed, not drawn: physically based materials, a studio key light, a cool rim, an HDRI reflection, soft contact shadow on an invisible floor;
- **Tech:** - Names: a clean sans at medium weight in the film's script (28–32 px; Noto Sans SC 500 in our demo). Specs and numbers: a monospaced face (15–22 px; JetBrains Mono) so digits line up and read as measurement. A neutral g
- **Use for:** Hardware launches, Product pages, Spec explainers
- **Source:** `lemomo-ai/lemo-opuscar` → `teardown`

### Instruction Manual Art · 说明书插画
> The film is a printed assembly manual: one sheet of off-white paper, black line art in true isometric (45°), flat white parts, faceless people at real proportions, and the manual's own signs (step numbers, parts call-outs, dotted guide lines, flat arrows, magnifier circles, a do/don't box) telling the story. The view never turns; the camera only travels over the page. References (grammar only): flat-pack furniture and construction-toy building manuals, aircraft safety…
- **Palette:** #F4F1EA #1E1D1B #FFFFFF #ECE8DF #DCD7CC #F7D35A
- One angle: true isometric, orthographic. Azimuth 45° (every object is seen across one vertical edge), elevation 35.264° (arctan 1/√2): the three axes meet at 120° on screen, horizontal edges run at 30°, vertical edges stay vertical, nothing gets smaller with distance. The whole film keeps this one…
- The frame is the paper. The page is seen square-on; there is no desk, no folded card in 3D, no perspective on the sheet. Every shot is a part of one printed page.
- Line art with flat fills. One ink line weight, flat colour, at most three values per object (top lightest), no gradients, no cast shadows.
- **Not:** Not Isometric Infographic (no coloured diorama, no data panels), not Isometric People Scene (no painted scene, no faces), not Blueprint (dark ground, technical dimensions), not Exploded Teardown (no rendered product, no photoreal materials), not a slide deck (no header bars, centred titles or page…
- **Tech:** - Subtitles bottom left, left-aligned: Chinese (e.g. Noto Sans SC 500, 38 px) over English (Inter 500, 32 px, ink at about 78 %), one line each, an 8 px yellow bar on the left marking the line being spoken. No box, o
- **Use for:** Assembly and set-up guides, Safety instructions, Product onboarding
- **Source:** `lemomo-ai/lemo-opuscar` → `instruction-manual`

### Isometric Infographic · 等距信息图
> A system diagram comes alive: an isometric diorama of flat three-tone blocks, thin ink labels and Isotype numbers, where things open up to show their insides and the numbers are drawn, not stated. References (grammar only): *Monument Valley* (true-isometric architecture, flat colour blocks, three fixed tones per face, a camera that pans and zooms but never breaks the projection); *SimCity 2000*-style cutaway dioramas (a floating board with soil strata, the whole system…
- **Palette:** #231A2C
- Flat, true isometric. No perspective, no outlines on solids; shapes are separated only by the three tones of each face. The projection never rotates or tilts.
- Infographic furniture is part of the picture: leader lines, label pins, dashed cut lines, hatched section faces, tracking rings, a legend, a route line all live in the world.
- Numbers are built from icons (Isotype), and they add up.
- **Not:** Not low-poly 3D (no perspective, no lighting beyond three face tones), not a flat 2D explainer (everything has isometric depth), not a blueprint (colour blocks, not line drawings on blue).
- **Tech:** - Three tones per face chosen from its normal: top light, left (+y) mid, right (+x) dark. Derive tones from one base colour: mix toward warm white ~20 % for the top and toward a cool dark (e.g. #231A2C) ~22 % for t
- **Use for:** Process explainers, Supply chains, Annual reports
- **Source:** `lemomo-ai/lemo-opuscar` → `iso-infographic`

### Line-Art Cutaway · 线稿剖面图解
> A real-sized object, modelled in 3D and traced live into a black-line technical drawing on warm white paper: it turns, comes apart, is cut open and is flown into, while numbered leaders, dimension lines and section hatching stay attached to its parts. One single accent colour belongs to the one path the film explains (a signal, a current, an airflow). References (grammar only): textbook and patent drawings (line hierarchy, hatching, leaders), engineering title blocks,…
- **Palette:** #F6F5F0 #141414 #5A5955 #FBFBF9 #EDEDEA #DCDCD8
- everything is line on paper: warm white paper with a faint grid, black ink outlines, light grey value only to give volume. No lighting drama, no shadows, no reflections, no depth of field;
- the lines have a hierarchy: the silhouette is thickest, edges where one part hides another are medium, creases and small parts are thinnest and greyer;
- one accent, one meaning: a single saturated colour marks the path the film is about, and nothing else (no accent decoration, no accent buttons, no accent backgrounds);
- **Motion:** 3. creases and small parts (small depth jump or normal angle): about 1 px, a lighter graphite.
- **Use for:** Hardware explainers, Product engineering, Science education
- **Source:** `lemomo-ai/lemo-opuscar` → `hardcore-info`

### Pen Plotter · 笔式绘图仪
> A pen plotter on a desk draws the subject one stroke at a time: real pens, real ink on paper, real machine motion. Maps, charts and lettering appear as polylines a gantry lays down, with pen changes at a rack, pen-up travel and pen-down ink, and the camera lives on the desk with the machine. References (grammar only): flatbed plotters of survey and drafting offices (HP-GL era pen carousels, multi-pen drafting plots); hand-drafted topographic maps (contours, hachures,…
- **Palette:** #F1ECDF #16161C #763C1A #686662 #CC221A
- Every mark is a stroke. Nothing appears that a pen could not have drawn: no fills, no gradients, no type set as a font. Tone is hatching; weight is a wider nib or the same stroke traced twice; letters are single-line strokes or traced outlines.
- The machine is in the shot. Gantry, carriage, pen holder and pen rack are physical objects with weight; the pen is where the line ends.
- Machine time is honest. Pens move at plotter speed with acceleration and braking, drop and lift, and go to the rack to change. Time is saved by editing and by the camera, never by a pen that flies.
- **Not:** Not Blueprint (no white-on-blue, no CAD chrome), not Data Storytelling (no screen-space charts that grow by tweening), not Whiteboard Explainer or One-line Drawing (no hand, no marker; the line is mechanical, not gestural), not Engineering Briefing Board (the sheet is being made, not presented).
- **Motion:** - Kinematics: trapezoidal velocity per move. Reference values: pen-down ≈ 60–125 mm/s, pen-up ≈ 200–300 mm/s, acceleration ≈ 1000–2500 mm/s²; drop and lift ≈ 0.07–0.1 s; a pen change ≈ 2–4 s (travel to the rack, lowe
- **Use for:** Maps and terrain, Measurements and records, Generative and data drawings
- **Source:** `lemomo-ai/lemo-opuscar` → `pen-plotter`

## Print & Printmaking — 8 styles

### Copperplate Engraving · 铜版画
> An intaglio plate that engraves itself: a burin cuts swelling lines into copper, a proof is pulled, and the figure builds up — outline, hatching, cross-hatching — until engraved lettering, magnified details and a hand-laid wash make a finished plate. References (grammar only): 19th-century natural-history plates — Haeckel, Audubon, Westwood, the *Britannica* copperplates (centred subject, numbered roundels, roman title over an italic name, "del." / "sculp." credits, the…
- **Palette:** #F1E8D2 #1C1510
- **Not:** Not a woodcut (black block, white gouges — woodcut), not a pen sketch (loose broken lines — urban-sketch), not an engineering drawing (blueprint), not a sepia filter.
- **Tech:** - Ink is one warm near-black (~#1c1510). Width ratios: outlines heaviest (swelling ×0.45–1.35), first hatching from a hair (~0.18 px) to ~2 px, crossing ~0.8×, third family ~0.6×, hair and stipple finest. Spacing i
- **Use for:** Museum labels, Science explainers, Brand heritage
- **Source:** `lemomo-ai/lemo-opuscar` → `engraving`

### Halftone Dossier · 网点档案
> A retro print case file: cream archive paper, overprinted halftone dots in a few flat inks, huge heavy headlines with misregistered shadows, rubber stamps that slam, and thick-outlined characters. The film is a file that is read out one exhibit at a time. References (grammar only, never copy): Ben-Day-dot pop-art printing (Roy Lichtenstein era comics) for dot density as shading; riso/offset overprint zines for multiply layers and misregistration; police mugshot height…
- The whole film is paper. A warm cream sheet with low-frequency mottling, fine grain, a vignette and a fold; dark scenes are printed on it too, never glowing.
- Shading is never a gradient: it is halftone dots whose size follows a density field. Two or three dot layers at different screen angles overprint (multiply); that is the "printed" feel.
- Bureaucratic apparatus: case numbers, file chips, numbered exhibits, height charts, name plates, stamps. Their seriousness is the frame; the subject can be grave or trivial.
- **Not:** Not Risograph (no grainy two-ink riso texture as the whole look, no zine collage), not Swiss motion (no grid-driven kinetic type on white), not Rhythm Game Show (no candy sets, no rhythm-game rounds). Dots, paper and stamps must be visible in every frame.
- **Motion:** - Line boil: turbulence displacement (small, ~5 px) reseeded ~10×/s plus a fine ink-grain mask that eats a little of every fill. Characters and hand-drawn props only; never on text, halftone, HUD or captions.
- **Use for:** Humour, Pet content, Social shorts
- **Source:** `lemomo-ai/lemo-opuscar` → `halftone-dossier`

### Pop Art · 波普艺术
> Sixties screen-print and pop-art poster language used to tell something: Ben-Day dots fixed to the paper, heavy black key lines, flat red, yellow and blue, plates that never quite register. Every frame is one whole printed poster; the camera pushes into the dots, pulls back to the wall of prints, and moves through the shapes of the print itself. References (grammar only): 1960s silkscreen editions (the same image repeated across a sheet, each pull a little different, one…
- **Palette:** #E4232B #FFD21F #1E62B0 #141414 #F8F2E2
- A printed object, not an illustration. Four plates (red, yellow, blue, black key) on paper. Every middle tone is a dot screen; there are no gradients, no soft shadows, no transparency.
- Dots live on the paper. The screen is fixed in page space at 45°: the closer the camera, the bigger the dots, until one dot is the size of a coin. Distance and emphasis are told by dot size.
- Repetition is meaning. The same print pulled again and again, edge to edge, with small differences in register and ink: mass production, copies, sameness. Changing one tile's colourway against the wall is the strongest gesture the style has.
- **Not:** Not Halftone Dossier (cream archive paper, soft colours, characters), not Risograph Print (pink/blue/yellow soy inks overprinting into new colours), not Silkscreen Travel Poster (scenic places in flat layered colour, no dot screen), not Swiss Motion Graphics (grid type with no printed image), and…
- **Motion:** - Labels: a paper slip with a black frame and a plate-coloured offset block behind it, tilted ±2°, at a fixed corner of the frame. Headline line (condensed or a heavy grotesque such as Archivo Black, 90–130 px) over
- **Use for:** Everyday-object explainers, Brand and product posters, Small data stories
- **Source:** `lemomo-ai/lemo-opuscar` → `pop-art`

### Risograph Print · 孔版印刷
> Animation that looks printed, frame by frame, on a stencil duplicator: two or three translucent spot inks overprinted on warm paper, halftone dots, ink grain, and plates that never quite line up. References (grammar only): Tom Haugomat's riso illustrations (colour fields and silhouettes, a small figure in a large world, extra colours made by overprinting); Jacques Tati's *Jour de fête* (comedy staged small in a wide frame, everyday sounds as rhythm); real riso prints…
- **Palette:** #F4EEE2 #0078BF #FFE800 #FF48B0 #00838A #FF7477
- A tiny palette: 2–3 spot inks on warm off-white paper.
- Overprint mixing: inks multiply, so two inks make a third colour and all three approach black; a tint of one ink over a solid of another gives the brightest mixes.
- Misregistration: every plate lands a few pixels off; edges show slivers of paper or a coloured halo.
- **Not:** Not flat vector art with a noise overlay (every colour comes from the plates), not CMYK pop-art halftone (no process colours, no keyline), not screen-print posters (riso ink is translucent and grainy, not opaque). Never show the RISO brand, logo or machine trade dress; ink names are colour…
- **Motion:** - Subtitles: a paper-white knockout strip (zero ink, small radius) with text on one plate, ~40–46 px; its edges catch misregistration fringes. Hold ≥ max(1.8 s, speech + 0.6 s).
- **Use for:** Indie brands, Zines, Lifestyle
- **Source:** `lemomo-ai/lemo-opuscar` → `risograph`

### Scratchboard Long Take · 刮版画长镜头
> A three-dimensional world rendered as a scratchboard print, ink and paper with one red, crossed by one unbroken camera move. Depth, weather and light are all cut lines; the camera travels through the print instead of the print being turned page by page. References (grammar only): wood engraving and scratchboard illustration (tone made by the width of parallel cuts), Japanese shin-hanga landscapes (layered planes of mountain, forest, water), and the single-take tracking shot…
- **Palette:** #16171B #EDE5CD #C4332B #DFA443
- Only ink, paper and one red. Every value is either ink or paper; grey exists only as a density of lines. One red is reserved for one small subject. A warm yellow may appear for the sun, a lamp or one material, never as a second accent.
- Tone is cut, not shaded. Shadow sides of hills carry knife lines that run down the fall line; skies are parallel horizontal cuts whose width makes the light; snow is paper with a few drift strokes; water is ink with cut ripples.
- Real depth, flat marks. The scene is built in 3D (terrain, rivers, thousands of trees, buildings), but every surface is drawn with flat marks fixed in world space, so the layers slide past each other like a printed diorama.
- **Not:** Not woodcut (flat printed blocks, a mostly static camera, one block per image). Not ukiyo-e (flat colour fields, no depth travel). Not a toon-shaded 3D game (no smooth shading, no gradients, no specular). Not a pencil sketch (no hatching that follows form loosely; every line is a knife cut with a…
- **Motion:** - Sizes at 1080p: at most three sizes per frame; nothing smaller than 28 px for Chinese or 22 px for Latin; every word at least 5% inside the frame. Left-aligned blocks, aligned by optical edge.
- **Use for:** Journeys, Wildlife, Landscapes
- **Source:** `lemomo-ai/lemo-opuscar` → `printed-long-take`

### Silkscreen Travel Poster · 丝印旅行海报
> Opaque, hard-edged flat inks pulled one colour at a time through a screen: 4–6 inks per poster, stepped colour bands instead of gradients, thin paper-white gaps where the registration slips. Information is revealed the way the print is made: one layer, one beat. References (grammar only): - 1930s–40s WPA national-park screen prints: 4–6 flat inks, lit and shade faces, stepped-band skies, a dark information band, concentric sun rings. - Fifty-Nine Parks (contemporary):…
- **Palette:** #F6CD98 #EE9A73 #9A7FA8 #3E7079 #1E3B3F #FBE6B4
- Registration: every layer offset 1–3 px at 1080p; a knocked-out shape leaves a crescent of bare paper.
- Overprint edge: a faint multiply ghost ~2 u off under each ink, leaving a darker sliver where ink laps over ink.
- Ink thickness: a light rim top-left, a dark rim bottom-right, fills only; fresh ink has a wet sheen that fades within a second.
- **Not:** Not risograph (translucent fluorescent overprint with halftone grain), not ukiyo-e (key-block line work with bokashi), not woodcut (carved line), not low-poly (3D facets). This style is opaque, line-free, flat and banded.
- **Tech:** - Texture budget: fine paper tile, mottle multiply ~55 %, pinholes ~75 %, light encode grain. More reads as risograph.
- **Use for:** Destination guides, Tourism, Event posters
- **Source:** `lemomo-ai/lemo-opuscar` → `silkscreen-poster`

### Vintage Engraving Collage · 复古版画拼贴
> A magazine collage made on a paper table: public-domain engravings, stamps, old photographs and printed ephemera are cut out with a white paper margin and laid over torn sheets of flat colour, and the pieces move like cut-out animation, on twos, with paper thickness and real shadows. Numbers are drawn as our own "data engravings": engraved lines that swell with the value. References (grammar only): Terry Gilliam's cut-out animation (hinged moves, pieces that pop out, the…
- **Palette:** #ECDFC2 #F6EEDB #221C17 #C65F3A #2F7F7A #E1AB3B
- Real printed matter, cut by hand. Every figure is a cut-out of a real public-domain print (an engraving, a stamp, a news photo, a line drawing), with a slightly rough white paper margin around it. Nothing is drawn in a vector or 3D way to look printed.
- Flat torn colour behind it. Large torn sheets of a few flat colours (teal sky, ochre disc, mustard sun, cream strips, paper clouds) make the space; their edges show a white fibre fringe.
- It is paper on a table. Every piece has a thickness (a 1–1.5 px cut edge), a shadow from a top-left light that grows softer and further as the piece lifts, and a paper back that shows when it turns over. The table is old paper, visible at the edges.
- **Not:** Not Halftone Dossier (that one is a case file of documents; here the printed matter is cut free and performs), not Woodcut Print or Copperplate Engraving (we never re-engrave the whole frame; engravings arrive as found pieces), not Paper Pop-up Book (no 3D folds or depth stages), not a scrapbook…
- **Tech:** - On screen: Chinese ≥ 34 px, English labels ≥ 24 px, data numbers large enough to read at the widest framing they appear in.
- **Use for:** The history of an object, Magazine-style explainers on ideas and society, Archive and collecting stories
- **Source:** `lemomo-ai/lemo-opuscar` → `vintage-collage`

### Woodcut Print · 木刻版画
> A relief print that carves itself: every frame is a black wood block, and light only exists where a knife has cut it away. One colour at most, and only for the thing that burns. References (grammar only): Frans Masereel *Passionate Journey* (1919) and Lynd Ward *Gods' Man* (1929), wordless woodcut novels told as a sequence of self-contained plates; Käthe Kollwitz's woodcuts, where emotion lives in the direction of the gouge; Gustave Doré's engraving, where line spacing and…
- **Not:** Not copperplate engraving (no swelling burin lines on white, no crosshatch built up from white ground), not linocut poster art (no flat colour areas), not a black-and-white photo run through a threshold filter (the cuts must follow the form).
- **Tech:** - Captions are letterpress in the paper margin, below the plate, like a plate caption in a woodcut novel. They never cover the image. A letterpress old-style face (IM Fell English, OFL) around 40–44 px, in ink, pushe
- **Use for:** Folk tales, Craft brands, Book trailers
- **Source:** `lemomo-ai/lemo-opuscar` → `woodcut`

## Procedural canvas — 7 styles

### Crosshatch ink
> A sketchy ink line that boils on 2s, crosshatch and coloured-pencil shading clipped inside shapes, stipple, paper grain. Warm cream paper and wood by day; navy "inside the computer" worlds with periwinkle lines and glowing accents.
- **Palette:** #3A2417 #F4ECD9 #EFE5CF #D6A466 #F0C55A #5F9C5C
- ink(points, { w, color, amt, key, frac, double }): a wobbly stroke reseeded every boil step; frac writes it on.
- paint(points, { fill, w, line, tex: [...] }): fill, then textures clipped inside — hatch (angle, gap, dash, dens(x, y)), cross, pencil (coloured-pencil strokes), stipple — then the ink outline.
- Shade with a density function (dens: (x, y) => 0..1) rather than flat fills: light from the top-left, darker toward the bottom-right.
- **Motion:** On 2s: lines boil (re-wobble) every 2 frames even in held shots — the drawing is alive when nothing moves.
- **Source:** `cth9191/animate` → `crosshatch`

### Cut paper
> Torn-edge paper shapes with soft drop shadows, paper grain and crayon in the fills, patterns (stripes, dots, gingham, wood grain), full-bleed colour worlds, and characters with simple faces. Collage-style animation: playful, warm, busy with small life.
- **Palette:** #2A1D18 #FBF6EA #F3EAD6 #26315F #C08048 #D9A441
- cut(points, fill, { pat, crayon, grain, shadow, tear, sy, sb }): every shape is torn paper — a wobbly torn edge (tear), a soft shadow (sy offset, sb blur), grain and an optional crayon scribble in the fill.
- Patterns: pat.stripes, pat.dots, pat.gingham, pat.grainWood, … clipped inside the shape.
- One dominant wall colour per scene, a floor or table, then props in front.
- **Motion:** On 2s: everything (boil, camera, moves) keys on B = floor(F / 2).
- **Source:** `cth9191/animate` → `cut-paper`

### Isometric line art
> Calm, precise product illustration: objects in 2:1 dimetric isometric on a white ground, drawn only with constant hairlines. Grey silhouettes and edges, lighter inner and receding lines, faces filled white so nearer objects hide farther lines. Rounded slabs and plates with visible thickness, stacked layers, grids of repeated parts (keys, vents, pillars, ports), and one tiny dark accent per frame. Motion on 1s with spring settles; otherwise still. Studied from MIT-licensed…
- **Palette:** #FFFFFF #A4A4AC #E0E0E4 #232327 #5C5C64 #9A9AA2
- **Motion:** On 1s (ones: true): motion is smooth; nothing boils. Held frames are truly still apart from tiny idle life (the hero's bob, a lamp toggling once a second, steam, a leaf sway).
- **Source:** `cth9191/animate` → `isometric`

### Math
> A manim-style math explainer look. Coloured math on a near-black stage: - serif type that is Written on - axes, number planes and graphs that ShowCreation sweeps draw - equations and shapes that Transform into each other - a tracking dot with a live decimal readout - a small pi-shaped hero with eyes that watches the math happen
- **Palette:** #0E0E10 #FFFFFF #BBBBBB #888888 #444444 #29ABCA
- **Motion:** On 1s (STYLE.ones = true): TT advances every frame. Easing is manim's smooth (smoothM, a sigmoid with inflection 10) or thereBack for Indicate / hop moves. Never linear, except a value that a tracker drives.
- **Source:** `cth9191/animate` → `math`

### Pixel
> Pixel art. Every picture is drawn at a low internal resolution — 90x160, 135x240, 180x320 for a 9:16 frame — with whole-pixel primitives in a limited palette, then scaled up nearest-neighbour to 1080x1920. Hard square pixels, ordered (Bayer) dithering instead of gradients, a built-in 5x7 bitmap font, sprites from string arrays, and screen effects that belong to a device: an LCD grid for a handheld, scanlines and a curved-tube vignette for an arcade. Resolution can tell…
- **Palette:** #14101E #232A4E #2F5FA8 #5FB4E6 #A8F0F0 #F4F0E6
- **Motion:** On 2s (STYLE.ones = false). TT steps at 12 fps; a one-pixel-per-step move is a steady 12 low-res px/s, sprites have two frames, and on-1s motion would only add in-between positions that pixel art doesn't draw. A piece that needs smooth scrolling can set…
- **Source:** `cth9191/animate` → `pixel`

### Riso
> A three-ink risograph print on cream paper: halftone screens at their own angles, overprints instead of mixed colours, plates a few pixels off register, ink dropouts that sparkle in the darks. Flat, bright, a little worn, on 2s.
- **Palette:** #F2ECE3
- **Motion:** On 2s: TT steps every 2 frames, wobble reseeds with B; misregistration, dropouts and line pressure cycle through 3 variants (B % 3), so the print shimmers without crawling.
- **Source:** `cth9191/animate` → `riso`

### Sketchbook
> Graphite and one accent colour on a warm sketchbook page. Every line is drawn by hand and boils on 2s. Things get pencilled in, inked over, then coloured with a quick scribble, and hand lettering on the page does the narrating. The page is the world: its dot grid, spiral binding, smudges and coffee ring stay in view, and the camera moves across the page instead of cutting away from it.
- **Palette:** #F2EAD8 #2A2420 #6F6A63 #9A948B #D97757 #B85C3F
- **Motion:** On 2s (TT steps every 2 frames). Everything boils, including the page grain.
- **Source:** `cth9191/animate` → `sketchbook`

## Sketch & Board — 7 styles

### Chalkboard · 黑板粉笔
> A real classroom blackboard on which chalk writes itself, stroke by stroke in true stroke order, with no hand, no chalk stick and no eraser in sight. One idea is taught the way a teacher does it: write what people think, wipe it with one pass, write what is true in the same place. References (grammar only): a primary-school literacy lesson on a sliding double blackboard; the way a teacher underlines the parts of a character, circles one component and wipes a wrong line.…
- A clean, freshly wiped board. One even deep ink green with its own fine grain and very slow mottling. No history on the slate: no old swirls, no ghost lessons, no floating dust, no bokeh.
- Writing that grows like a hand writes. Strokes appear along their centre line in the correct stroke order, with pressure: pressed starts and corners, points that lift, 捺 feet that spread, hooks flicked off.
- Three chalks at most. White for structure, one accent chalk for the single part the lesson tracks, one pale chalk for a second hand (a pupil, a visitor).
- **Not:** Not Whiteboard Explainer: that style is a bright glossy board, coloured markers, floating marker props and magnets, ghost marks of old lessons, and a camera travelling across a knowledge map of many regions to explain how something works. Chalkboard is a dark matte slate with nothing floating in…
- **Tech:** - Sizes at 1080p: big characters 300–450 px; labels ≥ 55 px CJK and ≥ 30 px Latin cap height; small writing gets heavier chalk so no stroke is thinner than 3 px.
- **Use for:** Word origins, Myth-busting, Lessons
- **Source:** `lemomo-ai/lemo-opuscar` → `chalkboard`

### Marker on Paper · 马克笔白纸速写
> A pad of matte white paper and one bullet-tip permanent marker in black, with a red and a blue marker for meaning only: blue is what we know, red is what we want. A problem is drawn, reasoned out and answered one sheet at a time, stroke by stroke, with no hand and no pen in sight. When a sheet is done it is pushed through or peeled away and the next one begins. References (grammar only): one-idea-per-drawing science explainers made with a marker on paper, and a maths…
- **Palette:** #FAF9F5 #1B1C20 #E23B2E #2456D6 #463F33
- The frame is the sheet. A warm matte white paper fills the screen; no desk, no pad edge, no props, no hand, no pen.
- One bullet-tip marker line. Thick (6–10 px at full frame), near-constant width, a slightly denser touch-down, a slight lift at the end, corners overshot because each side is a separate stroke.
- Three inks with fixed meanings. Black builds everything; blue marks the givens; red marks the unknown and, later, the answer. Red is always the last stroke on a sheet.
- **Not:** Not Whiteboard Explainer: that is a glossy board with ghost marks, floating markers and magnets, and a camera travelling over one big knowledge map. Not Chalkboard: dark slate, chalk grain, wipe-and-rewrite. Not a sketchnote: no dot grid, no fineliner, no grey or yellow marker fills, no page-wide…
- **Tech:** - Canvas 2D. Each stroke is a filled ribbon (bullet nib, width ≈ constant, ±3 % noise, a 0.86→1 ramp over the first 3 widths, a 10 % lift over the last 2) built from a resampled, Chaikin-smoothed polyline with a slow arm
- **Use for:** Worked problems, Science explainers, Lessons
- **Source:** `lemomo-ai/lemo-opuscar` → `marker-paper`

### One-line Drawing · 一笔画
> A single ink line that never leaves the paper. Everything on screen is that one line being drawn; scenes don't cut, they morph. References (grammar only): Osvaldo Cavandoli's *La Linea* (1971) — one line is both the world and the character, and transformations of the line are the jokes and the transitions; Gjon Mili's 1949 photographs of Picasso drawing with light — the confidence and speed of a single gesture; Norman McLaren's *Begone Dull Care* and *Boogie-Doodle* — lines…
- **Palette:** #1D1A17
- One continuous line on warm white paper. The pen never lifts: in code the whole film can literally be one point array, from the first touch of the nib to the last frame.
- Everything is a line: characters, places, objects, even time. No fills, no shading, no second line weight, no background art.
- We watch the line being drawn: the camera follows the nib with a little lag and anticipation.
- **Not:** Not a whiteboard explainer (no hand, no marker, no erasing, no text-heavy boards), not ink wash (no tones, no brush bloom as a look), not a line-art animation with cuts and many strokes.
- **Motion:** - Text is written, like the line: a handwriting face (e.g. Caveat) for subtitles, ink at ~84 %, no box, centred near the bottom, written on left to right (~0.2 s + ~17 ms per character) behind a soft paper-colour
- **Use for:** Brand stories, Life milestones, Minimal ads
- **Source:** `lemomo-ai/lemo-opuscar` → `one-line`

### Sketchnote · 视觉笔记
> One page of visual notes on dot-grid paper, drawn while you watch: a black fineliner writes and draws, a grey marker gives volume and shadow, one yellow marker carries the single thing that matters. Banners, rounded boxes, fat arrows, icons and hand lettering grow stroke by stroke; the camera rides the pen across the page and ends by pulling back until the whole page reads as a poster. References (grammar only): live sketchnoting and graphic recording of talks (banners,…
- **Palette:** #FBFAF6 #1E1E22 #5B5852 #F5AA00
- The frame is the page. Warm white dot-grid paper fills the screen; there is no desk, no notebook edge, no hand and no pen prop.
- Everything is drawn in front of you, at the speed of a pen: outlines first, then the marker, then the words. Nothing fades in, nothing slides in.
- Three tools only: one black fineliner, one grey marker (three strengths), one yellow marker.
- **Not:** Not Whiteboard Explainer (no hand, no wipe, a page that is kept, not erased; tone and volume from marker, not a bare marker line), not Urban Sketch · Pen & Wash (no watercolour, no perspective scene), not Chalkboard, not Data Storytelling (charts are hand-drawn notes on the page, not a chart…
- **Tech:** - Paper: a flat warm white with a faint grain texture anchored to the page, and a dot grid (26 px pitch, 1.3 px dots) drawn in world space so it scales with the camera.
- **Use for:** Lecture notes, Science explainers, One-page summaries
- **Source:** `lemomo-ai/lemo-opuscar` → `sketchnote`

### Stick-figure Explainer · 火柴人讲解
> Plain stick people on warm paper, one accent colour, and a logic you can watch: people stand on a "system line", react to each other, and hold hands. A held hand is not two arms touching but one continuous curve from one shoulder to the next, so a crowd can join into a line, a ring or a shape, and a red pulse can run through all of them. References (grammar only): explainer channels that argue with stick people and one accent colour (one idea per screen, generous white…
- **Palette:** #F3F0EA #24242C #9C978C #E2DDD2 #EB4A2A #E9E4DA
- The people are the diagram. Each figure is a round head and single curved lines, all one weight (an "even hose" body). No faces, no hands, no props for heads. The figures act out the idea: who changed, who reacts, who is connected.
- Bodies are continuous. The head sits on the neck with no gap; limbs grow from one point on the torso; every limb is one smooth curve, never a polyline with a corner at the elbow or knee.
- Hands join into one line. Two held hands become one tangent-continuous curve between two shoulders. A row of people holding hands is a single line; a ring of people is a closed shape.
- **Not:** Not Whiteboard Explainer (no hand drawing the frame, no marker texture), not Pictogram Motion (figures are drawn lines, not filled ISO-style pictograms), not Data Storytelling (the people are the chart), not Mid-century Cartoon (no character design, no faces, no props).
- **Tech:** - Line weight: one weight per figure (≈ 8 px for a figure 380 px tall). In a still scene, scale it with √(height/380), clamped 0.6–1.05; when the camera changes scale across orders of magnitude (fractal pull-backs, a
- **Use for:** Science explainers, Networks & social ideas, Data comparisons
- **Source:** `lemomo-ai/lemo-opuscar` → `stick-explainer`

### Tablet Sketch Explainer · 平板速写讲解
> The whole frame is a cream drawing canvas on a tablet, seen while someone draws and explains: grainy pencil lines go down first, flat colour blocks come after, shifted off the line and not quite filled, and the canvas itself is pinched, panned and turned between ideas. References (grammar only): draw-along explainers and time-lapse recordings of tablet sketching; pencil-and-marker recipe and craft illustration; off-register risograph colour. Never copy their drawings,…
- **Palette:** #F3EADB #43362E #A8998A #DC6A4C #F1C04F
- One canvas. Every frame is a region of one page. The page fills up as the film goes and is seen whole at least once; nothing exists off the page (no device bezel, no app toolbar, no hand).
- Line first, colour second. Objects are drawn in graphite (white inside), then coloured as a separate pass. Colour sits *under* the pencil and is visibly shifted off it (offset 5–12 canvas units, down-right), with a ragged edge.
- Still drawing. Some evidence that the drawing is in progress always stays: light construction lines left in, a block coloured half way, one object with its line only.
- **Not:** Not the sketchnote (dotted paper, ink fineliner that boils, grey marker + one yellow, a pen you never see). Not a whiteboard explainer (white board, black marker, hand). Not urban sketch pen-and-wash (watercolour washes that bleed). Not a vector flat explainer (no pencil grain, no off-register).
- **Tech:** - Roles: a title (≈100 canvas px) with a mustard block under one word and a coral underline; chapter capsules (circled number + word on an offset block) when a film has chapters; notes 32–50 px with a short pencil leader
- **Use for:** Food & drink explainers, Craft and how-to, Lifestyle science
- **Source:** `lemomo-ai/lemo-opuscar` → `ipad-sketch`

### Whiteboard Explainer · 白板讲解
> An explainer drawn live on one glossy dry-erase board: single-line handwriting that is actually *written* stroke by stroke, floating markers with no hand, magnets that can move, an eraser that can rewind, and a camera that travels across the board instead of cutting. References (grammar only): RSA Animate / Cognitive Media (one continuous board, the camera travels instead of cutting, a full-board view); minutephysics (one sentence = one drawing, the simplest geometry that…
- **Palette:** #23262C #2A5CB3 #D97757 #2E8B57 #C8363A #1F2A44
- One physical whiteboard. Everything the viewer learns is drawn in dry-erase marker in front of them, in real handwriting order.
- The board is a map: each idea lives in its own region; the camera travels between regions, often led by the pen. Distance on the board = distance in the argument.
- Real marker, not animated text: ink pools where the nib lands, dry streaks and speckle, strokes overshoot and don't quite close, ghosts of old lessons remain, a glossy sheen drifts slower than the board, and every stroke makes a sound.
- **Not:** Not Blueprint (no blue sheet, no drafting conventions), not Crayon Picture Book (no wax texture, no children's story), not a kinetic-type explainer (text is handwritten stroke by stroke, never animated as blocks).
- **Tech:** - Board: a warm white gradient, a faint scuff and micro-scratch tile, a few dozen ghost marks (old words, circles, arrows) at 5–10 % in grey or pale blue, and a soft diagonal window sheen (white, 10–16 %) mov
- **Use for:** Explainers, Online courses, Science
- **Source:** `lemomo-ai/lemo-opuscar` → `whiteboard`

## Traditional Crafts — 7 styles

### Chinese Ink Wash · 中国水墨
> Xieyi ink painting on rice paper, animated: blank paper is space, one brushstroke is a mountain, a wave, a gesture or a cut. References (grammar only): Shanghai Animation Film Studio's *Feelings of Mountains and Water* (1988) (blank-paper space, ink bloom, guqin pacing, figures in a few strokes); the bamboo-forest fight of *Crouching Tiger, Hidden Dragon* (weightlessness, stillness before action). Copy none of their characters, compositions or music.
- **Palette:** #B02E22
- **Not:** Not watercolour (no colour washes), not vector art with a brush texture (no flat fills or closed outlines), not a calligraphy title sequence.
- **Tech:** - Subtitles are inscriptions (题跋): a classical italic serif (Cormorant Garamond italic), ink-coloured, no box, ≤ 2 lines, placed in each shot's empty paper. A small vermilion square marks the start of each line. They
- **Use for:** Wuxia, Cultural brands, Poetry
- **Source:** `lemomo-ai/lemo-opuscar` → `ink-wash`

### Gilded Illumination · 金箔彩绘
> The whole frame is one gilded miniature painting, and the story happens inside it: flat mineral pigments inside firm ink outlines, white-lead highlights and dots, and real gold leaf (laid in squares, with seams, burnished) that only shines when a light inside the picture moves across it. No book, no page, no desk: the picture fills the screen edge to edge, and at the end it can be revealed as one whole painting inside its own border. References (picture grammar only):…
- **Palette:** #22379A #C8321F #3F8F7A #D97A8A #2A1A10 #C99A3E
- Flat pigment, firm line. Every shape is one flat colour, a darker band just inside the outline, a firm ink outline (never hairline: at least ~2.5 px on screen in a wide shot, thicker in close-ups) and white-lead strokes on the edges that face the light. No gradients that model form, no soft shading.
- Gold is a material, not a colour. Gold leaf is laid in squares: you can see the leaf blocks, their seams and overlaps, a little red bole where the leaf broke, punched dots. It lies dark and warm until a light crosses it; then the squares flash one by one (each one tilted a little differently)…
- White lead in strokes and dots. Besides the edge strokes, white lead is laid as dots: triads on foliage and rock, a row of pearls along a hem, a band of pearls on a vermilion ring. They are what makes a flat shape read as painted, not as a vector illustration.
- **Not:** Not Stained Glass (no lead cames, no transmitted light), not Art Deco (no streamlined geometry, no metallic gradients as decoration), not Ukiyo-e (no woodblock bleed, no bokashi), not Paper-cut Lightbox, not a fantasy game map, not a flat vector illustration with yellow circles.
- **Tech:** - Sizes: text meant to be read ≥ 40 px at 1080p for titles, ≥ 32 px for English subtitles, ≥ 34 px for Chinese.
- **Use for:** Fables and picture-book stories, Holiday and festival shorts, Brand and origin stories
- **Source:** `lemomo-ai/lemo-opuscar` → `gilded-illumination`

### Paper-cut Lightbox · 纸雕灯影
> A layered paper-cut shadow box (纸雕灯) lit from behind: 6–9 sheets of cut card stacked in a shallow box, a warm light glowing through the paper, windows and moons burning through holes, soft shadows falling from each layer onto the next. The camera is a macro lens inside a lamp: it can show the box, or let the paper scenery fill the whole screen. References (grammar only): commercial paper-cut shadow-box lamps (纸雕灯 / "shadow box lightbox") for the layer stack and backlight;…
- **Palette:** #0A1330 #6A86C2 #3F5A92 #0E1532 #FFB862 #F0C890
- **Not:** Not flat paper-cut animation (here: depth, backlight, cast shadows), not shadow puppetry (no single screen, no rods), not a 3D diorama (every element is a flat sheet parallel to the box front).
- **Tech:** - box framing: under the box, on the dark of the room (serif 500, ~40 px CJK / ~38 px Latin, ~74 px from the bottom);
- **Use for:** Journeys and travel, Farewells and anniversaries, Places and their stories
- **Source:** `lemomo-ai/lemo-opuscar` → `paper-lantern`

### Red Paper-cut · 红色窗花剪纸
> Chinese window-flower paper-cuts brought to life: jointed red cut-outs on paper grounds, where the cut *is* the drawing and the holes are where the light gets in. References (grammar only): folk window flowers of Shaanxi and Yuxian (sawtooth, crescent, cloud and swirl cuts, fold-symmetric rosettes, *yin* and *yang* cutting); the 1958–59 Shanghai Animation Film Studio cut-paper shorts (jointed figures, profile acting, paper layers in parallax). Copy no studio character, no…
- **Palette:** #D2201F #C8102E #D7261E
- **Not:** Not shadow puppetry: no light behind a screen, no translucent dyed hide, no rods. Here the paper is front-lit and opaque; backlight is a special event you save for the moment that needs it. Not flat vector art (no strokes, no gradients), not a silhouette film (every shape's interior is cut).
- **Tech:** - Subtitles are a paper strip in the world, e.g. a red banner (横批) darker than the picture's reds so cream text holds, serrated edges, swallow-tail ends; a sturdy OFL serif (e.g. Fraunces SemiBold) around 44 px, low,
- **Use for:** Lunar New Year, Festive greetings, Folk tales
- **Source:** `lemomo-ai/lemo-opuscar` → `papercut-red`

### Shadow Puppetry · 皮影戏
> Chinese shadow theatre: translucent dyed-hide puppets, carved like lace, pressed against a cotton screen and lit from behind by oil lamps. References (grammar only): Lotte Reiniger's *The Adventures of Prince Achmed* (1926) for profile acting and lace-like scenery; Shaanxi / Huayin shadow theatre for carving, colour and gong-and-drum rhythm. Never reproduce a specific historical puppet, melody or recording, and never name them in the film.
- **Not:** Not a black silhouette film (colour is the second protagonist), not paper-cut (the light comes *through*), not stained glass (no lead lines; pieces move and overlap), not flat vector cut-out animation.
- **Tech:** - Subtitles belong to the theatre: a storyteller's placard (narrow dark-lacquer board, thin gold line, small carved seal), a label on a rod, or letters carved into hide. Classical OFL serif (e.g. Cormorant Garamond 6
- **Use for:** Myths & folklore, Heritage, Festivals
- **Source:** `lemomo-ai/lemo-opuscar` → `shadow-puppet`

### Stained Glass · 彩色玻璃窗
> A medieval stained-glass window seen from inside a dark stone hall, alive only where the sun touches it: light is the clock, the camera and the story. References (grammar only): the window prologue of *Beauty and the Beast* (1991) (chapters pane by pane, a storyteller's pace); the glass knight of *Young Sherlock Holmes* (1985) (glass that cracks and recombines piece by piece); 12th–13th-century Chartres glass (colour logic, grisaille, leading). Copy none of their…
- Cut pieces of coloured glass in dark lead cames, faces and folds painted in brown grisaille.
- Glass has no light of its own: it glows only when the sun is behind it and throws a soft coloured copy onto the stone floor; unlit, it is dark and milky.
- Figures move piece by piece, rigid and stepped.
- **Not:** Not vector art with black outlines, not a kaleidoscope or Voronoi filter, not Tiffany Art Nouveau, not mosaic (mosaic reflects; glass transmits).
- **Tech:** - Pieces: smooth Catmull-Rom cuts (no deep concave corners). Every piece is textured (multiply in its clip): streaks at a per-piece angle, hue drift (±10 %), darker aged edges by the lead, ±9 % thickness variat
- **Use for:** Legends, Heritage, Holiday stories
- **Source:** `lemomo-ai/lemo-opuscar` → `stained-glass`

### Ukiyo-e · 浮世绘
> Edo-period woodblock prints brought to life: flat colour blocks, carved ink lines, bokashi skies, paper you can feel, and a camera that moves over the print like an unrolling handscroll. References (grammar only): Hokusai's *Thirty-six Views* (one constant subject placed differently each time; bold geometric cropping); Hiroshige's *Fifty-three Stations* and *Hundred Famous Views* (small figures, rain lines, extreme foreground framing); the anime *Mononoke* (2007) (print…
- Paper is always visible: warm washi, long fibres, slight edge ageing.
- Each colour is its own block, slightly out of register (1.5–2.5 px) with the key line.
- Large colour areas show woodgrain and baren rubbing (uneven ink density, circular streaks) and fine goma-zuri specks.
- **Not:** Not a flat vector illustration with a paper overlay (no woodgrain, no misregistration), not Chinese ink wash (no bleeding washes, colour is printed, not painted), not anime cel shading (no light and shadow on forms).
- **Tech:** - Line: key lines 2.4–3 px; large contours are variable-width filled strokes, tapered at both ends, with ±20–35 % low-frequency width jitter. Distant things get a grey key line or none.
- **Use for:** Travel, Japanese culture, Poetry
- **Source:** `lemomo-ai/lemo-opuscar` → `ukiyoe`

## Cartoons — 6 styles

### 1930s Rubber Hose Cartoon · 1930s 橡皮管卡通
> Black-and-white hand-inked cartoons where every object is alive and swings to a hot jazz band. References (grammar only): early Fleischer Studios shorts (c. 1930–33) for "the whole world dances", surreal transformation, the bouncing-ball singalong and ink-and-pen framing devices; *Cuphead* for how a modern team finishes the look and scores it with a big band. Never use an existing cartoon character, name or silhouette, and never copy designs, melodies or logos. Avoid the…
- **Not:** Not a 1950s flat cartoon (no limited animation, no colour, no graphic backgrounds), not a silent film (the synchronised music is the engine), not a "retro filter" over modern animation (no joints, no rendered shading).
- **Tech:** - Characters: flat fills, one hard-edged form-shadow band (light grey) on the side away from an upper-left light, ink outline constant in screen space at any zoom (transform points first, then stroke; ~6 px at 10
- **Use for:** Food & drink, Retro ads, Kids
- **Source:** `lemomo-ai/lemo-opuscar` → `rubber-hose`

### 80s Cel Anime · 80 年代赛璐璐动画
> Hand-painted cel animation from the golden age of Japanese OVAs, re-created in code: flat two-tone cels over airbrushed backgrounds, backlit neon, limited-animation timing, played back as a late-80s videotape on a CRT television. References (grammar only): 1980s Japanese OVA and TV cel animation in general (painted-background vs flat-cel contrast, backlit light, held drawings, speed grammar, city-pop openings). Borrow the era's craft, never a specific work's characters,…
- Background painting: soft airbrushed gradients, glowing windows, wet reflections; painted once at load (colour + emissive pair), then only slid.
- Cel (characters, vehicles, props): flat fills, hard-edged shadow and highlight shapes, coloured outlines, never pure black; stepped at 12 or 8 fps.
- Light: backlit cel (透過光): signs, lamps, title letters glowing *through* the frame; flares, halation.
- **Tech:** Cel rendering. Fill, then a hard shadow crescent, then a hard highlight crescent, then the coloured outline. No gradients inside a cel shape (exception: one "harmony" painted still at a peak). Automatic shadi
- **Use for:** Music videos, Game trailers, Nostalgia
- **Source:** `lemomo-ai/lemo-opuscar` → `cel-anime-80s`

### Comic History Cartoon · 搞笑历史卡通
> Countries are paper puppets joined with brass split pins, standing on a map printed on paper; whoever takes a piece of land cuts a scrap of paper and slaps it onto the map. The whole film is one comic page on a table, a panel per moment, and the camera travels between the panels. References (grammar only): fast comic history explainers on video platforms (personified countries bickering over a map); cut-out paper animation (pinned joints, stepped poses, real shadows);…
- **Palette:** #F1E8D2 #2B2219 #6E93D6 #5D6672 #A6CCD3 #C8463A
- Every change of territory is a paper action. Land changes hands by being cut, slapped down, torn off, pressed flat, peeled at a corner, or covered with another layer. A country is never simply recoloured.
- The map is printed matter. An old engraved map on paper (coast ripples, graticule, ink borders, flat printed fills, small-caps names), not a map standing in a room and not a vector infographic.
- Countries are people made of paper. Puppets cut from card, joined with brass split pins, with oversized round heads and swapped expression heads. They personify a country or a side, never a real person.
- **Not:** Not Paper Pop-up Book (no folds that stand up from a spread), not Isometric Infographic or Data Storytelling (no charts, no clean vector map), not Shadow Puppetry (opaque colour, not silhouettes), not Mid-century Cartoon (cut paper with texture and pins, not cel lines).
- **Tech:** - Printed map (rule): equirectangular projection with longitude compressed by cos(centre latitude); about six engraved ripple lines outside each coast; dashed graticule; thin ink borders; flat fills with a lighter ri
- **Use for:** Territorial changes in history, Light explainers on geopolitics, Market share and turf-war stories
- **Source:** `lemomo-ai/lemo-opuscar` → `comic-history`

### Manga Panels · 黑白漫画分格
> A black-and-white Japanese manga page that moves: G-pen ink, screentone dots, one spot colour, panels that open on the beat, sound effects slammed in letter by letter, and a camera that travels across the paper and through the gutters. The panel is the cut. References (grammar only): Japanese shōnen / seinen manga printing and page grammar in general (screentone, focus lines, speed lines, hand-lettered sound effects, right-to-left reading, chapter title pages, colophons,…
- **Palette:** #F3F0E8 #121212 #F03C1E
- Only ink and paper. Every grey is a pattern of black dots or lines (screentone), never a continuous grey or a gradient.
- The panel is the unit of time. A new panel inking in *is* the cut; panels open in reading order (right → left, top → bottom) on the beat.
- Lettering is drawn, not typed. Sound effects are big, rotated, outlined and boiling; narration lives in boxes, speech in balloons.
- **Motion:** - Paper #F3F0E8 (warm, never pure white), ink #121212. A 512 px grey-noise grain multiplied at 10 % over every frame.
- **Use for:** Music videos, Product launches, Anime openings
- **Source:** `lemomo-ai/lemo-opuscar` → `manga-panels`

### Mid-century Cartoon · 50s 扁平卡通
> 1950s flat colour and limited animation for "follow along" films: colour printed a few pixels off its broken ink line, bodies that hold still while hands do the work, abstract colour-block rooms, a calm classroom narrator, and a cool-jazz combo. References (grammar only): UPA's early-1950s shorts (*Gerald McBoing-Boing*, *Rooty Toot Toot*): colour and line on separate cels, geometric people, colour-plane backgrounds, limited animation. 1950s classroom films (Coronet,…
- **Not:** Not the 1930s rubber-hose cartoon (no black-and-white, no bouncing world, no hot jazz). Not a whiteboard explainer: it shows *how to do*, not *why*. The pictures are printed, not written on.
- **Tech:** - Line: 3–5 px ink ribbons with ±40 % width breathing and 12–25 % breaks. Characters ~4 px, props 3–4.5 px, walls in plans thicker and broken. Hands: one outline around the union of palm and fingers, thin finger sepa
- **Use for:** Set-up guides, Help centres, How-to
- **Source:** `lemomo-ai/lemo-opuscar` → `midcentury-toon`

### Sci-Fi Sitcom Toon · 科幻情景喜剧卡通
> Adult-animation sci-fi sitcom: thick boiling outlines, flat colour, a duo whose reactions don't match, a glowing portal, and one palette per world. References (grammar only): adult-swim-era sci-fi sitcom cartoons (dialogue-driven comedy, reaction close-ups, boiling line, sci-fi hardware as household junk). Borrow the *grammar*, never the characters.
- Never reproduce any existing show's characters, silhouettes or colour combos (e.g. a spiky-blue-haired old man in a lab coat + a kid in a yellow shirt), names, catchphrases, burp gags, logos, or the look of any existing portal gun.
- Invent your own cast, props and portal device. Never write the source show's name in the film or docs; one line "inspired by adult-swim-era sci-fi sitcom cartoons" is enough.
- **Not:** Not a kids' cartoon (dry humour, long pauses), not anime (no sparkly eyes), not a vector explainer (lines boil).
- **Tech:** - Line: near-black (a slightly purple black reads best), ~7 px for characters and props, 4–6 px for background detail, round joins. Line width is constant in screen space: close-ups are "redrawn" at the same weig
- **Use for:** Comedy, Tech brands, Social shorts
- **Source:** `lemomo-ai/lemo-opuscar` → `scifi-toon`

## Data & Maps — 6 styles

### 3D Map Explainer · 立体地图解说
> Real elevation and real imagery built into a three-dimensional map with the vertical exaggerated, lit by one warm, low sun; a sea coloured by its real depth; and over it a layer of data that glows, flows and lights up along true geography: routes, lanes, measurements, pillars. One camera falls from space into the place, flies over it, cuts it open, and climbs back out. References (grammar only): news organisations' 3D terrain explainers (a dive from the whole region to the…
- **Palette:** #0E2230 #1F5A5C #E8D2A6 #FFA63D #FFC36B #D9E6EE
- The ground is real data. Elevation and bathymetry from public tiles, imagery from licence-clean satellite mosaics, coastlines and place names where they really are. Nothing on the ground is invented or traced; whatever is drawn (a route, a pipeline path) is labelled schematic.
- Two layers. The terrain says *what this place is like*; the glowing layer says *what happens here*. The data layer is the only thing that glows.
- Relief stands up. Heights are exaggerated (about ×3 for land, stated on screen) and lit by a low sun, so mountains read even from orbit.
- **Not:** Not Satellite Briefing (grey analyst imagery seen straight down, hairline measurements), not Transit Map (an abstract diagram), not Isometric Infographic or Low-poly Island (no stylised diorama), not Sci-fi Hologram HUD (no invented chrome, no wireframe terrain), not a slide deck over a map (no…
- **Tech:** - A condensed grotesk for everything Latin (e.g. Barlow Condensed, OFL): country names 600 at ~30 px with wide tracking (≈ 0.3 em); sea names 500 at ~21 px, pale blue; island and port names 15 px; data numbers 600 at
- **Use for:** News and geopolitics, Energy, trade and shipping, Rivers, borders and terrain
- **Source:** `lemomo-ai/lemo-opuscar` → `map-explainer`

### Blob Simulation · 小人模拟实验
> A crowd of small flocked characters, the Pips, runs a real simulation on a warm paper lab board: evolution, games, epidemics, queues, markets. The rules are written in code, the outcome is computed, and the result is shown with the Pips themselves: they are the data points, and at the end they line up into the chart. References (grammar only): agent-based simulation explainers on video (one character = one individual, rules then outcome); vinyl designer toys and flocked…
- **Palette:** #4A6FE3 #8B67D6 #E0607E #F2604A #F6BE45 #4FBF8F
- The simulation is real. Positions, headings, what each Pip eats, its energy, whether it survives and whether it has children all come from a deterministic run with a fixed seed; the picture interpolates the record. Nothing is placed by hand to make a point. Changing a rule changes the film.
- One Pip = one individual. Counts are Pips, distributions are Pips standing in printed bars, a population is a board full of Pips.
- A character you can follow. The camera can always drop to one Pip, see its face and its state, and rise again to the whole board. The story of a rule is told through one or two individuals, then proven by the crowd.
- **Not:** Not Isometric Infographic (no icon people, no isometric diagram, real perspective and depth of field), not Data Storytelling (charts are never floating panels), not Brick Toy or Low-poly Island (soft flocked bodies, not plastic or facets), not a game HUD.
- **Tech:** - Derived colours follow the rules and are never picked on their own: feet = body × 0.8; cheeks = body towards #FF9A8F 30%; kicked-up fluff #FFF7EA; printed bar grounds = team colour towards #F4EEE3 78%; glints whi
- **Use for:** Evolution and natural selection, Game theory and agent-based models, Epidemics, queues and markets
- **Source:** `lemomo-ai/lemo-opuscar` → `pip-simulation`

### Data Physicalization · 数据实物化
> Real statistics built as real objects: every unit is a countable piece of material (a plate, a block, a coin, a bar) stacked to exact scale on a crafted base, shot like a product in a studio — soft key, long shadows, shallow depth of field, physically based materials. The camera reads a number at the edge of one plate, follows the data as it grows, and pulls back until the chart is an installation. References (grammar only): data-sculpture and physical-visualisation…
- **Palette:** #C4BEB4 #C8CCD1 #9FD3D6 #D2B07A #1C1D20 #D4521C
- The unit is an object. One plate, block or coin equals one stated quantity, and the rule is said on screen once ("1 plate = 10 GW"). A heavier material marks every tenth unit, so the stack is its own ruler.
- Scale is exact. Heights, counts and areas are computed from the data; rounding is one unit at most and written in the facts. Two series compared on the same base use the same unit.
- Studio light, real matter. Metal reflects an HDRI, wood shows grain, acrylic transmits; nothing glows, nothing is outlined, no fake UI.
- **Not:** Not Isometric Infographic (no icons, no flat colour coding), not Glass Product Render (the object is data), not Data Storytelling (no paper chart or inked axes), not Dark Tech Keynote (no black stage or neon), not Brick Toy (no toy proportions, no characters).
- **Tech:** - Roles: a light grotesk for numbers (e.g. Inter 200–300; the hero reading 130–170 px, a stack reading 46–56 px); a sans for labels and verdicts in the film's language (e.g. Noto Sans SC 500, 24–46 px); a monospace f
- **Use for:** Annual reports, Investor decks, Energy data
- **Source:** `lemomo-ai/lemo-opuscar` → `data-physical`

### Data Storytelling · 数据叙事
> A chart that tells a story: real data, drawn mark by mark on cream paper by a red–blue pencil, with handwritten notes pinned to the numbers. The chart itself is the camera, the rhythm and the plot. References (grammar only): Hans Rosling's *200 Countries, 200 Years, 4 Minutes* (one dot is a character), Ed Hawkins' warming stripes (a diverging ramp on a reference mean, no axes), The Pudding / NYT scrollytelling (one idea at a time, growing axes, pinned notes). Copy none of…
- **Not:** Not a dashboard (one idea at a time), not a keynote with charts (no slides), never decoration.
- **Tech:** - The subtitle is the figure caption: a text serif (Newsreader), ink colour, left-aligned with the chart, ≤ 2 lines, with a hairline rule above it and a small mono kicker for the range drawn so far. Words appear on t
- **Use for:** Data journalism, Reports, Climate & science
- **Source:** `lemomo-ai/lemo-opuscar` → `dataviz`

### Projection-Mapped Model · 白模投影
> A pure white massing model of a real place stands on a plinth in a dark room, and a projector paints data onto it as light: one layer at a time, falling on the surfaces that face it, spilling a little past the plate. The model never changes; only the light on it does. References (grammar only): projection-mapped planning models in city galleries (the dark room, the soft throw, colour only on white surfaces); macro model photography (shallow focus at rooftop height);…
- **Palette:** #F3F3F1
- The model is real geometry of a real place: building footprints and heights from open data (§2), extruded at a stated scale (1:1000, 1:2000…). Nothing on the model is invented or "representative", and no generated image ever stands in for the place.
- The model is white; data is light. Colour is never painted into the material: it is projected, so it brightens surfaces that face the projector, fades on walls turned away, stops at the edge of the throw and reaches a little onto the plinth.
- Layers arrive one at a time, each with its own gesture of light (a wash, a pop-on, a rising level, a moving sun), and each answers the question the last one raised.
- **Not:** Not Isometric Infographic (no diorama or icons), not Low-poly Island (no invented terrain), not Sci-fi Hologram HUD (no wireframes; light lands on matter), not Satellite Briefing (no imagery), not a laser-scan or point-cloud film (no scan lines; light is projected, not measured).
- **Tech:** - Roles: a light grotesk for the figure (Inter Tight 200, 120–140 px), a sans for labels in the film's language (Noto Sans SC 300/500, 20–36 px), a monospace for instruments, years and coordinates (IBM Plex Mono, 18–
- **Use for:** Urban planning, Exhibitions, City data
- **Source:** `lemomo-ai/lemo-opuscar` → `white-model`

### Transit Map · 地铁线路图
> A metro schematic printed on a physical sheet: lines held to eight directions, white stops, black-outlined interchange capsules, water as a flat blue band. The network is drawn on by glowing pen tips while a real perspective camera moves over the paper: it rides a tip, drops low where a line dives under water, pulls back through levels of detail and sweeps across the densest knot at a low angle with a shallow focus. References (grammar only): the octilinear schematic…
- **Palette:** #F2EEE5 #1B1C1E #4A4740 #BCD6EA #8FB5D6 #5F88AD
- Eight directions only. Every line segment, river edge and coastline is horizontal, vertical or at 45°; every corner is one fillet radius. A line never wiggles.
- Growth is drawing. A line exists as far as its pen tip has travelled; stops light when the tip passes; an interchange appears only when the second line actually arrives, and it lands with weight.
- Ink on a sheet. The map is printed on paper with tooth and fibres, lit by one raking light, and the sheet lies on a dark table. The camera sees it as an object: in perspective, with depth of field, and with its edge in wide or low shots.
- **Not:** Not Data Storytelling (even a time chart is drawn as two lines with stops), not Blueprint (no white-on-blue linework), not Isometric Infographic (the map is flat; depth comes from the camera), not a 3D city map (no extruded buildings, no terrain), not a keynote (no slides, header bars, centred…
- **Tech:** - Paper: warm off-white, procedural and tileable, sampled in world coordinates so it never slides. Three layers: a cloud of value at about 9 G period with detail down to 0.04 G, a tooth at about 2.4 G period, and sho
- **Use for:** Transport, Growth over time, Networks
- **Source:** `lemomo-ai/lemo-opuscar` → `transit-map`

## Screens & Interfaces — 6 styles

### 1-bit Dither · 1-bit 点阵
> A real 3D world shown with exactly two inks: every grey becomes a pattern of dots that is fixed to the surfaces, outlines come from depth and normal breaks, and printed things (fax prints, newspapers, labels) carry their own physical dots. The camera moves freely through it; the pattern never swims. References (grammar only): 1-bit computer games with first-person 3D (the ordered-dither look of *Return of the Obra Dinn*), early Macintosh dithered graphics, wire-photo and…
- **Palette:** #16161A #E9E6D6
- Two inks, no grey. Every pixel is ink or paper. Tone is density of dots; there is no anti-aliasing, no grey text, no soft gradient on screen.
- The dots belong to the surface. The dither threshold is attached to each object (object-space, octave chosen from the screen footprint), so when the camera dollies or an object turns, the pattern rides with it like a printed texture.
- Drawn edges. Depth and normal breaks become one-pixel lines: ink where the surface is light, paper where it is dark. A black object against a black sky still has a white rim.
- **Not:** Not Halftone Dossier (that is printed paper and flat collage, not a navigable 3D world), not Woodcut or Copperplate (carved line, not dot density), not CRT ASCII Terminal (no glyph cells, no phosphor), not a greyscale render with a filter on top.
- **Motion:** - Screen space only for cuts and transitions, and every transition stays two-ink on every frame: a block dissolve (whole 16–32 px cells swap at once), a fax-scan wipe (the next picture replaces the frame row by row u
- **Use for:** History told through a chain of media, Printing, scanning and signals, Night scenes and space
- **Source:** `lemomo-ai/lemo-opuscar` → `one-bit-dither`

### Dark Tech Keynote · 暗色科技发布
> A software launch film where the interface itself is the star: near-black gradient, hairline grid, soft light, one brand accent, and UI that moves with snap-grid precision. Light reveals, one giant number, and a sound design that is as ordered as the pixels. References (grammar only): Apple product reveals (black stage, light sweeps, one line per screen, the lone giant number); Linear / Stripe / Vercel launch videos (snap-grid motion, 1 px lines, one accent); Steve Reich's…
- **Palette:** #B7F34A #8B7CFF #FF7A1A
- **Not:** Not a glass product render (no physical object), not a screencast (no real OS or apps), not a hologram HUD (no scanlines), not a chart film (one number, not a chart).
- **Tech:** - Stage: a near-black base with a radial lift at the upper centre, one large cool glow at single-digit opacity off-centre, a 50–55 % corner vignette. A hairline grid (white at ~3 %, every 4th line ~6 %) on a 48 px mo
- **Use for:** Product launches, SaaS, Keynotes
- **Source:** `lemomo-ai/lemo-opuscar` → `dark-keynote`

### Mascot Screencast · 像素小人录屏
> A product walkthrough that looks like a real screen recording, where a low-resolution mascot lives inside a high-resolution interface and acts out what the software is doing. References (grammar only): - Screen Studio-style product recordings: auto-zoom to the cursor, cursor smoothing, click push-ins, and a window floating on wallpaper. - Apple "Guided Tour" videos: real interface, calm narration, one feature per sentence. - Duolingo and Headspace mascot motion: squash and…
- **Not:** Not a dark tech keynote (no black stage, no invented abstract UI: this is the real product), not a pixel-art game (the world is hi-res vector UI; only the mascot and its props are pixels), not a real capture (nothing is a screenshot).
- **Motion:** - Captions sit in a pill at the bottom, never over the element being discussed and never under the mascot; hold ≥ max(1.8 s, speech + 0.6 s).
- **Use for:** Product tutorials, Feature launches, Onboarding
- **Source:** `lemomo-ai/lemo-opuscar` → `living-screencast`

### Sci-fi Hologram HUD · 科幻全息界面
> An object is scanned into a glowing wireframe. Target boxes lock onto its parts; each opens in a local exploded view, a leader pulls out, and its number rolls from garbage glyphs into the real value. It may light up, once, into a solid hologram. References (grammar only): the *Iron Man* / *Avengers* HUDs (target boxes, callouts, rolling numbers, layered depth); the *Oblivion* interfaces (one colour, hairlines, space); CAD exploded views. Copy none of their layouts, icons,…
- **Not:** Not a type-driven keynote (dark-keynote), not a drafting sheet (blueprint), not a product render (glass-product). The subject stays a wireframe; it may gain translucent faces once, and even then the lines stay on top.
- **Motion:** - Wireframe: additive ~1.3 px strokes in a few alpha levels set by depth fog (near bright, far ~25 %), plus two low-res glow passes.
- **Use for:** Spec walkthroughs, Launch videos, Trade shows
- **Source:** `lemomo-ai/lemo-opuscar` → `hologram-hud`

### Spreadsheet Film · 表格动画
> A whole film inside one spreadsheet window. Cells are the pixels, conditional formatting paints the pictures, the formula bar speaks the lines, and the camera is the sheet's own zoom and scroll. Every picture is made of numbers, and the picture turns out to be the answer. References (grammar only): music videos and campaigns built inside a real spreadsheet file (rectangular cell pixels, conditional-format colour bands, a selected cell as the hero), and the plain grey…
- **Palette:** #B8F25A #E8382D #2A2F6C #FFB21F #17120A #DCDBD5
- **Not:** Not a data-storytelling chart on paper (there is no paper, no pencil: the sheet is the medium), not a dashboard (one idea per beat, no widgets), not a screencast of real software (the shell is generic and drawn, every action is staged), not pixel art (cells are wide, carry values and sit in a live…
- **Tech:** 1. Cells are the pixels, and they are wide. A cell at 100 % is about 2.9 : 1 (the demo uses 64 × 22 px). Every diagonal and curve becomes horizontal stair-steps.
- **Use for:** Data literacy, Finance & costs, Analytics explainers
- **Source:** `lemomo-ai/lemo-opuscar` → `spreadsheet`

### Tabletop App Flythrough · 桌面卡片穿梭
> App screens and tools lie on a sunlit desk as printed paper cards; small pixel characters, popped up into voxel toys, carry the work from card to card, while one unbroken camera flies after them, whips between stops and finally pulls back over the whole desk. References (grammar only): one-take desktop tours in software launch films (windows laid flat as places, a small helper as the guide); macro toy photography (low warm sun, long soft shadows); pixel-art sprites (the…
- **Palette:** #E7E4F3 #CBC5E2 #FCFBFF #1D1A2E #807A96 #E2DFEE
- The desk is the world. A matte paper mat with a regular dot grid lies on a light wooden desk, lit by one low warm sun through a window. Everything sits on it and casts a long, soft shadow. A few everyday desk things (a pen, sticky notes, a mug, earbuds) sit around the edges as foreground and…
- Interfaces are paper cards. Phones, tools and dashboards are rounded slabs a few millimetres thick with the interface printed on top. They are places: characters stand and hop on them, and parts of the interface rise out of them as small 3D objects.
- The cast are pixel sprites made solid. One bevelled cube per pixel, thicker inside than at the edge, eyes standing proud. They lie on a card as flat stickers and pop up into toys; they blink, wait on the beat, get squashed and spring back.
- **Not:** Not a screen recording (no cursor, no glowing monitor, no real app chrome or logos); not a brick or clay toy film (pixel voxels on printed paper); not an isometric infographic (perspective camera, real light); not flat motion graphics (everything has thickness and a shadow).
- **Motion:** - One subtitle cue per spoken line, in a quiet bar at the bottom centre (a rounded ink box at about 72 % opacity, about 64 px above the frame edge): the spoken language on the first line (bold, about 40 px), a whole-
- **Use for:** App explainers, Workflows, Products
- **Source:** `lemomo-ai/lemo-opuscar` → `desktop-flythrough`

## Film & Tape — 5 styles

### 1920s Silent Film · 1920s 默片
> An engraved-illustration silent film projected in a picture house: ink line and silver wash, a 4:3 print that flickers and weaves between velvet curtains, intertitles instead of voices, and a cinema pianist who plays every beat. References (grammar only): Buster Keaton, *The General* (1926) and *Sherlock Jr.* (1924) — the whole gag in one locked-off wide shot, a deadpan face, a body that does the acting; Harold Lloyd, *Safety Last!* (1923) — the near-miss; Georges Méliès —…
- A 4:3 print in a gate between theatre curtains; the sides of the 16:9 frame are the picture house.
- An ink drawing with washed greys and hatching, printed on silver stock that flickers, weaves, scratches and burns at the edges.
- Nobody speaks. Beats are told by action in wide shots and by intertitle cards.
- **Not:** Not a noir (no hard shadows as mood, no voice-over), not a sepia photo filter on modern animation (the drawing itself is engraved and inked), not a Chaplin pastiche.
- **Motion:** - The intertitles are the subtitles; the .srt lists their text. A card holds 2.5–3.75 s (≥ max(1.8 s, reading time + 0.6 s)).
- **Use for:** Comedy, Retro brands, Silent storytelling
- **Source:** `lemomo-ai/lemo-opuscar` → `silent-film`

### CRT ASCII Terminal · CRT 字符终端
> Everything on screen is a real character on a monospace grid, lit by the phosphor of an old monochrome CRT. References (grammar only): 1970s–80s monochrome terminals and teletype logs (typed output, cursor, status lines); ASCII art and demoscene text-mode pictures (images from glyph density); analog-synth film scores of the early 1980s (cold pulse, patient drones). Copy no film's interface text, fonts or logos, and use no real agency names.
- **Tech:** - Subtitles are terminal output. A reserved LOG strip at the bottom: a dim separator, an inverse-video tag, then a prompt and the line in uppercase at ~45 px. It is typed word by word in sync with the voice (
- **Use for:** Developer tools, Sci-fi, Tech brands
- **Source:** `lemomo-ai/lemo-opuscar` → `ascii-crt`

### Double Exposure · 双重曝光
> A silhouette is a window. A dark animal shape from the first exposure holds a second photograph, the place that animal carries with it, while the world outside the shape is where it is now. Monochrome photographs, warm lamps as the only colour, and a camera that moves the outline and the world inside it at different speeds, so the window and the place slide past each other. References (grammar only): in-camera multiple exposure on black-and-white film (the backlit profile…
- Animal silhouette × landscape. The subject is a clean, recognisable animal profile (a horse, a fox, an owl in flight, a hare, a turtle); its fill is a real landscape or townscape photograph that belongs to it (its meadow, its marsh, the farm it grew up on, the island it returns to). The pairing is…
- Two speeds. Whenever the camera or the animal moves, the photograph inside the silhouette moves more slowly than the outline (or follows the body, never the frame). That parallax is what makes the medium move on screen.
- The animal is alive. It breathes, shifts its weight, lifts its head, beats its wings, swims. Its body deforms the way the real animal's body does, and the photograph inside bends with it. A rigid card sliding across the frame is the opposite of this style.
- **Not:** Not Vintage Collage (no paper cut-outs, no mixed print processes), not Ukiyo-e or Paper-cut (no flat graphic fills: the fill is always a photograph), not Shadow Puppetry (the silhouette is a window, not a lit cut-out), not a keynote (no header bars, no centred title cards, no slide transitions).
- **Tech:** - Very little type. Subtitles are quiet: a serif (e.g. Noto Serif SC 600 for Chinese, Newsreader italic for English; both OFL), Chinese about 36 px over English about 28 px, one line each, on a barely visible soft shadow
- **Use for:** Brand and city films, Documentary and series openings, Music video intros
- **Source:** `lemomo-ai/lemo-opuscar` → `double-exposure`

### Liminal Found Footage · 后室录像带
> Camcorder tapes recovered from empty, endless, fluorescent-lit spaces. Rules instead of monsters. Genre reference (grammar only): "the Backrooms" internet folklore and new-weird / rule-horror; 1990s consumer camcorder footage. Never use the word "Backrooms", wiki "Level" numbers, community entity names, or any existing organisation or logo inside the film. Everything on screen (rules, forms, company voice, any presence) is original.
- **Palette:** #D5BD66 #4D3D26 #8C763C #9FC7C0 #E6ECE6 #5E8F96
- One first-person camcorder recording (1990s VHS, 4:3), handheld, continuous.
- An empty, familiar-but-wrong interior that repeats: an office, a hotel floor, a school, a mall, a parking level, a hospital wing. Humming fluorescent light, no people.
- Dread from emptiness, repetition, bureaucratic rules, and the camera's own machinery failing at the wrong moment. Nothing chases anyone. A chill on the back of the neck, not a jump.
- **Not:** Not a horror film (no monster close-ups, no gore, no jump scares, no score stings), not an ASCII/CRT terminal piece (the artefacts are tape and lens, not phosphor and scanlines), not a ruin (clean is part of the style).
- **Tech:** - VHS camcorder pass (not a CRT): small line jitter (≤ 0.25 px low-frequency wobble), a head-switching band, tracking tears on demand, barrel + vignette on the image but not the OSD, luma blur + edge ringing, chr
- **Use for:** Horror, Mystery & ARG, Game teasers
- **Source:** `lemomo-ai/lemo-opuscar` → `backrooms`

### Scratch Film · 胶片直刻
> Direct animation: every picture looks scratched through black emulsion with a needle and tinted with transparent dye, redrawn by hand fifteen times a second and projected. Black is the ground; everything bright is a cut. Lines boil from drawing to drawing, light glows through every cut, colour lies in the grooves like dye. References (grammar only): the direct-animation tradition (films scratched and painted straight onto the film stock, without a camera), its boiling line…
- **Palette:** #050403 #FFF4DC #1FB39A #2F86FF #FF3220 #FFC81C
- Black is the ground, light is a cut. The frame is warm black emulsion. Everything bright is a scratch (one cream colour); everything coloured is transparent dye laid in or beside the cuts. A bright area is dense hatching, never a flat fill.
- The line boils. Each drawing is redrawn with a new hand tremble at 15 drawings a second: several near-parallel passes per line, uneven width, skips, chipped edges, an overshoot tail. Even a held frame moves.
- The whole frame is the drawing. Sea, sky, a room, a map: the world itself is scratched and dyed, edge to edge. The style is not a strip of film shown inside a scene.
- **Not:** Not a chalkboard or whiteboard explainer (no flat board, no clean vector strokes), not Ink Wash (no wet tonal washes, no paper), not ASCII / CRT (no raster, no character cells), not a neon sign (no tubes), not a collage (no photographs). Film props are not the subject: perforations, frame lines,…
- **Motion:** - The line boils. Each drawing is redrawn with a new hand tremble at 15 drawings a second: several near-parallel passes per line, uneven width, skips, chipped edges, an overshoot tail. Even a held frame moves.
- **Use for:** Things that happen in the dark, One mark to a whole system, Small adventures told in light and shadow
- **Source:** `lemomo-ai/lemo-opuscar` → `scratch-film`

## Light & Lines — 5 styles

### Circuit Board · 电路板
> The subject is drawn as a printed circuit board seen from straight above: the world is copper under green solder mask, routes are traces, places are pads, words are white silkscreen, and what flows (power, water, signals, goods) is light running along the copper. The camera rides that light and jumps between the scale of a map and the scale of a single component. References (grammar only): real PCB design files and assembly drawings (layers, clearances, designators, detail…
- **Palette:** #05190F #1C6A44 #4AA977 #D9B25B #F2EEE1
- A top-down board in every frame: copper pour with clearances cut around everything, traces with 0/45/90° runs and mitred corners, gold pads and vias, white monoline silkscreen. Nothing is drawn in perspective.
- Information moves as light on copper. The way the light moves *is* the explanation: a pulse, a stream, a rocking dash, a pad that flashes.
- Two scales on one board: whole regions (a map, a supply chain, a city) are drawn in the same language as single components, and the camera passes between them without changing medium.
- **Tech:** 6. Light: an additive layer (glow) with two blurs (≈24 px and ≈5 px) under a sharp copy. Current, water, lit pads all live here.
- **Use for:** Energy, Supply chains, Devices
- **Source:** `lemomo-ai/lemo-opuscar` → `circuit-board`

### Firefly Pointillism · 萤火光点
> Thousands of soft, breathing points of light on black make up the people, animals, grass, moon, rain and words. The points are never created or destroyed: they scatter, fly off and gather somewhere else as something new, and that is how this style tells a story. A moving pointillist painting, or a summer night of fireflies. References (grammar only): pointillism (Seurat: form out of discrete dots); Johansson's point-light walkers (1973: a few dots read as a person when the…
- **Palette:** #050708 #060907 #B2A076 #F5ECC6 #A3B286 #EEF5D6
- Black is more than half the frame. All light comes from the points themselves: no ambient light, no gradient sky, no solid surfaces.
- Everything is the same kind of point. Characters, grass, moon, stars, rain and titles come out of one renderer and differ only in colour, density and focus.
- Depth is size and blur. In-focus points are small and sharp, out-of-focus points become large, faint discs. Particles pulling from blur to sharp *is* focusing, and focusing is how a form appears.
- **Not:** Not a digital-rain, hologram or dark-keynote look (no cold blue, no wireframes, no tech); not a particle-logo reel (there are characters and a story); not a fluid gradient; not iron filings or hard pixels. The points are always round, soft and warm.
- **Tech:** - Titles and credits are made of points: the text is rendered to a mask and sampled on a jittered grid (not randomly), one particle per sample. A 140–170 px CJK title needs about 3,400 points, a 30–40 px Latin line a
- **Use for:** Picture-book stories, Many becoming one, Night and nature lyric
- **Source:** `lemomo-ai/lemo-opuscar` → `firefly-pointillism`

### Flow-field Wind Lines · 流场风线
> An invisible field — wind, current, traffic, any flow — made visible as thousands of thin ink streamlines engraved on warm paper, with darker strokes running along them at the local speed. The lines are computed from data or a physical model, never drawn by hand; they bend round coasts, mountains and objects, change colour as the magnitude crosses meaningful thresholds, and the camera travels over the printed world beneath them. References (grammar only): meteorological…
- **Palette:** #ECE0C4 #E9D3A6 #262C38 #2C3A4A #3E525C #705C3A
- Every line is a streamline of a real field. Thousands of long, thin, continuous lines that never cross; their pattern *is* the information (a vortex, a jet, a sink, a wake).
- Two layers of ink: a fine engraved base line, and short tapered strokes that run along it, faster where the field is stronger. Motion comes from the strokes and the field changing, not from the lines jittering.
- Warm paper, blue-black ink, one warm ramp for magnitude. The paper is the screen; the world under the lines is printed (a chart, a landscape, a sky), not photographed.
- **Not:** Not a particle effect (no glowing dots, no additive light, no bloom), not Data Storytelling (no axes floating on blank paper as the main picture), not Satellite Briefing (no photographs), not a weather app (no rainbow ramp, no neon on black), not a keynote (no slides, header bars, chapter numbers).
- **Tech:** - Level of detail: a level's weight is 1 − |log₂(on-screen seed spacing / target)|; two neighbouring levels always sum to one, so density stays constant through any zoom. Seed spacing ≈ 36 px at 1080p and a half-leng
- **Use for:** Storms, monsoons and other weather, Ocean currents and river floods, Any flow measured against a threshold
- **Source:** `lemomo-ai/lemo-opuscar` → `flow-field`

### Neon Tubes · 霓虹灯管
> Real neon signs on a rainy night street: bent glass tubes filled with gas on painted boards, striking with a flicker, lighting the wet walls and doubling in every puddle. The figures on the signs are alive: an animal or a mascot made of one bent tube per pose moves from sign to sign by switching, frame by frame, like an animated sign, and the street answers on the beat. References (grammar only): night street photography of old shopping streets in the rain; neon shop…
- **Palette:** #1FF2D9 #FF3D9E #FF2A08 #3D75FF #0A1626 #2A0B0D
- Glass, not lines. A lit tube reads as a cylinder: a saturated gas column in the bore, a thin glass wall, a highlight along the top, a halo that spills onto whatever is behind. An unlit tube is still visible as clear glass or milky white (phosphor coated).
- Real gas colours. Clear glass + neon = red-orange; clear glass + argon and a drop of mercury = blue. Every other colour is a phosphor coating (milky when off).
- Built objects. Tubes stand off painted boards on supports with tie wires; strokes are joined by black-painted double-backs; every tube ends in a blacked-out electrode; a transformer box sits nearby.
- **Not:** Not a vector glow line on black (no bore, no board, no wet street); not LED "neon flex" (uniform, no electrodes); not Sci-fi Hologram HUD (screen light); not a cartoon drawn in glowing strokes (no in-betweens, no squash).
- **Motion:** - Readable at 1080p: hanzi tubes ≥ 60 px tall, Latin ≥ 18 px; hold ≥ CJK ÷ 4.5 + Latin ÷ 15 + 1.5 s from the moment the sign settles after its strike. A flickering or chasing sign does not count as readable.
- **Use for:** Shop openings and mascot stories, Nightlife and city-pop music videos, City and festival night idents
- **Source:** `lemomo-ai/lemo-opuscar` → `neon-tubes`

### Oscilloscope Math · 示波器数学
> Mathematics drawn by an electron beam on a phosphor screen: thin glowing green lines on near-black, a dotted graticule, monospace readouts and TeX formulas, every number on screen computed from the same values that draw the picture. The screen is a window onto a mathematical world larger than the frame, and the camera moves through it: it follows a point, dives into a corner, pulls back over a whole wave. Zooming is turning the instrument's knobs: the graticule refines and…
- **Palette:** #010402 #0B2412 #4DFF88 #8DFFB0 #E6FFEC #FFB547
- The maths is real. Circles, curves, readouts, cursors and the formula come from one set of numbers: an epicycle chain is the actual Fourier series, a readout is the value at the drawn point, a measured distance is computed. Freeze any frame and it checks out.
- Light, not ink. Everything is emitted light: a sharp core, a soft bloom, a white-hot centre where the beam is fast or new. Nothing is filled with flat colour.
- The screen is glass in front of a world. HUD (formula, readouts, subtitles, credits) is fixed to the glass; the world (curves, circles, axis, graticule) moves behind it.
- **Not:** Not Sci-fi Hologram HUD (no fantasy chrome, no cyan-magenta palette), not Data Storytelling (no bars and pies on white), not Blueprint (no paper, no drafting), not ASCII/CRT Terminal (no raster, no scanlines, no character grid).
- **Tech:** - Titles: a serif that matches TeX (e.g. STIX Two Text, OFL), 60–84 px, with the key word in italic; a Chinese line under it in a CJK serif (e.g. Noto Serif SC) ≥ 34 px. Written by the beam (outline traced, then fill
- **Use for:** Maths and physics lessons, Signals and electronics, Science explainers
- **Source:** `lemomo-ai/lemo-opuscar` → `oscilloscope-math`

## Painting & Illustration — 5 styles

### Colored-Pencil Science Illustration · 彩铅科普插画
> A real 3D cutaway world (ground, soil horizons, stones, buried structures, living things) redrawn every frame as a colored-pencil plate on toothed paper: four layers of pencil, a wobbling graphite contour, labels pencilled on cream paper tags. The camera can sink below the ground, and the drawing can be *drawn in* while you watch: horizons coloured in stroke by stroke, growing things drawn out from their base, fine lines spreading white over dark soil. References (grammar…
- **Palette:** #F8F4EA #8DAA45 #5E8A3A #B3D4E6 #4D3018 #66402A
- The whole frame is one pencil drawing. Sky, ground, soil, what lives in it and type are all pencil on the same paper; there is no "3D scene with a drawing in it". The sky is a loose blue wash with the clouds left as paper.
- The cutaway is the signature composition. Above the ground line, landscape; below it, the cut face of the soil, where the hidden things live (stones, burrows, seeds, pipes).
- It is a real 3D world. The camera can crane, push and truck through it, and things at different depths move at different speeds (multiplane parallax: the cut face slides over the far landscape).
- **Not:** Not Watercolor (no washes, blooms or wet edges: every tone is built from strokes), not Urban Sketch (no ink line plus wash; the line is graphite and coloured pencil), not Crayon Picture Book (fine, controlled hatching, not waxy scribbles), not Isometric People Scene (perspective camera, a real cut…
- **Motion:** - Only the contour boils: a new drawing every 2 frames, 3 drawings cycled, about 1 px. Hatching and colour fields do not boil.
- **Use for:** Natural-science cutaways, Picture-book explainers, Hidden structures and processes
- **Source:** `lemomo-ai/lemo-opuscar` → `colored-pencil`

### Crayon Picture Book · 蜡笔儿童绘本
> A picture-book page drawn live in wax crayon on toothy paper, with a watercolour wash that reveals what the crayon was hiding. References (grammar only): Raymond Briggs' *The Snowman* (1982) (hand-textured frames that breathe, wordless tenderness, a lyrical passage carried by one tune, still backgrounds with living figures). Copy none of its characters, song or imagery, and never name it in the film.
- **Palette:** #F4EFE3
- **Tech:** - Paper: warm off-white (around #f4efe3). The tooth is anchored to the page (it pans with the camera; on zoom two octaves cross-fade so grains stay ~1 px on screen), never screen-fixed: three octaves of value n
- **Use for:** Picture books, Bedtime stories, Kids' learning
- **Source:** `lemomo-ai/lemo-opuscar` → `crayon-book`

### Impasto Oil Painting · 油画厚涂
> Thick oil paint laid with a palette knife: big, flat, sharp-edged planes of colour, raked by light so every ridge of paint shows. Clarity first: value structure before texture, hard edges at the focus, calm planes everywhere else. References (grammar only): the opening titles of *The Umbrellas of Cherbourg* (1964) (overhead choreography read as moving colour); palette-knife street paintings (Leonid Afremov and the genre around him) (knife mosaic, vertical wet reflections,…
- **Palette:** #D97757 #F0A07A #F6C0A0
- **Not:** Not a Van Gogh swirl filter (strokes boiling everywhere), not a brush texture over flat vector art, not watercolour (paint is opaque), not a "painterly" photo filter (strokes are designed, not sampled from noise).
- **Motion:** - A serif display face (e.g. Cormorant, OFL). Subtitles, if there is a voice: plain serif, ≤ 2 lines, in a calm plane; hold ≥ max(1.8 s, speech + 0.6 s).
- **Use for:** Music videos, Art & culture, Emotional ads
- **Source:** `lemomo-ai/lemo-opuscar` → `impasto`

### Urban Sketch · Pen & Wash · 钢笔淡彩
> A sketchbook page drawn on location: fine sepia fineliner lines that wobble, overshoot and never quite close, with loose transparent watercolour dropped on top. The colour sits slightly off the lines, spills over them, and dissolves into cream cold-press paper at the page edge. References (grammar only): - Urban-sketching sketchbook pages: line first, then wash; colour off-register; handwritten date and place in the corner; the page edge breaking up into dabs. - *Paperman*…
- **Palette:** #C3C96F #7FA04A #9FBCD6 #D8C6A0 #7FA6B8 #C9573F
- **Not:** Not Watercolor Brush (no line-free wet-in-wet painting, no painterly edges without ink), not Whiteboard (no marker, no explainer diagrams), not Chinese Ink Wash (no brush calligraphy, no monochrome ink tones). Line and wash, both, always.
- **Motion:** - Ink: ~96 % coverage; world line width thinner far, thicker near (e.g. 1.3–3.4 px); wobble ~1 px; overshoot 3–8 px; a third to half of long strokes get one small gap. Strokes are baked with their **draw time per pix
- **Use for:** City & travel, Architecture, Lifestyle brands
- **Source:** `lemomo-ai/lemo-opuscar` → `urban-sketch`

### Watercolor Brush · 水彩笔刷
> A hand-painted journal page that paints itself: translucent brush strokes with dry-brush flying white on warm cotton paper, hand-written notes beside what is painted, nothing drawn with a vector line. References (grammar only): naturalist field-journal and botanical-plate watercolours (specimen + note); long horizontal handscroll panoramas (one continuous painted world); the textbook "transect" diagram (a gradient read across space). Borrow the grammar, never a specific…
- **Palette:** #F3E2C8 #9FB4C4 #5F7486 #C8442A #E8E0C0 #8EA860
- One sheet of warm, fibrous paper under everything; it is also the eraser (paper-coloured mist washes things away).
- Everything is individual brush strokes: a variable-width ribbon at partial opacity plus a few thin bristle tracks that break into dashes (flying white). Strokes overlap and darken where they cross, like transparent pigment. No vector outlines; a darker edge stroke along a form is the only "line".
- Things paint themselves in, stroke by stroke, structure before detail (trunk → branches → leaves; outline wash → shadow → accent).
- **Not:** Not ink wash (colour, not ink tones; no calligraphic brush-as-gesture), not impasto (no thick paint, no knife), not a children's picture book (no crayon, no cute outlines), not vector illustration with a watercolour texture laid on top.
- **Tech:** - Stroke (engine.js mk/drawS): a ribbon whose width follows a profile (brush, leaf, even, tip, trunk) with ~±22 % value-noise roughness, filled as a thin wash (≈ 0.55–0.6 body opacity when bristles ar
- **Use for:** Nature documentary, Travel, Science explainers
- **Source:** `lemomo-ai/lemo-opuscar` → `watercolor`

## Games — 4 styles

### 16-bit Pixel RPG · 16-bit 像素 RPG
> A short film that looks, sounds and *behaves* like a mid-90s console role-playing game: 320×180 pixels, a limited indexed palette, text boxes that type, menus, save files, chip music with echo. References (grammar only): mid-90s console RPGs as a system of dialog boxes, menus, battles, overworlds and save points; the palette tricks of indexed hardware (palette swaps, fades by steps, cycling); the colour-depth history of consoles (4 shades → 8-bit → 16-bit). Never use…
- 320×180 native pixels, scaled ×6 nearest-neighbour to 1080p; everything, text included, lives in the framebuffer.
- A limited, indexed palette; gradients are ordered dither, never blends.
- Sprites around 20–34 px tall animating in a handful of frames; faces act in portraits.
- **Not:** Not 2.5D Pixel Art (no depth of field, bloom or real-time light), not CRT nostalgia (no scanlines, no grain), not a parody.
- **Tech:** - Dither: 4×4 Bayer for gradients and glows; light shafts as a flat 50 % checker with a 25 % edge.
- **Use for:** Game trailers, Recaps, Nostalgia
- **Source:** `lemomo-ai/lemo-opuscar` → `pixel-rpg`

### 2.5D Pixel Art · 2.5D 像素
> Hand-made pixel sprites standing like paper cut-outs inside a lit, fogged, fully 3D diorama, shot from a high three-quarter angle through a tilt-shift lens: a toy world where every lamp throws a real shadow. References (grammar only): *Octopath Traveler* (Square Enix × Acquire, 2018) and its sequel (2023), the games that defined the HD-2D look. Learn the grammar: sprite-in-diorama, high 3/4 camera, tilt-shift focus band, point lights with shadows, heavy bloom and vignette,…
- **Not:** Not a voxel game (no cubic characters), not a flat 2D pixel RPG (the set is real 3D with real light), not a tilt-shift photo of a real miniature (textures are pixels, not materials).
- **Tech:** - Constant texel density: surfaces drawn per pixel on small canvases, NearestFilter, world-space UVs at one density (e.g. 24 px/m); sprites on a similar scale (a character ~30–60 px tall).
- **Use for:** Game trailers, Fantasy, Story films
- **Source:** `lemomo-ai/lemo-opuscar` → `hd-2d`

### Microgame Frenzy · 微游戏快闪
> A rapid-fire party-game film: one command word, a few seconds, one action. Every microgame is drawn in a completely different art style, and the film keeps getting faster. Genre reference (grammar only): the WarioWare series. Never use its name, characters, UI, microgames or music.
- **Palette:** #2A0F5C #FF2E88 #FFC928 #1FD1D1
- A microgame = a shouted command word + 2.5–4 s + one action + one result (success, or a funny failure).
- Each microgame uses a different visual medium (crayon, ink wash, terminal, risograph, pixel, blueprint, Swiss type, clay, cut paper, woodcut…). The jolt of each switch is both the joke and the beat.
- One fixed home look holds the film together: a show stage with a host, a lives counter and a stage number, which the film returns to between games.
- **Not:** Not Rhythm Game Show (one art style, rounds of bars, call-and-response), not a style sampler reel (every game has stakes; lives connect them), not a montage (each game has a rule grasped in under a second).
- **Motion:** - The command word is the subtitle: a heavy display face (e.g. Titan One), white with a thick ink outline, a coloured drop and a burst behind it, skewed a few degrees. It slams in over ~3 frames (overshoot → settle),
- **Use for:** Game trailers, Onboarding, Social shorts
- **Source:** `lemomo-ai/lemo-opuscar` → `microgame`

### Rhythm Game Show · 节奏综艺
> A rhythm-game variety show in flat vector: toy-like mascots with thick ink outlines on candy-coloured stripes and sunbursts, every hit landing on a fixed tempo grid, call-and-response patterns, and a judgement word when each round is won. References (grammar only): rhythm-action party games in the Rhythm Heaven mould (cue → answer, round cards, judgement words), Japanese variety-show telops (thick outlined captions, stripe and sunburst sets), WarioWare-style stage cards.…
- **Palette:** #FFB870 #FFA85A
- Everything is on the grid. One fixed, fast tempo. Every pop, drop, stamp, typed character and camera punch sits at a (bar, beat) and is also a sound event; the score is generated from the picture's own timeline, so they can't drift.
- One drawing kit, many sets. Flat fills, one heavy ink outline, round caps, hard offset shadows; each round gets a new saturated background colour and pattern.
- Characters are toys. One body construction for the whole cast, told apart by colour, a belly patch, one head accessory and a name tag. They hop on the beat, squash on hits, throw arms up on a shout.
- **Not:** Not a microgame frenzy (no timer or one-verb command per 3 s game, no change of art style per round), not a mid-century cartoon (no textured painted backgrounds, no character acting), not a keynote (no slow reveals, no gradients).
- **Tech:** - Vector only, SVG or canvas paths at 1920×1080: flat fills, one outline colour (near-black), 8 px outlines on characters and props, 5–7 px on small parts, round joins and caps.
- **Use for:** Tech timelines, Year in review, Variety shows
- **Source:** `lemomo-ai/lemo-opuscar` → `game-show`
