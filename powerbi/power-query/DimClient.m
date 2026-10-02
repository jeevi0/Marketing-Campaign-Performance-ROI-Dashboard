let
    Source   = Csv.Document(File.Contents(DataFolderPath & "dim_client.csv"),
                   [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                   {"ClientKey", Int64.Type}, {"Client", type text}, {"Industry", type text},
                   {"Segment", type text}, {"AccountManager", type text}}, "en-US")
in
    Typed
