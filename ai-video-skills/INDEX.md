# AI ভিডিও-জেনারেশন স্কিল লাইব্রেরি — ইনডেক্স

GitHub স্ক্যান করে **৫৪টি স্কিল** ইনস্টল করা হয়েছে (`library/.claude/skills/`)। প্রতিটির frontmatter পড়ে শ্রেণিবিন্যাস: কোনটা শুধু *প্রম্পট-ক্রাফট*, কোনটা *রেন্ডার পাইপলাইন*, কোনটা *API বাধ্যতামূলক*।

**স্ক্যান করা ১২টি রিপো:** `machina-exm/film-studio-skills`, `beshuaxian/higgsfield-seedance2-jineng`, `AKCodez/higgsfield-claude-skills`, `black-forest-labs/skills`, `DojoCodingLabs/remotion-superpowers`, `Rimagination/h3lite`, `Yacey/agnes-ai-generation-skill`, `kaomei/stickman-video-director`, `cosmicstack-labs/lazy-frames`, `scenario-labs/skills` (১৮০টি SKILL.md, তবে বেশিরভাগ Blender/3D — ভিডিও-জেনারেশন নয়), `zhanghaonan777/Seedance2-skill`, `Vincentwei1021/anything2explainer`।

## ইনস্টল রিপোর্ট (যা ভেঙেছিল, লুকাইনি)

- **`AKCodez/higgsfield-claude-skills`-এর ১৫টি স্টাইল স্কিল স্কিপ** — ওদের `SKILL.md` frontmatter-এ YAML ভাঙা (`Nested mappings are not allowed in compact mappings`, line 2)। একই ১৫টি `beshuaxian/higgsfield-seedance2-jineng` থেকে ঠিকভাবে এসেছে, তাই কিছু হারায়নি।
- **নাম সংঘর্ষ:** film-studio আর remotion — দুয়েরই `setup` ছিল। remotion-এর দুটো `remotion-setup` / `remotion-setup-guide` নামে সরিয়েছি, film-studio-রটা `film-studio-setup`।
- **অডিট নোট:** স্কিলগুলো এজেন্ট-পারমিশনে চলে। আমি frontmatter + বর্ণনা পড়ে যাচাই করেছি, কিন্তু `ugc-hot-girl`-এর মতো কনটেন্ট-সংবেদনশীল স্কিল ব্র্যান্ড/মনিটাইজড কাজে ব্যবহারের আগে নিজে পড়ে নিন।


## A. প্রি-প্রোডাকশন ডিসিপ্লিন (machina-exm/film-studio-skills)

| স্কিল | ধরন | কী কাজ করে | ব্যাকএন্ড |
|---|---|---|---|
| `studio-init` | prompt-craft | Scaffold an AI film studio before production starts.  — |
| `film-breakdown` | prompt-craft | Build scene plans and shot cards from scripts or ideas.  — |
| `asset-passport` | prompt-craft | Create film-asset passports before generation. Use for characters, locations, props, and state variants that need repeatable visual identity.  — |
| `reference-board` | prompt-craft | Build and lock reference boards before asset creation.  — |
| `shot-prompt` | prompt-craft | Turn a shot card into a 15-block prompt before video. Use when every in-frame asset is locked and a shot is ready to generate.  — |
| `stress-test` | prompt-craft | Combat-test draft film assets before locking them. Use after a passport and references exist and before any scene generation.  — |

## B. স্টাইল-ভিত্তিক প্রম্পট প্যাক (Seedance 2.0 / Higgsfield)

| স্কিল | ধরন | কী কাজ করে | ব্যাকএন্ড |
|---|---|---|---|
| `seedance-cinematic` | prompt-craft | Generate cinematic film-style video prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants cinematic, film-like, movie-quality, Hollywood  Seedance/Higgsfield |
| `seedance-3d-cgi` | prompt-craft | Generate 3D CGI and rendered video prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants 3D rendered, CGI, Pixar-style, Unreal Engine, p  Seedance/Higgsfield |
| `seedance-cartoon` | prompt-craft | Generate cartoon and animation style video prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants cartoon, 2D animation, cel-shaded, hand  Seedance/Higgsfield |
| `seedance-comic-to-video` | prompt-craft | Convert comic book panels, manga pages, webtoons, and illustrated storyboards into animated video using Seedance 2.0 on Higgsfield. Use whenever the u  Seedance/Higgsfield |
| `seedance-fight-scenes` | prompt-craft | Generate intense fight scene and action sequence video prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants fight scenes, combat, marti  Seedance/Higgsfield |
| `seedance-anime-action` | prompt-craft | Generate anime-style video prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants anime, Japanese animation style, shonen action, seinen   Seedance/Higgsfield |
| `seedance-motion-design-ad` | prompt-craft | Generate motion design advertisement video prompts for software and tech companies using Seedance 2.0 on Higgsfield. Use whenever the user wants to cr  Seedance/Higgsfield |
| `seedance-ecommerce-ad` | prompt-craft | Generate e-commerce product advertisement video prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants product ads, e-commerce videos, pr  Seedance/Higgsfield |
| `seedance-product-360` | prompt-craft | Generate product 360° turntable, multi-angle showcase, and product reveal video prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants a   Seedance/Higgsfield |
| `seedance-music-video` | prompt-craft | Generate music video and beat-synced visual content prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants to create a music video, lyric  Seedance/Higgsfield |
| `seedance-social-hook` | prompt-craft | Generate viral social media hook video prompts for TikTok, Instagram Reels, and YouTube Shorts using Seedance 2.0 on Higgsfield. Use whenever the user  Seedance/Higgsfield, Runway/Kling |
| `seedance-brand-story` | prompt-craft | Generate brand storytelling and narrative video prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants to create a brand story video, com  Seedance/Higgsfield |
| `seedance-fashion-lookbook` | prompt-craft | Generate fashion lookbook, model showcase, and style video prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants fashion video content,   Seedance/Higgsfield, Runway/Kling |
| `seedance-food-beverage` | prompt-craft | Generate food and beverage video prompts for Seedance 2.0 on Higgsfield. Use whenever the user wants food videos, recipe content, restaurant promos, b  Seedance/Higgsfield, Runway/Kling |
| `seedance-real-estate` | prompt-craft | 为 Seedance 2.0（Higgsfield）生成房地产、建筑和室内设计展示视频提示。在用户想要财产巡览、房地产清单、建筑展示、室内设计视频、家居登台内容、财产营销、虚拟巡览、施工揭示或任何房地产/建筑视频时使用。在以下情况下触发：房地产、财产、房屋、公寓、建筑、室内设计、房屋巡览、清单视频、 | Seedance/Higgsfield |
| `ugc-video-auto` | api-orchestration | Full UGC ad video pipeline — generates a character image on Higgsfield, then creates a Seedance 2.0 video from it. Orchestrates the complete flow from | Seedance/Higgsfield |
| `ugc-hot-girl` | prompt-craft | Generate a detailed AI image prompt for creating an attractive female UGC ad character. Use when the user wants to create a "hot girl" character image | Seedance/Higgsfield |

## C. Black Forest Labs — FLUX / FLUX 3 ভিডিও (অফিসিয়াল)

| স্কিল | ধরন | কী কাজ করে | ব্যাকএন্ড |
|---|---|---|---|
| `flux-3-video` | prompt-craft | Use when routing a general FLUX 3 video request. Select only the specialists needed for diagnosis, direction, audio, or execution.  BFL FLUX |
| `flux-3-generate` | render-pipeline | Use when submitting or polling a FLUX 3 video API job. Also covers drafts, downloads, and technical validation.  BFL FLUX |
| `flux-3-prompt-doctor` | prompt-craft | Use when diagnosing a FLUX 3 brief before generation. Resolve missing, conflicting, or schema-changing requirements.  BFL FLUX |
| `flux-3-cinematic-inserts` | prompt-craft | Use when writing a FLUX 3 text-to-video prompt for a standalone shot. Covers shot craft, reliable concept patterns, camera, continuity, and review.  BFL FLUX |
| `flux-3-keyframes-continuation` | prompt-craft | Use when a FLUX 3 video must be built from supplied images or video. Covers keyframes (i2v) and continuation (v2v).  BFL FLUX |
| `flux-3-audio-dialogue` | prompt-craft | Use when directing FLUX 3 audio, dialogue, or voiceover. Covers ambience, effects, music, silence, and timing.  BFL FLUX |
| `flux-3-product-ads` | prompt-craft | Use when building a finished product ad from FLUX 3 - shot design, voiceover, action-to-word sync, evidence-gated copy, deterministic assembly, and QC  BFL FLUX, Remotion |
| `flux-3-archival-formats` | prompt-craft | Use when a FLUX 3 video needs a period or archival look. Covers naming a recording format instead of a mood, per-format artifacts, and templates.  BFL FLUX |
| `flux-image-best-practices` | prompt-craft | Comprehensive guide for BFL FLUX image generation models. Covers prompting, T2I, I2I, structured JSON, hex colors, typography, multi-reference editing  BFL FLUX |
| `bfl-api` | api-orchestration | BFL FLUX API integration guide covering endpoints, async polling patterns, rate limiting, error handling, webhooks, and regional endpoints with Python  BFL FLUX |

## D. Remotion ডেলিভারি লেয়ার (DojoCodingLabs/remotion-superpowers)

| স্কিল | ধরন | কী কাজ করে | ব্যাকএন্ড |
|---|---|---|---|
| `create-video` | render-pipeline | Full video production pipeline — from a text prompt to a live Studio preview with voiceover, music, sound effects, stock footage, and motion graphics,  Remotion, TwelveLabs, Pexels, ElevenLabs/audio AI |
| `create-short` | render-pipeline | Create a short-form vertical video (TikTok, Instagram Reels, YouTube Shorts). Optimized 9:16 pipeline with a live Studio preview, auto-captions, hook-  Remotion, Pexels, ElevenLabs/audio AI |
| `remotion-production` | render-pipeline | Media orchestration for Remotion videos. Generates and sources the assets a video needs (voiceover, music, sound effects, stock footage, AI images and  Remotion, TwelveLabs, Pexels, ElevenLabs/audio AI, Gemini/Veo |
| `generate-clip` | render-pipeline | Generate AI video clips for your Remotion project. Create unique footage from text descriptions or animate still images into video — no stock footage   Seedance/Higgsfield, Remotion, Pexels, Gemini/Veo, Runway/Kling |
| `generate-image` | render-pipeline | Generate AI images for your Remotion project. Describe what you need — backgrounds, thumbnails, characters, abstract art — and get production-ready im  BFL FLUX, Remotion, Gemini/Veo, OpenAI |
| `add-voiceover` | render-pipeline | Generate a voiceover narration and add it to your Remotion project. Provide a script or describe what the narration should say, and this will generate  Remotion, ElevenLabs/audio AI |
| `add-music` | render-pipeline | Generate background music and add it to your Remotion project. Describe the mood/genre you want, and this will generate a commercially licensed track   Remotion, ElevenLabs/audio AI |
| `add-captions` | render-pipeline | Add TikTok-style, karaoke, YouTube or minimal captions to your Remotion video. Gets word-level captions through the official remotion-captions flow (w  Remotion, ElevenLabs/audio AI |
| `add-transitions` | prompt-craft | Add professional scene transitions to your Remotion video. Choose from fade, slide, wipe, flip, clock-wipe and light-leak overlays — with spring or li  Remotion |
| `find-footage` | render-pipeline | Search and download stock footage from Pexels for your Remotion project. Provide a description of what you need and this will find, preview, and downl  Remotion, Pexels |
| `analyze-footage` | render-pipeline | Analyze existing video files with TwelveLabs AI. Get a timestamped scene map of your footage, ask questions about it, find specific moments across a l  Remotion, TwelveLabs, Pexels |
| `review-video` | prompt-craft | Review a Remotion video with AI vision. Starts with a cheap local check of rendered still frames, then has TwelveLabs watch the full render and score   Remotion, TwelveLabs |
| `transcribe` | render-pipeline | Transcribe audio or video files to text with timestamps. Produces word-level Caption JSON through the official remotion-captions flow (whisper-webgpu, | Remotion, ElevenLabs/audio AI |
| `remotion-setup` | render-pipeline | First-run setup wizard for Remotion Superpowers. Checks dependencies, scaffolds a Remotion project if needed, installs and updates Remotion's 12 offic | Seedance/Higgsfield, BFL FLUX, Remotion, TwelveLabs, Pexels, ElevenLabs/audio AI, Gemini/Veo, Runway/Kling |
| `remotion-setup-guide` | render-pipeline | Knowledge for helping users set up the Remotion Superpowers plugin. Covers API key acquisition, dependency installation, Remotion's official Agent Ski | Remotion, fal.ai, TwelveLabs, ElevenLabs/audio AI, Gemini/Veo, Runway/Kling, OpenAI |

## E. অর্কেস্ট্রেটর / API স্কিল

| স্কিল | ধরন | কী কাজ করে | ব্যাকএন্ড |
|---|---|---|---|
| `agnes-ai-generation` | api-orchestration | Call Agnes AI / Sapiens AI generation APIs for text, image, and video. Use when the user asks to use Agnes models, Agnes Image, Agnes Video, Agnes 2.0  Agnes API |
| `seedance-auto-generate` | render-pipeline | Automatically generate a Seedance 2.0 video on Higgsfield using Playwright browser automation. Use when the user provides an image and wants to create | Seedance/Higgsfield, Runway/Kling |
| `higgsfield-image-auto` | render-pipeline | Automatically generate an AI image on Higgsfield using Playwright browser automation. Use when the user has an image prompt and wants to generate it o | Seedance/Higgsfield, BFL FLUX, OpenAI |
| `lazy-frames` | render-pipeline | >  ElevenLabs/audio AI |

## F. লোকাল রানটাইম

| স্কিল | ধরন | কী কাজ করে | ব্যাকএন্ড |
|---|---|---|---|
| `h3lite` | render-pipeline | Use when configuring, repairing, planning, or running MiniMax H3 locally on a Windows NVIDIA computer, especially when installation compatibility, com  Seedance/Higgsfield, MiniMax H3, ComfyUI |

## G. অন্যান্য

| স্কিল | ধরন | কী কাজ করে | ব্যাকএন্ড |
|---|---|---|---|
| `directing-stickman-videos` | prompt-craft | Turn topics, requirements, articles or scripts into stickman (stick figure) animated videos: explainers, short stories and faceless YouTube, Shorts or  Gemini/Veo |
