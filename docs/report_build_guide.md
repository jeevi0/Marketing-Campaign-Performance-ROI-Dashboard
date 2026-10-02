# Report Build Guide — Power BI Desktop

Step-by-step instructions to build `Marketing_Campaign_ROI_Dashboard.pbix` from the files in this repo.
Canvas: **16:9, 1280 × 720**. Theme: `powerbi/theme/marketing_roi_theme.json`.

---

## Step 1 — Load data (Power Query)

1. **Home → Transform data → Manage Parameters → New**
   - Name `DataFolderPath`, Type *Text*, Current value = full path to `data\model\` **with trailing backslash**.
2. **New Source → Blank Query → Advanced Editor** — paste each script from `powerbi/power-query/` and name the query after the file:
   `FactPerformance`, `DimClient`, `DimCampaign`, `DimChannel`, `DimGeography`.
   *(Alternative: `FactPerformance_FromGitHub.m` reads straight from your public repo.)*
3. **Close & Apply.**

## Step 2 — Model

1. **Modeling → New table** → paste `DimDate` from `powerbi/dax/measures.dax`.
   Then **Table tools → Mark as date table → Date**.
2. **Model view** — create relationships (all *Many-to-one, Single* direction):

   | From (many) | To (one) |
   |---|---|
   | `FactPerformance[Date]` | `DimDate[Date]` |
   | `FactPerformance[ClientKey]` | `DimClient[ClientKey]` |
   | `FactPerformance[CampaignKey]` | `DimCampaign[CampaignKey]` |
   | `FactPerformance[ChannelKey]` | `DimChannel[ChannelKey]` |
   | `FactPerformance[GeoKey]` | `DimGeography[GeoKey]` |

   ⚠️ Do **not** relate `DimCampaign[ClientKey]` to `DimClient` — it creates an ambiguous path. Client filters reach campaigns through the fact table.
3. **Sort by column:** `DimDate[Month]` → `Month No`; `DimDate[Year Month]` → `YearMonthKey`; `DimDate[Weekday]` → `Weekday No`; `DimChannel[ChannelGroup]` → `ChannelGroupSort`.
4. **Data categories:** `DimGeography[Country]` = Country/Region, `[State]` = State or Province, `[MapLocation]` = Place.
5. **Hide** all key columns and `RowID` in the fact table (right-click → Hide in report view).
6. **Home → Enter data** → create a table `_Measures` with one column, load it, and add every measure from `measures.dax`. Set formats as noted in the comments. Hide the dummy column — the table jumps to the top of the Fields pane.

## Step 3 — Theme & page template

1. **View → Themes → Browse for themes** → `marketing_roi_theme.json`.
2. Build one page as a template, then duplicate it 5 times:
   - **Header band**: rectangle 1280 × 64, fill `#0F2A4A`. Title text box *"Marketing Campaign Performance & ROI Dashboard"* (white, Segoe UI Semibold 18).
   - **Subtitle**: card visual with `Selected Period Label`, no background, light text.
   - **Navigation**: **Insert → Buttons → Navigator → Page navigator** in the top-right of the header.
   - **Slicer row** (y = 72): Date (*Between*, `DimDate[Date]`), Client, Channel Group, Country, Objective — dropdown style.
     **View → Sync slicers** → sync all five across every page.
3. Rename the pages: *Executive Overview, Campaign Performance, Channel Analysis, Client Analysis, Geographical Analysis, Detailed Data*.

---

## Step 4 — Pages

### Page 1 · Executive Overview
| Visual | Fields | Notes |
|---|---|---|
| 7 × **Card (new)** | `Total Spend`, `Total Impressions`, `Total Clicks`, `Total Conversions`, `CTR`, `CPA`, `ROI` | Add reference label `Spend YoY Label` (or the YoY % measures) under each value |
| **Line chart** | X `DimDate[Year Month]`, Y `Total Revenue`, `Total Spend` | Markers on; one Y axis only (both in $) |
| **Clustered bar** | Y `DimChannel[ChannelGroup]`, X `Total Spend` | Data labels; tooltip `Spend Share %` |
| **Clustered bar** | Y `DimClient[Client]`, X `ROI` | Bars → *fx* → Field value `ROI Color` |
| **Funnel** | `Total Impressions`, `Total Clicks`, `Total Leads`, `Total Conversions` | Values only (no category) |
| **Multi-row card** | `Net Profit`, `Top Channel by ROI`, `Top Client by Revenue`, `CPL`, `Active Campaigns` | "Highlights" panel |

### Page 2 · Campaign Performance
| Visual | Fields | Notes |
|---|---|---|
| **Clustered bar** | Y `DimCampaign[Campaign]`, X `Total Spend` | Filter pane → Top N = 12 by `Total Spend` |
| **Line chart** | X `DimDate[Week Start]`, Y `Total Clicks` | Date trend |
| **Line chart** | X `DimDate[Week Start]`, Y `Total Conversions` | Separate chart — no dual axis |
| **Scatter** | Details `Campaign`, X `CPA`, Y `ROI`, Size `Total Spend` | Analytics pane: X average line, Y constant line at 0 |
| **Table** | Campaign, Objective, Spend, Clicks, Conversions, CTR, CPA, Revenue, ROI, `Campaign ROI Rank` | ROI font colour → `ROI Color`; CPA → `CPA Color` |
| **Line chart** (optional) | X `DimDate[Date]`, Y `CPA 7D Rolling` | Smoothed CPA trend |

### Page 3 · Channel / Partner Analysis
| Visual | Fields | Notes |
|---|---|---|
| 4 × **Column chart** | X `ChannelGroup`; Y = `Total Spend` / `CTR` / `CPA` / `ROI` | Small multiples feel; same channel colours on every chart |
| **Stacked area** | X `Year Month`, Y `Total Spend`, Legend `ChannelGroup` | Monthly spend mix |
| **Matrix** | Rows `ChannelGroup` → `Channel`; Values Spend, Impressions, Clicks, Conversions, CTR, CPA, ROI | Expand to level 2; "Other" = Email, X (Twitter), Affiliate |

> Tip: set channel colours once (Format → Colors) on the first chart: Google `#2A78D6`, Meta `#EB6834`, LinkedIn `#1BAF7A`, YouTube `#EDA100`, Display `#E87BA4`, Other `#008300`. Keep the same mapping on every visual.

### Page 4 · Client Analysis
| Visual | Fields | Notes |
|---|---|---|
| **Clustered column** | X `Client`, Y `Budget (Pro-rated)`, `Total Spend` | Tooltip: `Budget Utilization`, `Budget Status` |
| **Bar chart** | Y `Client`, X `Conversion Contribution %` | Sorted descending |
| **Bar chart** | Y `Client`, X `CPA` | Bars → `CPA Color`; Analytics → constant line = `CPA Benchmark` (fx) |
| **Table** | Client, Industry, Budget (Pro-rated), Spend, Budget Utilization, Budget Status, Clicks, Leads, Conversions, Conversion Contribution %, CPA, Revenue, ROI | `Budget Status` font colour → `Budget Status Color` |

### Page 5 · Geographical Analysis
| Visual | Fields | Notes |
|---|---|---|
| **Map / Filled map** | Location `MapLocation`, Bubble size `Total Spend`, Tooltip Leads, Conversions, ROI | Enable maps in *Options → Security* if disabled |
| **Clustered column** | X `Country`, Y `Total Spend`, `Total Revenue` | |
| **Bar chart** | Y `Country`, X `ROI` | `ROI Color` |
| **Clustered column** | X `Country`, Y `Total Leads`, `Total Conversions` | |
| **Matrix** | Rows `Country` → `State`; Values Spend, Leads, Conversions, CPA, Revenue, ROI | Drill down country → state |

### Page 6 · Detailed Data Table
| Visual | Fields | Notes |
|---|---|---|
| **Table** | `DimDate[Date]`, `Client`, `Campaign`, `Channel`, `Impressions`, `Clicks`, `Spend`, `Conversions`, `Revenue` (+ optional `Country`, `State`, `Leads`) | Use the fact columns as *Sum*; totals row on; alternating rows from theme |
| **Drill-through** | Add `Client`, `Campaign`, `ChannelGroup` to the *Drill through* well | Right-click any bar on other pages → *Drill through → Detailed Data* |

---

## Step 5 — Polish

- **Tooltips page** (optional): a small 320 × 240 page (*Page information → Allow use as tooltip*) with CTR, CPC, CPA, ROI cards — assign it to charts on pages 2–5.
- **Bookmarks**: *Reset filters* button on every page (bookmark with all slicers cleared, *Data* only).
- **Edit interactions**: on the Executive page set KPI cards to *None* so clicking a chart doesn't blank them, if preferred.
- **Accessibility**: add Alt text to each visual; check tab order (*View → Selection*).
- **Performance**: *Optimize → Performance analyzer*; all measures should render in < 200 ms on this dataset.

## Step 6 — Publish to GitHub

1. Save as `powerbi/Marketing_Campaign_ROI_Dashboard.pbix` (≈ 3–5 MB).
   *Optional:* **File → Save as → Power BI Project (.pbip)** as well for text-diffable source control.
2. Take screenshots of every page and overwrite the PNGs in `docs/images/` (keep the file names).
3. Commit & push:
   ```bash
   git init
   git add .
   git commit -m "Marketing Campaign Performance & ROI Dashboard"
   git branch -M main
   git remote add origin https://github.com/<your-username>/Marketing-Campaign-Performance-ROI-Dashboard.git
   git push -u origin main
   ```
4. Add repo **topics**: `power-bi`, `dax`, `power-query`, `marketing-analytics`, `dashboard`, `data-visualization`, `roi`.
