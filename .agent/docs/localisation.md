# Localisation — Dari and Pashto

BOMS ships in three languages. English reads left to right; **Dari (`fa`)** and
**Pashto (`ps`)** mirror the whole shell.

Language is a **tenant setting** — `tenants.default_language_id`. There is no
per-user and no per-page override.

---

## 1 · Never label the direction

The top-bar switcher names the **language**:

```
🌐 English ▾        🌐 دری ▾        🌐 پښتو ▾
```

Never `EN (LTR)`, never an `RTL` badge, never `(RTL) دری`. Direction follows
from the language; a shopkeeper in Kabul does not need to be told which way
their own script runs. `LTR` / `RTL` may appear in a spec note or a schema
comment — that is documentation, not interface.

## 2 · What mirrors, what does not

| Mirrors | Stays left-to-right |
|---------|---------------------|
| Sidebar → right edge | Numbers and money |
| Drawers open from the **left** | SKUs, transaction and document numbers |
| Text and table columns right-align, column **order reverses** | **Barcodes and QR codes** |
| Back arrows, chevrons, steppers | Dates and times |
| Progress and timeline direction | Latin product codes |

**Barcode and QR are never mirrored.** A mirrored Code 128 does not scan. On a
mirrored screen the label *card* moves to the other side, but its contents are
drawn left-to-right — `svg.label_card()` and `dsl.label_card()` both do this by
flipping the canvas back for that block.

In CSS, a left-to-right run inside right-to-left text uses `.ltr-island`
(`direction: ltr; unicode-bidi: isolate`) — defined in
`specs/design/tokens/theme.css`.

## 3 · Type

Dari and Pashto are set in **Vazirmatn**. It carries the four-eye heh, the
Persian kaf and yeh, and Pashto's ښ ځ ټ ډ ړ ږ — which Inter does not have and
Noto Naskh renders poorly at UI sizes.

```
--font-sans: Inter, …           Latin
--font-rtl:  Vazirmatn, …       Dari and Pashto
```

**Never letter-space Perso-Arabic.** It is a joining script; tracking pulls the
joins apart and browsers fall back to unshaped glyphs. `svg.txt()` zeroes
tracking automatically when it detects the script — do not undo that.

Digits: the wireframes and the design use **Western digits** in data
(`1,284`, `AFN 48,000`, `ADF26-0042`) and Eastern Arabic digits only inside
prose (`۱۲ سپتمبر`). Keeping money and codes in Western digits is what Afghan
accounting software does, and it keeps tabular columns aligned across languages.

## 4 · How the localised boards are built

They are **not drawn by hand.** The English board is reflected and then
translated, so one layout change updates all three versions and they cannot
drift apart.

```
.agent/scripts/wireframes/
  dsl.mirror(elements, x0, width)   geometric reflection — flips x, negates
                                    line/arrow points, swaps text alignment
  i18n.localise(elements, locale)   string substitution + re-measure
  build.py  LOCALISED = ["02-Inventory"]
```

```bash
python3 .agent/scripts/wireframes/build.py            # builds all three
python3 .agent/scripts/wireframes/build.py --coverage # what is still English
```

### The string tables

`i18n.py` holds three dictionaries:

- `SHARED` — people, places, product names and Gregorian months, written the
  same way in both Perso-Arabic locales
- `FA` — Dari UI terms
- `PS` — Pashto UI terms

After an exact-match miss a **fragment pass** runs: month names, product names,
ledger type names and a small set of common words are substituted inside
composed strings such as `"12 Sep"` or `"4 of 4 received"`. That is why the
tables are ~700 entries rather than several thousand.

### What is deliberately left in English

1. **Spec note boxes.** They name real tables, columns and SQL —
   `inventory_stock_transactions` is not a word to translate. `dsl.note()` tags
   them `spec` and `localise()` skips them.
2. **Identifiers shown as data**: `is_main`, `lifecycle_status`, file names,
   `platform_sequences`, URLs.
3. **Numbers, SKUs, barcodes, document numbers.**

`--coverage` lists everything still reading as English so the list above stays
an explicit decision rather than an oversight.

## 5 · Terminology

The table below is the house vocabulary. Use it; do not re-invent a term per
screen.

| English | Dari (fa) | Pashto (ps) |
|---------|-----------|-------------|
| Inventory | موجودی | زېرمه |
| Items | اقلام | توکي |
| Stock ledger | دفتر موجودی | د زېرمې دفتر |
| Warehouse | انبار | ګودام |
| On hand | در انبار | په ګودام کې |
| On rent | در کرایه | په کرایه |
| Owned | در تملک | ملکیت |
| Reserved | رزرو شده | ریزرو شوي |
| Available | قابل دسترس | شته |
| Reservations | رزروها | ریزرونه |
| Transfers | انتقالات | لېږدونه |
| Average cost | قیمت اوسط | اوسط بیه |
| Sale price | قیمت فروش | د پلور بیه |
| Rental price | قیمت کرایه | د کرایې بیه |
| Deposit | تضمین | تضمین |
| Late fee | جریمه تأخیر | د ځنډ جریمه |
| Cleaning buffer | مهلت پاک‌کاری | د پاکولو موده |
| Barcode | بارکد | بارکوډ |
| Draft | مسوده | مسوده |
| Post (a document) | ثبت | ثبت |
| Dispose | ضایعات | له منځه وړل |
| Adjustment | تعدیل | سمون |
| Customer | مشتری | پیرودونکی |
| Purchase order | فرمایش خرید | د پیرود فرمایش |

Dari here is **Afghan Persian**, not Iranian Persian: `اوسط` not `میانگین`,
`مسوده` not `پیش‌نویس`, `فرمایش` not `سفارش`, `کرایه` not `اجاره`.

> The Pashto table was written from standard administrative and commercial
> usage. Have a native speaker review it before the strings ship — particularly
> the ledger type names and the report titles.
