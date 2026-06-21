# Thin prose stylesheet (Tailwind Typography)

Builds `../src/uhome_server/static/thin/prose.css` from `thin_pages.py` class names
using **Tailwind CSS** and **`@tailwindcss/typography`**.

```bash
cd thin-prose-build
npm install
npm run build
```

Run after changing Tailwind classes in `src/uhome_server/thin_pages.py`.

The compiled CSS is **checked in** so `pip install` and CI do not require Node.
