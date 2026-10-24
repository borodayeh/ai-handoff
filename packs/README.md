# packs/

Project handoff packs live here, one file per project: `<slug>-pack.md`.

```bash
python3 scripts/handoff.py new myproject --out packs   # creates packs/myproject-pack.md
python3 scripts/handoff.py validate packs/*.md
```

CI validates every `*-pack.md` on push, so a pack with a missing section or a decision without a
rejected alternative can't be committed quietly.

Keep this repository private if your packs contain project state you wouldn't publish.

Repo: [borodayeh/ai-handoff](https://github.com/borodayeh/ai-handoff)

---

## پوشه‌ی پک‌ها

پک هر پروژه اینجا نگه داشته می‌شود، یک فایل برای هر پروژه: `<slug>-pack.md`.

```bash
python3 scripts/handoff.py new myproject --out packs   # می‌سازد packs/myproject-pack.md
python3 scripts/handoff.py validate packs/*.md
```

هر بار که push می‌کنی، CI همه‌ی `*-pack.md` را چک می‌کند؛ پس پکی که بخشی را کم دارد یا تصمیمی
بدون گزینه‌ی ردشده دارد، بی‌سروصدا کامیت نمی‌شود.

اگر پک‌ها وضعیت پروژه‌ای را دارند که نمی‌خواهی منتشر شود، این ریپو را خصوصی نگه دار.

ریپو: [borodayeh/ai-handoff](https://github.com/borodayeh/ai-handoff)
