# 3D ডেমো — সফটওয়্যার র্যাস্টারাইজার

স্কিল: [`ai-video-skills/library/.claude/skills/3d-animation/`](../ai-video-skills/library/.claude/skills/3d-animation/SKILL.md)

| ফাইল | কী |
|---|---|
| `3d-demo-1080x1920.mp4` | ১২ সেকেন্ড, 1080×1920, 30 fps, ১.৬ MB |
| `frames/contact-sheet.jpg` | ৬টি স্টিল |
| `build.py` | রেন্ডারার — numpy জেড-বাফার র্যাস্টারাইজার → ffmpeg |
| `sheet.py` | contact sheet |

## পাইপলাইন (কোনো DCC নেই, GPU নেই, ব্রাউজার নেই)

```
vertices → model matrix (squash + spin) → look-at view → perspective project
        → per-triangle barycentric fill + z-buffer
        → per-face flat Lambert + rim   (facet-ই ডিটেইল)
        → key light বরাবর y=0-তে প্রজেক্টেড hard shadow
        → depth fog → vignette → 1.44× supersample downscale → ffmpeg
```

## ৩টি 3D অ্যানিমেশন নিয়ম যা এখানে কোডে আছে

1. **Squash & stretch ভলিউম রক্ষা করে** — `s_y·s_x·s_z = 1`, এবং স্ট্রেচ হয় **পথের দিকে**,
   উল্লম্ব গতির (speed) ওপর নির্ভর করে (সর্বোচ্চ ১.৪২×)।
2. **ওজন = স্পেসিং** — বাউন্সের উচ্চতা প্রতি ধাপে ×0.56 কমে; ফ্লাইট টাইম `T = 2√(2h/g)`,
   তাই ছোট বাউন্স দ্রুত, আর মাটিতে থাকার সময়ও ছোট হয়।
3. **এক ক্যামেরা মুভ, eased** — orbit −0.42→+0.24 rad + dolly ২৭→২০.৬ ইউনিট, `0.5−0.5·cos(πp)`;
   ফোকাল লেন্থ পুরো শটে স্থির (38° vertical FOV)।

## সৎ সীমা

- এটা **র্যাস্টারাইজার, রেন্ডারার নয়** — রিফ্লেকশন, রিফ্র্যাকশন (গ্লাস), GI, soft shadow,
  motion blur, DOF — কিছুই নেই।
- 2560×1440-এ রেন্ডার করে LANCZOS-এ 1080×1920-এ নামানো (1.44× supersample)।
- ১২ সেকেন্ড = ৩৬০ ফ্রেম = **৪ মিনিট ১৫ সেকেন্ড** (≈০.৭ সেকেন্ড/ফ্রেম)।
- ফন্ট DejaVu; spin করা জ্যামিতিতে ফেসেটই ডিটেইল, তাই টেক্সচার লাগেনি।
