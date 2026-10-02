// OPTIONAL: load the fact table straight from your public GitHub repo instead of a local folder.
// Replace <your-username>. Use the same pattern for the dim_*.csv files.
let
    Url      = "https://raw.githubusercontent.com/<your-username>/Marketing-Campaign-Performance-ROI-Dashboard/main/data/model/fact_campaign_performance.csv",
    Source   = Csv.Document(Web.Contents(Url),
                   [Delimiter = ",", Columns = 12, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                   {"RowID", Int64.Type}, {"Date", type date},
                   {"CampaignKey", Int64.Type}, {"ClientKey", Int64.Type},
                   {"ChannelKey", Int64.Type}, {"GeoKey", Int64.Type},
                   {"Impressions", Int64.Type}, {"Clicks", Int64.Type},
                   {"Spend", Currency.Type}, {"Leads", Int64.Type},
                   {"Conversions", Int64.Type}, {"Revenue", Currency.Type}}, "en-US")
in
    Typed
