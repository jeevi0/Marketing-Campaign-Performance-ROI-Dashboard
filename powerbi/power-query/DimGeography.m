let
    Source   = Csv.Document(File.Contents(DataFolderPath & "dim_geography.csv"),
                   [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                   {"GeoKey", Int64.Type}, {"Country", type text}, {"State", type text},
                   {"Region", type text}, {"CountryCode", type text}}, "en-US"),
    // Helps the map visual geocode unambiguously
    AddLoc   = Table.AddColumn(Typed, "MapLocation", each [State] & ", " & [Country], type text)
    // After load: set Country = Country/Region, State = State or Province, MapLocation = Place
in
    AddLoc
