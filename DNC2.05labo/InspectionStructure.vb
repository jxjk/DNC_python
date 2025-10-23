'200311 oda ロボット/検査モジュール用のファイル作成
Imports Newtonsoft.Json

Public Module CommonConst
    Public Const EMPTY_CODE As String = "999"
    Public Const EMPTY_TEXT As String = "-"
    Public Const EMPTY_ZERO As String = "00"
End Module

<JsonObject("Parameter")>
Public Structure Parameter
    <JsonProperty("Name")>
    Public Property Name As String

    <JsonProperty("Value")>
    Public Property Value As String

    Sub New(name As String, value As String, Optional emptyCodeZero As Boolean = False)
        Me.Name = name

        If value.Equals(EMPTY_CODE) Then
            If emptyCodeZero Then
                Me.Value = EMPTY_ZERO
            Else
                Me.Value = EMPTY_TEXT
            End If
        Else
            Me.Value = value
        End If
    End Sub
End Structure

<JsonObject("Feature")>
Public Class Feature

    <JsonProperty("Parameters")>
    Public Property Parameters As New List(Of Parameter)
End Class

<JsonObject("FeatureRecognitionResult")>
Public Class FeatureRecognitionResult

    <JsonProperty("Features")>
    Public Property Features As New List(Of Feature)
End Class

<JsonObject("InspectionStructure")>
Public Class InspectionStructure

#Region "Header"
    <JsonProperty("@Work_Kind")>
    Public Property Work_Kind As String

    <JsonProperty("@Part_Number")>
    Public Property Part_Number As String

    <JsonProperty("@Feature_Joined_ID")>
    Public ReadOnly Property Feature_Joined_ID As String
        Get
            Dim sb As New System.Text.StringBuilder
            For Each f As Feature In Me.FeatureRecognitionResult.Features
                For Each p As Parameter In f.Parameters
                    If p.Name.Equals("ID") Then
                        If p.Value.Equals(EMPTY_TEXT) Then
                            sb.Append("00")
                        Else
                            sb.Append(p.Value)
                        End If
                    End If
                Next
            Next
            Return sb.ToString()
        End Get
    End Property

    <JsonProperty("@Order_qty")>
    Public Property Order_qty As String

    <JsonProperty("@Material")>
    Public Property Material As String

    <JsonProperty("@Surface_Finish")>
    Public Property Surface_Finish As String

    <JsonProperty("@Heat_Treatment")>
    Public Property Heat_Treatment As String

    <JsonProperty("@Insertion_Guide")>
    Public Property Insertion_Guide As String

    <JsonProperty("@Outer_Diameter")>
    Public Property Outer_Diameter As String

    <JsonProperty("@Full_Length")>
    Public Property Full_Length As String
#End Region

#Region "FeatureRecognitionResult"
    Private _featureRecognitionResult As New FeatureRecognitionResult

    <JsonProperty("FeatureRecognitionResult")>
    Public Property FeatureRecognitionResult As FeatureRecognitionResult
        Get
            Return Me._featureRecognitionResult
        End Get
        Set(value As FeatureRecognitionResult)
            Me._featureRecognitionResult = value
        End Set
    End Property
#End Region

#Region "MeasurementMargin"
    <JsonProperty("MeasurementMargin")>
    Public Property MeasurementMargin As New List(Of Parameter)
#End Region

End Class

