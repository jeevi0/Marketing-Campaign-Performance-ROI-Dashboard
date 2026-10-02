let
    Source   = Csv.Document(File.Contents(DataFolderPath & "dim_campaign.csv"),
                   [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                   {"CampaignKey", Int64.Type}, {"CampaignCode", type text}, {"Campaign", type text},
                   {"ClientKey", Int64.Type}, {"Objective", type text}, {"Theme", type text},
                   {"StartDate", type date}, {"EndDate", type date}, {"Budget", Currency.Type},
                   {"Status", type text}}, "en-US"),
    // Planned flight length - used by the pro-rated budget measure
    AddDays  = Table.AddColumn(Typed, "FlightDays",
                   each Duration.Days([EndDate] - [StartDate]) + 1, Int64.Type)
in
    AddDays
