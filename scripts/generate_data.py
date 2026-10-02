"""
Marketing Campaign Performance & ROI Dashboard - synthetic data generator
=========================================================================

Creates a realistic, fully fictional multi-client / multi-channel digital
marketing dataset and writes it as a star schema (for Power BI) plus one flat
file (for quick inspection in Excel).

Run:
    pip install pandas numpy
    python scripts/generate_data.py

Outputs (relative to repo root):
    data/model/dim_client.csv
    data/model/dim_campaign.csv
    data/model/dim_channel.csv
    data/model/dim_geography.csv
    data/model/fact_campaign_performance.csv
    data/raw/marketing_campaign_performance_flat.csv

All company names are invented. Currency = USD. Seeded, so output is reproducible.
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
START = pd.Timestamp("2025-01-01")
END = pd.Timestamp("2026-06-30")

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "data" / "model"
RAW = ROOT / "data" / "raw"

rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------
# Channel benchmarks: CPM (USD), CTR, click->lead rate, lead->conversion rate
CHANNELS = [
    # key, channel,           group,      type,          cpm,  ctr,    lead_rt, l2c
    (1, "Google Ads",        "Google",   "Search",       60.0, 0.0350, 0.080, 0.30),
    (2, "Meta Ads",          "Meta",     "Social",       12.0, 0.0110, 0.060, 0.25),
    (3, "LinkedIn Ads",      "LinkedIn", "Social",       45.0, 0.0055, 0.100, 0.25),
    (4, "YouTube Ads",       "YouTube",  "Video",        11.0, 0.0045, 0.045, 0.25),
    (5, "Display Network",   "Display",  "Programmatic",  4.0, 0.0030, 0.035, 0.22),
    (6, "Email Marketing",   "Other",    "Owned",        25.0, 0.0250, 0.060, 0.30),
    (7, "X (Twitter) Ads",   "Other",    "Social",        7.0, 0.0080, 0.030, 0.22),
    (8, "Affiliate",         "Other",    "Partner",      15.0, 0.0140, 0.070, 0.30),
]
dim_channel = pd.DataFrame(
    CHANNELS,
    columns=["ChannelKey", "Channel", "ChannelGroup", "ChannelType",
             "_cpm", "_ctr", "_lead_rate", "_lead_to_conv"],
)
group_order = {"Google": 1, "Meta": 2, "LinkedIn": 3, "YouTube": 4, "Display": 5, "Other": 6}
dim_channel["ChannelGroupSort"] = dim_channel["ChannelGroup"].map(group_order)

GEOS = [
    # key, country,        state,              region,         cpm_mult, aov_mult
    (1,  "India",          "Maharashtra",      "APAC",          0.35, 0.45),
    (2,  "India",          "Karnataka",        "APAC",          0.35, 0.45),
    (3,  "India",          "Delhi",            "APAC",          0.36, 0.45),
    (4,  "India",          "Tamil Nadu",       "APAC",          0.32, 0.42),
    (5,  "India",          "Telangana",        "APAC",          0.33, 0.43),
    (6,  "India",          "Gujarat",          "APAC",          0.31, 0.42),
    (7,  "United States",  "California",       "North America", 1.25, 1.20),
    (8,  "United States",  "New York",         "North America", 1.30, 1.25),
    (9,  "United States",  "Texas",            "North America", 1.05, 1.05),
    (10, "United States",  "Illinois",         "North America", 1.00, 1.00),
    (11, "United Kingdom", "England",          "EMEA",          1.05, 1.05),
    (12, "United Kingdom", "Scotland",         "EMEA",          0.95, 0.95),
    (13, "UAE",            "Dubai",            "EMEA",          0.85, 1.00),
    (14, "Singapore",      "Singapore",        "APAC",          0.90, 1.00),
    (15, "Australia",      "New South Wales",  "APAC",          1.00, 1.05),
    (16, "Australia",      "Victoria",         "APAC",          0.95, 1.00),
]
dim_geo = pd.DataFrame(
    GEOS, columns=["GeoKey", "Country", "State", "Region", "_cpm_mult", "_aov_mult"]
)
dim_geo["CountryCode"] = dim_geo["Country"].map(
    {"India": "IN", "United States": "US", "United Kingdom": "GB",
     "UAE": "AE", "Singapore": "SG", "Australia": "AU"}
)

# Clients: industry, revenue per conversion (AOV / deal value), channel mix, markets
CLIENTS = [
    (1, "NovaTech Solutions",   "B2B SaaS",          "Enterprise",  260.0,
     {1: .35, 3: .35, 4: .10, 5: .10, 6: .10},            [7, 8, 9, 11, 14, 2]),
    (2, "UrbanThreads Apparel", "E-commerce",        "Mid-Market", 150.0,
     {1: .25, 2: .40, 4: .10, 5: .10, 8: .15},            [1, 2, 3, 4, 7, 9]),
    (3, "GreenLeaf Organics",   "FMCG",              "Mid-Market",  45.0,
     {1: .20, 2: .35, 4: .25, 5: .20},                    [1, 2, 3, 6, 13]),
    (4, "Apex Realty Group",    "Real Estate",       "Enterprise",  255.0,
     {1: .40, 2: .30, 4: .15, 5: .15},                    [1, 3, 5, 13]),
    (5, "BrightPath EdTech",    "Education",         "SMB",        170.0,
     {1: .30, 2: .30, 4: .20, 6: .10, 7: .10},            [1, 2, 4, 5, 3, 14]),
    (6, "MediCare Plus Clinics","Healthcare",        "Mid-Market", 115.0,
     {1: .50, 2: .25, 5: .15, 6: .10},                    [1, 2, 4, 5]),
    (7, "SwiftMove Logistics",  "Logistics",         "Enterprise",  325.0,
     {1: .30, 3: .40, 5: .10, 6: .10, 7: .10},            [7, 9, 10, 11, 12, 15, 16]),
    (8, "FinEdge Capital",      "BFSI",              "Enterprise",  205.0,
     {1: .35, 2: .20, 3: .20, 4: .15, 8: .10},            [1, 3, 2, 8, 11, 14, 15]),
]
dim_client = pd.DataFrame(
    [(c[0], c[1], c[2], c[3]) for c in CLIENTS],
    columns=["ClientKey", "Client", "Industry", "Segment"],
)
dim_client["AccountManager"] = ["Priya Nair", "Arjun Mehta", "Sara Thomas", "Rahul Iyer",
                                "Priya Nair", "Sara Thomas", "Arjun Mehta", "Rahul Iyer"]

OBJECTIVES = {
    "Lead Generation": dict(rev_mult=1.00, ctr_mult=1.00, conv_mult=1.10),
    "Sales / Conversions": dict(rev_mult=1.15, ctr_mult=1.05, conv_mult=1.20),
    "Brand Awareness": dict(rev_mult=0.70, ctr_mult=0.75, conv_mult=0.55),
    "Retargeting": dict(rev_mult=1.10, ctr_mult=1.40, conv_mult=1.60),
    "Product Launch": dict(rev_mult=0.90, ctr_mult=1.10, conv_mult=0.90),
}
THEMES = ["Q1 Kickoff", "Summer Sale", "Festive Season", "Year-End Push", "Lead Sprint",
          "New Launch", "Webinar Series", "Brand Lift", "Retargeting Boost", "Spring Promo"]

# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------
campaign_rows, campaign_meta = [], {}
ckey = 1
total_days = (END - START).days + 1
for client_key, client, industry, seg, aov, mix, markets in CLIENTS:
    n_campaigns = int(rng.integers(3, 6))
    themes = ["Always-On"] + list(rng.choice(THEMES, size=n_campaigns, replace=False))
    for theme in themes:
        always_on = theme == "Always-On"
        objective = "Lead Generation" if always_on else rng.choice(list(OBJECTIVES), p=[.32, .25, .15, .15, .13])
        duration = total_days if always_on else int(rng.integers(45, 240))
        start = START + pd.Timedelta(days=int(rng.integers(0, total_days - duration + 1)))
        end = start + pd.Timedelta(days=duration - 1)
        chans = list(mix)
        n_ch = min(len(chans), int(rng.integers(2, 5)))
        p = np.array([mix[c] for c in chans]); p = p / p.sum()
        chosen_ch = sorted(rng.choice(chans, size=n_ch, replace=False, p=p).tolist())
        n_geo = min(len(markets), int(rng.integers(2, 6)))
        chosen_geo = sorted(rng.choice(markets, size=n_geo, replace=False).tolist())
        daily_budget = {"Enterprise": 2400, "Mid-Market": 1300, "SMB": 650}[seg] * rng.uniform(.6, 1.5)
        if always_on:                                  # lower, steady baseline budget
            daily_budget *= 0.45
        budget = round(daily_budget * duration, -2)
        pacing = rng.uniform(0.82, 1.08)          # actual spend / budget
        quality = rng.lognormal(0, 0.25)           # creative/targeting quality
        code = f"CMP-{client_key:02d}{ckey:03d}"
        name = f"{client.split()[0]} | {theme} | {objective.split(' /')[0]}"
        campaign_rows.append((ckey, code, name, client_key, objective, theme,
                              start.date(), end.date(), budget))
        campaign_meta[ckey] = dict(client_key=client_key, aov=aov, mix=mix, chans=chosen_ch,
                                   geos=chosen_geo, start=start, end=end, budget=budget,
                                   pacing=pacing, quality=quality, objective=objective)
        ckey += 1

dim_campaign = pd.DataFrame(
    campaign_rows,
    columns=["CampaignKey", "CampaignCode", "Campaign", "ClientKey", "Objective",
             "Theme", "StartDate", "EndDate", "Budget"],
)
dim_campaign["Status"] = np.where(pd.to_datetime(dim_campaign["EndDate"]) >= END,
                                  "Active", "Completed")

# ---------------------------------------------------------------------------
# Fact table (grain: Date x Campaign x Channel x Geography)
# ---------------------------------------------------------------------------
ch_idx = dim_channel.set_index("ChannelKey")
geo_idx = dim_geo.set_index("GeoKey")
dow_factor = np.array([1.05, 1.08, 1.06, 1.04, 0.98, 0.88, 0.85])   # Mon..Sun
month_factor = {1: .90, 2: .92, 3: 1.0, 4: .97, 5: .98, 6: .95, 7: .97, 8: 1.0,
                9: 1.03, 10: 1.12, 11: 1.18, 12: 1.10}               # festive Q4 lift

frames = []
for ck, m in campaign_meta.items():
    dates = pd.date_range(m["start"], m["end"], freq="D")
    n = len(dates)
    ch_w = np.array([m["mix"][c] for c in m["chans"]]); ch_w = ch_w / ch_w.sum()
    geo_w = rng.dirichlet(np.ones(len(m["geos"])) * 3)
    obj = OBJECTIVES[m["objective"]]
    base_daily = m["budget"] * m["pacing"] / n
    season = np.array([dow_factor[d.dayofweek] * month_factor[d.month] for d in dates])
    season = season / season.mean()
    # gentle learning curve: performance improves over first ~3 weeks
    learn = 0.80 + 0.20 * (1 - np.exp(-np.arange(n) / 10))
    for c, cw in zip(m["chans"], ch_w):
        ch = ch_idx.loc[c]
        for g, gw in zip(m["geos"], geo_w):
            geo = geo_idx.loc[g]
            spend = base_daily * cw * gw * season * rng.lognormal(0, 0.18, n)
            cpm = ch["_cpm"] * geo["_cpm_mult"] * rng.lognormal(0, 0.10, n)
            impressions = np.maximum(np.round(spend / cpm * 1000), 0)
            ctr = ch["_ctr"] * obj["ctr_mult"] * m["quality"] ** 0.5 * rng.lognormal(0, 0.15, n)
            clicks = rng.binomial(impressions.astype(np.int64), np.clip(ctr, 0, 0.5))
            lead_rt = ch["_lead_rate"] * obj["conv_mult"] * m["quality"] * learn
            leads = rng.binomial(clicks, np.clip(lead_rt, 0, 0.9))
            conv = rng.binomial(leads, np.clip(ch["_lead_to_conv"] * rng.lognormal(0, .1, n), 0, 1))
            rev_per_conv = m["aov"] * geo["_aov_mult"] * obj["rev_mult"] * rng.lognormal(0, 0.20, n)
            revenue = conv * rev_per_conv
            frames.append(pd.DataFrame({
                "Date": dates.date,
                "CampaignKey": ck,
                "ClientKey": m["client_key"],
                "ChannelKey": c,
                "GeoKey": g,
                "Impressions": impressions.astype(np.int64),
                "Clicks": clicks,
                "Spend": spend.round(2),
                "Leads": leads,
                "Conversions": conv,
                "Revenue": revenue.round(2),
            }))

fact = pd.concat(frames, ignore_index=True)
fact = fact[fact["Impressions"] > 0].sort_values(["Date", "CampaignKey", "ChannelKey", "GeoKey"])
fact.insert(0, "RowID", np.arange(1, len(fact) + 1))

# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------
MODEL.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

public = lambda df: df[[c for c in df.columns if not c.startswith("_")]]
public(dim_client).to_csv(MODEL / "dim_client.csv", index=False)
public(dim_campaign).to_csv(MODEL / "dim_campaign.csv", index=False)
public(dim_channel).to_csv(MODEL / "dim_channel.csv", index=False)
public(dim_geo).to_csv(MODEL / "dim_geography.csv", index=False)
fact.to_csv(MODEL / "fact_campaign_performance.csv", index=False)

flat = (fact
        .merge(dim_client[["ClientKey", "Client", "Industry"]], on="ClientKey")
        .merge(dim_campaign[["CampaignKey", "Campaign", "Objective"]], on="CampaignKey")
        .merge(dim_channel[["ChannelKey", "Channel", "ChannelGroup"]], on="ChannelKey")
        .merge(dim_geo[["GeoKey", "Country", "State"]], on="GeoKey")
        .sort_values("RowID"))
flat = flat[["Date", "Client", "Industry", "Campaign", "Objective", "Channel",
             "ChannelGroup", "Country", "State", "Impressions", "Clicks", "Spend",
             "Leads", "Conversions", "Revenue"]]
flat.to_csv(RAW / "marketing_campaign_performance_flat.csv", index=False)

# Summary
s, r = fact["Spend"].sum(), fact["Revenue"].sum()
print(f"Rows: {len(fact):,} | Campaigns: {len(dim_campaign)} | Clients: {len(dim_client)}")
print(f"Spend ${s:,.0f} | Revenue ${r:,.0f} | ROI {(r - s) / s:.1%} | "
      f"CTR {fact.Clicks.sum() / fact.Impressions.sum():.2%} | CPA ${s / fact.Conversions.sum():,.2f}")
