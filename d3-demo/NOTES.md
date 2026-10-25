# D3 unit-chart demo: video build notes

A 10-minute D3 v7 demo for IFSC 54503. Each of the 1,289 reported AI incidents is one dot. The same dots rearrange into four views: by year, by risk domain, by intent, and as each year's share (a unit Marimekko).

```
d3-demo/
├── data/aiid_incidents_2018_2025.csv   1,289 rows: incident_id, year, title, risk_domain, intent
├── prep_data.py                        Step 0: workbook → CSV
├── style.css                           shared by every step, so diffs show only D3 code
├── step-01.html … step-06.html         each step builds on the previous one
└── NOTES.md
```

## Run locally

```bash
cd d3-demo
npx serve .                 # or: python3 -m http.server 8000
```
Then open `step-01.html` in the browser. The D3 CDN needs an internet connection. In VS Code, **Live Server** works too.

## Verified data facts

| Check | Result |
|---|---|
| Rows / unique `incident_id` | 1,289 / 1,289 |
| Not classified (no MIT fields) | 55, written as "Not classified" |
| Per year | 2018: 46 · 2019: 44 · 2020: 91 · 2021: 80 · 2022: 106 · 2023: 174 · 2024: 299 · 2025: 449 |
| Malicious use share | 1 of 46 (2%) in 2018 → 237 of 449 (53%) in 2025 |
| Intent | Intentional 643 · Unintentional 578 · Other 13 · Not classified 55 |

> **Say on camera, once:** each dot is a *reported* incident. Growth reflects reporting and ingestion as well as real-world frequency.

## Run-of-show

| Time | Step | Beat |
|---|---|---|
| 0:00–0:45 | — | What D3 is; why a unit chart (every dot is real) |
| 0:45–1:45 | 01 | Load, group, band scale |
| 1:45–3:15 | 02 | Grid math + data join → a bar chart made of dots |
| 3:15–4:30 | 03 | Sort + color + HTML legend |
| 4:30–6:30 | 04 | **The morph**: four views, one `update()` |
| 6:30–7:45 | 05 | Tooltip, legend highlight |
| 7:45–9:15 | 06 | Accessibility pass |
| 9:15–10:00 | — | Takeaways, when not to use D3 |

---

## Step 0: Data prep (off-camera or ~20 s)

**Say:** "I exported one row per incident and let D3 do all the grouping in the browser, so the counting rule is visible in code."

**Pitfall:** if you open the HTML by double-clicking, the browser blocks `d3.csv` under `file://`. The page catches the error and tells the viewer to run a local server.

---

## Step 1: Load, group, scale

**Show:** the empty frame with year ticks, then DevTools Console with the `Map(8)`.

**Say:**
1. **Margin convention.** A fixed 1000×540 coordinate system. `viewBox` makes it responsive with no resize code.
2. **`d3.csv` returns a Promise.** `await` it; `autoType` turns `"2018"` into `2018`.
3. **`d3.group` produces a Map** from year to that year's incidents.
4. **`scaleBand`** gives each year an equal-width column.

```js
const incidents = await d3.csv("data/aiid_incidents_2018_2025.csv", d3.autoType);
const byYear = d3.group(incidents, d => d.year);
const years = d3.sort(byYear.keys());
const x = d3.scaleBand().domain(years).range([margin.left, width - margin.right]).paddingInner(0.15);
```

---

## Step 2: One dot per incident

**Show:** a step-01 → step-02 diff, the blue dot columns, then the Elements panel: select a `<circle>` and type `$0.__data__` in the console.

**Say:**
1. **Fit the grid.** Try spacings from large to small and keep the first where the biggest year, 449 incidents, still fits vertically.
2. **Every incident gets an (x, y) slot.** Dots fill rows left to right, bottom to top. This is just arithmetic, not a D3 feature.
3. **The data join.** `selectAll` → `data` → `join` creates one `<circle>` per incident.
4. **The key function** `d => d.incident_id` says "this circle *is* this incident". Step 4 depends on it.
5. **The y scale is in incidents.** Each full row holds `cols` incidents, so the axis reads counts.

```js
for (const [year, group] of byYear) {
  const left = x(year) + (x.bandwidth() - cols * step) / 2;
  group.forEach((d, i) => {
    d.x = left + (i % cols) * step + step / 2;
    d.y = bottom - Math.floor(i / cols) * step - step / 2;
  });
}

svg.append("g").selectAll("circle")
  .data(incidents, d => d.incident_id)
  .join("circle")
    .attr("class", "dot")
    .attr("cx", d => d.x).attr("cy", d => d.y).attr("r", step * 0.42);
```

**Pitfall:** v3/v4-era code with separate `enter()`/`exit()` chains. Most AI-generated D3 still writes it that way; `.join()` replaces it.

---

## Step 3: Color by risk domain

**Show:** the diff (sort + `fill` + legend), then the result reading as stacked bars.

**Say:**
1. **Sort within each column** by domain order, largest domain first, so colors form bands. Malicious use sits on the baseline, where its growth is easiest to compare.
2. **`scaleOrdinal`** maps domain → color, using the Okabe–Ito palette, which is safe for common color-vision deficiencies.
3. **The legend is an HTML `<ul>`, built with the same join.** D3 works on any DOM, not just SVG.

```js
group.sort(byDomainOrder);
const color = d3.scaleOrdinal(DOMAINS.map(d => d.key), DOMAINS.map(d => d.color));
d3.select("#legend").selectAll("li").data(DOMAINS).join("li") /* swatch + label */;
```

---

## Step 4: The morph (the centerpiece)

**Show:** click through all four views slowly. Then show the code in this order: `VIEWS`, `update()`, `shareByYear()`.

**Say:**
1. **Separate layout from drawing.** Each view only writes `d.x, d.y, d.r` onto the incidents; one `update()` draws whatever positions are there.
2. **Object constancy.** Because of the key, the same `<circle>` moves to its new slot, so your eye can follow an incident between views.
3. **Two layouts cover four views.** `columns()` serves year, domain, and intent; `shareByYear()` is the Marimekko.
4. **How the Marimekko works:** every year gets the same number of rows, so a domain's band height is its share of that year, and column width is the year's total. The code tries every row count and keeps the one that gives the biggest dots.
5. **Labels use a keyed join too.** Year labels slide between "By year" and "Share", and domain labels fade in and out.
6. **Axis generators can transition:** `yAxisG.transition().call(axis)`.

```js
const VIEWS = {
  year:   () => columns(d => d.year,        years,                   byDomainOrder, k => [String(k)]),
  domain: () => columns(d => d.risk_domain, DOMAINS.map(d => d.key), byYearOrder,   k => twoLines(domainLabel.get(k))),
  intent: () => columns(d => d.intent,      INTENTS,                 byDomainOrder, k => [k]),
  share:  shareByYear,
};

dotsG.selectAll("circle")
  .data(incidents, d => d.incident_id)
  .join(enter => enter.append("circle") /* start at baseline, r = 0 */)
  .transition().duration(900)
    .delay(d => ((d.x - margin.left) / innerW) * 300)    // left-to-right sweep
    .attr("cx", d => d.x).attr("cy", d => d.y).attr("r", d => d.r);
```

**Points worth one sentence each:**
- In the share view, each column's rows stretch slightly so it reaches exactly 100%. Without that stretch, the y-axis shares would be wrong.
- Event handlers receive `(event, d)` in v6 and later; `d3.event` no longer exists.
- Clicking again mid-animation interrupts the old transition cleanly, because a new transition on the same element replaces it.

---

## Step 5: Details on demand

**Show:** hover several dots, including one from 2018 and one from 2025, then hover the legend.

**Say:**
1. **`d3.pointer(event, figure)`** gives the pointer position relative to the figure, which is where the tooltip goes.
2. **Use `.text()`, never `.html()`, for data.** Incident titles come from the internet.
3. **Highlighting is one function:** `classed("is-dimmed", …)`, with CSS handling the fade.
4. **Call out the gap:** "This only works with a mouse." That sets up step 6.

```js
tooltip.append("strong").text(d.title);   // safe: no HTML injection
dotsG.selectAll("circle").classed("is-dimmed", d => key !== null && d.risk_domain !== key);
```

---

## Step 6: Accessibility pass

**Show:** Tab through the view buttons and the legend, press Enter on a legend item, open the data table, and turn on a screen reader (VoiceOver: Cmd+F5) to hear the live update. If you can, toggle reduced motion in the OS settings to show transitions switch off.

| Fix | Code | Why |
|---|---|---|
| View buttons expose state | `aria-pressed` instead of a CSS class | Screen readers announce "pressed" |
| Legend items become `<button>`s | Click pins a domain, hover previews it; Enter and Space work | Highlighting works without a mouse |
| SVG gets a name and description | `role="img"`, `<title>`, a `<desc>` that updates per view | The chart has an accessible summary |
| Live region | `<p aria-live="polite">` is filled by `describe()` | Clicking a view announces what changed |
| Data table | `<details>` + `<table>` built with `d3.rollup` and joins, `<caption>`, `scope` | A full text alternative for all 1,289 dots |
| Reduced motion | `matchMedia("(prefers-reduced-motion: reduce)")` sets duration to 0 | Respects the OS setting |

**Honest limit to say on camera:** individual dots aren't keyboard-focusable, because 1,289 tab stops would be worse than none. The table is the accessible path to the details.

---

## Wrap-up talking points (45 s)

- **D3's strengths:** full control, data-bound DOM, animated transitions.
- **D3's cost:** you build everything yourself, including axes, legends, layout math, and accessibility.
- **When not to use it:** for a quick exploratory chart, Vega-Lite, Observable Plot, or Tableau gets you there in minutes.
