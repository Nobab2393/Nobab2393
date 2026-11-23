# AI Video Skills Library

GitHub থেকে স্ক্যান করা AI ভিডিও-জেনারেশন স্কিলের সংগ্রহ — **৫৬টি ইনস্টল করা**।

```
ai-video-skills/
├── README.md          ← এই ফাইল
├── INDEX.md           ← ৫৬টি স্কিলের পূর্ণ তালিকা (ধরন + ব্যাকএন্ড)
├── PLAYBOOK.md        ← ৫৬টি পড়ে সংকলিত ইউনিফায়েড প্রোডাকশন প্লেবুক
└── library/
    └── .claude/skills/  ← আসল স্কিল ফাইলগুলো (৫৬টি ফোল্ডার)
```

## কীভাবে ব্যবহার করব
- **এজেন্ট (আমি):** `ai-video-skills/library/.claude/skills/<name>/SKILL.md` পড়ে ওয়ার্কফ্লো মানি। রুট `.claude/skills/`-এ রাখা হয়নি, যাতে মেইন রিপোর MiniMax-H3 স্কিলের সঙ্গে নাম সংঘর্ষ না হয়।
- **আপনি:** কোনো একটা স্কিল চাইলে বলুন "seedance-anime-action দিয়ে..." — আমি ওটার SKILL.md পড়ে সেই ফরম্যাটে কাজ করব।
- **হাতে চালাতে:** `npx skills add https://github.com/<repo> --skill <name>` (রিপো নাম INDEX.md-এ আছে)।

## উৎস রিপো (১৬)
machina-exm/film-studio-skills · beshuaxian/higgsfield-seedance2-jineng · AKCodez/higgsfield-claude-skills · black-forest-labs/skills · DojoCodingLabs/remotion-superpowers · Rimagination/h3lite · Yacey/agnes-ai-generation-skill · kaomei/stickman-video-director · cosmicstack-labs/lazy-frames · scenario-labs/skills · zhanghaonan777/Seedance2-skill · Vincentwei1021/anything2explainer · lemomo-ai/lemo-opuscar · cth9191/animate · artemnovitckii/claude-animation-skills · tuzhechen2005/opus-video-skills

## সতর্কতা
স্কিলগুলো এজেন্ট-পারমিশনে চলে। frontmatter ও বর্ণনা যাচাই করা হয়েছে, কিন্তু কোনো স্কিল চালানোর আগে পুরো `SKILL.md` পড়ে নেওয়া ভালো — বিশেষ করে যা API key বা বাইরের সার্ভিস চায়।
