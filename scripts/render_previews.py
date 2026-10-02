"""
Renders static PNG previews of the six report pages from the dataset, so the
GitHub README shows what the dashboard looks like. These are design mockups
computed from the same CSVs Power BI loads - replace them with real Power BI
screenshots (docs/images/) once you have built the .pbix.

Run:  python scripts/render_previews.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "data" / "model"
OUT = ROOT / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)

# ---- palette (matches powerbi/theme/marketing_roi_theme.json) -------------
NAVY, PAGE, CARD, BORDER = "#0F2A4A", "#F4F6FA", "#FFFFFF", "#E3E7EE"
INK, INK2, MUTED, GRID = "#0B1B2B", "#52514E", "#8A8F98", "#EEF1F5"
SERIES = ["#2A78D6", "#EB6834", "#1BAF7A", "#EDA100", "#E87BA4", "#008300"]
BLUE, ORANGE = SERIES[0], SERIES[1]
GOOD, WARN, BAD = "#1B7F4C", "#C98500", "#C0392B"
TABS = ["Overview", "Campaigns", "Channels", "Clients", "Geography", "Data Table"]
GROUPS = ["Google", "Meta", "LinkedIn", "YouTube", "Display", "Other"]
GCOL = dict(zip(GROUPS, SERIES))
PAGES = ["Executive Overview", "Campaign Performance", "Channel Analysis",
         "Client Analysis", "Geographical Analysis", "Detailed Data"]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": BORDER,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.titleweight": "bold", "axes.titlesize": 10.5, "axes.titlecolor": INK,
                     "axes.titlelocation": "left", "axes.titlepad": 10})

# ---- data -------------------------------------------------------------------
f = pd.read_csv(M / "fact_campaign_performance.csv", parse_dates=["Date"])
cl = pd.read_csv(M / "dim_client.csv"); cp = pd.read_csv(M / "dim_campaign.csv",
                                                         parse_dates=["StartDate", "EndDate"])
ch = pd.read_csv(M / "dim_channel.csv"); geo = pd.read_csv(M / "dim_geography.csv")
df = (f.merge(cl, on="ClientKey").merge(cp.drop(columns="ClientKey"), on="CampaignKey")
       .merge(ch, on="ChannelKey").merge(geo, on="GeoKey"))
SUMS = ["Spend", "Impressions", "Clicks", "Leads", "Conversions", "Revenue"]


def kpis(g):
    g = g[SUMS].sum() if isinstance(g, pd.DataFrame) else g
    return dict(**g, CTR=g.Clicks / g.Impressions, CPA=g.Spend / g.Conversions,
                CPL=g.Spend / g.Leads, ROI=(g.Revenue - g.Spend) / g.Spend,
                ROAS=g.Revenue / g.Spend, CPC=g.Spend / g.Clicks)


def agg(by):
    a = df.groupby(by)[SUMS].sum()
    a["CTR"] = a.Clicks / a.Impressions
    a["CPA"] = a.Spend / a.Conversions
    a["ROI"] = (a.Revenue - a.Spend) / a.Spend
    a["ROAS"] = a.Revenue / a.Spend
    return a


def money(v, d=1):
    for lim, s in [(1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if abs(v) >= lim:
            return f"${v / lim:.{d}f}{s}"
    return f"${v:,.0f}"


def num(v, d=1):
    for lim, s in [(1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if abs(v) >= lim:
            return f"{v / lim:.{d}f}{s}"
    return f"{v:,.0f}"


fmt_money = mt.FuncFormatter(lambda v, _: money(v, 1 if abs(v) < 1e7 else 0))
fmt_num = mt.FuncFormatter(lambda v, _: num(v, 0))
fmt_pct = mt.FuncFormatter(lambda v, _: f"{v:.0%}")
roi_color = lambda r: BAD if r < 0 else (WARN if r < 1 else GOOD)


# ---- page chrome ------------------------------------------------------------
def page(idx, subtitle):
    fig = plt.figure(figsize=(16, 9), dpi=110, facecolor=PAGE)
    hdr = fig.add_axes([0, 0.915, 1, 0.085]); hdr.set_axis_off()
    hdr.add_patch(plt.Rectangle((0, 0), 1, 1, color=NAVY, transform=hdr.transAxes))
    hdr.text(0.012, 0.62, "Marketing Campaign Performance & ROI Dashboard", color="white",
             fontsize=15, weight="bold", va="center")
    hdr.text(0.012, 0.25, f"{PAGES[idx]}  ·  {subtitle}", color="#B9C7DA", fontsize=9.5, va="center")
    x = 0.995
    for i in range(len(PAGES) - 1, -1, -1):
        w = 0.068
        x -= w + 0.004
        active = i == idx
        hdr.add_patch(plt.Rectangle((x, 0.26), w, 0.46, transform=hdr.transAxes,
                                    fc="white" if active else "#1D3F66", ec="none"))
        hdr.text(x + w / 2, 0.49, TABS[i], ha="center", va="center", fontsize=8,
                 color=NAVY if active else "#C9D5E5", weight="bold" if active else "normal")
    # slicer bar
    sl = fig.add_axes([0.01, 0.865, 0.98, 0.04]); sl.set_axis_off()
    for j, (lab, val) in enumerate([("Date", "01 Jan 2025 – 30 Jun 2026"), ("Client", "All"),
                                    ("Channel", "All"), ("Country", "All"), ("Objective", "All")]):
        x0 = j * 0.2
        sl.add_patch(plt.Rectangle((x0, 0.1), 0.19, 0.8, transform=sl.transAxes, fc=CARD, ec=BORDER))
        sl.text(x0 + 0.008, 0.5, f"{lab}:", va="center", fontsize=8.5, color=MUTED)
        sl.text(x0 + 0.008 + 0.0065 * (len(lab) + 2), 0.5, val, va="center", fontsize=8.5, color=INK)
        sl.text(x0 + 0.18, 0.5, "▾", va="center", ha="right", fontsize=9, color=MUTED)
    fig.text(0.99, 0.006, "Preview rendered from the project dataset · fictional data",
             ha="right", fontsize=7, color=MUTED)
    return fig


def panel(fig, rect, title=None):
    ax = fig.add_axes(rect)
    ax.set_facecolor(CARD)
    for s in ax.spines.values():
        s.set_visible(False)
    bg = FancyBboxPatch((rect[0] - 0.006, rect[1] - 0.045), rect[2] + 0.012, rect[3] + 0.085,
                        boxstyle="round,pad=0,rounding_size=0.006", transform=fig.transFigure,
                        fc=CARD, ec=BORDER, lw=1, zorder=-10)
    fig.patches.append(bg)
    if title:
        ax.set_title(title)
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.tick_params(length=0)
    return ax


def card(fig, rect, label, value, foot=None, foot_color=MUTED):
    ax = fig.add_axes(rect); ax.set_axis_off()
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fc=CARD, ec=BORDER))
    ax.add_patch(plt.Rectangle((0, 0.12), 0.018, 0.76, color=BLUE, transform=ax.transAxes))
    ax.text(0.09, 0.74, label.upper(), fontsize=8, color=INK2, weight="bold", va="center")
    ax.text(0.09, 0.42, value, fontsize=19, color=INK, weight="bold", va="center")
    if foot:
        ax.text(0.09, 0.14, foot, fontsize=7.8, color=foot_color, va="center")


def hbar(ax, labels, values, colors, fmt, sort=True):
    s = pd.Series(values, index=labels)
    if sort:
        s = s.sort_values()
    cols = colors if isinstance(colors, str) else [colors[l] if isinstance(colors, dict) else colors for l in s.index]
    ax.barh(s.index, s.values, color=cols, height=0.62, edgecolor=CARD, linewidth=2)
    ax.grid(axis="y", visible=False); ax.grid(axis="x", color=GRID)
    span = s.abs().max()
    for y, v in enumerate(s.values):
        ax.text(v + span * 0.015 if v >= 0 else v - span * 0.015, y, fmt(v), va="center",
                ha="left" if v >= 0 else "right", fontsize=8, color=INK2)
    ax.set_xlim(min(0, s.min() * 1.25), s.max() * 1.18)
    return s


def table(ax, frame, col_w, fmts, color_cols=None, fs=8.2):
    ax.set_axis_off(); ax.grid(False)
    n = len(frame)
    rh = 1 / (n + 1)
    xs = np.cumsum([0] + col_w[:-1])
    ax.add_patch(plt.Rectangle((0, 1 - rh), 1, rh, color=NAVY, transform=ax.transAxes))
    for x, c, w in zip(xs, frame.columns, col_w):
        right = c in fmts
        ax.text(x + (w - 0.008 if right else 0.008), 1 - rh / 2, c, color="white", weight="bold",
                fontsize=fs, va="center", ha="right" if right else "left", transform=ax.transAxes)
    for i, (_, row) in enumerate(frame.iterrows()):
        y = 1 - rh * (i + 1.5)
        if i % 2:
            ax.add_patch(plt.Rectangle((0, y - rh / 2), 1, rh, color="#F7F9FC", transform=ax.transAxes))
        for x, c, w in zip(xs, frame.columns, col_w):
            v = row[c]
            right = c in fmts
            txt = fmts[c](v) if right else str(v)
            color = INK
            if color_cols and c in color_cols:
                color = color_cols[c](v)
            ax.text(x + (w - 0.008 if right else 0.008), y, txt, fontsize=fs, va="center",
                    ha="right" if right else "left", color=color, transform=ax.transAxes)


T = kpis(df)
monthly = df.set_index("Date").resample("MS")[SUMS].sum()
monthly["ROI"] = (monthly.Revenue - monthly.Spend) / monthly.Spend
monthly["CPA"] = monthly.Spend / monthly.Conversions
mlab = [d.strftime("%b\n%y") if d.month in (1, 7) else d.strftime("%b") for d in monthly.index]
h1_25 = kpis(df[(df.Date >= "2025-01-01") & (df.Date <= "2025-06-30")])
h1_26 = kpis(df[(df.Date >= "2026-01-01") & (df.Date <= "2026-06-30")])
yoy = lambda k: (h1_26[k] - h1_25[k]) / h1_25[k]


def arrow(v, good_up=True):
    up = v >= 0
    c = GOOD if up == good_up else BAD
    return f"{'▲' if up else '▼'} {abs(v):.1%} H1'26 vs H1'25", c


# =============================================================================
# 1. EXECUTIVE OVERVIEW
# =============================================================================
fig = page(0, "Headline KPIs for all clients, channels and markets")
cards = [("Total Spend", money(T["Spend"], 2), *arrow(yoy("Spend"))),
         ("Impressions", num(T["Impressions"]), *arrow(yoy("Impressions"))),
         ("Clicks", num(T["Clicks"], 2), *arrow(yoy("Clicks"))),
         ("Conversions", num(T["Conversions"]), *arrow(yoy("Conversions"))),
         ("CTR", f"{T['CTR']:.2%}", f"CPC ${T['CPC']:.2f}", MUTED),
         ("CPA", f"${T['CPA']:.2f}", *arrow(yoy("CPA"), good_up=False)),
         ("ROI", f"{T['ROI']:.1%}", f"ROAS {T['ROAS']:.2f}x · Rev {money(T['Revenue'])}", MUTED)]
w = 0.98 / 7
for i, c in enumerate(cards):
    card(fig, [0.01 + i * w + 0.002, 0.715, w - 0.008, 0.125], *c)

ax = panel(fig, [0.045, 0.40, 0.56, 0.235], "Monthly Spend vs Revenue")
x = np.arange(len(monthly))
ax.plot(x, monthly.Revenue, color=BLUE, lw=2, marker="o", ms=3.5, label="Revenue")
ax.plot(x, monthly.Spend, color=ORANGE, lw=2, marker="o", ms=3.5, label="Spend")
ax.fill_between(x, monthly.Spend, monthly.Revenue, color=BLUE, alpha=0.06)
ax.set_xticks(x, mlab, fontsize=7.5); ax.yaxis.set_major_formatter(fmt_money)
ax.legend(loc="upper left", frameon=False, ncol=2, fontsize=8)
ax.set_xlim(-0.5, len(x) - 0.5); ax.set_ylim(0, monthly.Revenue.max() * 1.15)

g = agg("ChannelGroup").reindex(GROUPS)
ax = panel(fig, [0.70, 0.40, 0.285, 0.235], "Spend by Channel")
s = hbar(ax, GROUPS, g.Spend.values, GCOL, lambda v: f"{money(v)} · {v / T['Spend']:.0%}")
ax.xaxis.set_major_formatter(fmt_money)

c = agg("Client")
ax = panel(fig, [0.105, 0.06, 0.30, 0.255], "ROI by Client")
s = c.ROI.sort_values()
ax.barh(s.index, s.values, color=[roi_color(v) for v in s.values], height=0.62)
ax.grid(axis="y", visible=False); ax.grid(axis="x", color=GRID)
ax.axvline(0, color=INK2, lw=0.8); ax.xaxis.set_major_formatter(fmt_pct)
for yy, v in enumerate(s.values):
    ax.text(v + (0.06 if v >= 0 else -0.06), yy, f"{v:.0%}", va="center",
            ha="left" if v >= 0 else "right", fontsize=8, color=INK2)
ax.set_xlim(s.min() - 0.5, s.max() * 1.2)

ax = panel(fig, [0.45, 0.06, 0.25, 0.255], "Conversion Funnel")
ax.set_axis_off()
stages = [("Impressions", T["Impressions"], None), ("Clicks", T["Clicks"], T["CTR"]),
          ("Leads", T["Leads"], T["Leads"] / T["Clicks"]),
          ("Conversions", T["Conversions"], T["Conversions"] / T["Leads"])]
widths = [1.0, 0.82, 0.64, 0.48]
for i, ((lab, v, r), wd) in enumerate(zip(stages, widths)):
    yy = 0.84 - i * 0.235
    wd = wd * 0.86
    ax.add_patch(FancyBboxPatch((0.45 - wd / 2, yy - 0.08), wd, 0.16,
                                boxstyle="round,pad=0,rounding_size=0.02", fc=SERIES[0],
                                alpha=1 - i * 0.18, ec="none", transform=ax.transAxes))
    ax.text(0.45, yy, f"{lab}  {num(v, 2)}", ha="center", va="center", color="white",
            fontsize=9, weight="bold", transform=ax.transAxes)
    if r is not None:
        ax.text(0.45 + wd / 2 + 0.015, yy, f"{r:.2%}", fontsize=7.5, va="center",
                color=INK2, transform=ax.transAxes, ha="left")

ax = panel(fig, [0.735, 0.06, 0.25, 0.255], "Highlights")
ax.set_axis_off()
best_ch = g.ROI.idxmax(); worst_cl = c.ROI.idxmin(); top_cl = c.Revenue.idxmax()
items = [("Net profit", money(T["Revenue"] - T["Spend"], 2)),
         ("Top channel by ROI", f"{best_ch} ({g.ROI.max():.0%})"),
         ("Top client by revenue", top_cl),
         ("Lowest ROI client", f"{worst_cl} ({c.ROI.min():.0%})"),
         ("Active campaigns", f"{df.CampaignKey.nunique()} across {df.ClientKey.nunique()} clients"),
         ("Cost per lead", f"${T['CPL']:.2f}")]
for i, (k, v) in enumerate(items):
    yy = 0.92 - i * 0.165
    ax.text(0.02, yy, k, fontsize=8, color=MUTED, transform=ax.transAxes)
    ax.text(0.02, yy - 0.075, v, fontsize=9.5, color=INK, weight="bold", transform=ax.transAxes)
fig.savefig(OUT / "01_executive_overview.png", facecolor=PAGE); plt.close(fig)

# =============================================================================
# 2. CAMPAIGN PERFORMANCE
# =============================================================================
fig = page(1, "Spend, clicks, conversions, CPA and ROI by campaign")
cm = agg("Campaign")
top = cm.sort_values("Spend", ascending=False)
ax = panel(fig, [0.20, 0.50, 0.24, 0.31], "Campaign-wise Spend (Top 12)")
s = top.Spend.head(12)
hbar(ax, s.index, s.values, BLUE, money)
ax.tick_params(axis="y", labelsize=7.2); ax.xaxis.set_major_formatter(fmt_money)

ax = panel(fig, [0.50, 0.50, 0.225, 0.31], "Clicks by Week")
wk = df.set_index("Date").resample("W-MON")[["Clicks", "Conversions"]].sum().iloc[1:-1]  # full weeks only
ax.plot(wk.index, wk.Clicks, color=BLUE, lw=1.6)
ax.yaxis.set_major_formatter(fmt_num); ax.set_ylabel("Clicks", fontsize=8)
ax.tick_params(axis="x", labelsize=7.5)
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %y"))
ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax = panel(fig, [0.765, 0.50, 0.22, 0.31], "Conversions by Week")
ax.plot(wk.index, wk.Conversions, color=ORANGE, lw=1.6)
ax.yaxis.set_major_formatter(fmt_num); ax.set_ylabel("Conversions", fontsize=8)
ax.tick_params(axis="x", labelsize=7.5)
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%b %y"))
ax.xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator(bymonth=[1, 4, 7, 10]))

ax = panel(fig, [0.045, 0.06, 0.26, 0.33], "CPA vs ROI (each dot = campaign)")
ax.scatter(cm.CPA, cm.ROI, s=np.sqrt(cm.Spend) / 3, color=[roi_color(r) for r in cm.ROI],
           alpha=0.85, edgecolor=CARD, linewidth=1.5)
ax.axhline(0, color=INK2, lw=0.8); ax.axvline(T["CPA"], color=MUTED, lw=0.8, ls="--")
ax.text(T["CPA"], ax.get_ylim()[1] * 0.95, f" avg CPA ${T['CPA']:.0f}", fontsize=7.5, color=MUTED)
ax.yaxis.set_major_formatter(fmt_pct); ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.set_xlabel("CPA", fontsize=8); ax.set_ylabel("ROI", fontsize=8); ax.grid(axis="x", color=GRID)

ax = panel(fig, [0.35, 0.06, 0.635, 0.33], "Campaign Scorecard (Top 10 by Spend)")
t = top.head(10).reset_index()[["Campaign", "Spend", "Clicks", "Conversions", "CTR", "CPA", "Revenue", "ROI"]]
table(ax, t, [0.33, 0.09, 0.09, 0.1, 0.07, 0.08, 0.11, 0.13],
      {"Spend": money, "Clicks": num, "Conversions": num, "CTR": lambda v: f"{v:.2%}",
       "CPA": lambda v: f"${v:,.2f}", "Revenue": money, "ROI": lambda v: f"{v:.1%}"},
      {"ROI": roi_color})
fig.savefig(OUT / "02_campaign_performance.png", facecolor=PAGE); plt.close(fig)

# =============================================================================
# 3. CHANNEL ANALYSIS
# =============================================================================
fig = page(2, "Google · Meta · LinkedIn · YouTube · Display · Other channels")
g = agg("ChannelGroup").reindex(GROUPS)
for i, (metric, title, fm) in enumerate([("Spend", "Spend", money), ("CTR", "CTR", lambda v: f"{v:.2%}"),
                                         ("CPA", "CPA", lambda v: f"${v:,.0f}"),
                                         ("ROI", "ROI", lambda v: f"{v:.0%}")]):
    ax = panel(fig, [0.045 + i * 0.245, 0.50, 0.19, 0.30], f"{title} by Channel")
    ax.bar(GROUPS, g[metric], color=[GCOL[k] for k in GROUPS], width=0.62, edgecolor=CARD, linewidth=2)
    for xx, v in enumerate(g[metric]):
        ax.text(xx, v, fm(v), ha="center", va="bottom", fontsize=7.5, color=INK2)
    ax.tick_params(axis="x", labelsize=7.5, rotation=0)
    ax.yaxis.set_major_formatter({"Spend": fmt_money, "CTR": mt.FuncFormatter(lambda v, _: f"{v:.1%}"),
                                  "CPA": mt.FuncFormatter(lambda v, _: f"${v:,.0f}"), "ROI": fmt_pct}[metric])
    ax.set_ylim(min(0, g[metric].min() * 1.2), g[metric].max() * 1.15)

ax = panel(fig, [0.045, 0.06, 0.44, 0.33], "Monthly Spend Mix by Channel")
mc = df.pivot_table(index=pd.Grouper(key="Date", freq="MS"), columns="ChannelGroup",
                    values="Spend", aggfunc="sum").reindex(columns=GROUPS).fillna(0)
ax.stackplot(np.arange(len(mc)), *[mc[k] for k in GROUPS], colors=SERIES, labels=GROUPS,
             edgecolor=CARD, linewidth=0.8)
ax.set_xticks(np.arange(len(mc)), mlab, fontsize=7.5); ax.yaxis.set_major_formatter(fmt_money)
ax.legend(loc="upper left", frameon=False, ncol=6, fontsize=7.5, bbox_to_anchor=(0, 1.02))
ax.set_xlim(0, len(mc) - 1); ax.set_ylim(0, mc.sum(axis=1).max() * 1.18)

ax = panel(fig, [0.53, 0.06, 0.455, 0.33], "Channel Matrix")
cc = agg(["ChannelGroup", "Channel"]).reset_index()
cc["Grp"] = cc.ChannelGroup.map({k: i for i, k in enumerate(GROUPS)})
cc = cc.sort_values(["Grp", "Spend"], ascending=[True, False])
t = cc[["ChannelGroup", "Channel", "Spend", "Impressions", "Clicks", "Conversions", "CTR", "CPA", "ROI"]]
t = t.rename(columns={"ChannelGroup": "Group"})
table(ax, t, [0.09, 0.17, 0.1, 0.12, 0.1, 0.12, 0.08, 0.1, 0.12],
      {"Spend": money, "Impressions": num, "Clicks": num, "Conversions": num,
       "CTR": lambda v: f"{v:.2%}", "CPA": lambda v: f"${v:,.2f}", "ROI": lambda v: f"{v:.0%}"},
      {"ROI": roi_color}, fs=7.8)
fig.savefig(OUT / "03_channel_analysis.png", facecolor=PAGE); plt.close(fig)

# =============================================================================
# 4. CLIENT ANALYSIS
# =============================================================================
fig = page(3, "Client-wise performance, budget pacing, contribution and CPA")
c = agg("Client")
bud = cp.merge(cl, on="ClientKey").groupby("Client").Budget.sum()
c["Budget"] = bud
c["Util"] = c.Spend / c.Budget
order = c.sort_values("Spend", ascending=False).index
ax = panel(fig, [0.045, 0.50, 0.44, 0.30], "Budget vs Spend by Client")
xx = np.arange(len(order))
ax.bar(xx - 0.2, c.loc[order, "Budget"], width=0.38, color="#9DB9E3", label="Budget", edgecolor=CARD)
ax.bar(xx + 0.2, c.loc[order, "Spend"], width=0.38, color=BLUE, label="Spend", edgecolor=CARD)
for i, k in enumerate(order):
    u = c.loc[k, "Util"]
    ax.text(i + 0.2, c.loc[k, "Spend"], f"{u:.0%}", ha="center", va="bottom", fontsize=7.3,
            color=BAD if u > 1.05 else (WARN if u < 0.9 else GOOD), weight="bold")
ax.set_xticks(xx, [k.replace(" ", "\n", 1) for k in order], fontsize=7.2)
ax.yaxis.set_major_formatter(fmt_money); ax.legend(frameon=False, fontsize=8, loc="upper right")

ax = panel(fig, [0.555, 0.50, 0.18, 0.30], "Conversion Contribution %")
share = (c.Conversions / c.Conversions.sum()).sort_values()
share.index = [k.split()[0] for k in share.index]
hbar(ax, share.index, share.values, BLUE, lambda v: f"{v:.1%}")
ax.tick_params(axis="y", labelsize=7.2); ax.xaxis.set_major_formatter(fmt_pct)

ax = panel(fig, [0.81, 0.50, 0.175, 0.30], "CPA vs Benchmark")
s = c.CPA.sort_values()
ax.barh(s.index, s.values, color=[BAD if v > T["CPA"] else GOOD for v in s.values], height=0.62)
ax.axvline(T["CPA"], color=INK, lw=1, ls="--")
ax.text(T["CPA"], len(s) - 0.35, f" avg ${T['CPA']:.0f}", fontsize=7.5, color=INK)
ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
for yy, v in enumerate(s.values):
    ax.text(v + 2, yy, f"${v:,.0f}", va="center", fontsize=7.5, color=INK2,
            bbox=dict(fc=CARD, ec="none", pad=0.6))
ax.set_yticklabels([]); ax.grid(axis="y", visible=False); ax.grid(axis="x", color=GRID)
ax.set_xlim(0, s.max() * 1.25)
for yy, k in enumerate(s.index):
    ax.text(-1, yy, "", fontsize=1)
ax.set_yticks(range(len(s)), [k.split()[0] for k in s.index], fontsize=7.2)

ax = panel(fig, [0.045, 0.06, 0.94, 0.33], "Client Performance Summary")
t = c.loc[order].reset_index().merge(cl[["Client", "Industry", "AccountManager"]], on="Client")
t["Conv. Share"] = t.Conversions / t.Conversions.sum()
t["Status"] = np.where(t.Util > 1.05, "Over budget", np.where(t.Util < 0.9, "Under-paced", "On track"))
t = t[["Client", "Industry", "Budget", "Spend", "Util", "Status", "Clicks", "Leads", "Conversions",
       "Conv. Share", "CPA", "Revenue", "ROI"]].rename(columns={"Util": "Utilization"})
table(ax, t, [0.13, 0.07, 0.075, 0.075, 0.075, 0.085, 0.07, 0.065, 0.075, 0.07, 0.06, 0.08, 0.07],
      {"Budget": money, "Spend": money, "Utilization": lambda v: f"{v:.0%}", "Clicks": num,
       "Leads": num, "Conversions": num, "Conv. Share": lambda v: f"{v:.1%}",
       "CPA": lambda v: f"${v:,.2f}", "Revenue": money, "ROI": lambda v: f"{v:.1%}"},
      {"ROI": roi_color, "Status": lambda v: {"Over budget": BAD, "Under-paced": WARN}.get(v, GOOD),
       "CPA": lambda v: BAD if v > T["CPA"] else INK})
fig.savefig(OUT / "04_client_analysis.png", facecolor=PAGE); plt.close(fig)

# =============================================================================
# 5. GEOGRAPHICAL ANALYSIS
# =============================================================================
fig = page(4, "Spend, leads, conversions and ROI by country and state")
co = agg("Country").sort_values("Spend", ascending=False)
ax = panel(fig, [0.045, 0.50, 0.27, 0.30], "Spend & Revenue by Country")
xx = np.arange(len(co))
ax.bar(xx - 0.2, co.Spend, width=0.38, color=ORANGE, label="Spend", edgecolor=CARD)
ax.bar(xx + 0.2, co.Revenue, width=0.38, color=BLUE, label="Revenue", edgecolor=CARD)
ax.set_xticks(xx, [k.replace("United ", "U. ") for k in co.index], fontsize=7.5)
ax.yaxis.set_major_formatter(fmt_money); ax.legend(frameon=False, fontsize=8)

ax = panel(fig, [0.37, 0.50, 0.17, 0.30], "ROI by Country")
s = co.ROI.sort_values()
ax.barh([k.replace("United ", "U. ") for k in s.index], s.values,
        color=[roi_color(v) for v in s.values], height=0.6)
for yy, v in enumerate(s.values):
    ax.text(v + 0.05, yy, f"{v:.0%}", va="center", fontsize=7.5, color=INK2)
ax.set_xlim(0, s.max() * 1.3); ax.xaxis.set_major_formatter(fmt_pct)
ax.grid(axis="y", visible=False); ax.grid(axis="x", color=GRID)

ax = panel(fig, [0.595, 0.50, 0.39, 0.30], "Leads & Conversions by Country")
xx = np.arange(len(co))
ax.bar(xx - 0.2, co.Leads, width=0.38, color="#9DB9E3", label="Leads", edgecolor=CARD)
ax.bar(xx + 0.2, co.Conversions, width=0.38, color=BLUE, label="Conversions", edgecolor=CARD)
for i in range(len(co)):
    ax.text(i + 0.2, co.Conversions.iloc[i], num(co.Conversions.iloc[i]), ha="center",
            va="bottom", fontsize=7.2, color=INK2)
ax.set_xticks(xx, co.index, fontsize=7.5); ax.yaxis.set_major_formatter(fmt_num)
ax.legend(frameon=False, fontsize=8)

st = agg(["Country", "State"]).reset_index().sort_values("Spend", ascending=False)
ax = panel(fig, [0.09, 0.06, 0.27, 0.33], "Spend by State (Top 12)")
s = st.head(12).set_index("State").Spend
hbar(ax, s.index, s.values, BLUE, money)
ax.tick_params(axis="y", labelsize=7.5); ax.xaxis.set_major_formatter(fmt_money)
ax.xaxis.set_major_locator(mt.MaxNLocator(4))

ax = panel(fig, [0.39, 0.06, 0.595, 0.33], "State / Country Detail")
t = st[["Country", "State", "Spend", "Leads", "Conversions", "CPA", "Revenue", "ROI"]].head(12)
table(ax, t, [0.17, 0.17, 0.11, 0.1, 0.12, 0.09, 0.12, 0.12],
      {"Spend": money, "Leads": num, "Conversions": num, "CPA": lambda v: f"${v:,.2f}",
       "Revenue": money, "ROI": lambda v: f"{v:.1%}"}, {"ROI": roi_color}, fs=7.8)
fig.savefig(OUT / "05_geographical_analysis.png", facecolor=PAGE); plt.close(fig)

# =============================================================================
# 6. DETAILED DATA TABLE
# =============================================================================
fig = page(5, "Row-level drill-through table · export to Excel/CSV from the visual menu")
ax = panel(fig, [0.02, 0.07, 0.96, 0.725], "Campaign Performance Detail (latest rows, sorted by Date, Spend)")
d = (df.sort_values(["Date", "Spend"], ascending=[False, False])
       .head(26)[["Date", "Client", "Campaign", "Channel", "Impressions", "Clicks", "Spend",
                  "Conversions", "Revenue"]].copy())
d["Date"] = d.Date.dt.strftime("%d-%b-%Y")
tot = df[SUMS].sum()
table(ax, d, [0.08, 0.15, 0.27, 0.11, 0.09, 0.07, 0.08, 0.08, 0.07],
      {"Impressions": lambda v: f"{v:,.0f}", "Clicks": lambda v: f"{v:,.0f}",
       "Spend": lambda v: f"${v:,.2f}", "Conversions": lambda v: f"{v:,.0f}",
       "Revenue": lambda v: f"${v:,.2f}"}, fs=8)
fig.text(0.025, 0.035, f"Total ({len(df):,} rows):   Impressions {tot.Impressions:,.0f}   ·   Clicks "
         f"{tot.Clicks:,.0f}   ·   Spend \\${tot.Spend:,.2f}   ·   Conversions {tot.Conversions:,.0f}"
         f"   ·   Revenue \\${tot.Revenue:,.2f}", fontsize=8.5, color=INK, weight="bold")
fig.savefig(OUT / "06_detailed_data_table.png", facecolor=PAGE); plt.close(fig)

print("KPI summary:", {k: round(v, 4) for k, v in T.items()})
print("Saved previews to", OUT)
