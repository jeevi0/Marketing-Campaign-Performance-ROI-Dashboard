// FactPerformance - grain: Date x Campaign x Channel x Geography (one row per day)
let
    Source   = Csv.Document(
                   File.Contents(DataFolderPath & "fact_campaign_performance.csv"),
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
