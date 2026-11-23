# Claude Animation Style — শেখা + প্রমাণ

## যা শেখা হয়েছে

"Claude animation" কোনো ভিডিও মডেলের লুক নয়। Claude একটা ছোট প্রোগ্রাম লেখে যেটা অ্যানিমেশনটা
আঁকে, আর সেই প্রোগ্রাম MP4-এ রেন্ডার হয়। এই একটাই সত্য বাকি সব সিদ্ধান্ত ঠিক করে দেয়:

| বৈশিষ্ট্য | মানে |
|---|---|
| **প্রতিটি ফ্রেম `t`-এর ফাংশন** | `window.seek(t)` — কোনো `Math.random`, timer বা CSS transition নেই |
| **ফ্ল্যাট ভেক্টর** | ৪–৫টি রঙ, গ্রেডিয়েন্ট নেই, ১০৮০p-এ আউটলাইন ≥ ৩px |
| **স্প্রিং ইজিং** | `cubic-bezier(0.34,1.56,0.64,1)`, ১২ ফ্রেমে থামে |
| **একটাই অ্যাকসেন্ট** | করাল শুধু একটা জিনিসে; বাকিটা গ্রাউন্ড/ইঙ্ক/গ্রে |
| **এলিমেন্ট-ক্যারিড ট্রানজিশন** | ফেড নয় — একটা শেপ বড় হয়ে ফ্রেম ভরে *পরের ব্যাকগ্রাউন্ড হয়* |
| **টাইপ আর্কিটেকচার** | একটাই ভারী গ্রোটেস্ক; দৈত্যাকার সংখ্যা (ফ্রেমের উচ্চতার ~৩০%) |

সম্পূর্ণ স্পেক: [`../ai-video-skills/library/.claude/skills/claude-animation-style/SKILL.md`](../ai-video-skills/library/.claude/skills/claude-animation-style/SKILL.md)
· ইজিং ম্যাথ: [`references/motion-grammar.md`](../ai-video-skills/library/.claude/skills/claude-animation-style/references/motion-grammar.md)
· প্যালেট: [`references/looks-palettes.md`](../ai-video-skills/library/.claude/skills/claude-animation-style/references/looks-palettes.md)

## প্রমাণ (এই ফোল্ডার)

| ফাইল | কী |
|---|---|
| `claude-animation-style-demo-1080x1920.mp4` | ৬ সেকেন্ড, 1080×1920, 30 fps, H.264 — ৫টি বিট |
| `frames/contact-sheet.jpg` | ৬টি স্টিল + সবুজ রেখায় ৯:১৬ safe area |
| `build.py` | রেন্ডারার — PIL @2× supersample → ffmpeg। ব্রাউজার লাগে না |
| `sheet.py` | contact sheet জেনারেটর |

বিট-ম্যাপ: `0.0s` করাল ডিস্ক পপ (overshoot) → `0.6s` তিনটি ইঙ্ক বার staggered →
`2.45s` দৈত্য "4" count-up → `3.78s` ডিস্ক বড় হয়ে করাল গ্রাউন্ড হয় →
`4.3s` "ONE ACCENT. / ONE MEANING." মাস্ক থেকে উঠে আসে।

## সীমাবদ্ধতা — যা সত্যি

- **Chromium/Playwright নেই এই স্যান্ডবক্সে** (egress শুধু GitHub/PyPI/npm), তাই ব্রাউজার-ক্যাপচার
  পথটা চালানো যায়নি। একই ইজিং ম্যাথ PIL-এ পোর্ট করা হয়েছে — লুকটা কার্ভ আর প্যালেট থেকে আসে,
  রেন্ডারার থেকে নয়।
- **ফন্ট:** DejaVu Sans Bold (সিস্টেমে একমাত্র)। আসল লুকে Inter Tight/Poppins লাগে — ইন্টারনেট
  খোলা থাকলে সেগুলো নামিয়ে নিলে টাইপ আরও নিখুঁত হবে।
- ডেমোটা **loop-ready নয়** (৬ সেকেন্ডের বিট-ডেমো, শেষ ফ্রেম প্রথম ফ্রেমে ফেরে না)।

## কখন এই স্টাইল, কখন নয়

- **হ্যাঁ:** ব্যাখ্যা, ডেটা, প্রোডাক্ট, "কীভাবে কাজ করে", স্ট্যাট, লঞ্চ রিল।
- **না:** মুখ, অভিনয়, ডায়ালগ, ক্যারেক্টার ধারাবাহিকতা — ওখানে ইমেজ-জেনারেশন + ffmpeg টাইমলাইন
  পাইপলাইন (`quiet-wolf/` দেখুন) লাগে, কারণ কোডে আঁকা ক্যারেক্টার একই মুখ ধরে রাখতে পারে না।
