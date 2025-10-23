'200311 oda ロボット/検査モジュール用のファイル作成
Imports Newtonsoft.Json

Class InspectionData : Inherits JsonData

    Public Data As New InspectionStructure

    Public Sub New()
    End Sub

    Public Sub New(partNumber As String)
        Data.Part_Number = partNumber
        MyBase.Init(Me.Data)
    End Sub

    Public Overrides Sub SetJsonSerial(setData As String, JsonFormat As Formatting)
        MyBase.SetJsonSerial(setData, JsonFormat)
        Data = DirectCast(MyBase.Core, InspectionStructure)
    End Sub

End Class
