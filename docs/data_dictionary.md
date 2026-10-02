# Data Dictionary

Period **1 Jan 2025 – 30 Jun 2026** · Currency **USD** · All entities fictional.

## FactPerformance — `fact_campaign_performance.csv` (90,709 rows)
Grain: one row per **Date × Campaign × Channel × State**.

| Column | Type | Description |
|---|---|---|
| RowID | int | Surrogate row id |
| Date | date | Activity date |
| CampaignKey | int | → DimCampaign |
| ClientKey | int | → DimClient |
| ChannelKey | int | → DimChannel |
| GeoKey | int | → DimGeography |
| Impressions | int | Ad impressions served |
| Clicks | int | Ad clicks |
| Spend | decimal | Media cost (USD) |
| Leads | int | Form fills / enquiries attributed to the click |
| Conversions | int | Leads that became customers / purchases |
| Revenue | decimal | Revenue attributed to the conversions (USD) |

Funnel rule: `Impressions ≥ Clicks ≥ Leads ≥ Conversions`.

## DimClient — `dim_client.csv` (8 rows)
| Column | Description |
|---|---|
| ClientKey | Primary key |
| Client | Client name |
| Industry | B2B SaaS, E-commerce, FMCG, Real Estate, Education, Healthcare, Logistics, BFSI |
| Segment | Enterprise / Mid-Market / SMB |
| AccountManager | Agency owner of the account (use for RLS) |

## DimCampaign — `dim_campaign.csv` (39 rows)
| Column | Description |
|---|---|
| CampaignKey | Primary key |
| CampaignCode | Business code, e.g. `CMP-01001` |
| Campaign | `Client | Theme | Objective` |
| ClientKey | Owning client (informational — not related in the model) |
| Objective | Lead Generation, Sales / Conversions, Brand Awareness, Retargeting, Product Launch |
| Theme | Always-On, Festive Season, Summer Sale, … |
| StartDate / EndDate | Planned flight |
| Budget | Planned budget for the full flight (USD) |
| Status | Active (runs to period end) / Completed |
| FlightDays | *Added in Power Query* — EndDate − StartDate + 1 |

## DimChannel — `dim_channel.csv` (8 rows)
| ChannelKey | Channel | ChannelGroup | ChannelType |
|---|---|---|---|
| 1 | Google Ads | Google | Search |
| 2 | Meta Ads | Meta | Social |
| 3 | LinkedIn Ads | LinkedIn | Social |
| 4 | YouTube Ads | YouTube | Video |
| 5 | Display Network | Display | Programmatic |
| 6 | Email Marketing | Other | Owned |
| 7 | X (Twitter) Ads | Other | Social |
| 8 | Affiliate | Other | Partner |

`ChannelGroupSort` keeps the groups in the order above.

## DimGeography — `dim_geography.csv` (16 rows)
| Column | Description |
|---|---|
| GeoKey | Primary key |
| Country | India, United States, United Kingdom, UAE, Singapore, Australia |
| State | State / province / emirate / city-state |
| Region | APAC, North America, EMEA |
| CountryCode | ISO-2 |
| MapLocation | *Added in Power Query* — `State, Country` for map geocoding |

## DimDate — DAX calculated table
Date, Year, Quarter, Year Quarter, Month No, Month, Year Month, YearMonthKey, Week Start (Monday), Weekday, Weekday No, Is Weekend.

## Flat file — `data/raw/marketing_campaign_performance_flat.csv`
The fact table joined to all dimensions (Date, Client, Industry, Campaign, Objective, Channel, ChannelGroup, Country, State, Impressions, Clicks, Spend, Leads, Conversions, Revenue). Handy for Excel or a quick single-table Power BI model.
