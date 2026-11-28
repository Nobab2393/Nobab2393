# Pastel cast cards — the previous default (still valid for the comedy series)

এই লুকটা ছিল আগের ডিফল্ট — «মরে বাঁচা» আর «যমের অফিস»-এ এটাই ব্যবহৃত হয়েছে।
২০২৬-১১-২৩ থেকে নতুন কাজের ডিফল্ট বদলে গেছে — দেখুন [`STYLE.md`](STYLE.md) (2D cel-shaded)।
পুরোনো কমেডি সিরিজের ধারাবাহিকতার জন্য এই ডকটা যেমন আছে তেমনই থাকুক।

রেফারেন্স: [`pastel-cast-cards.png`](pastel-cast-cards.png) — পাঁচটা কার্ড, ক্রিম → মিন্ট → পিঙ্ক → আইস → লাইলাক।

---

## চেহারা (কী দেখে মনে রাখতে হবে)

| | |
|---|---|
| ধরন | ফ্ল্যাট ভেক্টর কার্টুন, বাচ্চাদের বইয়ের ছবি — **গ্র্যাডিয়েন্ট নেই, ছায়া নেই, টেক্সচার নেই** |
| রেখা | মোটা, সমান কালো-বাদামি আউটলাইন (`#151514`), সব আকৃতির চারপাশে একই ওজন |
| রং | প্রতিটা আকৃতিতে **একটাই সলিড ফিল**, প্যাস্টেল |
| মুখ | সামনে থেকে বাস্ট · বড় গোল ডট-চোখ + ছোট সাদা হাইলাইট · সরু ভুরু · ছোট নাক · সরল হাসি |
| চুল | এক রঙের সলিড ব্লক, সরল জ্যামিতিক আকার |
| শরীর | কাঁধ থেকে নিচ পর্যন্ত, **হাত নেই**, ছোট গলা |
| কার্ড | উঁচু গোল-কোণা কার্ড (প্রায় ১:২), প্যাস্টেল ব্যাকগ্রাউন্ড, কার্ডের ভেতরে চরিত্র |
| ক্যাপশন | কার্ডের নিচে কালো স্ট্রিপ: **নাম** (সাদা, বোল্ড) + **ভূমিকা** (ধূসর, ছোট) |

## প্যালেট (রেফারেন্স থেকে মাপা)

| ব্যবহার | হেক্স |
|---|---|
| কালি / আউটলাইন / পেজ | `#151514` · পেজ ব্যাকগ্রাউন্ড `#151515` |
| কার্ড ১–৫ | `#F3E3C3` (ক্রিম) · `#D7EBD0` (মিন্ট) · `#F6D9E3` (পিঙ্ক) · `#D8EEF2` (আইস) · `#E6E0F3` (লাইলাক) |
| ত্বক | `#B9825A` · `#A56A44` · `#C8916B` · `#C98A5E` |
| চুল | `#1E1612` |
| পোশাক | সবুজ `#2E7D5B` · লাল `#C8372D` · নীল `#2B4C9B` · হলুদ `#F2B134` · সাদা `#FFFFFF` · কমলা-সোনালি `#E8A33D` |
| ব্লাশ (শুধু বাচ্চা) | `#E8907E` @ ৪৫ % |

## অনুপাত (কার্ডের প্রস্থ = ১)

- কার্ড: প্রস্থ ১ · উচ্চতা ২ · কোণা-ব্যাসার্ধ ০.০৮
- পাঁচটা কার্ড এক সারিতে: ফাঁক ০.১০ · বাইরের মার্জিন ০.০৬
- মাথা: ব্যাস ≈ ০.৩৫ · গলা ≈ ০.০৮ · কাঁধের প্রস্থ ≈ ০.৯০, কার্ডের নিচ পর্যন্ত
- আউটলাইন: ≈ ০.০১৪ (কার্ড ২৪৮ px হলে ≈ ৩.৫ px)
- চোখ: ব্যাস ≈ ০.০৫, চোখের ফাঁক ≈ ০.১২; নিচে ক্যাপশন স্ট্রিপের উচ্চতা ≈ ০.২৬

## প্রম্পট টেমপ্লেট (Hailuo / Nano Banana / যেকোনো ইমেজ মডেল)

> flat vector cartoon character card, cute children's-book style: one rounded rectangle card with a
> plain pastel background, a single front-facing bust of **{name}**, **{age/role}**, **{skin tone}**
> skin, **{hair}**, wearing **{garment}**; thick even dark-brown outlines (`#151514`), solid flat
> colour fills only, no gradients, no shading, no texture, no highlights except one small white dot
> in each eye; simple geometric face — two round black dot eyes, thin eyebrows, small nose, simple
> smile; head and shoulders only, no arms; card corner radius about 8 % of its width.
> No text inside the card.

**নেগেটিভ:** photorealistic, 3d render, cgi, gradient, airbrush, soft shadow, drop shadow, texture,
noise, halftone, extra fingers, arms, open mouth screaming, realistic eyes with iris detail, dark
background, moody lighting, text, watermark, logo.

## কোডে বানানোর রেসিপি (PIL)

`film.py`-এর পুরোনো `cast_card()` একই কাঠামোয় লেখা ছিল — নতুন স্টাইলে বদলাতে হবে শুধু:

1. `lay = Image.new("RGBA", (W, H), pastel)` এবং `rounded_rectangle(radius=W*0.08)` দিয়ে কার্ড,
2. বাস্ট PNG (স্বচ্ছ) কার্ডের নিচ পর্যন্ত বসানো, `ImageDraw` দিয়ে `outline=INK, width=int(W*0.014)`,
3. নিচে কালো স্ট্রিপ (উচ্চতা `0.26*H`), নাম `w=700`, ভূমিকা `w=400` ধূসরে,
4. কোনো গ্রেড, ভিনিয়েট বা স্পেকল **নয়** — এ স্টাইলে ছবি পরিষ্কার থাকে (নয়ার গ্রেড বন্ধ)।

## মনে রাখার নিয়ম

- এই স্টাইলে **ভয়/nuar গ্রেড নেই** — রং প্যাস্টেল, আলো সমান, ছবি উজ্জ্বল।
- প্রতিটা চরিত্রের কার্ডের প্যাস্টেল রং আলাদা (একই সিরিজে পাঁচটা আলাদা প্যাস্টেল)।
- নাম আর ভূমিকা ইংরেজি বা বাংলা — যেটা প্রজেক্টের ভাষা; রেফারেন্সে ইংরেজি ছিল।
