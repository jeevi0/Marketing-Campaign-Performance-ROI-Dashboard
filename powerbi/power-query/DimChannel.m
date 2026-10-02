let
    Source   = Csv.Document(File.Contents(DataFolderPath & "dim_channel.csv"),
                   [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                   {"ChannelKey", Int64.Type}, {"Channel", type text}, {"ChannelGroup", type text},
                   {"ChannelType", type text}, {"ChannelGroupSort", Int64.Type}}, "en-US")
    // After load: Column tools > Sort by column: ChannelGroup -> ChannelGroupSort
in
    Typed
