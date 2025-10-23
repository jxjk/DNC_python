'200311 oda ロボット/検査モジュール用のファイル作成
Imports Newtonsoft.Json

MustInherit Class JsonData
    Protected Property Core

    Sub Init(ByRef JsonDataObject)
        Me.Core = JsonDataObject
    End Sub

    Function GetJsonSerial(JsonFormat As Formatting) As String
        Dim settings As New JsonSerializerSettings()
        settings.Formatting = JsonFormat
        Return JsonConvert.SerializeObject(Core, settings)
    End Function

    Overridable Sub SetJsonSerial(setData As String, JsonFormat As Formatting)
        Dim settings As New JsonSerializerSettings()
        settings.Formatting = JsonFormat
        Me.Core = JsonConvert.DeserializeObject(Of InspectionStructure)(setData, settings)
    End Sub

End Class
