# AI ভিডিও প্লেবুক — ৫৪টি স্কিল পড়ে যা শিখলাম

সব স্কিল (~৫৪টি) frontmatter + বডি পড়ে সিদ্ধান্ত: এই ইনডাস্ট্রির স্কিলগুলো আসলে **তিনটি আলাদা স্তরে** কাজ করে। বেশিরভাগ মানুষ একটা স্তর ভুলে গিয়ে ব্যর্থ হয়।

```
স্তর ১: প্রি-প্রোডাকশন  →  স্তর ২: প্রম্পট  →  স্তর ৩: এক্সিকিউশন + অ্যাসেম্বলি
(identity লক করা)          (স্টাইল-নির্দিষ্ট)     (মডেল কল → ক্যাপশন/মিউজিক/কাট)
```

## স্তর ১ — প্রি-প্রোডাকশন (আসল পার্থক্য এখানেই)

`film-studio-skills`-এর পুরো ৭টি স্কিল এই একটা নিয়মে চলে: **কিছুই জেনারেট করার আগে identity লক করো।**

| ধাপ | স্কিল | আউটপুট |
|---|---|---|
| ১ | `studio-init` | প্রজেক্ট ফোল্ডার, ভার্সনিং, প্রোডাকশন লগ |
| ২ | `film-breakdown` | স্ক্রিপ্ট → সিন প্ল্যান + শট কার্ড |
| ৩ | `reference-board` | রেফারেন্স বোর্ড (লুক, প্যালেট, লেন্স) লক |
| ৪ | `asset-passport` | প্রতিটি চরিত্র/লোকেশন/প্রপের "পাসপোর্ট" — চুল, পোশাক, দাগ, উচ্চতা, state-variant |
| ৫ | `stress-test` | লক করার আগে অ্যাসেট ভাঙার চেষ্টা (variance টেস্ট) |
| ৬ | `shot-prompt` | শট কার্ড → ১৫-ব্লক প্রম্পট |

**যে ভুলটা আমি নিজেও করেছিলাম:** আগের ভিডিওগুলোতে চরিত্রের ছবি আলাদা আলাদা প্রম্পটে বানিয়েছি, পাসপোর্ট/বোর্ড ছাড়া। ফলে চেহারা শটে-শটে সরেছে। সঠিক পথ: `asset-passport` → একই রেফারেন্স সব শটে, তারপর `flux-3-keyframes-continuation` দিয়ে শট জোড়া।

## স্তর ২ — প্রম্পট (স্টাইলভেদে ভিন্ন ব্যাকরণ)

একই "প্রম্পট" সব মডেলে কাজ করে না — প্রতিটি পরিবারে আলাদা স্ট্রাকচার:

- **MiniMax H3** (আগে ইনস্টল করা): ৩টি ফিল্ড — `integrated_multimodal_description` / `overall_soundscape` / `non_diegetic_music`; ডায়ালগ `<d>[ভাষা] ...</d>`; টাইমকোড `At 00:03.500`.
- **Seedance 2.0 / Higgsfield**: স্টাইল-নির্দিষ্ট ১৫টি আলাদা স্কিল (cinematic, anime-action, fight-scenes, cartoon, comic-to-video, product-360, music-video, social-hook, ecommerce, fashion, food, real-estate, brand-story, 3D-CGI, motion-design)।
- **FLUX 3 / BFL**: `flux-3-prompt-doctor` আগে ডায়াগনোজ, তারপর `flux-3-video` রাউটার, দরকারে `flux-3-audio-dialogue` বা `flux-3-cinematic-inserts`।
- **Remotion**: প্রম্পট নয় — কোড। React কম্পোনেন্টে টাইমলাইন।

## স্তর ৩ — এক্সিকিউশন + অ্যাসেম্বলি

`remotion-superpowers` (১৫ স্কিল) পুরো ডেলিভারি লেয়ার: `create-video` (টেক্সট → স্টুডিও প্রিভিউ), `create-short` (৯:১৬), `generate-clip`/`generate-image` (AI অ্যাসেট), `add-voiceover`/`add-music`/`add-captions`/`add-transitions`, `find-footage` (Pexels), `analyze-footage`/`review-video` (TwelveLabs), `transcribe`।

**মূল শিক্ষা:** ভালো AI ভিডিও = ৭০% প্রি-প্রোডাকশন + ২০% অ্যাসেম্বলি + ১০% প্রম্পট। যারা শুধু প্রম্পট নিয়ে মেতে থাকে, ওদের আউটপুট প্রতি শটে বদলে যায়।

## কী এখানে চলে, কী চলে না

| শ্রেণি | স্কিল সংখ্যা | এই স্যান্ডবক্সে |
|---|---|---|
| prompt-craft (শুধু প্রম্পট লেখে) | ৩৩ | ✅ পুরোটা চলে |
| render-pipeline (Remotion/ffmpeg) | ১৮ | ⚠️ npm খোলা, তাই Remotion বসানো যাবে; কিন্তু AI অ্যাসেট (voice/music/clip) API key ছাড়া হবে না |
| api-orchestration (সরাসরি মডেল কল) | ৩ | ❌ `api.minimax.io`, `fal.ai`, `api.higgsfield` — সব বন্ধ (HTTP 000) |

**অর্থাৎ:** এই মুহূর্তে আমি সত্যিকারের নতুন AI ক্লিপ জেনারেট করতে পারব না (কোনো ভিডিও API-ই খোলা নেই)। পারব — পূর্ণ প্রোডাকশন কিট বানাতে: পাসপোর্ট, রেফারেন্স বোর্ড, ১৫-ব্লক শট প্রম্পট, H3/Seedance/FLUX প্রম্পট, আর ffmpeg/Remotion অ্যাসেম্বলি।

## আপনার তিনটা ইউজ-কেসে সুপারিশ

| কনটেন্ট | স্ট্যাক |
|---|---|
| বাংলা মোটিভেশনাল শর্ট (Law 5 ধরনের) | `asset-passport` → `seedance-cartoon` বা `seedance-motion-design-ad` → `create-short` (ক্যাপশন/মিউজিক) |
| কার্টুন স্টোরি (Emu War ধরনের) | `asset-passport` + `reference-board` → `seedance-cartoon` / `seedance-comic-to-video` → `add-voiceover` + `add-captions` |
| অ্যানিমে ফাইট | `seedance-anime-action` + `seedance-fight-scenes` → `flux-3-keyframes-continuation` (ক্ল্যাশ কনটিনিউইটি) → `add-transitions` + `add-music` |
| সিনেমাটিক এক্সপ্লেইনার (Odyssey ধরনের) | `film-breakdown` → `shot-prompt` (১৫-ব্লক) → H3 প্রম্পটে অনুবাদ → `review-video` |

## ইনস্টলেশন-বাস্তবতা (স্কিল লেখকদের জন্য শিক্ষা)

1. **ভাঙা YAML সবচেয়ে বড় সমস্যা** — AKCodez-এর ১৫টি স্কিল এতেই পড়েছে। `name:`/`description:`-এ nested mapping বা multiline রাখলে CLI স্কিপ করে।
2. **নাম সংঘর্ষ নীরবে ওভাররাইট করে** — দুটো রিপোতে `setup` থাকলে পরে যেটা ইনস্টল হয় সেটা বাঁচে। ইনস্টলের আগে name-prefix ব্যবহার করুন।
3. **স্কিল = প্রসিডিউর, ক্ষমতা নয়** — যে স্কিল API দাবি করে, API না থাকলে সেটা শুধু সুন্দর ডকুমেন্ট।
